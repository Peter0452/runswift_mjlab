"""Skill evaluation of a dribble checkpoint for the v22 scenarios.

Deterministic policy on the deploy-matched training config (vision, delay,
ball randomization as in training), one JSON line per test:

  approach  ball 4-8 m away (half at any bearing, half in view), 0.5 m/s
            command: share touched within 15 s, time to the first touch,
            mean approach speed, falls.
  search    after the first touch (+1 s) the ball is moved 2-4 m away at any
            bearing, as if taken: share found (touched again) within 12 s,
            time to see it again, time to touch it, falls.
  kick      every window is a kick window (slot 82): share of windows with a
            kick, kick ground speed (mean, p90), direction error (mean, share
            within 15 deg), time to kick, robot standing at window end, the
            window success, falls.
  transition (not run by default) dribble at 0.5 / 1.0 / 1.5 m/s, then switch
            to a kick window mid-dribble (direction 0-90 deg off the
            robot-to-ball line): share kicked within 4 s (straight < 30 deg,
            angled), time to kick (mean, p90), kick speed, error, falls.

Checkpoints trained with DRIBBLE_GENES need the same DRIBBLE_GENES set.

  DRIBBLE_GENES=... .venv/bin/python scripts/tools/dribble_skill_eval.py CKPT
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict

import torch

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.scripts.play_bhuman_kick import BHumanKickPlayConfig, BHumanKickPolicy
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

TASK = "Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1"


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("checkpoint")
  ap.add_argument("--num-envs", type=int, default=512)
  ap.add_argument("--seed", type=int, default=7)
  ap.add_argument("--tests", default="approach,search,kick,transition")
  ap.add_argument(
    "--kick-min-deg",
    type=float,
    default=None,
    help="kick test: only kick directions at least this far off the ball line",
  )
  ap.add_argument(
    "--bhuman-near",
    type=float,
    default=None,
    help="B-Human's kick policy acts in kick windows within this distance (m) "
    "of the ball before the kick (teacher probe)",
  )
  args = ap.parse_args()
  dev = "cuda:0" if torch.cuda.is_available() else "cpu"

  ec = load_env_cfg(TASK)
  ec.scene.num_envs = args.num_envs
  ec.seed = args.seed
  tw = ec.commands["twist"]
  tw.speed_curriculum = False
  tw.stop_prob = 0.0
  tw.top_band_prob = 0.0
  tw.unknown_start_prob = 0.0
  tw.collinear_drill_prob = 0.0
  tw.lost_needs_touch = True
  tw.speed_limit_vx = (tw.speed_limit_vx[1],) * 2
  tw.speed_limit_vy = (tw.speed_limit_vy[1],) * 2
  tw.speed_limit_wz = (tw.speed_limit_wz[1],) * 2
  ac = load_rl_cfg(TASK)
  base = ManagerBasedRlEnv(cfg=ec, device=dev)
  env = RslRlVecEnvWrapper(base, clip_actions=ac.clip_actions)
  runner = load_runner_cls(TASK)(env, asdict(ac), device=dev)
  runner.load(args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=dev)
  policy = runner.get_inference_policy(device=dev)
  cmd = base.command_manager.get_term("twist")
  if args.bhuman_near is not None:
    student = policy
    teacher = BHumanKickPolicy(
      base,
      BHumanKickPlayConfig(
        num_envs=args.num_envs, print_kicks=False, strong_kick="always"
      ),
    )

    def policy(obs):
      a = student(obs)
      b = teacher(obs).to(a.device)
      near = cmd.kick_mode & ~cmd.kick_done & (cmd.ball_trunk_dist <= args.bhuman_near)
      return torch.where(near.unsqueeze(-1), b, a)

  c = cmd.cfg
  n, dt = args.num_envs, base.step_dt
  tag = "/".join(args.checkpoint.split("/")[-2:])

  def setup(kick: float, far: float, any_bearing: float, speed: float) -> None:
    c.kick_prob, c.vanish_prob, c.far_spawn_prob = kick, 0.0, far
    c.far_spawn_range = (4.0, 8.0)
    c.spawn_any_prob = any_bearing
    c.ball_speed_range = (speed, speed)
    cmd.speed_hi = speed

  def run(seconds: float, step_fn) -> None:
    torch.manual_seed(args.seed)
    with torch.inference_mode():
      obs, _ = env.reset()
      for k in range(int(round(seconds / dt))):
        obs, _, dones, extras = env.step(policy(obs))
        done = dones.bool()
        fell = done & ~extras.get("time_outs", torch.zeros_like(done)).bool()
        step_fn(k * dt + dt, done, fell)

  def emit(test: str, **kv) -> None:
    print(json.dumps({"ckpt": tag, "test": test, **kv}), flush=True)

  tests = args.tests.split(",")
  if "approach" in tests:
    setup(kick=0.0, far=1.0, any_bearing=0.5, speed=0.5)
    start_d = torch.zeros(n, device=dev)
    t_touch = torch.full((n,), float("nan"), device=dev)
    over = torch.zeros(n, dtype=torch.bool, device=dev)
    fell_any = torch.zeros(n, dtype=torch.bool, device=dev)

    def approach_step(t, done, fell):
      if t <= dt * 1.5:
        start_d[:] = cmd.ball_trunk_dist
      new = ~over & cmd.has_touched
      t_touch[new] = t
      fell_any[:] |= fell & ~over
      over[:] |= new | done

    run(16.0, approach_step)
    ok = ~torch.isnan(t_touch) & (t_touch <= 15.0)
    emit(
      "approach",
      envs=n,
      start_dist=round(float(start_d.mean()), 2),
      touched_15s=round(float(ok.float().mean()), 3),
      time_to_touch=round(float(t_touch[ok].mean()), 2) if ok.any() else None,
      approach_speed=round(float((start_d[ok] / t_touch[ok]).mean()), 2)
      if ok.any()
      else None,
      fall=round(float(fell_any.float().mean()), 3),
    )

  if "search" in tests:
    setup(kick=0.0, far=0.0, any_bearing=0.0, speed=0.5)
    touch_t = torch.full((n,), float("nan"), device=dev)
    vanish_t = torch.full((n,), float("nan"), device=dev)
    seen_t = torch.full((n,), float("nan"), device=dev)
    found_t = torch.full((n,), float("nan"), device=dev)
    over = torch.zeros(n, dtype=torch.bool, device=dev)
    fell_any = torch.zeros(n, dtype=torch.bool, device=dev)

    def search_step(t, done, fell):
      first = torch.isnan(touch_t) & cmd.has_touched & ~over
      touch_t[first] = t
      go = torch.isnan(vanish_t) & ~torch.isnan(touch_t) & (t - touch_t >= 1.0) & ~over
      if go.any():
        ids = go.nonzero().squeeze(-1)
        cmd._move_ball(ids, (2.0, 4.0))
        vanish_t[go] = t
      active = ~torch.isnan(vanish_t) & ~over
      seen = active & torch.isnan(seen_t) & (cmd.see_ball > 0.5) & (t - vanish_t > dt)
      seen_t[seen] = t
      if seen.any():
        seen_d.append(cmd.ball_trunk_dist[seen].clone())
      # Spin while the ball is still unseen: yaw rate and trunk tilt.
      looking = active & torch.isnan(seen_t)
      if looking.any():
        r = base.scene["robot"].data
        spin.append(r.root_link_ang_vel_w[looking, 2].abs().clone())
        pitch.append(r.joint_pos[looking, 1].clone())  # head pitch (+ = down)
        g = r.projected_gravity_b[looking]
        tilt.append(torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0))).clone())
      found = active & torch.isnan(found_t) & cmd.has_touched & (t - vanish_t > dt)
      found_t[found] = t
      fell_any[:] |= fell & active
      over[:] |= done | (active & (t - vanish_t > 12.0))

    spin: list[torch.Tensor] = []
    tilt: list[torch.Tensor] = []
    pitch: list[torch.Tensor] = []
    seen_d: list[torch.Tensor] = []
    run(24.0, search_step)
    tried = ~torch.isnan(vanish_t)
    sp_all = torch.cat(spin) if spin else torch.zeros(0, device=dev)
    tl_all = torch.cat(tilt) if tilt else torch.zeros(0, device=dev)
    found = tried & ~torch.isnan(found_t)
    seen = tried & ~torch.isnan(seen_t)
    emit(
      "search",
      vanished=int(tried.sum()),
      found_12s=round(float(found.sum() / tried.sum().clamp(min=1)), 3),
      time_to_see=round(float((seen_t - vanish_t)[seen].mean()), 2)
      if seen.any()
      else None,
      time_to_touch=round(float((found_t - vanish_t)[found].mean()), 2)
      if found.any()
      else None,
      fall=round(float(fell_any[tried].float().mean()), 3) if tried.any() else None,
      spin_rate=round(float(sp_all.mean()), 2) if len(sp_all) else None,
      tilt_p90=round(float(tl_all.quantile(0.9)), 1) if len(tl_all) else None,
      head_pitch_deg=round(math.degrees(float(torch.cat(pitch).mean())), 1)
      if pitch
      else None,
      seen_dist=round(float(torch.cat(seen_d).mean()), 2) if seen_d else None,
    )

  if "kick" in tests:
    setup(kick=1.0, far=0.0, any_bearing=0.0, speed=0.5)
    if args.kick_min_deg is not None:
      c.kick_min_angle = math.radians(args.kick_min_deg)
    speeds, errs, waits, stills, oks, kicked, feet, ball_left, sp3 = (
      [] for _ in range(9)
    )
    falls = torch.zeros((), device=dev)
    windows = torch.zeros((), device=dev)

    def kick_step(t, done, fell):
      nonlocal falls, windows
      ev = cmd.kick_event
      if ev.any():
        speeds.append(cmd.kick_speed[ev].clone())
        # Ground and 3D launch speed straight from the ball (kick_speed is 3D
        # only with kick_air_ok).
        bv = base.scene["ball"].data.root_link_lin_vel_w[ev]
        sp3.append(torch.stack((bv[:, :2].norm(dim=-1), bv.norm(dim=-1)), dim=-1))
        errs.append(cmd.kick_err[ev].clone())
        waits.append(cmd.kick_wait[ev].clone())
        # Kicking-foot yaw minus the kick direction, signed so +90 deg is
        # B-Human's inside-of-the-foot kick for either foot.
        q = base.scene["robot"].data.body_link_quat_w[:, cmd._gait_feet_ids]
        yaw = torch.atan2(
          2 * (q[..., 0] * q[..., 3] + q[..., 1] * q[..., 2]),
          1 - 2 * (q[..., 2] ** 2 + q[..., 3] ** 2),
        )
        left = torch.where(
          cmd.touch_lr.any(-1), cmd.touch_lr[:, 0], cmd.last_touch_side > 0
        )
        kyaw = torch.atan2(cmd.ball_cmd_dir_w[:, 1], cmd.ball_cmd_dir_w[:, 0])
        rel = torch.where(left, yaw[:, 0], yaw[:, 1]) - kyaw
        rel = torch.atan2(torch.sin(rel), torch.cos(rel)) * torch.where(left, 1.0, -1.0)
        feet.append(torch.rad2deg(rel[ev]).clone())
      # Window ends are judged by the command before its resample: the window
      # success flag is set on the step a window ends.
      ended = cmd.window_len - cmd.time_left < dt * 1.5
      ended = ended & (t > 1.0) & ~done
      if ended.any():
        oks.append(cmd.window_success[ended].float().clone())
        # v32: the kick finished (ball left 0.5 m) by the window's end.
        ball_left.append(cmd.prev_window_kick_done[ended].float().clone())
        stills.append(
          (base.scene["robot"].data.root_link_lin_vel_w[ended, :2].norm(dim=-1) < 0.25)
          .float()
          .clone()
        )
      windows = windows + ended.float().sum()
      falls = falls + fell.float().sum()
      kicked.append(ev.float().sum())

    run(30.0, kick_step)
    sp = torch.cat(speeds) if speeds else torch.zeros(0, device=dev)
    er = torch.cat(errs) if errs else torch.zeros(0, device=dev)
    wt = torch.cat(waits) if waits else torch.zeros(0, device=dev)
    nk = float(sum(float(x) for x in kicked))
    emit(
      "kick",
      windows=int(windows),
      kicks_per_window=round(nk / max(float(windows), 1.0), 3),
      kick_speed=round(float(sp.mean()), 2) if len(sp) else None,
      kick_ground_speed=round(float(torch.cat(sp3)[:, 0].mean()), 2) if sp3 else None,
      kick_3d_speed=round(float(torch.cat(sp3)[:, 1].mean()), 2) if sp3 else None,
      kick_3d_p90=round(float(torch.cat(sp3)[:, 1].quantile(0.9)), 2) if sp3 else None,
      kick_speed_p90=round(float(sp.quantile(0.9)), 2) if len(sp) else None,
      share_ge_5ms=round(float((sp >= 5.0).float().mean()), 3) if len(sp) else None,
      share_ge_7ms=round(float((sp >= 7.0).float().mean()), 3) if len(sp) else None,
      err_deg=round(float(torch.rad2deg(er).mean()), 1) if len(er) else None,
      within_15deg=round(float((er <= math.radians(15)).float().mean()), 3)
      if len(er)
      else None,
      time_to_kick=round(float(wt.mean()), 2) if len(wt) else None,
      foot_yaw_p50=round(float(torch.cat(feet).median()), 1) if feet else None,
      inside_foot_share=round(
        float(((torch.cat(feet) > 60) & (torch.cat(feet) < 120)).float().mean()), 3
      )
      if feet
      else None,
      window_success=round(float(torch.cat(oks).mean()), 3) if oks else None,
      ball_left_share=round(float(torch.cat(ball_left).mean()), 3)
      if ball_left
      else None,
      still_at_end=round(float(torch.cat(stills).mean()), 3) if stills else None,
      falls_per_window=round(float(falls / windows.clamp(min=1)), 3),
    )

  if "transition" in tests:
    for speed in (0.5, 1.0, 1.5):
      # kick_prob > 0 keeps the kick logic on (it is skipped at 0); ~no kick draws.
      setup(kick=1.0e-9, far=0.0, any_bearing=0.0, speed=speed)
      sw_t = torch.full((n,), float("nan"), device=dev)
      kick_t = torch.full((n,), float("nan"), device=dev)
      k_speed = torch.full((n,), float("nan"), device=dev)
      k_err = torch.full((n,), float("nan"), device=dev)
      v_sw = torch.zeros(n, device=dev)
      off = torch.empty(n, device=dev).uniform_(0.0, math.pi / 2)
      over = torch.zeros(n, dtype=torch.bool, device=dev)
      fell_any = torch.zeros(n, dtype=torch.bool, device=dev)

      def trans_step(
        t,
        done,
        fell,
        off=off,
        sw_t=sw_t,
        kick_t=kick_t,
        k_speed=k_speed,
        k_err=k_err,
        v_sw=v_sw,
        over=over,
        fell_any=fell_any,
      ):
        # Switch to a kick window while dribbling: touched, >= 4 s in, ball
        # within 1 m, mid dribble window. Direction = robot-to-ball line
        # turned by off (0-90 deg, as in training).
        go = (
          torch.isnan(sw_t)
          & ~over
          & cmd.has_touched
          & (t >= 4.0)
          & (cmd.ball_trunk_dist < 1.0)
          & ~cmd.kick_mode
        )
        if go.any():
          ids = go.nonzero().squeeze(-1)
          r = base.scene["robot"].data
          to_ball = (
            base.scene["ball"].data.root_link_pos_w[ids, :2]
            - r.root_link_pos_w[ids, :2]
          )
          sign = torch.where(torch.rand(len(ids), device=dev) < 0.5, -1.0, 1.0)
          h = torch.atan2(to_ball[:, 1], to_ball[:, 0]) + sign * off[ids]
          cmd.ball_cmd_dir_w[ids] = torch.stack((h.cos(), h.sin()), dim=-1)
          cmd.kick_offset[ids] = off[ids]
          cmd.kick_mode[ids] = True
          cmd.kick_done[ids] = False
          cmd._kicked_once[ids] = False
          cmd.kick_wait[ids] = 0.0
          cmd.ball_cmd_speed[ids] = 0.0
          cmd.cmd_drift[ids] = 0.0
          cmd.time_left[ids] = 6.0
          cmd.window_len[ids] = 6.0
          v_sw[ids] = r.root_link_lin_vel_w[ids, :2].norm(dim=-1)
          sw_t[go] = t
        active = ~torch.isnan(sw_t) & ~over
        ev = active & torch.isnan(kick_t) & cmd.kick_event & cmd.kick_mode
        kick_t[ev] = t
        k_speed[ev] = cmd.kick_speed[ev]
        k_err[ev] = cmd.kick_err[ev]
        fell_any[:] |= fell & active
        over[:] |= done | (active & (t - sw_t > 4.0))

      run(16.0, trans_step)
      tried = ~torch.isnan(sw_t)
      ok = tried & ~torch.isnan(kick_t)
      emit(
        "transition",
        dribble_speed=speed,
        switched=int(tried.sum()),
        robot_speed_at_switch=round(float(v_sw[tried].mean()), 2)
        if tried.any()
        else None,
        kicked_4s=round(float(ok.sum() / tried.sum().clamp(min=1)), 3),
        time_to_kick=round(float((kick_t - sw_t)[ok].mean()), 2) if ok.any() else None,
        time_to_kick_p90=round(float((kick_t - sw_t)[ok].quantile(0.9)), 2)
        if ok.any()
        else None,
        kick_speed=round(float(k_speed[ok].mean()), 2) if ok.any() else None,
        err_deg=round(float(torch.rad2deg(k_err[ok]).mean()), 1) if ok.any() else None,
        time_straight=round(
          float((kick_t - sw_t)[ok & (off < math.radians(30))].mean()), 2
        )
        if (ok & (off < math.radians(30))).any()
        else None,
        time_angled=round(
          float((kick_t - sw_t)[ok & (off >= math.radians(30))].mean()), 2
        )
        if (ok & (off >= math.radians(30))).any()
        else None,
        straight_kicked=round(
          float(
            (ok & (off < math.radians(30))).sum()
            / (tried & (off < math.radians(30))).sum().clamp(min=1)
          ),
          3,
        ),
        angled_kicked=round(
          float(
            (ok & (off >= math.radians(30))).sum()
            / (tried & (off >= math.radians(30))).sum().clamp(min=1)
          ),
          3,
        ),
        fall=round(float(fell_any[tried].float().mean()), 3) if tried.any() else None,
      )


if __name__ == "__main__":
  main()
