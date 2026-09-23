"""AMP observation group for kick tasks (keep kick resets; no motion spawn)."""

from __future__ import annotations

from mjlab.amp.curriculums import anneal_style_reward
from mjlab.managers import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.velocity import mdp


def with_kick_amp_obs_group(cfg, *, style_weight: float = 0.3):
  """Add legs+gravity AMP obs; leave kick ``reset_base`` / ball phase intact.

  Unlike velocity ``with_amp_obs_group``, does **not** replace resets with
  ``reset_from_pose_pool`` — Near needs ball/goal spawn and plant latch.
  """
  if cfg.curriculum is None:
    cfg.curriculum = {}
  cfg.curriculum["amp_style_weight"] = CurriculumTermCfg(
    func=anneal_style_reward,
    params={
      "start_weight": style_weight,
      "end_weight": style_weight,
      "start_step": 0,
      "end_step": 1,
    },
  )

  amp_joint_names = (
    r".*_Hip_.*",
    r".*_Knee_.*",
    r".*_Ankle_.*",
  )
  cfg.observations["amp"] = ObservationGroupCfg(
    terms={
      "joint_pos": ObservationTermCfg(
        func=mdp.joint_pos_rel,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=amp_joint_names)},
      ),
      "joint_vel": ObservationTermCfg(
        func=mdp.joint_vel_rel,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=amp_joint_names)},
      ),
      "base_lin_vel": ObservationTermCfg(func=mdp.base_lin_vel),
      "projected_gravity": ObservationTermCfg(func=mdp.projected_gravity),
    },
    concatenate_terms=True,
    enable_corruption=False,
  )
  return cfg
