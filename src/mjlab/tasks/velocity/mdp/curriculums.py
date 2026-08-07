from __future__ import annotations

from typing import TYPE_CHECKING, Any, Required, TypedDict, cast

import torch

from mjlab.entity import Entity
from mjlab.managers.curriculum_manager import CurriculumTermCfg
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
