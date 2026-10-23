---
name: k1-real2sim-findings
description: First real-robot kick-loop recordings (2026-10-09) - on/off causes and real-vs-sim gaps; doc + tools locations
metadata:
  node_type: memory
  type: project
  originSessionId: 3a20863c-73ea-4c5a-b1e6-51ea45110a55
  modified: 2026-10-20T04:33:04.946Z
---

Robot K1 #291 (user: other robots may differ; 291 vision mostly correct). Real K1 runs real_1009_1120 / _1122 (h022_c2_18450, caps 1.5,1.5,2.0) analysed in
runswift_mjlab/docs/K1_REAL2SIM_2026-10-09.md. On/off causes: one real dynamic fall
(knee -74 Nm, wz cap 2.0 outside training); runner "zombie" after falls (damping set,
policy keeps running when a handled robot tilts < 70 deg, never re-enters custom mode);
/nubots_walk/enable flickers 0.3-0.6 s that reset the policy mid-step; external loss of
motor authority while upright near the ball (cause outside runner - log Booster mode).
Real vs sim (driven steps): cadence ~20 % slower, knee torque higher / hip lower,
heavier tail of hard footfalls (p90 33-43 vs 27 m/s2), vision ~16 Hz vs every step,
ball lost 2-13 %. Tools in k1_policy_runner: --kick-record, kick_record_analyze.py,
real_sim_compare.py.

**Dribble run dribble_1019_1634 vs kick runs (analysed 2026-10-20, scratchpad deep.py-style per-joint analysis; sim ref = MuJoCo runner swaA fixed 0.5 m/s):**
- Lag q vs target ~4 steps (80 ms) on real AND sim → delay is not the gap.
- Real torques exceed the MuJoCo runner EFFORT_LIMIT and the 30 Nm B-Human ankle clip: knee max 64–74, ankle pitch 45–52, hip roll 41 Nm. The MuJoCo runner saturates ankles/hip roll at 24/25 constantly → sim2sim is harsher than the robot there.
- Real torque fits the commanded PD poorly (knee tau/PD slope 0.17–0.38, corr 0.55–0.74 vs sim 0.6, 0.86–0.9); knee tracking error +50% → weakest-tracking joint on the robot.
- In every real run: left hip pitch p99 ~30% above right, right ankle roll ~50% above left; sim symmetric → robot-specific asymmetry (#291).
- Knee: real p99 higher but p50 LOWER than sim (dribble 3.7 vs 5.8, kick 4.7–6.1 vs 9.3 Nm). Excess is only within ±2 steps of footfalls (p90 28–31 vs 19–25 Nm sim); elsewhere equal → landing impacts, not steady weight/CoM. Hip pitch lower throughout.
- Trunk pitch gap is NOT consistent: kick real leans ~1.5–2° less forward than sim, dribble real ~7° more forward (sim dribble −6.8°).
- Cadence gap is task-dependent (kick real 20% slower, dribble real ~15% faster) → not a fixed actuator speed property.
- Impacts (softer median, harder tail), smoother actions (0.10 vs 0.15) and vision (~16–17 Hz, 2–13% lost, ~4–5% gate rejects) repeat in both tasks.

**Why:** user wants a sim2real bridge; these are measured, not guessed.
**How to apply:** use the doc's numbers before changing DR / runner; runner fixes
(fall latch, enable debounce, authority check, mode logging) not yet implemented as of
2026-10-09. Related: [[kick-dr-from-amp-walk]], [[k1-kick-objectives]].
