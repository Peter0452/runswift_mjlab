"""Curriculum terms for get-up tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
  from mjlab.envs import ManagerBasedRlEnv
  from mjlab.managers.curriculum_manager import CurriculumTermCfg


class speed_pressure_curriculum:
  """Linearly ramp a not-standing time-penalty weight over env steps.

  Port of ``booster_train`` ``k1_getup/curriculum.speed_pressure_curriculum``.
  Starts loose so the policy can discover any rise, then tightens so only fast
  per-posture paths survive.
  """

  def __init__(self, cfg: CurriculumTermCfg, env: ManagerBasedRlEnv):
    params = cfg.params
    self.term_name = str(params.get("term_name", "time_penalty"))
    self.start_weight = float(params.get("start_weight", -0.3))
    self.end_weight = float(params.get("end_weight", -5.0))
    self.start_step = int(params.get("start_step", 8_000))
    self.end_step = int(params.get("end_step", 50_000))
    self._term_cfg = env.reward_manager.get_term_cfg(self.term_name)
    self._term_cfg.weight = self.start_weight

  def __call__(
    self,
    env: ManagerBasedRlEnv,
    env_ids: torch.Tensor,
    term_name: str = "time_penalty",
    start_weight: float = -0.3,
    end_weight: float = -5.0,
    start_step: int = 8_000,
    end_step: int = 50_000,
  ) -> dict[str, torch.Tensor]:
    del env_ids, term_name, start_weight, end_weight, start_step, end_step
    s = env.common_step_counter
    if s <= self.start_step:
      w = self.start_weight
    elif s >= self.end_step:
      w = self.end_weight
    else:
      f = (s - self.start_step) / (self.end_step - self.start_step)
      w = self.start_weight + f * (self.end_weight - self.start_weight)
    self._term_cfg.weight = w
    return {"weight": torch.tensor(w)}
