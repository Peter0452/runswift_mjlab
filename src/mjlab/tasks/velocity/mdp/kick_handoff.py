"""Reset a fraction of walk envs from a live kick-tracker rollout.

The frozen stage-2 kick policy plays one clip from the first frame inside a
small tracking sim. The resulting root and joint state is copied onto the
walk robot, and that env's twist command starts at zero or within ±0.5 m/s
and ±0.5 rad/s. The walk policy being trained takes the next action. The
other envs keep the normal AMP motion reset.
"""

from __future__ import annotations

import copy
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

import torch

from mjlab.managers.event_manager import EventTermCfg
from mjlab.utils.logging import print_info

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_REPO = Path(__file__).resolve().parents[5]
DEFAULT_KICK_TASK = "Mjlab-Tracking-Flat-Booster-K1-Kick-Stage2"
DEFAULT_KICK_CKPTS = (
  _REPO / "logs/rsl_rl/k1_kick_tracking/2026-09-29_08-23-57/model_80000.pt",
)
DEFAULT_KICK_CKPT = DEFAULT_KICK_CKPTS[0]
_FALL_Z = 0.35


def select_handoff_ids(env_ids: torch.Tensor, fraction: float) -> torch.Tensor:
  """Pick which resetting envs play a kick before the walk policy starts."""
  if env_ids.numel() == 0 or fraction <= 0.0:
    return env_ids[:0]
  if fraction >= 1.0:
    return env_ids
  pick = torch.rand(env_ids.shape[0], device=env_ids.device) < fraction
  return env_ids[pick]


def sample_handoff_command(
  count: int,
  *,
  stand_prob: float,
  limit: float,
  device: torch.device | str,
) -> tuple[torch.Tensor, torch.Tensor]:
  """Stand, or a twist with each component inside ±``limit``.

  Returns ``(stand_mask, command)`` with ``command`` shaped ``(count, 3)``
  as linear x, linear y, yaw rate.
  """
  if count == 0:
    empty = torch.zeros(0, device=device)
    return empty.bool(), empty.reshape(0, 3)
  stand = torch.rand(count, device=device) < stand_prob
  small = (torch.rand(count, 3, device=device) * 2.0 - 1.0) * limit
  command = torch.where(stand.unsqueeze(-1), torch.zeros_like(small), small)
  return stand, command


class kick_handoff_reset:
  """Post-reset event: online kick rollout, then a stand or small walk command."""

  def __init__(self, cfg: EventTermCfg, env: ManagerBasedRlEnv):
    params = cfg.params
    self.fraction = float(params.get("fraction", 0.35))
    self.stand_prob = float(params.get("stand_prob", 0.5))
    self.cmd_limit = float(params.get("cmd_limit", 0.5))
    self.batch_size = int(params.get("batch_size", 32))
    self.kick_task = str(params.get("kick_task", DEFAULT_KICK_TASK))
    listed = params.get("kick_checkpoints")
    if listed is None:
      single = params.get("kick_checkpoint")
      listed = (single,) if single is not None else DEFAULT_KICK_CKPTS
    self.kick_checkpoints = tuple(Path(path) for path in listed)
    self._walk_env = env
    self._kick_env = None
    self._kick_policies: list = []
    self._joint_index: torch.Tensor | None = None
    self._calls = 0
    self.last_selected = 0
    self.last_applied = 0

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    del env_ids

  def close(self) -> None:
    if self._kick_env is not None:
      self._kick_env.close()
      self._kick_env = None
      self._kick_policies = []

  def __del__(self) -> None:
    try:
      self.close()
    except Exception:
      return

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | None,
    **params,
  ) -> None:
    del params
    if env_ids is None or self.fraction <= 0.0:
      return
    chosen = select_handoff_ids(env_ids, self.fraction)
    self.last_selected = int(chosen.numel())
    self.last_applied = 0
    if chosen.numel() == 0:
      return
    self._ensure_kick(env.device)
    applied = 0
    for start in range(0, int(chosen.numel()), self.batch_size):
      chunk = chosen[start : start + self.batch_size]
      applied += self._roll_and_copy(env, chunk)
    self.last_applied = applied
    self._calls += 1
    if self._calls == 1 or self._calls % 25 == 0:
      print_info(
        f"[kick_handoff] copied {applied}/{int(chosen.numel())} "
        f"kick endings into the walk env "
        f"(fraction {self.fraction:.2f}, cmd ±{self.cmd_limit:g} or stand)"
      )

  def _ensure_kick(self, device: torch.device | str) -> None:
    if self._kick_env is not None:
      return
    missing = [path for path in self.kick_checkpoints if not path.is_file()]
    if missing:
      raise FileNotFoundError(
        "Kick checkpoint for the walk handoff fine-tune was not found: "
        + ", ".join(str(path) for path in missing)
      )
    from mjlab.envs import ManagerBasedRlEnv
    from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
    from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
    from mjlab.tasks.tracking.tracking_env_cfg import VELOCITY_RANGE

    env_cfg = load_env_cfg(self.kick_task, play=True)
    env_cfg.scene.num_envs = self.batch_size
    env_cfg.terminations.pop("anchor_pos", None)
    env_cfg.terminations.pop("anchor_ori", None)
    env_cfg.terminations.pop("ee_body_pos", None)
    motion_cmd = env_cfg.commands["motion"]
    motion_cmd.debug_vis = False
    motion_cmd.sampling_mode = "start"
    motion_cmd.pose_range = {
      "x": (-0.05, 0.05),
      "y": (-0.05, 0.05),
      "z": (-0.01, 0.01),
      "roll": (-0.1, 0.1),
      "pitch": (-0.1, 0.1),
      "yaw": (-0.2, 0.2),
    }
    motion_cmd.velocity_range = dict(VELOCITY_RANGE)
    motion_cmd.joint_position_range = (-0.1, 0.1)
    motion_cmd.strike_pos_noise = (0.1, 0.1)
    motion_cmd.strike_vel_noise = (0.05, 0.05)
    if "goal" in env_cfg.commands:
      env_cfg.commands["goal"].debug_vis = False

    agent_cfg = load_rl_cfg(self.kick_task)
    kick_env = ManagerBasedRlEnv(cfg=env_cfg, device=str(device), render_mode=None)
    wrapped = RslRlVecEnvWrapper(kick_env, clip_actions=agent_cfg.clip_actions)
    runner_cls = load_runner_cls(self.kick_task) or MjlabOnPolicyRunner
    runner = runner_cls(wrapped, asdict(agent_cfg), device=str(device))
    policies = []
    last = len(self.kick_checkpoints) - 1
    for index, path in enumerate(self.kick_checkpoints):
      runner.load(
        str(path),
        load_cfg={"actor": True},
        strict=True,
        map_location=str(device),
      )
      policy = runner.get_inference_policy(device=str(device))
      # The runner keeps one actor. Copy every policy except the last, which
      # can stay on that module after its checkpoint is loaded.
      policies.append(policy if index == last else copy.deepcopy(policy).eval())
    self._kick_env = wrapped
    self._kick_policies = policies
    names = ", ".join(path.name for path in self.kick_checkpoints)
    print_info(
      f"[kick_handoff] loaded frozen kick policies {names} "
      f"({self.batch_size} rollout envs)"
    )

  def _roll_and_copy(self, env: ManagerBasedRlEnv, walk_ids: torch.Tensor) -> int:
    assert self._kick_env is not None and self._kick_policies
    kick = self._kick_env
    raw = kick.unwrapped
    count = int(walk_ids.numel())
    kick.reset()
    cmd = raw.command_manager.get_term("motion")
    starts = cmd.motion.clip_starts
    ends = cmd.motion.clip_ends
    if starts is None or ends is None:
      raise RuntimeError("Kick motion has no clip boundaries.")
    sub = torch.arange(count, device=raw.device)
    clip_ids = cmd._sample_clip_ids(count)
    frames = starts[clip_ids]
    clip_end = ends[clip_ids]

    def _frames(env_ids: torch.Tensor) -> torch.Tensor:
      del env_ids
      return frames

    orig_resample = cmd._resample_command
    orig_start = cmd._start_mode_frames
    cmd._start_mode_frames = _frames  # type: ignore[method-assign]
    try:
      cmd._resample_command(sub)
      raw.sim.forward()
      raw.observation_manager.reset(sub)
      raw.action_manager.reset(sub)
      hold_frame = cmd.time_steps.clone()
      hold_frame[sub] = clip_end - 1

      def _hold(env_ids: torch.Tensor) -> None:
        cmd.time_steps[env_ids] = hold_frame[env_ids]

      cmd._resample_command = _hold  # type: ignore[method-assign]
      obs = kick.get_observations()
      pick = torch.zeros(kick.num_envs, dtype=torch.long, device=raw.device)
      if len(self._kick_policies) > 1:
        pick[:count] = torch.randint(
          0, len(self._kick_policies), (count,), device=raw.device
        )
      saved = torch.zeros(count, dtype=torch.bool, device=raw.device)
      buf = self._empty_state(count, raw)
      max_steps = int((ends - starts).max().item()) + 5
      for _ in range(max_steps):
        on_last = cmd.time_steps[:count] >= (clip_end - 1)
        actions = self._kick_actions(obs, pick)
        obs, _, _, _ = kick.step(actions)
        newly = on_last & ~saved
        if bool(newly.any()):
          self._snapshot(raw, newly, buf)
          saved |= newly
        if bool(saved.all()):
          break
    finally:
      cmd._start_mode_frames = orig_start
      cmd._resample_command = orig_resample

    return self._write_walk_state(env, walk_ids, raw, saved, buf)

  def _kick_actions(self, obs, pick: torch.Tensor) -> torch.Tensor:
    """Actions for this step. ``pick`` chooses the checkpoint per env."""
    with torch.no_grad():
      chosen = self._kick_policies[0](obs)
      for index, policy in enumerate(self._kick_policies[1:], start=1):
        other = policy(obs)
        chosen = torch.where(pick.unsqueeze(-1) == index, other, chosen)
    return chosen

  def _empty_state(self, count: int, raw) -> dict[str, torch.Tensor]:
    robot = raw.scene["robot"]
    n_j = robot.data.joint_pos.shape[-1]
    device = raw.device
    return {
      "pos": torch.zeros(count, 3, device=device),
      "quat": torch.zeros(count, 4, device=device),
      "lin": torch.zeros(count, 3, device=device),
      "ang": torch.zeros(count, 3, device=device),
      "q": torch.zeros(count, n_j, device=device),
      "qd": torch.zeros(count, n_j, device=device),
    }

  def _snapshot(self, raw, newly: torch.Tensor, buf: dict[str, torch.Tensor]) -> None:
    robot = raw.scene["robot"]
    origin = raw.scene.env_origins[: newly.shape[0]]
    buf["pos"][newly] = (
      robot.data.root_link_pos_w[: newly.shape[0]][newly] - origin[newly]
    )
    buf["quat"][newly] = robot.data.root_link_quat_w[: newly.shape[0]][newly]
    buf["lin"][newly] = robot.data.root_link_lin_vel_w[: newly.shape[0]][newly]
    buf["ang"][newly] = robot.data.root_link_ang_vel_w[: newly.shape[0]][newly]
    buf["q"][newly] = robot.data.joint_pos[: newly.shape[0]][newly]
    buf["qd"][newly] = robot.data.joint_vel[: newly.shape[0]][newly]

  def _write_walk_state(
    self,
    env: ManagerBasedRlEnv,
    walk_ids: torch.Tensor,
    raw,
    saved: torch.Tensor,
    buf: dict[str, torch.Tensor],
  ) -> int:
    upright = saved & (buf["pos"][:, 2] >= _FALL_Z)
    if not bool(upright.any()):
      return 0
    ids = walk_ids[upright]
    robot = env.scene["robot"]
    kick_robot = raw.scene["robot"]
    q = buf["q"][upright]
    qd = buf["qd"][upright]
    q, qd = self._match_joints(kick_robot, robot, q, qd)
    limits = robot.data.soft_joint_pos_limits[ids]
    q = torch.maximum(torch.minimum(q, limits[:, :, 1]), limits[:, :, 0])
    origin = env.scene.env_origins[ids]
    pose = torch.cat((buf["pos"][upright] + origin, buf["quat"][upright]), dim=-1)
    vel = torch.cat((buf["lin"][upright], buf["ang"][upright]), dim=-1)
    robot.write_root_link_pose_to_sim(pose, env_ids=ids)
    robot.write_root_link_velocity_to_sim(vel, env_ids=ids)
    robot.write_joint_state_to_sim(q, qd, env_ids=ids)
    env.sim.forward()
    self._lift_sunk_feet(env, robot, ids)
    self._set_command(env, ids)
    return int(ids.numel())

  def _match_joints(self, kick_robot, walk_robot, q, qd):
    if self._joint_index is None:
      kick_names = list(kick_robot.joint_names)
      walk_names = list(walk_robot.joint_names)
      if kick_names == walk_names:
        self._joint_index = torch.arange(len(walk_names), device=q.device)
      else:
        self._joint_index = torch.tensor(
          [kick_names.index(name) for name in walk_names],
          device=q.device,
          dtype=torch.long,
        )
    index = self._joint_index
    return q[:, index], qd[:, index]

  def _lift_sunk_feet(self, env, robot, ids: torch.Tensor) -> None:
    try:
      foot_ids, _ = robot.find_sites(("left_foot", "right_foot"))
    except Exception:
      return
    foot_z = robot.data.site_pos_w[ids][:, foot_ids, 2]
    origin_z = env.scene.env_origins[ids, 2]
    sink = (origin_z.unsqueeze(-1) - foot_z).max(dim=-1).values
    lift = sink.clamp(min=0.0)
    if not bool((lift > 0.0).any()):
      return
    pos = robot.data.root_link_pos_w[ids].clone()
    quat = robot.data.root_link_quat_w[ids]
    pos[:, 2] += lift + 0.005
    robot.write_root_link_pose_to_sim(torch.cat((pos, quat), dim=-1), env_ids=ids)
    env.sim.forward()

  def _set_command(self, env: ManagerBasedRlEnv, ids: torch.Tensor) -> None:
    twist = env.command_manager.get_term("twist")
    stand, command = sample_handoff_command(
      int(ids.numel()),
      stand_prob=self.stand_prob,
      limit=self.cmd_limit,
      device=env.device,
    )
    twist.vel_command_b[ids, :3] = command
    twist.vel_command_w[ids] = command
    twist.is_standing_env[ids] = stand
    twist.is_heading_env[ids] = False
    twist.is_forward_env[ids] = False
    twist.is_world_env[ids] = False
