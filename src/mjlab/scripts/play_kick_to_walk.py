"""Setup B: Walk → Kick → Walk play FSM in the Kick Near env.

Starts ~1.5 m from the ball under AMP Walk (``model_9950``), switches to Kick
when inside the kick zone, then back to Walk after post-kick settle.

Example:
  uv run --no-sync python -m mjlab.scripts.play_kick_to_walk --viewer viser
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import torch
import tyro
from tensordict import TensorDict

from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.kick.mdp.ball_phase import ensure_ball_phase_updated
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.lab_api.math import quat_apply_inverse, wrap_to_pi, yaw_quat
from mjlab.utils.torch import configure_torch_backends
from mjlab.viewer import NativeMujocoViewer, ViserPlayViewer

_DEFAULT_KICK_TASK = "Mjlab-Kick-Near-Amp-Booster-K1"
_DEFAULT_WALK_TASK = "Mjlab-Velocity-Flat-Amp-DA-Muon-Booster-K1"
_DEFAULT_WALK_CKPT = Path(
  "logs/rsl_rl/k1_velocity_amp_symmetric_muon_wwcmu50_roughft/"
  "2026-09-21_20-34-24_stageA/model_9950.pt"
)
_DEFAULT_SETTLE_S = 1.0

# Phase ids (per-env int).
_PHASE_APPROACH = 0  # Walk in from spawn
_PHASE_KICK = 1  # Kick policy
_PHASE_EXIT = 2  # Walk after settle

# Kick Near leg action order (12-D).
_KICK_LEG_JOINTS: tuple[str, ...] = (
  "Left_Hip_Pitch",
  "Right_Hip_Pitch",
  "Left_Hip_Roll",
  "Right_Hip_Roll",
  "Left_Hip_Yaw",
  "Right_Hip_Yaw",
  "Left_Knee_Pitch",
  "Right_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Right_Ankle_Pitch",
  "Left_Ankle_Roll",
  "Right_Ankle_Roll",
)

# AMP Walk full-body action / joint-pos order (22-D).
_WALK_JOINTS: tuple[str, ...] = (
  "Head_Yaw",
  "Head_Pitch",
  "Left_Shoulder_Pitch",
  "Left_Shoulder_Roll",
  "Left_Elbow_Pitch",
  "Left_Elbow_Yaw",
  "Right_Shoulder_Pitch",
  "Right_Shoulder_Roll",
  "Right_Elbow_Pitch",
  "Right_Elbow_Yaw",
  "Left_Hip_Pitch",
  "Left_Hip_Roll",
  "Left_Hip_Yaw",
  "Left_Knee_Pitch",
  "Left_Ankle_Pitch",
  "Left_Ankle_Roll",
  "Right_Hip_Pitch",
  "Right_Hip_Roll",
  "Right_Hip_Yaw",
  "Right_Knee_Pitch",
  "Right_Ankle_Pitch",
  "Right_Ankle_Roll",
)

_WALK_UPPER_JOINTS: tuple[str, ...] = _WALK_JOINTS[:10]


def _latest_kick_checkpoint(log_root: Path) -> Path:
  """Newest existing ``model_*.pt`` under ``k1_kick_approach`` (by mtime)."""
  root = (log_root / "k1_kick_approach").resolve()
  if not root.is_dir():
    raise FileNotFoundError(f"No kick log dir at {root}")
  candidates: list[tuple[float, int, Path]] = []
  for path in root.glob("**/model_*.pt"):
    try:
      if not path.is_file():
        continue
      mtime = path.stat().st_mtime
    except OSError:
      continue
    try:
      step = int(path.stem.split("_")[1])
    except (IndexError, ValueError):
      step = -1
    candidates.append((mtime, step, path))
  if not candidates:
    raise FileNotFoundError(f"No model_*.pt under {root}")
  candidates.sort(key=lambda t: (t[0], t[1]))
  return candidates[-1][2]


def _resolve_scale_dict(
  scale: float | dict[str, float], joint_names: tuple[str, ...]
) -> torch.Tensor:
  """Match ``BaseAction`` scale dict (regex keys) onto ``joint_names``."""
  out = torch.ones(len(joint_names), dtype=torch.float32)
  if isinstance(scale, (float, int)):
    out[:] = float(scale)
    return out
  for i, name in enumerate(joint_names):
    for pattern, value in scale.items():
      if re.fullmatch(pattern, name):
        out[i] = float(value)
        break
  return out


@dataclass(frozen=True)
class KickToWalkPlayConfig:
  kick_task: str = _DEFAULT_KICK_TASK
  walk_task: str = _DEFAULT_WALK_TASK
  kick_checkpoint: str | None = None
  """Kick ``.pt``. Default: latest under ``logs/rsl_rl/k1_kick_approach``."""
  walk_checkpoint: str = str(_DEFAULT_WALK_CKPT)
  """AMP Walk ``model_9950`` (75-D / 22-D)."""
  settle_time_s: float = _DEFAULT_SETTLE_S
  spawn_radius_m: float = 1.5
  """Robot–ball spawn distance (m)."""
  kick_enter_m: float = 0.55
  """Walk→Kick when ball distance ≤ this (Near outer spawn)."""
  approach_speed: float = 0.9
  """Body-frame approach speed while Walk is closing on the ball."""
  approach_yaw_gain: float = 2.0
  approach_turn_speed: float = 1.2
  exit_vx: float = 0.0
  """Twist ``vx`` seeded once at Kick→Walk exit (then joystick owns cmd)."""
  num_envs: int | None = 1
  device: str | None = None
  viewer: Literal["auto", "native", "viser"] = "auto"
  no_terminations: bool = False
  log_root: str = "logs/rsl_rl"


class WalkKickWalkFsmPolicy:
  """Walk approach → Kick → Walk exit (hard switches)."""

  def __init__(
    self,
    *,
    env: RslRlVecEnvWrapper,
    kick_policy,
    walk_policy,
    settle_time_s: float,
    kick_enter_m: float,
    approach_speed: float,
    approach_yaw_gain: float,
    approach_turn_speed: float,
    exit_vx: float,
    walk_scale_legs: torch.Tensor,
    kick_scale: torch.Tensor,
    walk_scale_full: torch.Tensor,
    walk_leg_indices: torch.Tensor,
    walk_upper_indices: torch.Tensor,
  ) -> None:
    self.env = env
    self.kick_policy = kick_policy
    self.walk_policy = walk_policy
    self.settle_time_s = float(settle_time_s)
    self.kick_enter_m = float(kick_enter_m)
    self.approach_speed = float(approach_speed)
    self.approach_yaw_gain = float(approach_yaw_gain)
    self.approach_turn_speed = float(approach_turn_speed)
    self.exit_vx = float(exit_vx)
    self.walk_scale_legs = walk_scale_legs
    self.kick_scale = kick_scale
    self.walk_scale_full = walk_scale_full.to(env.device)
    self.walk_leg_indices = walk_leg_indices
    self.walk_upper_indices = walk_upper_indices
    n = env.num_envs
    device = env.device
    self._phase = torch.full(
      (n,), _PHASE_APPROACH, dtype=torch.long, device=device
    )
    self._last_walk_action = torch.zeros(n, len(_WALK_JOINTS), device=device)
    self._leg_scale_ratio = (self.walk_scale_legs / self.kick_scale).to(device)
    self._prev_ep_len = torch.zeros(n, dtype=torch.long, device=device)

  def _raw_env(self) -> ManagerBasedRlEnv:
    return self.env.unwrapped

  def _ball_dist(self) -> torch.Tensor:
    raw = self._raw_env()
    robot_xy = raw.scene["robot"].data.root_link_pos_w[:, :2]
    ball_xy = raw.scene["ball"].data.root_link_pos_w[:, :2]
    return torch.linalg.norm(ball_xy - robot_xy, dim=-1)

  def _free_arms(self, env_ids: torch.Tensor) -> None:
    if env_ids.numel() == 0:
      return
    robot = self._raw_env().scene["robot"]
    q = robot.data.joint_pos[env_ids][:, self.walk_upper_indices]
    robot.set_joint_position_target(
      q, joint_ids=self.walk_upper_indices, env_ids=env_ids
    )

  def _apply_walk_upper_body(
    self, a_walk: torch.Tensor, env_ids: torch.Tensor
  ) -> None:
    if env_ids.numel() == 0:
      return
    robot = self._raw_env().scene["robot"]
    default_q = robot.data.default_joint_pos
    assert default_q is not None
    idx = self.walk_upper_indices
    a_u = a_walk[env_ids][:, idx]
    scale = self.walk_scale_full[idx]
    q_des = a_u * scale + default_q[env_ids][:, idx]
    robot.set_joint_position_target(q_des, joint_ids=idx, env_ids=env_ids)

  def _set_twist(
    self,
    env_ids: torch.Tensor,
    vx: torch.Tensor | float,
    vy: torch.Tensor | float,
    wz: torch.Tensor | float,
    *,
    standing: bool = False,
  ) -> None:
    if env_ids.numel() == 0:
      return
    twist = self._raw_env().command_manager.get_term("twist")
    if isinstance(vx, (float, int)):
      twist.vel_command_b[env_ids, 0] = float(vx)
    else:
      twist.vel_command_b[env_ids, 0] = vx
    if isinstance(vy, (float, int)):
      twist.vel_command_b[env_ids, 1] = float(vy)
    else:
      twist.vel_command_b[env_ids, 1] = vy
    if isinstance(wz, (float, int)):
      twist.vel_command_b[env_ids, 2] = float(wz)
    else:
      twist.vel_command_b[env_ids, 2] = wz
    if twist.vel_command_b.shape[1] > 3:
      twist.vel_command_b[env_ids, 3] = 0.0
    if hasattr(twist, "is_standing_env"):
      twist.is_standing_env[env_ids] = standing
    if hasattr(twist, "vel_command_w"):
      twist.vel_command_w[env_ids, :] = 0.0
      twist.vel_command_w[env_ids, 0] = twist.vel_command_b[env_ids, 0]

  def _drive_approach(self, env_ids: torch.Tensor) -> None:
    """Body-frame Walk cmd toward the ball + yaw to face it."""
    if env_ids.numel() == 0:
      return
    raw = self._raw_env()
    robot = raw.scene["robot"]
    ball = raw.scene["ball"]
    root_quat = robot.data.root_link_quat_w[env_ids]
    delta_w = torch.zeros(env_ids.numel(), 3, device=raw.device)
    delta_w[:, :2] = (
      ball.data.root_link_pos_w[env_ids, :2]
      - robot.data.root_link_pos_w[env_ids, :2]
    )
    dist = torch.linalg.norm(delta_w[:, :2], dim=-1).clamp(min=1e-3)
    delta_b = quat_apply_inverse(yaw_quat(root_quat), delta_w)
    heading_err = wrap_to_pi(torch.atan2(delta_b[:, 1], delta_b[:, 0]))
    wz = (
      self.approach_yaw_gain * heading_err
    ).clamp(-self.approach_turn_speed, self.approach_turn_speed)
    # Forward component along body-x toward ball; soften when bearing is large.
    face = (heading_err.abs() < 0.8).float()
    speed = self.approach_speed * (0.35 + 0.65 * face)
    dir_b = delta_b[:, :2] / dist.unsqueeze(-1)
    vx = speed * dir_b[:, 0]
    vy = speed * dir_b[:, 1] * 0.35  # light lateral; prefer yaw
    self._set_twist(env_ids, vx, vy, wz, standing=False)

  def _update_phase(self) -> torch.Tensor:
    raw = self._raw_env()
    ep = raw.episode_length_buf
    reset = ep < self._prev_ep_len
    self._prev_ep_len = ep.clone()
    if bool(reset.any()):
      self._phase[reset] = _PHASE_APPROACH
      self._last_walk_action[reset] = 0.0
      n_r = int(reset.sum().item())
      print(f"[Walk↔Kick] reset → APPROACH n={n_r}")

    state = ensure_ball_phase_updated(raw, ball_cfg_name="ball")
    assert state.kick_detected is not None
    assert state.time_since_kick_s is not None
    dist = self._ball_dist()

    # APPROACH → KICK
    to_kick = (self._phase == _PHASE_APPROACH) & (dist <= self.kick_enter_m)
    if bool(to_kick.any()):
      print(
        f"[Walk↔Kick] APPROACH→KICK n={int(to_kick.sum().item())}  "
        f"d≤{self.kick_enter_m:.2f}m  (free arms)"
      )
      self._phase[to_kick] = _PHASE_KICK

    # KICK → EXIT
    settled = state.kick_detected & (
      state.time_since_kick_s >= self.settle_time_s
    )
    to_exit = (self._phase == _PHASE_KICK) & settled
    if bool(to_exit.any()):
      t_mean = float(state.time_since_kick_s[to_exit].mean().item())
      print(
        f"[Walk↔Kick] KICK→EXIT n={int(to_exit.sum().item())}  "
        f"t_since_kick≈{t_mean:.2f}s  seed_vx={self.exit_vx:.2f}"
      )
      self._phase[to_exit] = _PHASE_EXIT
      self._last_walk_action[to_exit] = 0.0
      ids = to_exit.nonzero(as_tuple=False).flatten()
      self._set_twist(
        ids,
        self.exit_vx,
        0.0,
        0.0,
        standing=abs(self.exit_vx) < 1e-3,
      )

    # Kick teacher off whenever Walk owns the body.
    walk_own = self._phase != _PHASE_KICK
    raw._setup_b_walk_mode = walk_own

    # Free arms every Kick step.
    kick_ids = (self._phase == _PHASE_KICK).nonzero(as_tuple=False).flatten()
    self._free_arms(kick_ids)

    # Approach: drive Walk cmd toward ball every frame.
    approach_ids = (self._phase == _PHASE_APPROACH).nonzero(
      as_tuple=False
    ).flatten()
    self._drive_approach(approach_ids)

    return self._phase

  def _build_walk_obs(self) -> TensorDict:
    raw = self._raw_env()
    robot = raw.scene["robot"]
    default_q = robot.data.default_joint_pos
    assert default_q is not None
    q = robot.data.joint_pos_biased - default_q
    default_qd = robot.data.default_joint_vel
    assert default_qd is not None
    qd = robot.data.joint_vel - default_qd
    twist = raw.command_manager.get_term("twist")
    cmd = twist.vel_command_b[:, :3]
    actor = torch.cat(
      (
        robot.data.root_link_ang_vel_b,
        robot.data.projected_gravity_b,
        q,
        qd,
        self._last_walk_action,
        cmd,
      ),
      dim=-1,
    )
    assert actor.shape[-1] == 75, f"expected 75-D walk obs, got {actor.shape[-1]}"
    return TensorDict({"actor": actor}, batch_size=[raw.num_envs])

  def _walk_actions_to_kick(self, a_walk: torch.Tensor) -> torch.Tensor:
    return a_walk[:, self.walk_leg_indices] * self._leg_scale_ratio

  def __call__(self, obs: TensorDict) -> torch.Tensor:
    phase = self._update_phase()
    use_walk = phase != _PHASE_KICK
    a_kick = self.kick_policy(obs)

    if not bool(use_walk.any()):
      return a_kick

    walk_obs = self._build_walk_obs()
    a_walk = self.walk_policy(walk_obs)
    self._last_walk_action = torch.where(
      use_walk.unsqueeze(-1), a_walk, self._last_walk_action
    )
    walk_ids = use_walk.nonzero(as_tuple=False).flatten()
    self._apply_walk_upper_body(a_walk, walk_ids)
    a_from_walk = self._walk_actions_to_kick(a_walk)
    return torch.where(use_walk.unsqueeze(-1), a_from_walk, a_kick)


def _load_policy(task_id: str, ckpt: Path, device: str, num_envs: int = 1):
  env_cfg = load_env_cfg(task_id, play=True)
  env_cfg.scene.num_envs = num_envs
  agent_cfg = load_rl_cfg(task_id)
  env = ManagerBasedRlEnv(cfg=env_cfg, device=device, render_mode=None)
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
  runner_cls = load_runner_cls(task_id) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(
    str(ckpt), load_cfg={"actor": True}, strict=True, map_location=device
  )
  policy = runner.get_inference_policy(device=device)
  return policy, env, agent_cfg


def run_kick_to_walk_play(cfg: KickToWalkPlayConfig) -> None:
  configure_torch_backends()
  device = cfg.device or ("cuda:0" if torch.cuda.is_available() else "cpu")

  kick_ckpt = (
    Path(cfg.kick_checkpoint)
    if cfg.kick_checkpoint is not None
    else _latest_kick_checkpoint(Path(cfg.log_root))
  )
  walk_ckpt = Path(cfg.walk_checkpoint)
  if not kick_ckpt.exists():
    raise FileNotFoundError(f"Kick checkpoint not found: {kick_ckpt}")
  if not walk_ckpt.exists():
    raise FileNotFoundError(f"Walk checkpoint not found: {walk_ckpt}")

  r = float(cfg.spawn_radius_m)
  print(f"[INFO]: Kick ckpt: {kick_ckpt}")
  print(f"[INFO]: Walk ckpt: {walk_ckpt}  (75-D AMP)")
  print(
    f"[INFO]: Walk→Kick→Walk  spawn≈{r:.2f}m  "
    f"enter≤{cfg.kick_enter_m:.2f}m  settle={cfg.settle_time_s:.2f}s  "
    f"approach_v={cfg.approach_speed:.2f}"
  )

  print(f"[INFO]: Loading Walk policy from {cfg.walk_task} …")
  walk_policy, walk_env, _ = _load_policy(
    cfg.walk_task, walk_ckpt, device, num_envs=1
  )

  env_cfg = load_env_cfg(cfg.kick_task, play=True)
  kick_agent_cfg = load_rl_cfg(cfg.kick_task)
  if cfg.no_terminations:
    env_cfg.terminations = {}
    print("[INFO]: Terminations disabled")
  if cfg.num_envs is not None:
    env_cfg.scene.num_envs = cfg.num_envs

  # Start outside Near kick band; Walk closes the gap.
  if "reset_base" in env_cfg.events:
    env_cfg.events["reset_base"].params["radius_range"] = (r * 0.95, r * 1.05)
    env_cfg.events["reset_base"].params["spawn_on_approach_side"] = True
    print(
      f"[INFO]: Spawn radius_range="
      f"{env_cfg.events['reset_base'].params['radius_range']}"
    )

  env = ManagerBasedRlEnv(cfg=env_cfg, device=device, render_mode=None)
  env = RslRlVecEnvWrapper(env, clip_actions=kick_agent_cfg.clip_actions)

  kick_runner_cls = load_runner_cls(cfg.kick_task) or MjlabOnPolicyRunner
  kick_runner = kick_runner_cls(env, asdict(kick_agent_cfg), device=device)
  kick_runner.load(
    str(kick_ckpt), load_cfg={"actor": True}, strict=True, map_location=device
  )
  kick_policy = kick_runner.get_inference_policy(device=device)

  walk_env_cfg = load_env_cfg(cfg.walk_task, play=True)
  walk_scale_full = _resolve_scale_dict(
    walk_env_cfg.actions["joint_pos"].scale, _WALK_JOINTS
  )
  kick_scale = _resolve_scale_dict(
    env_cfg.actions["joint_pos"].scale, _KICK_LEG_JOINTS
  )
  walk_leg_indices = torch.tensor(
    [_WALK_JOINTS.index(n) for n in _KICK_LEG_JOINTS], dtype=torch.long
  )
  walk_upper_indices = torch.tensor(
    [_WALK_JOINTS.index(n) for n in _WALK_UPPER_JOINTS],
    dtype=torch.long,
    device=device,
  )
  walk_scale_legs = walk_scale_full[walk_leg_indices]

  policy = WalkKickWalkFsmPolicy(
    env=env,
    kick_policy=kick_policy,
    walk_policy=walk_policy,
    settle_time_s=cfg.settle_time_s,
    kick_enter_m=cfg.kick_enter_m,
    approach_speed=cfg.approach_speed,
    approach_yaw_gain=cfg.approach_yaw_gain,
    approach_turn_speed=cfg.approach_turn_speed,
    exit_vx=cfg.exit_vx,
    walk_scale_legs=walk_scale_legs,
    kick_scale=kick_scale,
    walk_scale_full=walk_scale_full,
    walk_leg_indices=walk_leg_indices.to(device),
    walk_upper_indices=walk_upper_indices,
  )

  if cfg.viewer == "auto":
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    resolved_viewer = "native" if has_display else "viser"
  else:
    resolved_viewer = cfg.viewer

  try:
    if resolved_viewer == "native":
      NativeMujocoViewer(env, policy).run()
    elif resolved_viewer == "viser":
      ViserPlayViewer(env, policy).run()
    else:
      raise RuntimeError(f"Unsupported viewer backend: {resolved_viewer}")
  finally:
    env.close()
    walk_env.close()


def main() -> None:
  import mjlab.tasks  # noqa: F401

  args = tyro.cli(
    KickToWalkPlayConfig,
    default=KickToWalkPlayConfig(),
    prog="play-kick-to-walk",
    config=__import__("mjlab").TYRO_FLAGS,
  )
  run_kick_to_walk_play(args)


if __name__ == "__main__":
  main()
