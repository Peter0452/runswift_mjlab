"""B-Human's explicit leg PD (Booster Gym ``T1_Ball.step``).

Per physics substep (2 ms, decimation 10):

  tau = kp * (target - q) - kd * qd_filt
  tau -= min(friction, |tau|) * sign(tau)        # joint friction (0-2 Nm DR)
  tau = clip(tau, -torque_clip, torque_clip)     # 50/50/30/60/30/30 Nm

``qd_filt`` is a low-passed finite-difference velocity
(``0.78 * qd_filt + 0.22 * (q - q_prev) / dt``), not the simulator velocity.
The new target reaches the motor at substep ``delay`` of the policy step
(0-9, sampled per episode by the kick command); before that the previous
target is held. Gains are per env so the kick command can randomize them at
every reset. The unclipped torque, averaged over the substeps, feeds B-Human's
torque rewards (``torque_sum`` / ``torque_count``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import mujoco
import mujoco_warp as mjwarp
import torch

from mjlab.actuator.actuator import ActuatorCmd
from mjlab.actuator.pd_actuator import IdealPdActuator, IdealPdActuatorCfg

if TYPE_CHECKING:
  from mjlab.entity import Entity

_VEL_FILTER = 0.22  # weight of the new finite-difference sample


@dataclass(kw_only=True)
class BHumanPdActuatorCfg(IdealPdActuatorCfg):
  torque_clip: float
  """Hard torque clip (Nm); also the MuJoCo motor force range."""
  decimation: int = 10
  """Physics substeps per policy step (the target delay is 0..decimation-1)."""

  def build(
    self, entity: Entity, target_ids: list[int], target_names: list[str]
  ) -> BHumanPdActuator:
    return BHumanPdActuator(self, entity, target_ids, target_names)


class BHumanPdActuator(IdealPdActuator[BHumanPdActuatorCfg]):
  """Stateful explicit PD; overriding ``compute`` keeps it out of PD fusion."""

  def initialize(
    self,
    mj_model: mujoco.MjModel,
    model: mjwarp.Model,
    data: mjwarp.Data,
    device: str,
  ) -> None:
    super().initialize(mj_model, model, data, device)
    n = data.nworld
    k = len(self._target_names)
    z = torch.zeros(n, k, device=device)
    self.torque_clip = torch.full((n, k), self.cfg.torque_clip, device=device)
    self.friction = z.clone()
    self.delay = torch.zeros(n, dtype=torch.long, device=device)
    self.held_target = z.clone()
    self.prev_pos = z.clone()
    self.vel_fd = z.clone()
    self.vel_filt = z.clone()
    self.torque_sum = z.clone()
    self.torque_count = 0
    self._substep = 0
    self._needs_init = torch.ones(n, dtype=torch.bool, device=device)

  def reset(self, env_ids: torch.Tensor | slice | None = None) -> None:
    super().reset(env_ids)
    ids = slice(None) if env_ids is None else env_ids
    self.vel_fd[ids] = 0.0
    self.vel_filt[ids] = 0.0
    self._needs_init[ids] = True

  def compute(self, cmd: ActuatorCmd) -> torch.Tensor:
    assert self.stiffness is not None and self.damping is not None
    init = self._needs_init.clone()
    if bool(init.any()):
      # After a reset the motor holds the reset pose until the first target.
      self.prev_pos[init] = cmd.pos[init]
      self.held_target[init] = cmd.pos[init]
      self._needs_init[:] = False
    switch = (self.delay == self._substep % self.cfg.decimation) & ~init
    self.held_target = torch.where(
      switch.unsqueeze(-1), cmd.position_target, self.held_target
    )
    self._substep += 1
    tau = self.stiffness * (self.held_target - cmd.pos)
    tau = tau - self.damping * self.vel_filt
    tau = tau - torch.minimum(self.friction, tau.abs()) * torch.sign(tau)
    self.torque_sum += tau
    self.torque_count += 1
    return torch.clamp(tau, -self.torque_clip, self.torque_clip)

  def update(self, dt: float) -> None:
    pos = self.entity.data.joint_pos[:, self.target_ids]
    self.vel_fd = (pos - self.prev_pos) / dt
    self.vel_filt = self.vel_filt * (1.0 - _VEL_FILTER) + self.vel_fd * _VEL_FILTER
    self.prev_pos = pos.clone()

  def pop_mean_torque(self) -> torch.Tensor:
    """Unclipped torque averaged over the substeps since the last call."""
    mean = self.torque_sum / max(self.torque_count, 1)
    self.torque_sum = torch.zeros_like(self.torque_sum)
    self.torque_count = 0
    return mean

  def sync_substep(self) -> None:
    """Start a policy step: substep 0, empty torque average. Called by the
    action term, since the env also runs ``compute`` outside the physics loop
    (when it writes reset states)."""
    self._substep = 0
    self.torque_sum.zero_()
    self.torque_count = 0
