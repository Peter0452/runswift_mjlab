# Dribble

Move the ball at a commanded velocity, with a kick mode (slot 82), search for
a lost ball, and approach from far. Task
`Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1`, experiment
`k1_dribble_amp`, code `src/k1/tasks/dribble/mdp/dribble.py` and
`dribble_rewards.py`.

Sources: session memory `k1-dribble-speed` (the full v13–v53 log),
`dribble-kick-objectives`, `dribble-speed-over-slow`,
`gait-penalty-weighting`; runner docs `k1_policy_runner/python-implementation/DRIBBLE_POLICY_IO.md`.

## Current best (2026-10-23, work paused by the user at ~11:40)

| Model | Why | Source checkpoint |
|---|---|---|
| **v51_11750** | Most balanced: power 3.07 / p90 5.10 m/s, error 14.6° (72 % within 15°), search 55 %; fails slow dribble, falls, jitter, tilt gates | `2026-10-23_08-22-20_dribble_aimhead_v51/model_11750.pt` |
| v51_11250 | Best kick technique and time: inside-foot 41 %, straight-kick time 0.95 / 1.20 / 1.37 s at 0.5 / 1.0 / 1.5 m/s | same run, `model_11250.pt` |
| v51_10750 | Cleanest gates (3 fails); search 59 % | same run, `model_10750.pt` |
| v49_10250 | Previous base; error 14.6°, search 42.5 %, passes v17 slow dribble | `2026-10-23_05-35-32_dribble_aimwide_v49/model_10250.pt` |
| swa_v17 / swa_v16 / swaA_v15b | Earlier pure-dribble deploy candidates (no kick mode) | `logs/rsl_rl/k1_dribble_amp/swa_v15/*.pt` |

ONNX for each is in `k1_policy_runner/dribble_models/` (named
`k1_dribble_<tag>_<version>_<iter>.onnx`). Loading a v20+ checkpoint needs the
same `DRIBBLE_GENES` env var it was trained with (the discriminator input
grows with `amp_cond`); each run dir has `genes.json`.

## How runs are made

- Per-run switches are **genes**: `DRIBBLE_GENES` (JSON) read in
  `dribble_rewards.py` and `rl_cfg.py`; empty = the v17 recipe. One gene change
  per run.
- Watcher `scripts/tools/dribble_watch_bench.sh` benches every N iterations:
  deploy-config eval, ONNX export, parity, runner bench, gate. It must get the
  run's genes in its env.
- Gate `scripts/tools/dribble_gate.py` vs v17: slow success (−0.08 at 0.3 /
  0.5 m/s, −0.03 at 0.8), falls, ball distance, runner falls 0, flat stance
  70–87 %, landing force, torque saturation, per-leg torque / Δq / jitter /
  angular rate ≤ ×1.15, tilt, stop, tracking, parity ≤ 1e-4.
- Evals: `scripts/tools/dribble_eval.py` (speed bins; `--odom`,
  `--ideal-vision`, `--nominal-ball`, `--no-joint-clip`, ...),
  `dribble_skill_eval.py` (approach / search / kick / transition tests),
  `k1_policy_runner/python-implementation/dribble_bench.py` (runner MuJoCo).

## What has been learned

**Speed ceiling.** Forward dribble speed plateaus near 0.85–0.9 m/s in the
deploy config (1.1–1.2 runner sim). Ball speed equals robot speed in every
bin, so the limit is how fast the robot moves while dribbling. Levers tried
and exhausted: tracking σ (v18), fast AMP mix (v19: +0.06 m/s but 16° forward
lean), command-conditioned AMP (v20: +0.05–0.08), push-and-chase gates (v21–v27),
drive weight (v31), cap obs. Deploy conditions (joint clip, torque clip,
delay) together cost ~0.14 m/s. Remaining levers are structural: kick-and-chase,
a faster locomotion base, or accept it.

**Kick power.** Stuck at ~3.0 m/s mean (p90 ~5) across every reward lever
(v33–v52), vs B-Human ~3.9–4.3. The kick-loop teacher (h011, imitation on
legs) anchors power: teacher off (v34) dropped to 2.63 m/s. More kick windows
(v52) trained approach/search, not kicking.

**B-Human cannot be copied action by action.** B-Human acting within 1.2 m
kicks 3.91 m/s (p90 7.24), 9.5°, inside foot 94 %. But imitating its actions
(v41) collapsed our kick (1.96 m/s, 37°), and teacher takeover (v43) also made
the student worse. Likely cause: B-Human acts on a gait clock our policy cannot
observe. Don't retry plain action imitation of B-Human.

**What worked (adopted):**
- v30: more far spawns and ball vanishing (approach / search practice) —
  search 23 → 44 %, falls down.
- v33: air balls allowed, higher kick cap and weight — power p90 4.85 → 5.30.
- v35: side kick gated by geometry (> 30° off the approach line) — better aim.
- v36: kick teacher only on straight kicks — inside foot 11 → 24 %.
- v42: side-kick weight 300 → 1000 — inside foot 40 %, best aim then.
- v49: fixed wide aim σ² 0.35 — aim −1.3°.
- v50/v51: reward the head ~15° down while the ball is lost — search
  40 → 60 %. Root cause: the head looked ~40° down with a 21° vertical
  half-FOV, so the view ended 2–3 m out and spinning faster (v48) couldn't help.

**What did not:** CAPS 2.0 (sluggish recoveries), signed aim penalty, pose
gate, adaptive aim curriculum (oscillates), quick-kick pay (`kick_quick_tau`
cut search twice), spin weight, B-Human imitation, blending dribble and kick
checkpoints (worst of both), kick_prob 0.5.

**Smoothness lineage:** runner leg jitter 0.066 (v17) → 0.080 (amp_cond) →
0.095 (sprint / vanish / kick scenarios) → ~0.10 (teacher era). The scenarios,
not the teacher, added most of it.

**Robot (swaA, #291, 2026-10-19):** 1.9 falls per upright minute vs 0.13 in
sim (0.80 in the deploy-matched sim). Falls came after fast yaw and large
knee/ankle tracking errors; the right leg was loaded more. This drove the
deploy-match config (`_dribble_deploy_match`) and the runner fall latch.

## Open

- Speed beyond ~0.9 m/s; kick power to B-Human level; jitter back toward 0.07.
- Next planned (not started): actor observation history (mjlab
  `ObservationGroupCfg.history_length`, runner `ObservationHistory`), warm
  started with zero columns; separate model version. **History length N = 10
  for joints, ball and every other dribble input (user, 2026-10-28).**
- Plan agreed 2026-10-28, to start after the current kick work, in this order:
  0 re-measure v51 on B-Human's ball; 1 fine-tune it there (desired_kl 0.002 +
  checkpoint averaging; the control for 3); 3 observation history N = 10 (new
  family dribble_v2); 2 speed toward **2 m/s** (user, 2026-10-28): push-and-chase
  with widened proximity / lost / success envelopes, chase caps (vx 2.0) with the
  runner's --dribble-speed-limits raised to match (contract, bundle with
  dribble_v2), and the robot fall gap (1.9 / min at ~0.8 m/s) closed first.
  Phase 4 (walk / dribble / kick controller compatibility) dropped for now.
- Runner run-time modes (kick / stop / dribble via buttons or a topic) are
  coded but untested on ROS.
- Trim the dribble runs (all checkpoints since 2026-10-20 are still kept) once
  the user says this work is finished.
