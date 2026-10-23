# Self-play striker

1v1 striker against striker on a randomised field, to get continuous ball
handling inside the runswift behaviour. Two forms: a **flat** striker (the
kick loop fine-tuned in self-play, 86 inputs) and a **two-level** striker (a
GRU controller choosing between frozen kick and walk skills every 0.2 s).

Sources: `docs/STRIKER_SELF_PLAY_PLAN.md` (living plan: I/O, rewards, phases,
integration), session memory `k1-striker-selfplay` (the v1–v16 and
controller v2–v7 log), code `src/mjlab/tasks/velocity/mdp/self_play.py`,
`rl/selfplay_runner.py`, `rl/striker_runner.py`, `rl/anchor.py`,
`config/k1_amp/selfplay_cfgs.py`.

Note: the Oct 12–16 code for this was stranded in a git stash and restored on
2026-10-23 (commit 69560d3); the original is branch
`archive/selfplay-stash-2026-10-16`.

## Tasks

| Task | What learns |
|---|---|
| `Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1` | phase 2: the kick skill, inside the game |
| `Mjlab-Velocity-Striker-Controller-Booster-K1` | phase 1 / 3: the controller, skills frozen |

Game: field 9×6 to 14×9 m, 2.4 m goals; goal or out ends the point and the
side that did not cause it restarts; 30 s episodes. Opponents: frozen mirror
copies and a pool (h022, walk 9950, controller v2, snapshots).

## Current best

| Model | Result | Where |
|---|---|---|
| **swa_v15v16_9100** (flat) | Actor-weight mean of v15/7600 + v16/8100–9100. Under the same scripted controller it beats the h022 kick: goal share 0.421 vs 0.402, 6/6 seeds, paired t = 4.3 (p ≈ 0.008). Deployed alone (user request) | `logs/rsl_rl/k1_kick_selfplay_amp/swa_v15v16/model_9100.pt`; `k1_policy_runner/kick_loop_models/k1_kick_loop_swa_v15v16_9100.onnx` |
| **controller_v2 / 1750** + h022 kick | Best two-level system: 0.441 goal share vs h022 (big eval, 1536 envs × 2 seeds) | `logs/rsl_rl/k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt` |

No retrained controller (v3–v7) beat controller_v2. The decision layer adds
only ~+0.02–0.04 over a scripted rule ("walk if the ball is > 3.5 m away, else
kick at goal").

## Measurement rules (learned the hard way)

- Judge phase-2 runs only with the **deterministic fixed-opponent eval**
  (`scripts/tools/selfplay_eval.py` → `logs/selfplay_eval/*.jsonl`), never by
  self-play curves; controllers with `scripts/tools/controller_eval.py` →
  `logs/controller_eval/`.
- Single 384-env evals vary ±0.02–0.05 by seed. Use ≥ 1536 envs × 2 seeds with
  a CI; the "0.454 bar" from small evals was noise.
- Check the mirror match ≈ 0.5 before trusting win rates. The field still has
  an unexplained handicap: h022 vs h022 gives ~0.41, not 0.5 (learner touches
  first only 22 % after its own restart; touch sensors differ between sides).
  Report results relative to the ~0.41 mirror.
- Run evals with `timeout -k 30 N .venv/bin/python ...`; a `timeout uv run`
  eval hung for 8 h holding the GPU.

## What was learned

1. **Every stage-3 positive shaping term must be re-audited for farming.**
   p2_kick_v1 farmed `search_turn` because in self-play the opponent takes the
   ball away; ball-lost became a penalty.
2. **Annealing the kick-technique terms degrades the kick** (goals and
   territory don't hold technique). Keep technique terms at full weight;
   anneal only approach / positioning shaping, with a floor.
3. **Self-play fine-tuning random-walks away from the warm start.** At
   desired_kl 0.01 with Muon, every run got worse against h022 the further it
   drifted (actor weight change 22–36 %, KL to h022 1.25–2.33 nats vs goal
   shares 0.26–0.14). Fixes: fixed LR 1e-4 and the **KL anchor**
   (`AnchoredAmpPPO`, β·KL to a frozen reference, β 0.5 → 0.1). Anchor to the
   best checkpoint after a reward fix, not to the old baseline (anchoring to
   h022 dragged a better approach back).
4. **Stage 3's `walk_speed` paid following a ball the opponent carried away.**
   `walk_engage` (closing speed toward the ball down to 0.6 m) replaced it in
   self-play only.
5. **Every run peaks a few hundred iterations after a fix, then slides.**
   Freezing α (v13) was the first run not to decline, supporting "continued
   annealing drove the slide".
6. **Possession change** (±6, zero-sum) plus γ 0.998 gave the first checkpoint
   above h022 vs h022 (v14/5100: 0.415). Gains were defensive; lowering the
   action-std cap to 0.4 (v15) gave the first attack gain. A further cap (0.25,
   v16) added nothing; SWA over v15/v16 was the best.
7. **A better low-level skill doesn't transfer without re-adapting the
   controller:** controller_v2 got worse with the SWA kick (0.394 vs 0.425 on
   4/4 seeds).
8. **Walking near the ball is disastrous** for these skills (scripted walk-if
   > 1 m: 0.11), so low walk use is rational. Better skills (a dribble skill,
   a kick robust in controller situations) are the real lever, not more
   controller training.
9. Controller GRU memory must be reset at kickoffs/restarts (the real runner
   zeroes it at each takeover); `MemoryResetPPO` splits BPTT at resets.
10. Controller aim directions must be held fixed in world between decisions
    (`aim_world`), as the runner does by IMU yaw.

## Open

- The ~0.09 field handicap cause.
- controller_v7 (SWA kick, v2 recipe) results were not recorded.
- Deferred sim2real items: detection false positives / multiple robots,
  aim and localisation noise, decision jitter, takeover states, GRU ONNX
  sequence parity.
- Integration into the runswift behaviour (`StrikerIntent`, `StrikerPolicy`),
  plan §7.
