"""Fixed-opponent evaluation of a two-level striker (the controller learns).

Deterministic controller, decision chunks as in training, the chosen kick
skill. GRU memory is zeroed at episode ends and at every kickoff / restart
(as the robot's runner does on each striker takeover), never at random.
Prints one JSON line per opponent.

  .venv/bin/python scripts/tools/controller_eval.py --kick-skill SKILL \
      [--controller CTRL] [--seed SD] [--opponents kick,walk]
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict

import torch

import mjlab.tasks  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

TASK = "Mjlab-Velocity-Striker-Controller-Booster-K1"
CTRL = (
  "logs/rsl_rl/k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt"
)


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--controller", default=CTRL)
  ap.add_argument("--kick-skill", required=True)
  ap.add_argument("--num-envs", type=int, default=384)
  ap.add_argument("--decisions", type=int, default=150)
  ap.add_argument("--seed", type=int, default=7)
  ap.add_argument("--opponents", default="kick,walk")
  ap.add_argument(
    "--aim-world",
    action="store_true",
    help="hold decisions' directions fixed in the world (aim_world)",
  )
  ap.add_argument(
    "--stochastic",
    action="store_true",
    help="sample the controller's actions with its noise, as in training",
  )
  args = ap.parse_args()
  dev = "cuda:0"
  ec = load_env_cfg(TASK)
  ec.scene.num_envs = args.num_envs
  ec.seed = args.seed
  oc = ec.actions["opponent"]
  oc.kick_skill_checkpoint = args.kick_skill
  oc.controller_checkpoint = args.controller
  oc.sample_copies = False
  oc.memory_reset_mean_s = 1.0e9  # kickoff / restart resets only
  oc.aim_world = args.aim_world
  ac = load_rl_cfg(TASK)
  rc = load_runner_cls(TASK)
  base = ManagerBasedRlEnv(cfg=ec, device=dev)
  venv = rc.make_vecenv(base, ac)
  runner = rc(venv, asdict(ac), device=dev)
  runner.load(args.controller, load_cfg={"actor": True}, strict=True, map_location=dev)
  model = runner.get_inference_policy(device=dev)
  opp = base.action_manager.get_term("opponent")
  cmd = base.command_manager.get_term("twist")
  kinds = [getattr(p, "kind", "?") for p in opp.slots]
  n, dt = args.num_envs, base.step_dt

  s: dict[str, float] = {}
  inner_step = base.step

  def step(action):
    out = inner_step(action)
    k = cmd.kick_event
    s["scored"] += float(cmd.contest_scored.sum())
    s["conceded"] += float(cmd.contest_conceded.sum())
    s["kicks"] += float(k.sum())
    s["kick_speed"] += float(cmd.kick_speed[k].sum())
    s["kick_err"] += float(torch.acos(cmd.kick_cos[k].clamp(-1, 1)).sum())
    s["terminated"] += float(base.termination_manager.terminated.sum())
    s["kick_skill"] += float(venv.kick.float().sum())
    s["steps"] += n
    return out

  base.step = step  # type: ignore[method-assign]
  for kind in args.opponents.split(","):
    slot = kinds.index(kind, 1)
    opp._sample_slots = lambda k, sl=slot: torch.full(
      (k,), sl, dtype=torch.long, device=dev
    )
    for key in (
      "scored",
      "conceded",
      "kicks",
      "kick_speed",
      "kick_err",
      "terminated",
      "kick_skill",
      "steps",
    ):
      s[key] = 0.0
    torch.manual_seed(args.seed)
    obs, _ = venv.reset()
    opp.slot[:] = slot
    model.reset()
    with torch.no_grad():
      for _ in range(args.decisions):
        obs, _, done, extras = venv.step(model(obs, stochastic_output=args.stochastic))
        model.reset(done.bool() | extras["memory_reset"])
    games = s["steps"] * dt / 30.0
    share = s["scored"] / max(s["scored"] + s["conceded"], 1)
    kicks = max(s["kicks"], 1.0)
    print(
      json.dumps(
        {
          "seed": args.seed,
          "controller": args.controller.split("/")[-2][-14:]
          + "/"
          + args.controller.split("/")[-1],
          "skill": args.kick_skill.split("/")[-2][-14:]
          + "/"
          + args.kick_skill.split("/")[-1],
          "opponent": kind,
          "goals_for": round(s["scored"] / games, 3),
          "goals_against": round(s["conceded"] / games, 3),
          "share": round(s["scored"] / max(s["scored"] + s["conceded"], 1), 3),
          # 95 % binomial interval of the share over this run's goals.
          "share_ci95": round(
            1.96
            * math.sqrt(
              max(share * (1 - share), 1e-6) / max(s["scored"] + s["conceded"], 1)
            ),
            3,
          ),
          "goals": int(s["scored"] + s["conceded"]),
          "stochastic": args.stochastic,
          "aim_world": args.aim_world,
          "kicks": round(s["kicks"] / games, 2),
          "kick_speed": round(s["kick_speed"] / kicks, 2),
          "kick_err_deg": round(math.degrees(s["kick_err"] / kicks), 1),
          "kick_skill_share": round(s["kick_skill"] / s["steps"], 3),
          "falls_per_game": round(s["terminated"] / games, 3),
        }
      ),
      flush=True,
    )


if __name__ == "__main__":
  main()
