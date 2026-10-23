---
name: k1-kick-staged-training
description: "User's 3-stage K1 kick curriculum (walk → approach → kick) and the warm-start handoff required between stages"
metadata:
  node_type: memory
  type: project
  originSessionId: 03a30a32-4b87-4b76-ade4-979cf900f3dd
  modified: 2026-10-01T04:00:16.997Z
---

User trains the K1 kick in stages, reusing one 83-dim actor obs layout:
1. Stage 1 (`Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1`, exp `k1_kick_stage1_amp`): walk; dims 75–82 (speed_limit, kick_direction, kick_range) are `constant_zeros` placeholders.
2. Stage 2 (`Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1`, exp `k1_kick_approach_amp`): slots 72–73 = ball xy (masked outside camera FOV), 74 unused (0), 75–77 per-episode |vx|,|vy|,|wz| limits, 78–79 kick dir from last-seen ball, 80–82 kick-range one-hot (unrewarded until stage 3). Actor must never see true ball state when unseen.
3. Stage 3: kick, enables kick_range.

**Why:** On 2026-10-01 a plain `--agent.resume` from stage1 model_9000 collapsed (episodes ~12 steps, KL 22) because the placeholder dims had normalizer std=0 (x100 amplification) and untrained weights.

**How to apply:** Hand off between stages with `scripts/prepare_warmstart.py --reset-obs-dims 74:83 --normalizer-count 10000000`, then train with `--agent.resume True --agent.warm-start True`. That fixed stage 2 (smoke test: ball dist 2.5→0.65 m in 60 iters). Use the same approach for stage 3 on any dims the previous stage held constant.

Stage 2 issue log lives in `runswift_mjlab/docs/K1_KICK_APPROACH_NOTES.md` (warm-start collapse, spec redesign, 2026-10-01 sim blow-up at iter 5121 of `approach_v2` → `physics_blowup` + `invalid_state` reward guard; last good ckpt `model_5100.pt`).

Stage 3 (user wants ONE policy, multi-kick loop: approach → kick → stay stable → re-find ball → kick again; exact ball speed deferred): task `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`, code `mdp/kick_loop.py`, notes `docs/K1_KICK_STAGE3_NOTES.md`, eval `scripts/tools/eval_kick_loop.py`. Kick range bins 1–4 / 4–8 / 8–10 m; robot should align and kick quickly within ~1–1.5 m. Rewards follow the user's list (ball vision, kick dir alignment, walk speed + limit, kick direction, kick vel + accurate, ball avoidance, single-foot avoidance). First full run 2026-10-01_23-57-30_stage3_v1.

Stage 3 lessons (2026-10-02, runs v1–v7, see docs/K1_KICK_STAGE3_NOTES.md "Run log"): zone-tied costs/style drops fence the ball (v1 hovered); per-second "staying up" reward must stay positive (v2 fell on purpose); kick speed rewards must be aim-gated (v3 sprayed); action std must be capped (std_range max 0.6) — it grew in every run otherwise. Ball memory (last-seen ball + age in slot 74, mirror keeps slot 74) and sharp aim fixed aim/goals. Tools: scripts/tools/reward_budget.py (flags) and watch_run.py (background watchdog).

Stage 3 outcome (2026-10-02 night, v1–v16): recommended ckpts stage3_v16/model_1700 (balanced) and stage3_v13/model_1650 (safest), ~71% kicks within 20°, falls after first 2 s ~1.5%. Key finding: continued training trades safety for productivity regardless of step size/style/fall penalty → select checkpoints by eval_kick_loop.py ~50–150 iters after a change. gamma 0.995, sharp aim, dof_pos_limits −10 helped. Open: real ball params, kick speed control.

Sim-to-real (2026-10-02, v17–v21): the user's gold standard for smoothness/stability is `k1_velocity_amp_symmetric_muon_wwcmu50_roughft/2026-09-21_20-34-24_stageA/model_9950.onnx`; compare kick models to it with `k1_policy_runner/python-implementation/sim2real_bench.py` (run with runswift_mjlab/.venv/bin/python). The user's acceptance is multi-objective: good kick AND posture close to the gold walk (knee gap, arms, head) AND smoothness (jitter ≤ ~2×). Real head camera: CAM_ANGLE_X/Y = 1.211 × 0.733 rad full FOV. From v21 the head is driven by a scripted ball tracker (same code in training and runner) so the user can control the head on the robot. action_rate did not smooth actions; CAPS (amp_ppo caps_temporal/spatial) did, but strong CAPS cost kick accuracy.

Gait/robot lessons (2026-10-02, v21–v32): the runner has no odometry, so training must use the same rotation-only ball memory (`memory_odometry=False`) or the head/approach fail on the robot. Stage 3 drifted to a crouched, wide, fast-stepping gait (stage 2 walked like the gold walk); walking-pose terms gated to ball > 1 m (base height, stance width, knee valgus) fix it without hurting the kick, but gating them up to 0.6 m cost kick quality, and raising AMP style weight cuts task rewards ((1−w)·task). A per-touchdown short-swing penalty was gamed (cadence rose). Judge checkpoints with 2 seeds × 1024 envs plus runner-sim `sim2real_bench.py` and `gait_bench.py` (walking-only, speed-matched); a policy standing still looks smooth.

Reward-design lessons (2026-10-03, v33–v38): (1) a target band far from current behaviour, or a band with a gentle Gaussian falloff, gives no gradient — use a monotonic ramp toward a curriculum target (long-kick swing speed moved only after that, v36). (2) Normalise speed rewards by min(cap, 1 m/s): speed/cap made higher caps pay less (v34 walked slower), speed/1 m/s made low caps not worth walking (v36 idled). (3) On resume the runner sets env.common_step_counter to the checkpoint's, so curricula keyed to it skip — count the term's own steps. (4) Compare heel-up, jitter and arms per speed bin; aggregates rise just because the robot walks faster. (5) Feasibility probe: scripted swings in the training sim launch the 0.1 kg ball at 7–12 m/s, so 7–8 m/s is a balance/skill problem, not a motor limit. Notes: docs/K1_KICK_STAGE3_NOTES.md.

More lessons (2026-10-03, v39–v46): measure kick speed with the nominal 0.1 kg ball (ball DR up to 0.25 kg hid a +36 % long-kick gain: v43/7550 long kicks 4.34 m/s mean, p90 6.75). CAPS limits the kick swing but not walking speed — phase-weighted CAPS (full while walking, ×0.5 within 0.8 m of the ball, `caps_near_ball_scale`) keeps walk smoothness and frees the swing. Per-kick aim reward must scale with ball power or the policy farms weak taps. Walking cruise ~1.3 m/s and cadence ~7 steps/s were not moved by reward size, farther balls or air_time. Best balanced sim checkpoint at this point: v43/7550 (v45/7800 more accurate).
