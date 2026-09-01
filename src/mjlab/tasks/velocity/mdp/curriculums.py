from __future__ import annotations

from typing import TYPE_CHECKING, Any, Required, TypedDict, cast

import numpy as np
import torch

from mjlab.entity import Entity
from mjlab.managers.curriculum_manager import CurriculumTermCfg


def htwk_velocity_levels(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | slice,
  command_name: str = "twist",
) -> float:
  """Grow HTWK command ranges while the current velocity is tracked."""
  del env_ids
  term = env.command_manager.get_term(command_name)
  if not getattr(term.cfg, "vel_curriculum", False):
    return float(getattr(term, "vel_scale", 1.0))
  error = term.metrics["error_vel_xy"].mean().item()
  if (
    error < term.cfg.vel_scale_error_thresh
    and term.vel_scale < 1.0
  ):
    term.vel_scale = min(1.0, term.vel_scale + term.cfg.vel_scale_step)
  return float(term.vel_scale)


def htwk_yaw_levels(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | slice,
  command_name: str = "twist",
) -> float:
  """Grow the commanded yaw range while yaw tracking remains reliable."""
  del env_ids
  term = env.command_manager.get_term(command_name)
  if not getattr(term.cfg, "yaw_curriculum", False):
    return float(getattr(term, "yaw_scale", 1.0))
  error = term.metrics["error_vel_yaw"].mean().item()
  if (
    error < term.cfg.yaw_scale_error_thresh
    and term.yaw_scale < 1.0
  ):
    term.yaw_scale = min(1.0, term.yaw_scale + term.cfg.yaw_scale_step)
  return float(term.yaw_scale)


def htwk_action_rate_curriculum(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | slice,
  command_name: str = "twist",
  term_name: str = "action_rate",
  start_weight: float = -0.1,
  end_weight: float = -1.0,
  error_thresh: float = 0.45,
  step: float = 3.0e-4,
) -> float:
  """Tighten action smoothness only after HTWK velocity tracking is good."""
  del env_ids
  command = env.command_manager.get_term(command_name)
  error = command.metrics["error_vel_xy"].mean().item()
  cfg = env.reward_manager.get_term_cfg(term_name)
  if env.common_step_counter == 0:
    cfg.weight = start_weight
  elif error < error_thresh and cfg.weight > end_weight:
    cfg.weight = max(end_weight, cfg.weight - step)
  return float(cfg.weight)


def htwk_shoulder_release(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor | slice,
  term_name: str = "shoulder_deviation",
  start_weight: float = -3.0,
  end_weight: float = -0.1,
  start_step: int = 60_000,
  end_step: int = 200_000,
) -> float:
  """Linearly release the teacher's shoulder lock in env-step units."""
  del env_ids
  step = env.common_step_counter
  if step <= start_step:
    weight = start_weight
  elif step >= end_step:
    weight = end_weight
  else:
    fraction = (step - start_step) / float(end_step - start_step)
    weight = start_weight + fraction * (end_weight - start_weight)
  cfg = env.reward_manager.get_term_cfg(term_name)
  cfg.weight = weight
  return float(weight)
from mjlab.managers.scene_entity_config import SceneEntityCfg

from .velocity_command import UniformVelocityCommandCfg

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv

_DEFAULT_SCENE_CFG = SceneEntityCfg("robot")


class penalty_scale_curriculum:
  """Holosoma T1-style adaptive penalty scaling from episode length.

  Scales a shared set of penalty reward weights by ``current_scale``:
  - start at ``initial_scale`` (typically 0.5)
  - if moving-average episode length < ``level_down_threshold`` → ``×(1-degree)``
  - if moving-average episode length > ``level_up_threshold`` → ``×(1+degree)``
  - clamp to ``[min_scale, max_scale]``

  Unlike staged ``reward_curriculum``, this never jumps 0.5→1.0 on a fixed step
  cliff; full strength only after many successful level-ups.
  """

  def __init__(self, cfg: CurriculumTermCfg, env: ManagerBasedRlEnv):
    params = cfg.params
    self.reward_names: list[str] = list(params["reward_names"])
    self.min_scale = float(params.get("min_scale", 0.5))
    self.max_scale = float(params.get("max_scale", 1.0))
    self.level_down_threshold = float(params.get("level_down_threshold", 150.0))
    self.level_up_threshold = float(params.get("level_up_threshold", 750.0))
    self.degree = float(params.get("degree", 0.001))
    self.current_scale = float(params.get("initial_scale", 0.5))
    self.num_compute_average_epl = max(
      1, int(params.get("num_compute_average_epl", 1000))
    )
    self.average_episode_length = 0.0

    self.original_weights: dict[str, float] = {}
    for name in self.reward_names:
      term_cfg = env.reward_manager.get_term_cfg(name)
      self.original_weights[name] = float(term_cfg.weight)
    self._apply_scale(env)

  def _apply_scale(self, env: ManagerBasedRlEnv) -> None:
    for name, original in self.original_weights.items():
      term_cfg = env.reward_manager.get_term_cfg(name)
      term_cfg.weight = original * self.current_scale

  def state_dict(self) -> dict[str, float]:
    """Persist the ramp so a resume does not restart at ``initial_scale``.

    Without this a resumed run silently trains against a different reward than
    the one it was configured with: every penalty in ``reward_names`` reverts to
    half strength and then re-ramps over ~1400 updates, so the policy first
    drifts to exploit the weaker penalties and is then punished for it while the
    objective is still moving.
    """
    return {
      "current_scale": self.current_scale,
      "average_episode_length": self.average_episode_length,
    }

  def load_state_dict(self, state: dict[str, float], env: ManagerBasedRlEnv) -> None:
    self.current_scale = float(state["current_scale"])
    self.average_episode_length = float(state["average_episode_length"])
    self._apply_scale(env)

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | slice,
    reward_names: list[str],
    **kwargs: Any,
  ) -> dict[str, torch.Tensor]:
    del reward_names, kwargs

    # Initial reset has no meaningful episode lengths yet.
    if env.common_step_counter == 0:
      return {
        "scale": torch.tensor(self.current_scale),
        "avg_episode_length": torch.tensor(self.average_episode_length),
      }

    if isinstance(env_ids, slice):
      lengths = env.episode_length_buf.to(dtype=torch.float)
    else:
      ids = env_ids.long()
      if ids.numel() == 0:
        return {
          "scale": torch.tensor(self.current_scale),
          "avg_episode_length": torch.tensor(self.average_episode_length),
        }
      lengths = env.episode_length_buf[ids].to(dtype=torch.float)

    batch_mean = float(lengths.mean().item())
    weight = min(float(lengths.numel()) / float(self.num_compute_average_epl), 1.0)
    self.average_episode_length = (
      self.average_episode_length * (1.0 - weight) + batch_mean * weight
    )

    if self.average_episode_length < self.level_down_threshold:
      self.current_scale *= 1.0 - self.degree
    elif self.average_episode_length > self.level_up_threshold:
      self.current_scale *= 1.0 + self.degree

    self.current_scale = float(
      max(self.min_scale, min(self.max_scale, self.current_scale))
    )
    self._apply_scale(env)

    return {
      "scale": torch.tensor(self.current_scale),
      "avg_episode_length": torch.tensor(self.average_episode_length),
    }


class nubots_terrain_mix_curriculum:
  """Ramp NuBots rough terrain mix when walk quality is stable.

  Starts at ``initial_proportions`` (flat / rough / wave) and switches to
  ``target_proportions`` once moving-average episode length exceeds
  ``ep_length_threshold`` and fall quality clears the configured gate:

  - If ``fell_over_rate_threshold`` is set: EMA ``fell_over`` rate must be below it.
  - Else if ``root_height_rate_threshold`` is set: EMA ``root_height`` rate must
    be below it (legacy Phase-0 gate).

  Optional ``restore_disturbances`` dict restores kick/push stds on ramp.
  """

  def __init__(self, cfg: CurriculumTermCfg, env: ManagerBasedRlEnv):
    params = cfg.params
    self.initial_proportions = np.array(params["initial_proportions"], dtype=float)
    self.target_proportions = np.array(params["target_proportions"], dtype=float)
    self.ep_length_threshold = float(params.get("ep_length_threshold", 600.0))
    self.root_height_rate_threshold = params.get("root_height_rate_threshold")
    self.fell_over_rate_threshold = params.get("fell_over_rate_threshold")
    self.failure_term_name = str(params.get("failure_term_name", "root_height"))
    if self.root_height_rate_threshold is not None:
      self.root_height_rate_threshold = float(self.root_height_rate_threshold)
    if self.fell_over_rate_threshold is not None:
      self.fell_over_rate_threshold = float(self.fell_over_rate_threshold)
    # Default legacy gate when neither is provided.
    if (
      self.root_height_rate_threshold is None and self.fell_over_rate_threshold is None
    ):
      self.root_height_rate_threshold = 0.02
    self.num_compute_average_epl = max(
      1, int(params.get("num_compute_average_epl", 2000))
    )
    self.restore_disturbances: dict[str, float] = dict(
      params.get("restore_disturbances") or {}
    )
    self.average_episode_length = 0.0
    self.root_height_rate = 0.0
    self.fell_over_rate = 0.0
    self.current_proportions = self.initial_proportions.copy()
    self.ramped = False
    self._apply_proportions(env)

  def _apply_proportions(self, env: ManagerBasedRlEnv) -> None:
    terrain = env.scene.terrain
    if terrain is None or terrain.terrain_origins is None:
      return
    proportions = self.current_proportions / self.current_proportions.sum()
    terrain.configure_env_origins(terrain.terrain_origins, proportions)

  def _restore_disturbances(self, env: ManagerBasedRlEnv) -> None:
    if not self.restore_disturbances:
      return
    try:
      kick = env.event_manager.get_term_cfg("kick_robot")
    except ValueError:
      kick = None
    if kick is not None:
      if "kick_lin_vel_std" in self.restore_disturbances:
        kick.params["kick_lin_vel_std"] = self.restore_disturbances["kick_lin_vel_std"]
      if "kick_ang_vel_std" in self.restore_disturbances:
        kick.params["kick_ang_vel_std"] = self.restore_disturbances["kick_ang_vel_std"]
    try:
      push = env.event_manager.get_term_cfg("push_robot")
    except ValueError:
      push = None
    if push is not None:
      if "push_force_std" in self.restore_disturbances:
        push.params["push_force_std"] = self.restore_disturbances["push_force_std"]
      if "push_torque_std" in self.restore_disturbances:
        push.params["push_torque_std"] = self.restore_disturbances["push_torque_std"]

  def _status(self, ramped: float) -> dict[str, torch.Tensor]:
    wave = (
      float(self.current_proportions[2]) if len(self.current_proportions) > 2 else 0.0
    )
    return {
      "ramped": torch.tensor(ramped),
      "flat_prop": torch.tensor(self.current_proportions[0]),
      "rough_prop": torch.tensor(self.current_proportions[1]),
      "wave_prop": torch.tensor(wave),
      "avg_episode_length": torch.tensor(self.average_episode_length),
      "root_height_rate": torch.tensor(self.root_height_rate),
      "fell_over_rate": torch.tensor(self.fell_over_rate),
    }

  def _gate_ok(self) -> bool:
    if self.average_episode_length <= self.ep_length_threshold:
      return False
    if self.fell_over_rate_threshold is not None:
      return self.fell_over_rate < self.fell_over_rate_threshold
    assert self.root_height_rate_threshold is not None
    return self.root_height_rate < self.root_height_rate_threshold

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | slice,
    **kwargs: Any,
  ) -> dict[str, torch.Tensor]:
    del kwargs

    if self.ramped:
      return self._status(1.0)

    if env.common_step_counter == 0:
      return self._status(0.0)

    if isinstance(env_ids, slice):
      lengths = env.episode_length_buf.to(dtype=torch.float)
      ids = torch.arange(env.num_envs, device=env.device)
    else:
      ids = env_ids.long()
      if ids.numel() == 0:
        return self._status(0.0)
      lengths = env.episode_length_buf[ids].to(dtype=torch.float)

    batch_mean = float(lengths.mean().item())
    weight = min(float(lengths.numel()) / float(self.num_compute_average_epl), 1.0)
    self.average_episode_length = (
      self.average_episode_length * (1.0 - weight) + batch_mean * weight
    )

    failure_term = env.termination_manager.get_term(self.failure_term_name)
    batch_root_rate = float(failure_term[ids].float().mean().item())
    self.root_height_rate = (
      self.root_height_rate * (1.0 - weight) + batch_root_rate * weight
    )

    if "fell_over" in env.termination_manager.active_terms:
      fell = env.termination_manager.get_term("fell_over")
      batch_fell = float(fell[ids].float().mean().item())
      self.fell_over_rate = self.fell_over_rate * (1.0 - weight) + batch_fell * weight

    if self._gate_ok():
      self.current_proportions = self.target_proportions.copy()
      self.ramped = True
      self._apply_proportions(env)
      self._restore_disturbances(env)

    return self._status(1.0 if self.ramped else 0.0)


class scheduled_terrain_mix_curriculum:
  """Apply fixed terrain proportions at configured PPO-iteration milestones."""

  def __init__(self, cfg: CurriculumTermCfg, env: ManagerBasedRlEnv):
    self.steps_per_iteration = max(1, int(cfg.params.get("steps_per_iteration", 24)))
    raw_stages = cfg.params["stages"]
    self.stages = [
      (int(stage["iteration"]), np.asarray(stage["proportions"], dtype=float))
      for stage in raw_stages
    ]
    self.stages.sort(key=lambda stage: stage[0])
    if not self.stages:
      raise ValueError("scheduled_terrain_mix_curriculum requires stages")
    self.current_stage = -1
    self.current_proportions = self.stages[0][1].copy()
    self._apply_stage(env, 0)

  def _apply_stage(self, env: ManagerBasedRlEnv, stage_idx: int) -> None:
    terrain = env.scene.terrain
    if terrain is None or terrain.terrain_origins is None:
      return
    proportions = self.stages[stage_idx][1]
    if proportions.sum() <= 0.0:
      raise ValueError("Terrain proportions must have a positive sum")
    terrain.configure_env_origins(
      terrain.terrain_origins, proportions / proportions.sum()
    )
    self.current_stage = stage_idx
    self.current_proportions = proportions.copy()

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | slice,
    **kwargs: Any,
  ) -> dict[str, torch.Tensor]:
    del env_ids, kwargs
    iteration = int(env.common_step_counter) // self.steps_per_iteration
    stage_idx = 0
    for idx, (start_iteration, _) in enumerate(self.stages):
      if iteration >= start_iteration:
        stage_idx = idx
      else:
        break
    if stage_idx != self.current_stage:
      self._apply_stage(env, stage_idx)
    proportions = self.current_proportions
    return {
      "stage": torch.tensor(float(stage_idx)),
      "iteration": torch.tensor(float(iteration)),
      "flat_prop": torch.tensor(float(proportions[0])),
      "rough_prop": torch.tensor(float(proportions[1])),
      "wave_prop": torch.tensor(float(proportions[2])),
    }


class clearance_terminate_curriculum:
  """Soft-start base-clearance termination while standing learns.

  Starts at ``initial_height`` (lenient) and creeps toward ``target_height``
  when moving-average episode length exceeds ``level_up_threshold``; softens
  again if lives collapse below ``level_down_threshold``.
  """

  def __init__(self, cfg: CurriculumTermCfg, env: ManagerBasedRlEnv):
    params = cfg.params
    self.term_name: str = str(params.get("term_name", "root_height"))
    self.param_key: str = str(params.get("param_key", "minimum_height"))
    self.initial_height = float(params.get("initial_height", 0.30))
    self.target_height = float(params.get("target_height", 0.43))
    self.min_height = float(params.get("min_height", self.initial_height))
    self.max_height = float(params.get("max_height", self.target_height))
    self.level_down_threshold = float(params.get("level_down_threshold", 80.0))
    self.level_up_threshold = float(params.get("level_up_threshold", 200.0))
    self.degree = float(params.get("degree", 0.002))
    self.num_compute_average_epl = max(
      1, int(params.get("num_compute_average_epl", 1000))
    )
    self.current_height = self.initial_height
    self.average_episode_length = 0.0
    self._apply(env)

  def _apply(self, env: ManagerBasedRlEnv) -> None:
    term_cfg = env.termination_manager.get_term_cfg(self.term_name)
    term_cfg.params[self.param_key] = self.current_height

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor | slice,
    **kwargs: Any,
  ) -> dict[str, torch.Tensor]:
    del kwargs

    if env.common_step_counter == 0:
      return {
        "minimum_height": torch.tensor(self.current_height),
        "avg_episode_length": torch.tensor(self.average_episode_length),
      }

    if isinstance(env_ids, slice):
      lengths = env.episode_length_buf.to(dtype=torch.float)
    else:
      ids = env_ids.long()
      if ids.numel() == 0:
        return {
          "minimum_height": torch.tensor(self.current_height),
          "avg_episode_length": torch.tensor(self.average_episode_length),
        }
      lengths = env.episode_length_buf[ids].to(dtype=torch.float)

    batch_mean = float(lengths.mean().item())
    weight = min(float(lengths.numel()) / float(self.num_compute_average_epl), 1.0)
    self.average_episode_length = (
      self.average_episode_length * (1.0 - weight) + batch_mean * weight
    )

    if self.average_episode_length < self.level_down_threshold:
      self.current_height -= self.degree * (self.target_height - self.min_height)
    elif self.average_episode_length > self.level_up_threshold:
      self.current_height += self.degree * (self.target_height - self.min_height)

    self.current_height = float(
      max(self.min_height, min(self.max_height, self.current_height))
    )
    self._apply(env)

    return {
      "minimum_height": torch.tensor(self.current_height),
      "avg_episode_length": torch.tensor(self.average_episode_length),
    }


class VelocityStage(TypedDict, total=False):
  """Command curriculum stage.

  Ranges left as ``None`` or omitted are unchanged. Optional ``rel_*`` fields
  update UniformVelocityCommand mode fractions when present.
  """

  step: Required[int]
  lin_vel_x: tuple[float, float] | None
  lin_vel_y: tuple[float, float] | None
  ang_vel_z: tuple[float, float] | None
  rel_forward_envs: float
  rel_standing_envs: float
  rel_heading_envs: float


def terrain_levels_vel(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor,
  command_name: str,
  asset_cfg: SceneEntityCfg = _DEFAULT_SCENE_CFG,
) -> dict[str, torch.Tensor]:
  asset: Entity = env.scene[asset_cfg.name]

  terrain = env.scene.terrain
  assert terrain is not None
  terrain_generator = terrain.cfg.terrain_generator
  assert terrain_generator is not None

  command = env.command_manager.get_command(command_name)
  assert command is not None

  # Compute the distance the robot walked.
  distance = torch.norm(
    asset.data.root_link_pos_w[env_ids, :2] - env.scene.env_origins[env_ids, :2],
    dim=1,
  )

  # Robots that walked far enough progress to harder terrains.
  move_up = distance > terrain_generator.size[0] / 2

  # Robots that walked less than half of their required distance go to
  # simpler terrains.
  move_down = (
    distance < torch.norm(command[env_ids, :2], dim=1) * env.max_episode_length_s * 0.5
  )
  move_down *= ~move_up

  # On the initial reset (before any env step) the robot is still at its spawn
  # pose rather than a walked-to position, so ``distance`` is meaningless and
  # would spuriously promote every env from level 0 to 1, ignoring
  # ``max_init_terrain_level``. Freeze levels on that first reset.
  if env.common_step_counter == 0:
    move_up = torch.zeros_like(move_up)
    move_down = torch.zeros_like(move_down)

  # Update terrain levels.
  terrain.update_env_origins(env_ids, move_up, move_down)

  # Compute per-terrain-type mean levels.
  levels = terrain.terrain_levels.float()
  result: dict[str, torch.Tensor] = {
    "mean": torch.mean(levels),
    "max": torch.max(levels),
  }

  # In curriculum mode num_cols == num_terrains (one column per type),
  # so the column index directly maps to the sub-terrain name.
  sub_terrain_names = list(terrain_generator.sub_terrains.keys())
  terrain_origins = terrain.terrain_origins
  assert terrain_origins is not None
  num_cols = terrain_origins.shape[1]
  if num_cols == len(sub_terrain_names):
    types = terrain.terrain_types
    for i, name in enumerate(sub_terrain_names):
      mask = types == i
      if mask.any():
        result[name] = torch.mean(levels[mask])

  return result


def commands_vel(
  env: ManagerBasedRlEnv,
  env_ids: torch.Tensor,
  command_name: str,
  velocity_stages: list[VelocityStage],
) -> dict[str, torch.Tensor]:
  del env_ids  # Unused.
  command_term = env.command_manager.get_term(command_name)
  assert command_term is not None
  cfg = cast(UniformVelocityCommandCfg, command_term.cfg)
  for stage in velocity_stages:
    if env.common_step_counter >= stage["step"]:
      if "lin_vel_x" in stage and stage["lin_vel_x"] is not None:
        cfg.ranges.lin_vel_x = stage["lin_vel_x"]
      if "lin_vel_y" in stage and stage["lin_vel_y"] is not None:
        cfg.ranges.lin_vel_y = stage["lin_vel_y"]
      if "ang_vel_z" in stage and stage["ang_vel_z"] is not None:
        cfg.ranges.ang_vel_z = stage["ang_vel_z"]
      if "rel_forward_envs" in stage:
        cfg.rel_forward_envs = float(stage["rel_forward_envs"])
      if "rel_standing_envs" in stage:
        cfg.rel_standing_envs = float(stage["rel_standing_envs"])
      if "rel_heading_envs" in stage:
        cfg.rel_heading_envs = float(stage["rel_heading_envs"])
  return {
    "lin_vel_x_min": torch.tensor(cfg.ranges.lin_vel_x[0]),
    "lin_vel_x_max": torch.tensor(cfg.ranges.lin_vel_x[1]),
    "lin_vel_y_min": torch.tensor(cfg.ranges.lin_vel_y[0]),
    "lin_vel_y_max": torch.tensor(cfg.ranges.lin_vel_y[1]),
    "ang_vel_z_min": torch.tensor(cfg.ranges.ang_vel_z[0]),
    "ang_vel_z_max": torch.tensor(cfg.ranges.ang_vel_z[1]),
    "rel_forward_envs": torch.tensor(cfg.rel_forward_envs),
    "rel_standing_envs": torch.tensor(cfg.rel_standing_envs),
    "rel_heading_envs": torch.tensor(cfg.rel_heading_envs),
  }
