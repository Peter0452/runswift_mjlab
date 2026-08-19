from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import torch

from mjlab.entity import Entity
from mjlab.managers.command_manager import CommandTerm, CommandTermCfg
from mjlab.utils.lab_api.math import (
  matrix_from_quat,
  quat_apply,
  wrap_to_pi,
)

if TYPE_CHECKING:
  import viser

  from mjlab.envs.manager_based_rl_env import ManagerBasedRlEnv
  from mjlab.viewer.debug_visualizer import DebugVisualizer


class UniformVelocityCommand(CommandTerm):
  cfg: UniformVelocityCommandCfg

  def __init__(self, cfg: UniformVelocityCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)

    if self.cfg.heading_command and self.cfg.ranges.heading is None:
      raise ValueError("heading_command=True but ranges.heading is set to None.")
    if self.cfg.ranges.heading and not self.cfg.heading_command:
      raise ValueError("ranges.heading is set but heading_command=False.")

    self.robot: Entity = env.scene[cfg.entity_name]

    self._command_dim = 4 if cfg.ranges.gait_frequency is not None else 3
    self.vel_command_b = torch.zeros(
      self.num_envs, self._command_dim, device=self.device
    )
    self.vel_command_w = torch.zeros(self.num_envs, 3, device=self.device)
    self.heading_target = torch.zeros(self.num_envs, device=self.device)
    self.heading_error = torch.zeros(self.num_envs, device=self.device)
    self.is_heading_env = torch.zeros(
      self.num_envs, dtype=torch.bool, device=self.device
    )
    self.is_standing_env = torch.zeros_like(self.is_heading_env)
    self.is_world_env = torch.zeros_like(self.is_heading_env)
    self.is_forward_env = torch.zeros_like(self.is_heading_env)

    self.metrics["error_vel_xy"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["error_vel_yaw"] = torch.zeros(self.num_envs, device=self.device)

    # Last non-zero gait Hz (restored when leaving still / joystick Zero).
    self._last_gait_freq = torch.zeros(self.num_envs, device=self.device)
    if cfg.ranges.gait_frequency is not None:
      lo, hi = cfg.ranges.gait_frequency
      self._last_gait_freq.fill_((lo + hi) * 0.5)

    # Set by create_gui() when the viewer is active.
    self._joystick_enabled: viser.GuiCheckboxHandle | None = None
    self._joystick_sliders: list[viser.GuiSliderHandle] = []
    self._joystick_get_env_idx: Callable[[], int] | None = None

    if cfg.grid_curriculum is not None and cfg.grid_curriculum.enabled:
      self._init_grid_curriculum()

  @property
  def command(self) -> torch.Tensor:
    return self.vel_command_b

  def _update_metrics(self) -> None:
    max_command_time = self.cfg.resampling_time_range[1]
    max_command_step = max_command_time / self._env.step_dt
    self.metrics["error_vel_xy"] += (
      torch.norm(
        self.vel_command_b[:, :2] - self.robot.data.root_link_lin_vel_b[:, :2], dim=-1
      )
      / max_command_step
    )
    self.metrics["error_vel_yaw"] += (
      torch.abs(self.vel_command_b[:, 2] - self.robot.data.root_link_ang_vel_b[:, 2])
      / max_command_step
    )
    if self.cfg.grid_curriculum is not None and self.cfg.grid_curriculum.enabled:
      self.metrics["grid_mean_lin_level"][:] = self._mean_lin_level
      self.metrics["grid_mean_ang_level"][:] = self._mean_ang_level
      self.metrics["grid_max_lin_level"][:] = self._max_lin_level
      self.metrics["grid_max_ang_level"][:] = self._max_ang_level

  def reset(self, env_ids: torch.Tensor | slice | None) -> dict[str, float]:
    assert isinstance(env_ids, torch.Tensor)
    # Booster updates the grid before clearing episode length / resampling.
    if self.cfg.grid_curriculum is not None and self.cfg.grid_curriculum.enabled:
      self._update_grid_curriculum(env_ids)
      self.filtered_lin_vel[env_ids] = 0.0
      self.filtered_ang_vel[env_ids] = 0.0
    return super().reset(env_ids)

  def _resample_command(self, env_ids: torch.Tensor) -> None:
    r = torch.empty(len(env_ids), device=self.device)
    grid = self.cfg.grid_curriculum
    if grid is not None and grid.enabled:
      self._resample_grid_commands(env_ids)
      if self.cfg.ranges.gait_frequency is not None:
        self.vel_command_b[env_ids, 3] = r.uniform_(*self.cfg.ranges.gait_frequency)
        self._last_gait_freq[env_ids] = self.vel_command_b[env_ids, 3]
    else:
      self.vel_command_b[env_ids, 0] = r.uniform_(*self.cfg.ranges.lin_vel_x)
      self.vel_command_b[env_ids, 1] = r.uniform_(*self.cfg.ranges.lin_vel_y)
      self.vel_command_b[env_ids, 2] = r.uniform_(*self.cfg.ranges.ang_vel_z)
      if self.cfg.ranges.gait_frequency is not None:
        self.vel_command_b[env_ids, 3] = r.uniform_(*self.cfg.ranges.gait_frequency)
        self._last_gait_freq[env_ids] = self.vel_command_b[env_ids, 3]
    if self.cfg.heading_command:
      assert self.cfg.ranges.heading is not None
      self.heading_target[env_ids] = r.uniform_(*self.cfg.ranges.heading)
      self.is_heading_env[env_ids] = r.uniform_(0.0, 1.0) <= self.cfg.rel_heading_envs
    self.is_standing_env[env_ids] = r.uniform_(0.0, 1.0) <= self.cfg.rel_standing_envs

    # Randomly assign world-frame envs.
    self.is_world_env[env_ids] = r.uniform_(0.0, 1.0) <= self.cfg.rel_world_envs
    # Copy sampled velocities as world-frame reference for world envs.
    self.vel_command_w[env_ids] = self.vel_command_b[env_ids, :3]

    # Forward-only envs: positive lin_vel_x, zero lateral and angular.
    # Disabled under grid curriculum (Booster samples omni from the grid).
    if grid is None or not grid.enabled:
      self.is_forward_env[env_ids] = r.uniform_(0.0, 1.0) <= self.cfg.rel_forward_envs
      fwd_ids = env_ids[self.is_forward_env[env_ids]]
      if len(fwd_ids) > 0:
        self.vel_command_b[fwd_ids, 0] = (
          self.vel_command_b[fwd_ids, 0].abs().clamp(min=0.3)
        )
        self.vel_command_b[fwd_ids, 1] = 0.0
        self.vel_command_b[fwd_ids, 2] = 0.0
    else:
      self.is_forward_env[env_ids] = False

    init_vel_mask = r.uniform_(0.0, 1.0) < self.cfg.init_velocity_prob
    init_vel_env_ids = env_ids[init_vel_mask]
    if len(init_vel_env_ids) > 0:
      root_pos = self.robot.data.root_link_pos_w[init_vel_env_ids]
      root_quat = self.robot.data.root_link_quat_w[init_vel_env_ids]
      lin_vel_b = self.robot.data.root_link_lin_vel_b[init_vel_env_ids]
      lin_vel_b[:, :2] = self.vel_command_b[init_vel_env_ids, :2]
      root_lin_vel_w = quat_apply(root_quat, lin_vel_b)
      root_ang_vel_b = self.robot.data.root_link_ang_vel_b[init_vel_env_ids]
      root_ang_vel_b[:, 2] = self.vel_command_b[init_vel_env_ids, 2]
      root_state = torch.cat(
        [root_pos, root_quat, root_lin_vel_w, root_ang_vel_b], dim=-1
      )
      self.robot.write_root_state_to_sim(root_state, init_vel_env_ids)

    # Standing envs: zero twist (and gait frequency if present).
    standing_ids = env_ids[self.is_standing_env[env_ids]]
    if len(standing_ids) > 0:
      self.vel_command_b[standing_ids, :] = 0.0
      self.vel_command_w[standing_ids, :] = 0.0
      if grid is not None and grid.enabled:
        self.env_curriculum_level[standing_ids] = 0
    # Booster still: freeze gait clock whenever twist magnitude is near zero.
    self._zero_gait_freq_when_still()

  def _init_grid_curriculum(self) -> None:
    grid = self.cfg.grid_curriculum
    assert grid is not None and grid.enabled
    n_lin = 1 + 2 * grid.lin_vel_levels
    n_ang = 1 + 2 * grid.ang_vel_levels
    self.curriculum_prob = torch.zeros(n_lin, n_ang, device=self.device)
    # Start mass at (0, 0) command level — easiest cell.
    self.curriculum_prob[grid.lin_vel_levels, grid.ang_vel_levels] = 1.0
    self.env_curriculum_level = torch.zeros(
      self.num_envs, 2, dtype=torch.long, device=self.device
    )
    self.filtered_lin_vel = torch.zeros(self.num_envs, 3, device=self.device)
    self.filtered_ang_vel = torch.zeros(self.num_envs, 3, device=self.device)
    self._mean_lin_level = 0.0
    self._mean_ang_level = 0.0
    self._max_lin_level = 0.0
    self._max_ang_level = 0.0
    for key in (
      "grid_mean_lin_level",
      "grid_mean_ang_level",
      "grid_max_lin_level",
      "grid_max_ang_level",
    ):
      self.metrics[key] = torch.zeros(self.num_envs, device=self.device)

  def _update_grid_filters(self) -> None:
    grid = self.cfg.grid_curriculum
    assert grid is not None
    w = grid.filter_weight
    lin = self.robot.data.root_link_lin_vel_b
    ang = self.robot.data.root_link_ang_vel_b
    self.filtered_lin_vel = w * lin + (1.0 - w) * self.filtered_lin_vel
    self.filtered_ang_vel = w * ang + (1.0 - w) * self.filtered_ang_vel

  def _update_grid_curriculum(self, env_ids: torch.Tensor) -> None:
    """Expand grid probability mass for successful long-horizon episodes."""
    grid = self.cfg.grid_curriculum
    assert grid is not None
    if len(env_ids) == 0:
      return

    max_steps = self._env.max_episode_length
    success = self._env.episode_length_buf[env_ids] > int(
      max_steps * (1.0 - grid.episode_length_toler)
    )
    success &= (
      torch.abs(self.filtered_lin_vel[env_ids, 0] - self.vel_command_b[env_ids, 0])
      < grid.lin_vel_x_toler
    )
    success &= (
      torch.abs(self.filtered_lin_vel[env_ids, 1] - self.vel_command_b[env_ids, 1])
      < grid.lin_vel_y_toler
    )
    success &= (
      torch.abs(self.filtered_ang_vel[env_ids, 2] - self.vel_command_b[env_ids, 2])
      < grid.ang_vel_yaw_toler
    )

    # Vectorized neighbor bump (Booster loops; same semantics).
    succ_ids = env_ids[success]
    if len(succ_ids) == 0:
      return
    xs = self.env_curriculum_level[succ_ids, 0] + grid.lin_vel_levels
    ys = self.env_curriculum_level[succ_ids, 1] + grid.ang_vel_levels
    rate = grid.update_rate
    n_lin, n_ang = self.curriculum_prob.shape
    for x, y in zip(xs.tolist(), ys.tolist(), strict=False):
      self.curriculum_prob[x, y] += rate
      if x > 0:
        self.curriculum_prob[x - 1, y] += rate
      if x < n_lin - 1:
        self.curriculum_prob[x + 1, y] += rate
      if y > 0:
        self.curriculum_prob[x, y - 1] += rate
      if y < n_ang - 1:
        self.curriculum_prob[x, y + 1] += rate
    self.curriculum_prob.clamp_(max=1.0)

  def _resample_grid_commands(self, env_ids: torch.Tensor) -> None:
    """Sample commands from Booster T1 grid curriculum probabilities."""
    grid = self.cfg.grid_curriculum
    assert grid is not None
    n = len(env_ids)
    flat = self.curriculum_prob.flatten()
    # Guard against all-zero (should not happen).
    if float(flat.sum()) <= 0.0:
      flat = flat + 1.0
    grid_idx = torch.multinomial(flat, n, replacement=True)
    n_ang = self.curriculum_prob.shape[1]
    # Row-major flatten of [lin, ang]: lin = idx // n_ang, ang = idx % n_ang.
    # (Booster's published code swaps these; we keep axes consistent with update.)
    lin_idx = torch.div(grid_idx, n_ang, rounding_mode="floor")
    ang_idx = grid_idx % n_ang
    lin_level = lin_idx - grid.lin_vel_levels
    ang_level = ang_idx - grid.ang_vel_levels
    self.env_curriculum_level[env_ids, 0] = lin_level
    self.env_curriculum_level[env_ids, 1] = ang_level

    self._mean_lin_level = float(
      torch.mean(self.env_curriculum_level[:, 0].abs().float())
    )
    self._mean_ang_level = float(
      torch.mean(self.env_curriculum_level[:, 1].abs().float())
    )
    self._max_lin_level = float(torch.max(self.env_curriculum_level[:, 0].abs()).item())
    self._max_ang_level = float(torch.max(self.env_curriculum_level[:, 1].abs()).item())

    jitter_x = torch.empty(n, device=self.device).uniform_(-0.5, 0.5)
    jitter_y = torch.empty(n, device=self.device).uniform_(-1.0, 1.0)
    jitter_z = torch.empty(n, device=self.device).uniform_(-0.5, 0.5)
    self.vel_command_b[env_ids, 0] = (
      lin_level.float() + jitter_x
    ) * grid.lin_vel_x_resolution
    self.vel_command_b[env_ids, 1] = (
      lin_level.abs().float() * jitter_y * grid.lin_vel_y_resolution
    )
    self.vel_command_b[env_ids, 2] = (
      ang_level.float() + jitter_z
    ) * grid.ang_vel_resolution

  def _update_command(self) -> None:
    if self.cfg.grid_curriculum is not None and self.cfg.grid_curriculum.enabled:
      self._update_grid_filters()

    if self.cfg.heading_command:
      self.heading_error = wrap_to_pi(self.heading_target - self.robot.data.heading_w)
      env_ids = self.is_heading_env.nonzero(as_tuple=False).flatten()
      self.vel_command_b[env_ids, 2] = torch.clip(
        self.cfg.heading_control_stiffness * self.heading_error[env_ids],
        min=self.cfg.ranges.ang_vel_z[0],
        max=self.cfg.ranges.ang_vel_z[1],
      )
    # World-frame envs: rotate world-frame linear vel into body frame.
    if self.is_world_env.any():
      w_ids = self.is_world_env.nonzero(as_tuple=False).flatten()
      heading = self.robot.data.heading_w[w_ids]
      cos_h = torch.cos(heading)
      sin_h = torch.sin(heading)
      vx_w = self.vel_command_w[w_ids, 0]
      vy_w = self.vel_command_w[w_ids, 1]
      self.vel_command_b[w_ids, 0] = cos_h * vx_w + sin_h * vy_w
      self.vel_command_b[w_ids, 1] = -sin_h * vx_w + cos_h * vy_w

    standing_env_ids = self.is_standing_env.nonzero(as_tuple=False).flatten()
    self.vel_command_b[standing_env_ids, :] = 0.0
    self.vel_command_w[standing_env_ids, :] = 0.0
    self._zero_gait_freq_when_still()

  def _zero_gait_freq_when_still(self) -> None:
    """Booster still: ``gait_frequency = 0`` when ``|cmd| < still_cmd_threshold``.

    Matches ``booster_gym`` zeroing ``gait_frequency`` for still envs so the
    open-loop gait clock / ``feet_swing`` freeze when twist is near zero
    (including joystick Zero with residual sampled frequency). Restores the
    last non-zero Hz when leaving still so play can walk again after Zero.
    """
    if self.cfg.ranges.gait_frequency is None or self._command_dim < 4:
      return
    speed = torch.norm(self.vel_command_b[:, :2], dim=1) + torch.abs(
      self.vel_command_b[:, 2]
    )
    still = speed < self.cfg.still_cmd_threshold
    moving = ~still
    # Remember commanded cadence while walking.
    active_freq = self.vel_command_b[:, 3] > 1.0e-8
    remember = moving & active_freq
    self._last_gait_freq[remember] = self.vel_command_b[remember, 3]
    self.vel_command_b[still, 3] = 0.0
    # Restore after Zero / near-zero twist without a resample.
    need_restore = moving & (self.vel_command_b[:, 3] <= 1.0e-8)
    self.vel_command_b[need_restore, 3] = self._last_gait_freq[need_restore]

  # GUI.

  def create_gui(
    self,
    name: str,
    server: viser.ViserServer,
    get_env_idx: Callable[[], int],
    on_change: Callable[[], None] | None = None,
    request_action: Callable[[str, Any], None] | None = None,
  ) -> None:
    """Create velocity joystick sliders in the Viser viewer."""
    from viser import Icon

    ranges = self.cfg.ranges

    axes = [
      ("lin_vel_x", ranges.lin_vel_x[1]),
      ("lin_vel_y", ranges.lin_vel_y[1]),
      ("ang_vel_z", ranges.ang_vel_z[1]),
    ]
    sliders: list = []

    with server.gui.add_folder(name.capitalize()):
      enabled = server.gui.add_checkbox("Enable", initial_value=False)

      for label, max_val in axes:
        max_input = server.gui.add_slider(
          f"Max {label}",
          initial_value=max_val,
          step=0.1,
          min=0.1,
          max=10.0,
        )
        slider = server.gui.add_slider(
          label,
          min=-max_val,
          max=max_val,
          step=0.05,
          initial_value=0.0,
        )

        @max_input.on_update
        def _(_ev, _s=slider, _m=max_input) -> None:
          _s.min = -_m.value
          _s.max = _m.value

        sliders.append(slider)

      zero_btn = server.gui.add_button("Zero", icon=Icon.SQUARE_X)

      @zero_btn.on_click
      def _(_) -> None:
        for s in sliders:
          s.value = 0.0

    # Store GUI state for compute() override.
    self._joystick_enabled = enabled
    self._joystick_sliders = sliders
    self._joystick_get_env_idx = get_env_idx

  def compute(self, dt: float) -> None:
    super().compute(dt)
    if self._joystick_enabled is not None and self._joystick_enabled.value:
      assert self._joystick_get_env_idx is not None
      idx = self._joystick_get_env_idx()
      for i, s in enumerate(self._joystick_sliders):
        self.vel_command_b[idx, i] = s.value
      # Joystick only sets vx/vy/wz; freeze gait clock when twist is still.
      self._zero_gait_freq_when_still()

  # Visualization.

  def _debug_vis_impl(self, visualizer: "DebugVisualizer") -> None:
    """Draw velocity command and actual velocity arrows."""
    env_indices = visualizer.get_env_indices(self.num_envs)
    if not env_indices:
      return

    cmds = self.command.cpu().numpy()
    base_pos_ws = self.robot.data.root_link_pos_w.cpu().numpy()
    base_quat_w = self.robot.data.root_link_quat_w
    base_mat_ws = matrix_from_quat(base_quat_w).cpu().numpy()
    lin_vel_bs = self.robot.data.root_link_lin_vel_b.cpu().numpy()
    ang_vel_bs = self.robot.data.root_link_ang_vel_b.cpu().numpy()

    scale = self.cfg.viz.scale
    z_offset = self.cfg.viz.z_offset

    for batch in env_indices:
      base_pos_w = base_pos_ws[batch]
      base_mat_w = base_mat_ws[batch]
      cmd = cmds[batch]
      lin_vel_b = lin_vel_bs[batch]
      ang_vel_b = ang_vel_bs[batch]

      # Skip if robot appears uninitialized (at origin).
      if np.linalg.norm(base_pos_w) < 1e-6:
        continue

      # Helper to transform local to world coordinates.
      def local_to_world(
        vec: np.ndarray, pos: np.ndarray = base_pos_w, mat: np.ndarray = base_mat_w
      ) -> np.ndarray:
        return pos + mat @ vec

      # Command linear velocity arrow (blue).
      cmd_lin_from = local_to_world(np.array([0, 0, z_offset]) * scale)
      cmd_lin_to = local_to_world(
        (np.array([0, 0, z_offset]) + np.array([cmd[0], cmd[1], 0])) * scale
      )
      visualizer.add_arrow(
        cmd_lin_from, cmd_lin_to, color=(0.2, 0.2, 0.6, 0.6), width=0.015
      )

      # Command angular velocity arrow (green).
      cmd_ang_from = cmd_lin_from
      cmd_ang_to = local_to_world(
        (np.array([0, 0, z_offset]) + np.array([0, 0, cmd[2]])) * scale
      )
      visualizer.add_arrow(
        cmd_ang_from, cmd_ang_to, color=(0.2, 0.6, 0.2, 0.6), width=0.015
      )

      # Actual linear velocity arrow (cyan).
      act_lin_from = local_to_world(np.array([0, 0, z_offset]) * scale)
      act_lin_to = local_to_world(
        (np.array([0, 0, z_offset]) + np.array([lin_vel_b[0], lin_vel_b[1], 0])) * scale
      )
      visualizer.add_arrow(
        act_lin_from, act_lin_to, color=(0.0, 0.6, 1.0, 0.7), width=0.015
      )

      # Actual angular velocity arrow (light green).
      act_ang_from = act_lin_from
      act_ang_to = local_to_world(
        (np.array([0, 0, z_offset]) + np.array([0, 0, ang_vel_b[2]])) * scale
      )
      visualizer.add_arrow(
        act_ang_from, act_ang_to, color=(0.0, 1.0, 0.4, 0.7), width=0.015
      )


@dataclass(kw_only=True)
class UniformVelocityCommandCfg(CommandTermCfg):
  entity_name: str
  heading_command: bool = False
  heading_control_stiffness: float = 1.0
  rel_standing_envs: float = 0.0
  still_cmd_threshold: float = 0.05
  """Zero ``gait_frequency`` when ``||vx,vy|| + |wz|`` is below this (Booster still)."""
  rel_heading_envs: float = 1.0
  rel_world_envs: float = 0.0
  """Fraction of environments that use world-frame velocity commands.
  World-frame envs sample linear velocity in world frame and rotate to body
  frame each step, so the command direction stays fixed in the world."""
  rel_forward_envs: float = 0.0
  """Fraction of environments that receive forward-only commands (positive
  lin_vel_x, zero lin_vel_y and ang_vel_z). Increases training coverage for
  straight-line walking, which is important for stair climbing."""
  init_velocity_prob: float = 0.0

  @dataclass
  class Ranges:
    lin_vel_x: tuple[float, float]
    lin_vel_y: tuple[float, float]
    ang_vel_z: tuple[float, float]
    heading: tuple[float, float] | None = None
    # When set, command is 4-D: [vx, vy, wz, gait_frequency_Hz].
    gait_frequency: tuple[float, float] | None = None

  ranges: Ranges

  @dataclass
  class GridCurriculumCfg:
    """Booster T1-style command grid curriculum.

    Starts probability mass at level (0, 0) ≈ near-zero commands and expands
    neighboring cells when an episode nearly times out with tracking within
    tolerance. See ``booster_gym/envs/T1.yaml`` ``commands.curriculum``.
    """

    enabled: bool = False
    update_rate: float = 0.1
    lin_vel_levels: int = 10
    ang_vel_levels: int = 10
    lin_vel_x_resolution: float = 0.2
    lin_vel_y_resolution: float = 0.1
    ang_vel_resolution: float = 0.2
    episode_length_toler: float = 0.1
    lin_vel_x_toler: float = 0.4
    lin_vel_y_toler: float = 0.2
    ang_vel_yaw_toler: float = 0.2
    filter_weight: float = 0.1

  grid_curriculum: GridCurriculumCfg | None = None

  @dataclass
  class VizCfg:
    z_offset: float = 0.2
    scale: float = 0.5

  viz: VizCfg = field(default_factory=VizCfg)

  def build(self, env: ManagerBasedRlEnv) -> UniformVelocityCommand:
    return UniformVelocityCommand(self, env)

  def __post_init__(self):
    if self.heading_command and self.ranges.heading is None:
      raise ValueError(
        "The velocity command has heading commands active (heading_command=True) but "
        "the `ranges.heading` parameter is set to None."
      )
