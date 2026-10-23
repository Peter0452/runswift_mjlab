"""AMP walking style for the B-Human kick port (optional, training only).

The discriminator sees the same leg features as our AMP walk (leg joint
positions relative to the default pose, leg joint velocities, projected
gravity) over ``num_steps`` policy steps, against the walking motion mix of
the gold AMP walk. Its style reward is added to the task reward only while
the robot walks to the ball (ball farther than ``near_ball`` and not kicked
yet), as in our own kick: near the ball the kick is free.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

from k1.robot.k1_whirlwind_constants import K1_JOINT_ORDER
from k1.tasks.bhuman.kick_command import BHumanKickCommand
from k1.tasks.bhuman.robot import DEFAULT_LEG_POS, LEG_JOINTS
from mjlab.amp.modules.amp import AMP
from mjlab.amp.modules.discriminator import Discriminator
from mjlab.motion import MotionLoader

WALK_DATASET = Path(__file__).resolve().parents[5] / "data" / "amp_mix_ww_cmu"
AUGMENTATIONS = [
  {"name": "mirror"},
  {"name": "speed", "percent": 10.0},
  {"name": "speed", "percent": -10.0},
  {"name": "speed", "percent": 20.0},
  {"name": "speed", "percent": -20.0},
]


class AmpStyle:
  def __init__(
    self,
    cmd: BHumanKickCommand,
    num_steps: int = 10,
    style_weight: float = 2.0,
    near_ball: float = 0.8,
    learning_rate: float = 1.0e-4,
    num_updates: int = 8,
    batch_size: int = 8192,
    dataset_root: Path = WALK_DATASET,
    device: str = "cuda:0",
  ):
    self.cmd = cmd
    self.style_weight = style_weight
    self.near_ball = near_ball
    self.num_updates = num_updates
    self.batch_size = batch_size
    self.dt = cmd.dt
    weights = None
    meta = dataset_root / "dataset_weights.json"
    if meta.is_file():
      weights = [float(w) for w in json.loads(meta.read_text())["weights"]]
    obs_dim = 12 + 12 + 3
    loader = MotionLoader(
      dataset_root=dataset_root,
      simulation_dt=self.dt,
      speed_factor=1.0,
      num_amp_obs_steps=num_steps,
      dataset_weights=weights,
      augmentations=AUGMENTATIONS,
      default_pose=torch.tensor(DEFAULT_LEG_POS, device=device),
      joint_indices=[K1_JOINT_ORDER.index(j) for j in LEG_JOINTS],
      include_base_lin_vel=False,
      include_base_ang_vel=False,
      include_projected_gravity=True,
      device=device,
    )
    disc = Discriminator(
      input_dim=obs_dim * num_steps,
      hidden_layer_sizes=[256, 128],
      reward_scale=1.0,
      reward_clamp_epsilon=1.0e-4,
      loss_type="bce",
      empirical_normalization=True,
      device=device,
    )
    self.amp = AMP(disc, loader, obs_dim, num_steps, device=device)
    self.optimizer = torch.optim.Adam(
      [
        {"params": disc.trunk.parameters(), "weight_decay": 1.0e-3},
        {"params": disc.linear.parameters(), "weight_decay": 1.0e-1},
      ],
      lr=learning_rate,
    )
    self.default = torch.tensor(DEFAULT_LEG_POS, device=device)

  def observation(self) -> torch.Tensor:
    """Current leg features (post-reset state for envs that just reset)."""
    robot = self.cmd.robot
    q = robot.data.joint_pos[:, self.cmd.leg_ids] - self.default
    qd = robot.data.joint_vel[:, self.cmd.leg_ids]
    return torch.cat((q, qd, robot.data.projected_gravity_b), -1)

  def start(self) -> None:
    self.amp.reset_history(self.observation())

  def reward(self, done: torch.Tensor) -> torch.Tensor:
    """Gated, weighted style reward for the step just taken (scaled by dt
    like the task terms)."""
    history = self.amp.process_step(self.observation(), done)
    style = self.amp.predict_style_reward(history)
    c = self.cmd
    walking = (c.ball_pos[:, :2].norm(dim=-1) > self.near_ball) & (
      c.ball_kicked_counter == 0
    )
    return self.style_weight * self.dt * style * walking.float()

  def update(self) -> dict[str, float]:
    policy_gen, expert_gen = self.amp.generators(self.num_updates, self.batch_size)
    stats = {"amp_loss": 0.0, "grad_pen": 0.0, "policy_pred": 0.0, "expert_pred": 0.0}
    for policy, expert in zip(policy_gen, expert_gen, strict=False):
      loss, pen, m = self.amp.compute_discriminator_batch(policy, expert)
      self.optimizer.zero_grad()
      (loss + pen).backward()
      self.optimizer.step()
      stats["amp_loss"] += loss.item() / self.num_updates
      stats["grad_pen"] += pen.item() / self.num_updates
      stats["policy_pred"] += float(m["policy_pred"]) / self.num_updates
      stats["expert_pred"] += float(m["expert_pred"]) / self.num_updates
    return stats

  def state_dict(self) -> dict:
    return {
      "discriminator": self.amp.discriminator.state_dict(),
      "optimizer": self.optimizer.state_dict(),
    }

  def load_state_dict(self, state: dict) -> None:
    self.amp.discriminator.load_state_dict(state["discriminator"])
    self.optimizer.load_state_dict(state["optimizer"])
