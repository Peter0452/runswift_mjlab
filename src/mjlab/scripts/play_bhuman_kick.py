"""Play B-Human's K1 kick policy (Booster Gym / Isaac Gym) in the stage-3 sim.

The B-Human policy (``K1_kick_inner.onnx``, MachineLearning/IsaacGymRL) is a
59 → 256 → 128 → 128 → 13 ELU MLP. It controls the 12 leg joints plus a gait
frequency, and expects its own observation layout (see ``t1_ball.py``
``_compute_observations`` and ``WalkingEngine.cpp``). This script runs it in
``Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`` (play mode) by building
those 59 inputs from the sim state every step and converting its leg targets
into our 22-D action. Arms are held at B-Human's fixed arm pose; the head is
driven by our scripted ball tracker as usual.

Differences from B-Human's training sim that remain: our MuJoCo K1 PD gains,
effort limits and ball (0.10 kg, r 0.08 m vs 0.29 kg, r 0.095 m); B-Human's
deployment also only switches to this policy within ~1.1 m of the ball (its
walk policy brings the robot there), so the ball spawns 0.4–1.5 m away by
default, like their training.

Example:
  uv run play-bhuman-kick
  uv run play-bhuman-kick --num-envs 16 --viewer viser --strong-kick always
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import onnx
import torch
import tyro
from onnx import numpy_helper

from mjlab.envs import ManagerBasedRlEnv
from mjlab.envs.mdp.actions import JointPositionAction
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg
from mjlab.tasks.velocity.mdp.kick_loop import KickLoopCommand
from mjlab.utils.lab_api.math import (
  quat_apply,
  quat_apply_inverse,
  wrap_to_pi,
  yaw_quat,
)
from mjlab.utils.torch import configure_torch_backends
from mjlab.viewer import NativeMujocoViewer, ViserPlayViewer

_TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
_DEFAULT_ONNX = Path(
  "../MachineLearning/IsaacGymRL/pre-trained/WalkAndKick/K1_kick_inner.onnx"
)

# B-Human leg order (URDF / Isaac Gym DOF order) with default pose and limits.
_LEGS: tuple[str, ...] = tuple(
  f"{side}_{j}"
  for side in ("Left", "Right")
  for j in (
    "Hip_Pitch",
    "Hip_Roll",
    "Hip_Yaw",
    "Knee_Pitch",
    "Ankle_Pitch",
    "Ankle_Roll",
  )
)
_LEG_DEFAULT = (-0.2, 0.0, 0.0, 0.4, -0.25, 0.0) * 2
_LEG_LOWER = (-3.0, -0.4, -1.0, 0.0, -0.87, -0.345) + (
  -3.0,
  -1.57,
  -1.0,
  0.0,
  -0.87,
  -0.345,
)
_LEG_UPPER = (2.21, 1.57, 1.0, 2.23, 0.345, 0.345) + (
  2.21,
  0.4,
  1.0,
  2.23,
  0.345,
  0.345,
)
# Arms are fixed joints in B-Human's URDF: shoulder roll baked in at ∓1.35 rad.
_ARM_POSE = {
  "Left_Shoulder_Pitch": 0.0,
  "Left_Shoulder_Roll": -1.35,
  "Left_Elbow_Pitch": 0.0,
  "Left_Elbow_Yaw": 0.0,
  "Right_Shoulder_Pitch": 0.0,
  "Right_Shoulder_Roll": 1.35,
  "Right_Elbow_Pitch": 0.0,
  "Right_Elbow_Yaw": 0.0,
}
_FEET = ("left_foot_link", "right_foot_link")
_SOLE_OFFSET = (0.0, 0.0, -0.038)

# K1_Ball.yaml normalization / gait / ball constants.
_CLIP_ACTIONS = 2.0
_DOF_VEL_SCALE = 0.1
_BALL_SCALE = 0.1
_FREQ_BASE = 1.5
_FREQ_CLIP = 0.5
_BALL_FRICTION = 0.3  # expected speed = sqrt(2 * 0.3 * range)
_BALL_VEL_MAX = 2.0  # WalkingEngine clips the ball velocity input to 2 m/s
_KICK_SPEED_RANGE = (0.5, 3.4)  # walkingEngine_k1.cfg kickVelocityRange (m/s)
_LONG_RANGE = 8.0  # our long bin; "auto" strong kicks start here


@dataclass
class BHumanKickPlayConfig:
  onnx_file: str = str(_DEFAULT_ONNX)
  """B-Human kick policy (59 inputs, 13 outputs)."""
  num_envs: int = 1
  device: str | None = None
  viewer: Literal["auto", "native", "viser"] = "auto"
  ball_distance: tuple[float, float] = (0.4, 1.5)
  """Ball spawn distance (m). B-Human trains and deploys this policy close."""
  strong_kick: Literal["auto", "always", "never"] = "auto"
  """Strong-kick flag: auto = for targets >= 8 m (our long bin)."""
  inaccurate_kick: bool = False
  """B-Human's "just hit the ball" flag (looser aim)."""
  perception: Literal["true", "camera"] = "true"
  """Ball input: "true" = exact sim ball (position and velocity, B-Human's
  training default); "camera" = the same camera model as our policy (seen only
  inside the head camera view, Gaussian noise 0.03 m + 5 % of distance, the
  task's dropout / delay; unseen -> the last detection, kept in world
  coordinates, i.e. with odometry; velocity estimated from detections)."""
  print_kicks: bool = True
  """Print each kick of env 0 (speed, aim error, target distance)."""


def _load_mlp(path: Path, device: str) -> torch.nn.Sequential:
  model = onnx.load(str(path))
  inits = {i.name: numpy_helper.to_array(i) for i in model.graph.initializer}
  layers: list[torch.nn.Module] = []
  idx = sorted(int(k.split(".")[0]) for k in inits if k.endswith(".weight"))
  for n, i in enumerate(idx):
    w = np.array(inits[f"{i}.weight"], copy=True)
    lin = torch.nn.Linear(w.shape[1], w.shape[0])
    lin.weight.data = torch.from_numpy(w)
    lin.bias.data = torch.from_numpy(np.array(inits[f"{i}.bias"], copy=True))
    layers.append(lin)
    if n < len(idx) - 1:
      layers.append(torch.nn.ELU())
  mlp = torch.nn.Sequential(*layers).to(device).eval()
  first = layers[0]
  last = layers[-1]
  assert isinstance(first, torch.nn.Linear) and isinstance(last, torch.nn.Linear)
  if first.in_features != 59 or last.out_features != 13:
    raise ValueError(
      f"{path.name}: expected 59 → 13, got {first.in_features} → {last.out_features}"
    )
  return mlp


class BHumanKickPolicy:
  """Builds B-Human's 59 inputs from the sim and returns our 22-D action."""

  def __init__(self, env: ManagerBasedRlEnv, cfg: BHumanKickPlayConfig):
    self.env = env
    self.cfg = cfg
    dev = env.device
    self.mlp = _load_mlp(Path(cfg.onnx_file), dev)
    self.robot = env.scene["robot"]
    self.ball = env.scene["ball"]
    cmd = env.command_manager.get_term("twist")
    term = env.action_manager.get_term("joint_pos")
    assert isinstance(cmd, KickLoopCommand)
    assert isinstance(term, JointPositionAction)
    assert torch.is_tensor(term._offset) and torch.is_tensor(term._scale)
    self.cmd = cmd
    self.term = term
    self.offset: torch.Tensor = term._offset
    self.scale: torch.Tensor = term._scale
    names = list(self.robot.joint_names)
    self.leg_ids = torch.tensor([names.index(n) for n in _LEGS], device=dev)
    self.feet_ids = [list(self.robot.body_names).index(n) for n in _FEET]
    targets = list(self.term._target_names)
    self.leg_cols = torch.tensor([targets.index(n) for n in _LEGS], device=dev)
    self.arm_cols = torch.tensor([targets.index(n) for n in _ARM_POSE], device=dev)
    self.arm_pose = torch.tensor(list(_ARM_POSE.values()), device=dev)
    self.leg_default = torch.tensor(_LEG_DEFAULT, device=dev)
    self.leg_lower = torch.tensor(_LEG_LOWER, device=dev)
    self.leg_upper = torch.tensor(_LEG_UPPER, device=dev)
    self.sole = torch.tensor(_SOLE_OFFSET, device=dev)
    n = env.num_envs
    self.phase = torch.zeros(n, device=dev)
    self.last_act = torch.zeros(n, 13, device=dev)  # obs "actions"
    self.freq_act = torch.zeros(n, device=dev)  # drives the gait (one step late)
    self.last_ball = torch.zeros(n, 2, device=dev)
    self.started = torch.zeros(n, dtype=torch.bool, device=dev)
    self.prev_kicks = torch.zeros(n, device=dev)

  def _camera_ball_w(self) -> tuple[torch.Tensor, torch.Tensor]:
    """Camera-limited ball estimate (world xy) and its velocity estimate."""
    cmd = self.cmd
    dev = self.env.device
    if not hasattr(self, "_est_w"):
      n = self.env.num_envs
      self._est_w = torch.zeros(n, 2, device=dev)
      self._est_vel = torch.zeros(n, 2, device=dev)
      self._est_prev = torch.zeros(n, 2, device=dev)
      self._est_valid = torch.zeros(n, dtype=torch.bool, device=dev)
    fresh = cmd.time_since_seen <= 1e-6  # detected this step (after dropout / delay)
    # Exactly the detection our policy gets this step (noise, dropout, delay
    # included): its level-frame ball, turned into world xy with the robot's
    # pose (B-Human's real ball model also uses odometry).
    yq = yaw_quat(self.robot.data.root_link_quat_w)
    det = torch.zeros(self.env.num_envs, 3, device=dev)
    det[:, :2] = cmd.masked_ball_b
    meas = self.robot.data.root_link_pos_w[:, :2] + quat_apply(yq, det)[:, :2]
    dt = self.env.step_dt
    new_vel = (meas - self._est_prev) / dt
    upd = fresh & self._est_valid
    self._est_vel = torch.where(
      upd.unsqueeze(-1), 0.7 * self._est_vel + 0.3 * new_vel, self._est_vel
    )
    self._est_vel = torch.where(
      (cmd.time_since_seen > 0.5).unsqueeze(-1), 0.0, self._est_vel
    )
    self._est_w = torch.where(fresh.unsqueeze(-1), meas, self._est_w)
    self._est_prev = torch.where(fresh.unsqueeze(-1), meas, self._est_prev)
    self._est_valid |= fresh
    reset = self.env.episode_length_buf == 0
    self._est_valid &= ~reset
    return self._est_w, self._est_vel

  def _ball_frame(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Ball pos / vel in B-Human's frame (between the soles, yaw only)."""
    data = self.robot.data
    feet_pos = data.body_link_pos_w[:, self.feet_ids]
    feet_quat = data.body_link_quat_w[:, self.feet_ids]
    sole = self.sole.expand(feet_pos.shape[0], 2, 3)
    origin = (feet_pos + quat_apply(feet_quat, sole)).mean(dim=1)
    yq = yaw_quat(data.root_link_quat_w)
    if self.cfg.perception == "camera":
      est_w, est_v = self._camera_ball_w()
      rel = torch.zeros_like(origin)
      rel[:, :2] = est_w - origin[:, :2]
      vel = torch.zeros_like(origin)
      vel[:, :2] = est_v
    else:
      rel = self.ball.data.root_link_pos_w - origin
      vel = self.ball.data.root_link_lin_vel_w.clone()
    rel[:, 2] = 0.0
    ball_b = quat_apply_inverse(yq, rel)[:, :2]
    vel[:, 2] = 0.0
    vel_b = quat_apply_inverse(yq, vel)[:, :2]
    speed = vel_b.norm(dim=-1, keepdim=True)
    vel_b = vel_b * (_BALL_VEL_MAX / speed.clamp(min=_BALL_VEL_MAX))
    yaw = torch.atan2(yq[:, 3], yq[:, 0]) * 2.0
    return ball_b, vel_b, yaw

  def _report_kicks(self) -> None:
    kicks = self.cmd._kicks
    if self.cfg.print_kicks and bool(kicks[0] > self.prev_kicks[0]):
      cos = float(self.cmd.kick_cos[0].clamp(-1.0, 1.0))
      print(
        f"[kick] speed {float(self.cmd.kick_speed[0]):.2f} m/s, "
        f"aim error {math.degrees(math.acos(cos)):.0f} deg, "
        f"target {float(self.cmd.target_dist[0]):.1f} m, "
        f"launch {math.degrees(float(self.cmd.kick_launch_angle[0])):.0f} deg"
      )
    self.prev_kicks[:] = kicks

  def __call__(self, obs) -> torch.Tensor:
    del obs
    env = self.env
    dt = env.step_dt
    data = self.robot.data
    ball_b, ball_vel_b, yaw = self._ball_frame()

    fresh = (env.episode_length_buf == 0) | ~self.started
    self.phase[fresh] = 0.0
    self.last_act[fresh] = 0.0
    self.freq_act[fresh] = 0.0
    self.last_ball[fresh] = ball_b[fresh]
    self.prev_kicks[fresh] = self.cmd._kicks[fresh]
    self.started[:] = True
    self._report_kicks()

    # Kick direction (relative to the robot's yaw) and requested ball speed.
    ball_w = self.ball.data.root_link_pos_w[:, :2]
    to_target = self.cmd.target_w - ball_w
    direction = wrap_to_pi(torch.atan2(to_target[:, 1], to_target[:, 0]) - yaw)
    dist = to_target.norm(dim=-1)
    if self.cfg.strong_kick == "always":
      strong = torch.ones_like(dist, dtype=torch.bool)
    elif self.cfg.strong_kick == "never":
      strong = torch.zeros_like(dist, dtype=torch.bool)
    else:
      strong = dist >= _LONG_RANGE
    lo, hi = _KICK_SPEED_RANGE
    speed = torch.sqrt(2.0 * _BALL_FRICTION * dist).clamp(lo, hi)
    speed = torch.where(strong, torch.full_like(speed, hi), speed)

    gait = torch.stack(
      (torch.cos(2 * math.pi * self.phase), torch.sin(2 * math.pi * self.phase)), -1
    )
    q = data.joint_pos[:, self.leg_ids] - self.leg_default
    qd = data.joint_vel[:, self.leg_ids] * _DOF_VEL_SCALE
    zeros = torch.zeros_like(dist).unsqueeze(-1)
    inaccurate = torch.full_like(zeros, float(self.cfg.inaccurate_kick))
    x = torch.cat(
      (
        data.projected_gravity_b,
        data.root_link_ang_vel_b,
        ball_b * _BALL_SCALE,
        (direction / math.pi).unsqueeze(-1),
        gait,
        q,
        qd,
        self.last_act,
        strong.float().unsqueeze(-1),
        zeros,  # over/undershoot (steal kicks only)
        inaccurate,
        ball_vel_b * _BALL_SCALE,
        zeros,  # ball vel z
        torch.sin(direction).unsqueeze(-1),
        torch.cos(direction).unsqueeze(-1),
        (speed * _BALL_SCALE).unsqueeze(-1),
        self.last_ball * _BALL_SCALE,
      ),
      dim=-1,
    )
    act = self.mlp(x).clamp(-_CLIP_ACTIONS, _CLIP_ACTIONS)

    # Leg targets as B-Human applies them, then into our action space.
    leg_target = (self.leg_default + act[:, :12]).clamp(self.leg_lower, self.leg_upper)
    target = self.offset.clone()
    target[:, self.leg_cols] = leg_target
    target[:, self.arm_cols] = self.arm_pose
    action = (target - self.offset) / self.scale

    # Gait clock: Isaac step k advances with the frequency from step k-1.
    freq = self.freq_act.clamp(-_FREQ_CLIP, _FREQ_CLIP) + _FREQ_BASE
    self.phase[:] = torch.fmod(self.phase + dt * freq, 1.0)
    self.freq_act[:] = self.last_act[:, 12]
    self.last_act[:] = act
    self.last_ball[:] = ball_b
    return action


def run(cfg: BHumanKickPlayConfig) -> None:
  configure_torch_backends()
  device = cfg.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
  env_cfg = load_env_cfg(_TASK, play=True)
  env_cfg.scene.num_envs = cfg.num_envs
  twist = env_cfg.commands["twist"]
  twist.ball_distance_range = cfg.ball_distance  # type: ignore[attr-defined]

  env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
  policy = BHumanKickPolicy(env, cfg)
  print(f"[INFO]: B-Human kick policy: {cfg.onnx_file}")
  vec_env = RslRlVecEnvWrapper(env)

  viewer = cfg.viewer
  if viewer == "auto":
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    viewer = "native" if has_display else "viser"
  if viewer == "native":
    NativeMujocoViewer(vec_env, policy).run()
  else:
    ViserPlayViewer(vec_env, policy).run()
  vec_env.close()


def main() -> None:
  import mjlab.tasks  # noqa: F401  (populates the task registry)

  cfg = tyro.cli(BHumanKickPlayConfig, args=sys.argv[1:], config=mjlab.TYRO_FLAGS)
  run(cfg)


if __name__ == "__main__":
  main()
