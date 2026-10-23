---
name: bhuman-kick-port
description: "B-Human's Booster Gym K1 kick training pipeline ported into runswift_mjlab (2026-10-18) - tasks, runner, validation, known deviations"
metadata:
  node_type: memory
  type: project
  originSessionId: 9e5ab7e4-02f7-447d-821c-fd8f902a8ee5
  modified: 2026-10-17T23:36:57.117Z
---

On 2026-10-18 the user asked to port MachineLearning/IsaacGymRL (B-Human Booster Gym) kick training into runswift_mjlab. Result: `src/mjlab/tasks/bhuman_kick/`, tasks `Mjlab-BHuman-Kick[-StageN]-Booster-K1` (Stage1..Stage6, cumulative per B-Human's readme), own PPO runner (`BHumanPpoRunner`, loads Booster Gym .pth via `--agent.bhuman-checkpoint`), eval `scripts/tools/eval_bhuman_kick.py`, doc `docs/K1_BHUMAN_KICK_PORT.md`. One shared-code change: opt-in `CommandTerm.post_physics_step` hook called in `ManagerBasedRlEnv.step` before terminations/rewards.

**Why:** a faithful B-Human baseline on our simulator, to compare/mix with our kick (see [[benchmark-gated-adoption]]); separate from the one-end-to-end-policy objective in [[k1-kick-objectives]].

**How to apply:** validation = B-Human's own K1_kick_inner.pth in the port (aim p50 ~3 deg, 79-93 % within 10 deg, scaled speed matches sqrt(2*0.3*range), falls 0.2-0.3/robot-min). Re-run that check after changing the port. Known deviations (one model for 3 robot variants, per-env sole friction instead of patch friction, ball damping per policy step) are listed in the doc. Their K1_walk_start_for_kick.pth falls 2-4/robot-min in stage 1 (unverified vs Isaac Gym). Pre-existing unrelated failures: tests/test_k1_kick_stage3.py (2 stale tests).

2026-10-18 later: user's B-Human kick benchmark v2 spec implemented as `scripts/tools/bench_bhuman_kick_v2.py` (pretrained 0.925 vs their 0.927). Port gained `--agent.decap` (mocap kick clips, from_kick_clips) and `--agent.amp` (gold-walk mix, gated off near ball). A/B started: runs ab_baseline / ab_decap / ab_decap_amp, 2000 stage-1 iterations each from K1_walk_start_for_kick.pth, to be judged on bench v2 + eval_bhuman_kick (iterations-to-real-kicks matters most for DecAP). Don't use bhuman_side clips as a prior for the port (they are B-Human's own policy rollouts).
