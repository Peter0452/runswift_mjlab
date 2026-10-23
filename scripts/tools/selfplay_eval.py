"""Fixed-opponent evaluation of a phase-2 (flat self-play kick) checkpoint.

Deterministic learner, ``--episodes``-long rollouts of ``--num-envs`` games
against each fixed opponent; prints game, kick and ball-handling metrics as
one JSON line per opponent so runs and checkpoints can be compared.

  uv run python scripts/tools/selfplay_eval.py CKPT [--controller CTRL_CKPT]
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
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

TASK = "Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1"
CTRL = (
  "logs/rsl_rl/k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt"
)


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("checkpoint")
  ap.add_argument("--controller", default=CTRL)
  ap.add_argument("--num-envs", type=int, default=512)
  ap.add_argument("--steps", type=int, default=1500)
  ap.add_argument("--seed", type=int, default=7)
  ap.add_argument("--opponents", default="kick,controller,walk")
  ap.add_argument(
    "--blind-opponent",
    action="store_true",
    help="zero the learner's opponent-detection inputs (as never seen)",
  )
  args = ap.parse_args()
  dev = "cuda:0" if torch.cuda.is_available() else "cpu"

  ec = load_env_cfg(TASK)
  ec.scene.num_envs = args.num_envs
  ec.seed = args.seed
  opp_cfg = ec.actions["opponent"]
  opp_cfg.controller_checkpoint = args.controller
  opp_cfg.sample_copies = False
  ac = load_rl_cfg(TASK)
  rc = load_runner_cls(TASK)
  base = ManagerBasedRlEnv(cfg=ec, device=dev)
  env = RslRlVecEnvWrapper(base, clip_actions=ac.clip_actions)
  runner = rc(env, asdict(ac), device=dev)
  runner.load(args.checkpoint, load_cfg={"actor": True}, strict=True, map_location=dev)
  policy = runner.get_inference_policy(device=dev)
  opp = base.action_manager.get_term("opponent")
  cmd = base.command_manager.get_term("twist")
  robot, ball = base.scene["robot"], base.scene["ball"]
  kinds = [getattr(p, "kind", "?") for p in opp.slots]
  n = args.num_envs
  dt = base.step_dt

  for kind in args.opponents.split(","):
    if kind not in kinds[1:]:
      print(json.dumps({"opponent": kind, "error": f"no slot; slots={kinds}"}))
      continue
    slot = kinds.index(kind, 1)
    opp._sample_slots = lambda k, s=slot: torch.full(
      (k,), s, dtype=torch.long, device=dev
    )
    torch.manual_seed(args.seed)
    obs, _ = env.reset()
    opp.slot[:] = slot
    s = {
      k: 0.0
      for k in (
        "scored",
        "conceded",
        "kicks",
        "kick_speed",
        "kick_err",
        "touches",
        "possessions",
        "prog_own",
        "terminated",
        "near",
        "lost",
      )
    }
    prev_touch = torch.zeros(n, dtype=torch.bool, device=dev)
    prev_last = cmd.last_touch.clone()
    with torch.no_grad():
      for _ in range(args.steps):
        if args.blind_opponent:
          obs = obs.clone()
          obs["actor"][:, -3:] = 0.0
        obs, _, _, extras = env.step(policy(obs))
        s["scored"] += float(cmd.contest_scored.sum())
        s["conceded"] += float(cmd.contest_conceded.sum())
        k = cmd.kick_event
        s["kicks"] += float(k.sum())
        s["kick_speed"] += float(cmd.kick_speed[k].sum())
        s["kick_err"] += float(torch.acos(cmd.kick_cos[k].clamp(-1, 1)).sum())
        touch = cmd.last_touch == 1
        foot = base.scene["feet_ball_contact"].data.found
        now = foot.reshape(n, -1).amax(dim=-1) > 0 if foot is not None else touch
        s["touches"] += float((now & ~prev_touch).sum())
        prev_touch = now
        s["possessions"] += float(((cmd.last_touch == 1) & (prev_last != 1)).sum())
        prev_last = cmd.last_touch.clone()
        vel = ball.data.root_link_lin_vel_w[:, :2]
        along = (vel * cmd.field_axis).sum(dim=-1) * dt
        s["prog_own"] += float((along * (cmd.last_touch == 1)).sum())
        s["terminated"] += float(base.termination_manager.terminated.sum())
        d = ball.data.root_link_pos_w[:, :2] - robot.data.root_link_pos_w[:, :2]
        s["near"] += float((d.norm(dim=-1) < 0.6).float().sum())
        s["lost"] += float(cmd.ball_lost.float().sum())
    games = n * args.steps * dt / 30.0  # 30 s games
    kicks = max(s["kicks"], 1.0)
    out = {
      "checkpoint": args.checkpoint.split("/")[-2][-14:]
      + "/"
      + args.checkpoint.split("/")[-1],
      "opponent": kind + ("-blind" if args.blind_opponent else ""),
      "goals_for": round(s["scored"] / games, 3),
      "goals_against": round(s["conceded"] / games, 3),
      "share": round(s["scored"] / max(s["scored"] + s["conceded"], 1), 3),
      "kicks": round(s["kicks"] / games, 2),
      "kick_speed": round(s["kick_speed"] / kicks, 2),
      "kick_err_deg": round(math.degrees(s["kick_err"] / kicks), 1),
      "touches": round(s["touches"] / games, 2),
      "possessions": round(s["possessions"] / games, 2),
      "touches_per_poss": round(s["touches"] / max(s["possessions"], 1), 2),
      "prog_in_poss_m": round(s["prog_own"] / games, 2),
      "near_ball": round(s["near"] / (n * args.steps), 3),
      "ball_lost": round(s["lost"] / (n * args.steps), 3),
      "falls_per_game": round(s["terminated"] / games, 3),
    }
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
  main()
