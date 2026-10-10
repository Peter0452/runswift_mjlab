"""Kick benchmark v2 (2026-10-07): the policy as the robot runs it, per situation.

Deployment-faithful by construction: the stage-3 env now applies the runner's
joint-target clip, B-Human's torque clip, the ball in the between-feet ground
frame, the lost-ball rule and the scripted head. On top of that each run fixes
the conditions that used to be averaged away:

  caps        low (0.5 / 0.3 / 0.6, runswift's) and high (2.0 / 1.5 / 1.5, ours)
  perception  camera (the head-camera model), world (a fresh ball at any bearing,
              as a team-ball / localisation feed would give), perfect (diagnostic)
  delay       zero and typical (2-8 physics steps = 10-40 ms)

Tracks (one episode per robot; every fall counts, from t = 0):
  near_grid   runswift's 36 near-ball tasks x 3 yaw perturbations, standing start
  close_any   ball 0.4-1.5 m at any bearing, walking start (B-Human's kick range)
  approach    ball 2-10 m at any bearing incl. behind, standing start; by bearing
  goal_grid   runswift's 90 goal-scoring approaches (manifest positions)
  full_loop   30 s kick loop on flat ground; push / bumps / moving / late
              detections variants (full size only)

usage:
  python scripts/tools/kick_bench2.py run NAME (CK | bhuman) [--size quick|full]
  python scripts/tools/kick_bench2.py compare NAME_A NAME_B
Results: docs/benchmarks_v2/NAME.json
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import torch

os.environ["KICK_EVAL"] = "1"  # no mid-kick starts in evaluation

import mjlab.tasks  # noqa: F401  # isort: skip
from mjlab.envs import ManagerBasedRlEnv
from mjlab.managers.event_manager import EventTermCfg
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.velocity import mdp as vmdp
from mjlab.tasks.velocity.config.k1_amp.env_cfgs import DEPLOY_Q_LIMITS
from mjlab.utils.lab_api.math import quat_apply_inverse, yaw_quat

TASK = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
DEV = "cuda:0"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "benchmarks_v2"
GOAL_GRID = (
  ROOT.parent / "runswift/benchmarks/results/2026-10-02/k1-score-grid/manifest.json"
)
CAPS = {"low": (0.5, 0.3, 0.6), "high": (2.0, 1.5, 1.5)}
DELAYS = {"zero": (0, 0), "typical": (2, 8)}
BALL_R = 0.08
# Benchmark balls (mass kg, radius m): the corners of the training range.
BALLS = {"large": (0.45, 0.13), "small": (0.05, 0.07)}
LEG = ("Hip_Pitch", "Hip_Roll", "Hip_Yaw", "Knee_Pitch", "Ankle_Pitch", "Ankle_Roll")
TORQUE_LIMIT = {"Hip_Pitch": 50, "Hip_Roll": 50, "Hip_Yaw": 30, "Knee_Pitch": 60}
TORQUE_LIMIT |= {"Ankle_Pitch": 30, "Ankle_Roll": 30}


@dataclass
class Run:
  """One env build: a track under one perception / delay setting."""

  track: str
  perception: str = "camera"
  delay: str = "typical"
  n: int = 512
  seconds: float = 12.0
  start: str = "stand"  # stand | walk
  terrain: str = "flat"  # flat | bumps
  variant: str = ""  # full_loop: push | moving | late_detect
  extra: dict = field(default_factory=dict)

  @property
  def key(self) -> str:
    v = f"/{self.variant}" if self.variant else ""
    if self.extra.get("heavy"):
      v += "/heavy"
    if self.extra.get("ball"):
      v += "/" + self.extra["ball"]
    return f"{self.track}{v}/{self.perception}/{self.delay}"


def plan(size: str, bhuman: bool) -> list[Run]:
  if size == "screen":
    # Evolution screen (~2 min): aim, approach / falls, the loop.
    return [
      Run("near_grid", "camera", "typical", n=216),
      # Ball sizes are an objective (2026-10-08): credit them in the screen.
      Run("near_grid", "camera", "typical", n=216, extra={"ball": "large"}),
      Run("approach", "camera", "typical", n=512, seconds=20.0),
      Run("approach", "world", "typical", n=256, seconds=6.0, variant="behind"),
      Run("full_loop", "camera", "typical", n=512, seconds=30.0, start="walk"),
    ]
  q = size == "quick"
  runs = [
    Run("near_grid", "perfect", "typical", n=216),
    Run("near_grid", "camera", "typical", n=216),
  ]
  if not q:
    runs += [
      Run("near_grid", "perfect", "zero", n=216),
      Run("near_grid", "camera", "zero", n=216),
    ]
  runs += [Run("close_any", "camera", "typical", n=256 if q else 1024, start="walk")]
  if not q:
    # Heavy ball (runswift's heavy-large / B-Human's training ball).
    runs += [
      Run("near_grid", "camera", "typical", n=216, extra={"heavy": True}),
      Run("near_grid", "perfect", "zero", n=216, extra={"heavy": True}),
      Run(
        "close_any", "camera", "typical", n=1024, start="walk", extra={"heavy": True}
      ),
    ]
    # Ball sizes (user 2026-10-08: training balls 0.07-0.13 m, 0.05-0.45 kg).
    runs += [
      Run("near_grid", "camera", "typical", n=216, extra={"ball": "large"}),
      Run(
        "close_any", "camera", "typical", n=1024, start="walk", extra={"ball": "large"}
      ),
      Run("near_grid", "camera", "typical", n=216, extra={"ball": "small"}),
    ]
  if not q:
    runs += [Run("close_any", "perfect", "typical", n=1024, start="walk")]
  if bhuman:
    return runs  # B-Human: kick league only (it has no approach of its own)
  runs += [Run("approach", "camera", "typical", n=256 if q else 1024, seconds=20.0)]
  if not q:
    runs += [
      Run("approach", "world", "typical", n=1024, seconds=20.0),
      Run("approach", "camera", "zero", n=1024, seconds=20.0),
      Run("goal_grid", "camera", "typical", n=180, seconds=115.0),
      Run("goal_grid", "world", "typical", n=180, seconds=115.0),
      Run("goal_grid", "world", "zero", n=180, seconds=115.0),
      Run("goal_grid", "camera", "typical", n=180, seconds=115.0, variant="unknown"),
      Run("approach", "camera", "typical", n=1024, seconds=20.0, variant="unknown"),
      Run("approach", "world", "typical", n=512, seconds=6.0, variant="behind"),
    ]
  runs += [
    Run(
      "full_loop", "camera", "typical", n=256 if q else 1024, seconds=30.0, start="walk"
    )
  ]
  if not q:
    for v, terrain in (("push", "flat"), ("moving", "flat"), ("late_detect", "flat")):
      runs.append(
        Run("full_loop", "camera", "typical", n=1024, seconds=30.0, start="walk",
            variant=v, terrain=terrain)
      )  # fmt: skip
    runs.append(
      Run("full_loop", "camera", "typical", n=1024, seconds=30.0, start="walk",
          variant="bumps", terrain="bumps")
    )  # fmt: skip
    # Quiet steps (2026-10-08): its own track so a champion gets the landing
    # metrics without re-running the others (they are measured everywhere).
    runs.append(
      Run("full_loop", "camera", "typical", n=512, seconds=30.0, start="walk",
          variant="landing")
    )  # fmt: skip
    runs.append(
      Run("full_loop", "camera", "typical", n=1024, seconds=30.0, start="walk",
          variant="robust")
    )  # fmt: skip
  return runs


# ---------------------------------------------------------------------------
# Environment


def make_env(run: Run, policy: str):
  import dataclasses

  from mjlab.tasks.velocity.config.k1_amp import env_cfgs as ec

  heavy = run.extra.get("heavy", False)
  mass, radius = BALLS.get(
    run.extra.get("ball", ""), (ec_defaults["mass"], ec_defaults["radius"])
  )
  ec._APPROACH_BALL_MASS = 0.29 if heavy else mass
  ec._APPROACH_BALL_RADIUS = 0.095 if heavy else radius

  cfg = load_env_cfg(TASK, play=False)
  cfg.scene.num_envs = run.n
  cfg.seed = int(os.environ.get("BENCH2_SEED", "1"))
  torch.manual_seed(cfg.seed)
  cfg.episode_length_s = run.seconds + 5.0
  keep_push = run.variant == "push"
  for k in (
    "push_near_ball",
    "ball_relocate_unseen",
    "ball_mass",
    "ball_friction",
    "stand_start",
  ):
    cfg.events.pop(k, None)
  cfg.events.pop("ball_bounce", None)
  if not keep_push:
    cfg.events.pop("push_robot", None)
  else:
    push = cfg.events["push_robot"]
    push.params["velocity_range"] = {
      "x": (-0.6, 0.6), "y": (-0.6, 0.6), "roll": (-0.6, 0.6), "pitch": (-0.6, 0.6),
    }  # fmt: skip
    push.interval_range_s = (2.0, 3.0)
  if run.start == "stand":
    cfg.events.pop("reset_robot_from_motion", None)
  # Nominal robot, like the runner's sim (robot randomization only in the
  # "robust" variant); no training head scan (the runner never scans).
  if run.variant != "robust":
    for k in ("pd_gains", "encoder_bias", "trunk_inertia", "limb_inertia",
              "foot_friction", "terrain_contact"):  # fmt: skip
      cfg.events.pop(k, None)
  cfg.actions["joint_pos"].scan_share = 0.0  # ty: ignore[unresolved-attribute]
  if run.terrain == "flat":
    assert cfg.scene.terrain is not None
    cfg.scene.terrain.terrain_type = "plane"
    cfg.scene.terrain.terrain_generator = None
  robot = cfg.scene.entities["robot"]
  lo, hi = DELAYS[run.delay]
  robot.articulation = dataclasses.replace(
    robot.articulation,
    actuators=tuple(
      dataclasses.replace(a, delay_min_lag=lo, delay_max_lag=hi)
      for a in robot.articulation.actuators
    ),
  )
  tw = cfg.commands["twist"]
  tw.resampling_time_range = (1.0e6, 1.0e6)
  tw.side_drill_prob = 0.0
  if run.perception in ("world", "perfect"):
    tw.fov_half_angle = math.pi
    tw.fov_vertical_half_angle = None
  if run.perception == "perfect":
    tw.ball_obs_noise = (0.0, 0.0)
    tw.vision_dropout = 0.0
    tw.vision_delay_steps = (0, 0)
    tw.ball_origin_jitter = 0.0
  if run.variant == "late_detect":
    tw.vision_delay_steps = (3, 6)
  if run.variant == "moving":
    tw.ball_spawn_speed = (0.0, 0.8)
    cfg.events["ball_nudge"] = EventTermCfg(
      mode="interval",
      interval_range_s=(3.0, 6.0),
      func=vmdp.ball_nudge,
      params={"speed_range": (0.3, 1.0), "prob": 0.3, "require_in_view": True},
    )
  if run.variant == "unknown":
    tw.unknown_start_prob = 1.0
  if run.variant == "behind":
    # Cold start, ball 8-10 m behind (runswift goal grid "away" starts, where
    # every miss was a fall within 0.8 s; 2026-10-09).
    tw.spawn_view_center = math.pi
    tw.spawn_view_half_angle = math.pi / 6
    tw.spawn_any_prob = 0.0
    tw.far_spawn_prob = 0.0
    tw.unknown_start_prob = 0.0
  if run.track == "close_any":
    tw.ball_distance_range = (0.4, 1.5)
    tw.spawn_view_half_angle = math.pi
  elif run.track == "approach" and run.variant == "behind":
    tw.ball_distance_range = (8.0, 10.0)
  elif run.track == "approach":
    tw.ball_distance_range = (2.0, 10.0)
    tw.spawn_view_half_angle = math.pi
  # Caps: first half of the robots low, second half high (set every step).
  agent = load_rl_cfg(TASK)
  u = ManagerBasedRlEnv(cfg=cfg, device=DEV)
  if policy == "bhuman":
    from mjlab.scripts.play_bhuman_kick import BHumanKickPlayConfig, BHumanKickPolicy

    env = RslRlVecEnvWrapper(u)
    obs, _ = env.reset()
    bh = BHumanKickPolicy(
      u,
      BHumanKickPlayConfig(
        num_envs=run.n,
        print_kicks=False,
        perception="camera" if run.perception == "camera" else "true",
      ),
    )
    return env, u, obs, bh
  env = RslRlVecEnvWrapper(u, clip_actions=agent.clip_actions)
  r = load_runner_cls(TASK)(env, asdict(agent), device=DEV)
  r.load(policy, load_cfg={"actor": True}, strict=True, map_location=DEV)
  pol = r.get_inference_policy(device=DEV)
  obs, _ = env.reset()
  return env, u, obs, pol


from mjlab.tasks.velocity.config.k1_amp import env_cfgs as _ec  # noqa: E402

ec_defaults = {
  "mass": getattr(_ec, "_APPROACH_BALL_MASS", 0.1),
  "radius": _ec._APPROACH_BALL_RADIUS,
}


def caps_tensor(n: int) -> torch.Tensor:
  c = torch.empty(n, 3, device=DEV)
  c[: n // 2] = torch.tensor(CAPS["low"], device=DEV)
  c[n // 2 :] = torch.tensor(CAPS["high"], device=DEV)
  return c


def near_grid_cases() -> list[tuple[float, float, float, float, float]]:
  """runswift kick_policies cases: (ball x, ball y, aim deg, range m, ball vx)."""
  out = []
  for x in (0.40, 0.75, 1.10):
    for y in (-0.12, 0.0, 0.12):
      for h in (-15.0, 0.0, 15.0):
        out.append((x, y, h, 3.0, 0.0))
  for r in (6.0, 9.0):
    for y in (-0.12, 0.0, 0.12):
      out.append((0.75, y, 0.0, r, 0.0))
  for y in (-0.12, 0.0, 0.12):
    out.append((0.90, y, 0.0, 3.0, -0.2))
  return out


def place(u, cmd, robot_xy, robot_yaw, ball_xy, ball_v, target_xy, unknown=False):
  """Standing robot at robot_xy / yaw, ball at ball_xy (env-local), target."""
  rob, ball = u.scene["robot"], u.scene["ball"]
  n = u.num_envs
  origin = u.scene.env_origins[:, :2]
  rs = rob.data.default_root_state.clone()
  rs[:, :2] = origin + robot_xy
  h = robot_yaw / 2
  rs[:, 3:7] = torch.stack(
    (h.cos(), torch.zeros_like(h), torch.zeros_like(h), h.sin()), dim=-1
  )
  rs[:, 7:] = 0.0
  rob.write_root_state_to_sim(rs)
  rob.write_joint_state_to_sim(
    rob.data.default_joint_pos.clone(), torch.zeros_like(rob.data.default_joint_vel)
  )
  bs = ball.data.default_root_state.clone()
  bs[:, :2] = origin + ball_xy
  bs[:, 2] = _ec._APPROACH_BALL_RADIUS
  bs[:, 3:7] = torch.tensor([1.0, 0.0, 0.0, 0.0], device=DEV)
  bs[:, 7:] = 0.0
  bs[:, 7:9] = ball_v
  ball.write_root_state_to_sim(bs)
  bw = origin + ball_xy
  cmd.target_w[:] = origin + target_xy
  cmd.last_seen_ball_w[:] = bw
  cmd.time_since_seen[:] = 0.0
  cmd.ball_lost[:] = False
  rel = torch.zeros(n, 3, device=DEV)
  rel[:, :2] = bw - rs[:, :2]
  cmd.last_seen_ball_b[:] = quat_apply_inverse(yaw_quat(rs[:, 3:7]), rel)[:, :2]
  cmd.last_seen_yaw[:] = robot_yaw
  cmd.kicked_since_target[:] = False
  cmd.never_seen[:] = unknown
  if unknown:
    cmd.time_since_seen[:] = 1.0e3
    cmd.last_seen_ball_b[:] = 0.0


def setup_grid(run: Run, u, cmd):
  """Explicit placements for near_grid / goal_grid. Returns per-env case info."""
  n = u.num_envs
  if run.track == "near_grid":
    cs = near_grid_cases()
    idx = torch.arange(n, device=DEV) % len(cs)
    rep = (torch.arange(n, device=DEV) // len(cs)) % 3
    t = torch.tensor(cs, device=DEV)[idx]
    yaw = torch.tensor([0.0, 2.0, -2.0], device=DEV)[rep] * math.pi / 180
    head = t[:, 2] * math.pi / 180
    ball = t[:, :2]
    tgt = ball + t[:, 3:4] * torch.stack((head.cos(), head.sin()), -1)
    v = torch.stack((t[:, 4], torch.zeros_like(t[:, 4])), -1)
    place(u, cmd, torch.zeros(n, 2, device=DEV), yaw, ball, v, tgt)
    return {"heading": head, "case": idx}
  # goal_grid: runswift manifest; negative goals rotate physical XY by pi.
  m = json.loads(GOAL_GRID.read_text())
  cs = m["cases"]
  idx = torch.arange(n, device=DEV) % len(cs)
  sgn = torch.tensor([c["direction"] for c in cs], device=DEV, dtype=torch.float)[idx]
  ball = torch.tensor([c["ball"] for c in cs], device=DEV)[idx]
  start = torch.tensor([c["start"] for c in cs], device=DEV)[idx]
  yaw = torch.tensor([c["yaw"] for c in cs], device=DEV)[idx]
  goal = torch.stack((7.0 * sgn, torch.zeros_like(sgn)), -1)
  place(
    u,
    cmd,
    start,
    yaw,
    ball,
    torch.zeros(n, 2, device=DEV),
    goal,
    unknown=run.variant == "unknown",
  )
  dist = (ball - start).norm(dim=-1)
  budget = torch.clamp(torch.ceil((1.5 * dist + 2) / 0.2 + 25), min=45.0)
  return {"goal_sign": sgn, "budget": budget, "case": idx, "goal": goal}


# ---------------------------------------------------------------------------
# Measurement


def bootstrap(x: torch.Tensor, reps: int = 1000) -> list[float]:
  """[mean, ci_lo, ci_hi, n] of a 1-D sample (NaN-free)."""
  x = x[~torch.isnan(x)].float()
  n = int(x.numel())
  if n == 0:
    return [float("nan"), float("nan"), float("nan"), 0]
  i = torch.randint(0, n, (reps, n), device=x.device)
  ms = x[i].mean(dim=1)
  return [float(x.mean()), float(ms.quantile(0.025)), float(ms.quantile(0.975)), n]


def measure(run: Run, policy: str) -> dict:
  env, u, obs, act = make_env(run, policy)
  cmd = u.command_manager.get_term("twist")
  rob, ball = u.scene["robot"], u.scene["ball"]
  n, dt = u.num_envs, u.step_dt
  caps = caps_tensor(n)
  info = None
  if run.track in ("near_grid", "goal_grid"):
    info = setup_grid(run, u, cmd)
    u.sim.forward()
    u.command_manager.compute(dt=0.0)
    obs = env.get_observations()
  origin = u.scene.env_origins[:, :2]
  # Initial geometry (bearing of the ball from the robot heading).
  q = rob.data.root_link_quat_w
  yaw0 = torch.atan2(
    2 * (q[:, 0] * q[:, 3] + q[:, 1] * q[:, 2]), 1 - 2 * (q[:, 2] ** 2 + q[:, 3] ** 2)
  )
  rel0 = ball.data.root_link_pos_w[:, :2] - rob.data.root_link_pos_w[:, :2]
  bearing0 = torch.rad2deg(
    torch.remainder(torch.atan2(rel0[:, 1], rel0[:, 0]) - yaw0 + math.pi, 2 * math.pi)
    - math.pi
  )
  del rel0  # (initial distance not reported)
  # Joint ids for torque / joint-stop metrics.
  names = rob.joint_names
  leg = [i for i, nm in enumerate(names) if any(nm.endswith(j) for j in LEG)]
  lim = torch.tensor(
    [TORQUE_LIMIT[next(j for j in LEG if names[i].endswith(j))] for i in leg],
    device=DEV,
  )
  knee = [k for k, i in enumerate(leg) if names[i].endswith("Knee_Pitch")]
  mjm = u.sim.mj_model
  act_names = [mjm.actuator(i).name.split("/")[-1] for i in range(mjm.nu)]
  act_leg = [act_names.index(names[i]) for i in leg]
  term = u.action_manager.get_term("joint_pos")
  qlo = torch.full((len(names),), -1e9, device=DEV)
  qhi = torch.full((len(names),), 1e9, device=DEV)
  import re

  for pat, (a, b) in DEPLOY_Q_LIMITS.items():
    for i, nm in enumerate(names):
      if re.fullmatch(pat, nm):
        qlo[i], qhi[i] = a, b
  z = lambda: torch.zeros(n, device=DEV)  # noqa: E731
  nan = lambda: torch.full((n,), float("nan"), device=DEV)  # noqa: E731
  alive = torch.ones(n, dtype=torch.bool, device=DEV)
  touched = torch.zeros(n, dtype=torch.bool, device=DEV)
  fell, fall_t = torch.zeros_like(alive), nan()
  touch_t, touch_err, touch_spd = nan(), nan(), z()
  last_contact, last_foot = (
    torch.full((n,), -1e9, device=DEV),
    torch.full((n,), -1e9, device=DEV),
  )
  init_v = ball.data.root_link_lin_vel_w[:, :2].clone()
  kick_t, kick_err = nan(), nan()
  kicks, on20, goals, dbl = z(), z(), z(), z()
  long_spd, long_need, long_n = z(), z(), z()
  rest_miss, rest_n = z(), z()
  knee_kick = z()
  sat_steps, stop_steps, steps = z(), z(), z()
  far_vx, far_cap, far_n = z(), z(), z()
  fast_h, fast_p, fast_n = z(), z(), z()
  arate, prev_a = z(), None
  # Landings: downward foot speed in the last 3 cm before touchdown, and the
  # foot-ground force on the first contact step.
  feet = [rob.body_names.index(f) for f in ("left_foot_link", "right_foot_link")]
  fsens, hsens = u.scene["feet_ground_contact"], u.scene["foot_height_scan"]
  td_sum, td_n, land_f, land_n = z(), z(), z(), z()
  goal_out, goal_t = torch.zeros(n, dtype=torch.long, device=DEV), nan()
  style_n = torch.zeros(2, 54, device=DEV)
  style_aim = torch.zeros(2, 54, device=DEV)
  style_spd = torch.zeros(2, 54, device=DEV)
  t = 0.0
  limit_s = run.seconds
  with torch.inference_mode():
    for _ in range(int(limit_s / dt)):
      cmd.speed_limit[:] = caps
      a = act(obs)
      obs, _, dones, ex = env.step(a)
      t += dt
      a_now = term._raw_actions
      if prev_a is not None:
        arate += alive.float() * (a_now - prev_a).abs().mean(-1)
      prev_a = a_now.clone()
      fz = rob.data.body_link_lin_vel_w[:, feet, 2]
      ff = torch.linalg.norm(fsens.data.force, dim=-1)
      zone = (hsens.data.heights < 0.03) & (ff <= 1.0) & alive[:, None]
      td_sum += (torch.clamp(-fz, min=0.0) * zone).sum(-1)
      td_n += zone.sum(-1)
      first = fsens.compute_first_contact(dt=dt) & alive[:, None]
      land_f += (ff * first).sum(-1)
      land_n += first.sum(-1)
      to = ex.get("time_outs")
      d = dones.bool()
      f = d & ~(to.bool() if to is not None else torch.zeros_like(d))
      # runswift's fall test, checked every step: trunk tilt > 60 deg or root
      # below 0.25 m (our termination is stochastic past 63 deg).
      gz = rob.data.projected_gravity_b[:, 2]
      f |= (-gz < 0.5) | (rob.data.root_link_pos_w[:, 2] < 0.25)
      newfall = alive & f
      fell |= newfall
      fall_t = torch.where(newfall, t, fall_t)
      if info is not None and "budget" in info:
        alive &= t < info["budget"]
      # Ball / contact events (only while alive and before any reset).
      v = ball.data.root_link_lin_vel_w[:, :2]
      sp = v.norm(dim=-1)
      foot, body = cmd.prev_touch.clone(), cmd.body_touch.clone()
      last_foot = torch.where(foot, t, last_foot)
      last_contact = torch.where(foot | body, t, last_contact)
      touched |= (foot | body) & alive
      head = info["heading"] if info is not None and "heading" in info else None
      if head is None:
        to_t = cmd.target_w - ball.data.root_link_pos_w[:, :2]
        head_now = torch.atan2(to_t[:, 1], to_t[:, 0])
      else:
        head_now = head
      launch = (
        alive & touch_t.isnan() & (sp >= 0.5) & ((v - init_v).norm(dim=-1) >= 0.3)
        & (t - last_foot <= 0.15)
      )  # fmt: skip
      touch_t = torch.where(launch, t, touch_t)
      win = alive & ~touch_t.isnan() & (t - touch_t <= 0.2) & (sp > touch_spd)
      touch_spd = torch.where(win, sp, touch_spd)
      e = torch.rad2deg(torch.atan2(v[:, 1], v[:, 0]) - head_now)
      e = torch.remainder(e + 180, 360) - 180
      touch_err = torch.where(win, e.abs(), touch_err)
      k = cmd.kick_event & alive
      err = torch.rad2deg(torch.acos(cmd.kick_cos.clamp(-1, 1)))
      first = k & kick_t.isnan()
      kick_t = torch.where(first, t, kick_t)
      kick_err = torch.where(first, err, kick_err)
      kicks += k.float()
      on20 += (k & (err <= 20)).float()
      lk = k & cmd.kick_long
      long_spd += torch.where(lk, cmd.kick_speed, 0.0)
      long_need += torch.where(
        lk, cmd.kick_speed / cmd.kick_speed_req.clamp(min=0.5), 0.0
      )
      long_n += lk.float()
      r = cmd.rest_event & alive
      miss = (ball.data.root_link_pos_w[:, :2] - cmd.rest_target_w).norm(dim=-1)
      rest_miss += torch.where(r, miss, 0.0)
      rest_n += r.float()
      goals += (cmd.goal_event & alive).float()
      # Kick style per situation (2026-10-07, user: the policy should know when
      # each style is best). Style: front (foot yaw to the kick line < 30 deg),
      # side (60-120 deg, inside or outside foot), other; hop = no foot on the
      # ground at contact. Situation: range bin x redirect (kick direction vs
      # robot heading: < 30, 30-60, > 60 deg).
      if bool(k.any()):
        fy = torch.rad2deg(cmd.kick_foot_yaw)
        st_ = torch.where(fy < 30, 0, torch.where((fy >= 60) & (fy <= 120), 1, 2))
        gnd = u.scene["feet_ground_contact"].data.found
        hop = (
          ~(gnd.reshape(n, -1)[:, :2] > 0).any(-1)
          if gnd is not None
          else torch.zeros_like(k)
        )
        st_ = torch.where(hop, st_ + 3, st_)
        td = cmd.target_dist
        rb = torch.where(td < 4, 0, torch.where(td < 8, 1, 2))
        qq = rob.data.root_link_quat_w
        yw = torch.atan2(
          2 * (qq[:, 0] * qq[:, 3] + qq[:, 1] * qq[:, 2]),
          1 - 2 * (qq[:, 2] ** 2 + qq[:, 3] ** 2),
        )
        to_t = cmd.target_w - ball.data.root_link_pos_w[:, :2]
        red = torch.rad2deg(
          (torch.atan2(to_t[:, 1], to_t[:, 0]) - yw + math.pi).remainder(2 * math.pi)
          - math.pi
        ).abs()
        sb = torch.where(red < 30, 0, torch.where(red < 60, 1, 2))
        cell = (rb * 3 + sb) * 6 + st_
        capg = (torch.arange(n, device=DEV) >= n // 2).long()
        for cg in (0, 1):
          m_ = k & (capg == cg)
          if bool(m_.any()):
            c_ = cell[m_]
            style_n[cg] += torch.bincount(c_, minlength=54).float()
            style_aim[cg] += torch.bincount(
              c_, weights=(err[m_] <= 20).float(), minlength=54
            )
            ratio = (cmd.kick_speed[m_] / cmd.kick_speed_req[m_].clamp(min=0.5)).clamp(
              max=1.5
            )
            style_spd[cg] += torch.bincount(c_, weights=ratio, minlength=54)
      dbl += (cmd.double_touch_event & alive).float()
      tq = u.sim.data.actuator_force[:, act_leg].abs()
      knee_kick = torch.where(
        k, torch.maximum(knee_kick, tq[:, knee].amax(-1)), knee_kick
      )
      sat_steps += (alive & (tq >= 0.98 * lim).any(-1)).float()
      raw_t = a_now * term._scale + term._offset
      stop_steps += (alive & ((raw_t < qlo) | (raw_t > qhi)).any(-1)).float()
      steps += alive.float()
      vb = rob.data.root_link_lin_vel_b
      far = alive & kick_t.isnan() & (cmd.dist > 2.5)
      far_vx += torch.where(far, vb[:, 0], 0.0)
      far_cap += torch.where(far, caps[:, 0], 0.0)
      far_n += far.float()
      fast = alive & (vb[:, :2].norm(dim=-1) > 1.0)
      g = rob.data.projected_gravity_b
      fast_h += torch.where(fast, rob.data.root_link_pos_w[:, 2], 0.0)
      fast_p += torch.where(fast, torch.rad2deg(torch.atan2(g[:, 0], -g[:, 2])), 0.0)
      fast_n += fast.float()
      if run.track == "goal_grid":
        bp = ball.data.root_link_pos_w[:, :2] - origin
        sg = info["goal_sign"]
        over = bp[:, 0] * sg >= 7.0 + BALL_R
        in_goal = bp[:, 1].abs() <= 1.25 - BALL_R
        side_out = bp[:, 1].abs() >= 4.5 + BALL_R
        wrong = bp[:, 0] * sg <= -(7.0 + BALL_R)
        undecided = goal_out == 0
        goal_out = torch.where(alive & undecided & over & in_goal, 1, goal_out)
        goal_out = torch.where(
          alive & undecided & ((over & ~in_goal) | side_out | wrong), 2, goal_out
        )
        goal_t = torch.where(alive & undecided & (goal_out == 1), t, goal_t)
        alive &= goal_out == 0
      alive &= ~d
      if not bool(alive.any()):
        break
  low = torch.arange(n, device=DEV) < n // 2
  res: dict = {}

  def put(name, x, mask=None):
    for cap, m in (("low", low), ("high", ~low)):
      mm = m if mask is None else (m & mask)
      res.setdefault(name, {})[cap] = bootstrap(x[mm])

  f = fell.float()
  put("fall_pct", 100 * f)
  put("fall_first_2s_pct", 100 * (fell & (fall_t <= 2.0)).float())
  ok15 = (~touch_t.isnan()) & (touch_err <= 15) & ~fell
  if run.track in ("near_grid", "close_any"):
    put("first_touch_15_pct", 100 * ok15.float())
    put("first_touch_err_deg", touch_err)
    put("first_touch_speed", torch.where(touch_t.isnan(), float("nan"), touch_spd))
  put("first_kick_pct", 100 * (~kick_t.isnan()).float())
  put("first_kick_s", kick_t)
  put("first_kick_20_pct", 100 * ((~kick_t.isnan()) & (kick_err <= 20)).float())
  put("kicks_20_pct", 100 * on20 / kicks.clamp(min=1), kicks > 0)
  put("long_3d", long_spd / long_n.clamp(min=1), long_n > 0)
  put("long_x_needed", long_need / long_n.clamp(min=1), long_n > 0)
  put("short_stop_m", rest_miss / rest_n.clamp(min=1), rest_n > 0)
  put("knee_peak_at_kick", knee_kick, kicks > 0)
  put("torque_sat_pct", 100 * sat_steps / steps.clamp(min=1))
  put("joint_stop_pct", 100 * stop_steps / steps.clamp(min=1))
  put("approach_vx", far_vx / far_n.clamp(min=1), far_n > 10)
  put("cap_use", far_vx / far_cap.clamp(min=1e-3), far_n > 10)
  put("fast_height_m", fast_h / fast_n.clamp(min=1), fast_n > 10)
  put("fast_pitch_deg", fast_p / fast_n.clamp(min=1), fast_n > 10)
  put("action_rate", arate / steps.clamp(min=1))
  put("touchdown_speed", td_sum / td_n.clamp(min=1), td_n > 0)
  put("landing_force", land_f / land_n.clamp(min=1), land_n > 0)
  put("double_touches", dbl)
  # Style table and selection quality per cap group.
  STYLES = ("front", "side", "other", "front_hop", "side_hop", "other_hop")
  RANGES, REDIRECT = ("short", "medium", "long"), ("straight", "angled", "sharp")
  table: dict = {}
  sel, div = {}, {}
  for cg, cap in ((0, "low"), (1, "high")):
    tot, best_used, used = 0.0, 0.0, set()
    for rbi, rn in enumerate(RANGES):
      for sbi, sn in enumerate(REDIRECT):
        cell_st = {}
        for sti, stn in enumerate(STYLES):
          c = (rbi * 3 + sbi) * 6 + sti
          nn = float(style_n[cg, c])
          if nn > 0:
            aim = float(style_aim[cg, c]) / nn
            spd = float(style_spd[cg, c]) / nn
            cell_st[stn] = [int(nn), round(aim, 3), round(spd, 3)]
        if cell_st:
          table.setdefault(cap, {})[f"{rn}/{sn}"] = cell_st
          cn = sum(v[0] for v in cell_st.values())
          for stn, v in cell_st.items():
            if v[0] >= 0.1 * cn:
              used.add(stn)
          ok = {k_: v for k_, v in cell_st.items() if v[0] >= 10}
          if len(ok) >= 2:
            # Good choice: a style within 5 % of the best score here (near-ties
            # are not mistakes; 2026-10-08).
            sc_ = {k_: v[1] * min(1.0, v[2]) for k_, v in ok.items()}
            top = max(sc_.values())
            tot += cn
            best_used += sum(cell_st[k_][0] for k_ in ok if sc_[k_] >= 0.95 * top)
    sel[cap] = (
      [100 * best_used / tot, 100 * best_used / tot, 100 * best_used / tot, int(tot)]
      if tot
      else [float("nan"), 0, 0, 0]
    )
    div[cap] = [float(len(used))] * 3 + [1]
  res["style_selection_pct"] = sel
  res["style_repertoire"] = div
  res["_styles"] = table
  if run.track == "full_loop":
    put("goals_per_ep", goals)
  if run.track == "goal_grid":
    put("goal_pct", 100 * (goal_out == 1).float())
    put("goal_s", goal_t)
    put("fall_before_contact_pct", 100 * (fell & ~touched).float())
  if run.track == "approach":
    for lo_b, hi_b, nm in ((0, 60, "front"), (60, 120, "side"), (120, 181, "behind")):
      m = (bearing0.abs() >= lo_b) & (bearing0.abs() < hi_b)
      put(f"fall_pct_{nm}", 100 * f, m)
      put(f"first_kick_pct_{nm}", 100 * (~kick_t.isnan()).float(), m)
      put(f"first_kick_s_{nm}", kick_t, m)
  env.close()
  del env, u
  torch.cuda.empty_cache()
  return res


# ---------------------------------------------------------------------------


def run_all(name: str, policy: str, size: str) -> None:
  OUT.mkdir(parents=True, exist_ok=True)
  out = OUT / f"{name}.json"
  out.parent.mkdir(parents=True, exist_ok=True)
  data = json.loads(out.read_text()) if out.exists() else {}
  data.setdefault("_meta", {}).update(
    {"policy": policy, "size": size, "date": time.strftime("%Y-%m-%d %H:%M")}
  )
  for run in plan(size, policy == "bhuman"):
    if run.key in data:
      continue
    t0 = time.time()
    data[run.key] = measure(run, policy)
    data[run.key]["_n"] = run.n
    out.write_text(json.dumps(data, indent=1))
    print(f"BENCH2 {name} {run.key} done in {time.time() - t0:.0f} s", flush=True)


def compare(a: str, b: str) -> None:
  A = json.loads((OUT / f"{a}.json").read_text())
  B = json.loads((OUT / f"{b}.json").read_text())
  print(
    f"| situation | metric | caps | {a} | {b} | verdict |\n|---|---|---|---|---|---|"
  )
  for key in sorted(set(A) & set(B)):
    if key.startswith("_"):
      continue
    for metric in sorted(set(A[key]) & set(B[key])):
      if metric.startswith("_"):
        continue
      for cap in ("low", "high"):
        x, y = A[key][metric].get(cap), B[key][metric].get(cap)
        if not x or not y or x[3] == 0 or y[3] == 0:
          continue
        ov = not (x[2] < y[1] or y[2] < x[1])
        verdict = (
          "tie (CIs overlap)"
          if ov
          else (f"{a} higher" if x[0] > y[0] else f"{b} higher")
        )
        print(
          f"| {key} | {metric} | {cap} | {x[0]:.3g} [{x[1]:.3g}, {x[2]:.3g}] n={x[3]}"
          f" | {y[0]:.3g} [{y[1]:.3g}, {y[2]:.3g}] n={y[3]} | {verdict} |"
        )


if __name__ == "__main__":
  if sys.argv[1] == "run":
    size = sys.argv[sys.argv.index("--size") + 1] if "--size" in sys.argv else "full"
    run_all(sys.argv[2], sys.argv[3], size)
  else:
    compare(sys.argv[2], sys.argv[3])
