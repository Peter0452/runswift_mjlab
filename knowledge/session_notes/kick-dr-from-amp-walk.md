---
name: kick-dr-from-amp-walk
description: "Kick training DR/actuator/latency settings deliberately inherit from the AMP walk; don't change them because other configs differ"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 03a30a32-4b87-4b76-ade4-979cf900f3dd
  modified: 2026-10-02T12:15:16.028Z
---

The K1 kick (stage 3) domain randomization, actuator model and latency settings are deliberately based on the AMP walk config (which transfers well to the real robot), plus a few kick-specific additions. Do not change training settings just because another source differs (e.g. runswift `booster_deploy` K1 effort limits 30/40 Nm vs training 68/112 Nm, the plain k1 walk's 0–2 step sensor delay, runner hip-roll target clip).

**Exception (user, 2026-10-07):** leg torque must use B-Human's kick clip (hip pitch/roll 50, hip yaw 30, knee 60, ankle pitch/roll 30 Nm) as a hard limit; the motor effort numbers we had (knee 112, hip roll 76, hip pitch 68, ...) are believed to be no-load ratings. Exact loaded limits are not known yet — keep them in one table so measured values can replace them.

**Why:** the user built it this way on purpose (2026-10-02); the AMP walk is the proven sim-to-real reference.

**How to apply:** report such mismatches as observations only; propose training changes only with evidence from robot data (e.g. a recorded run, measured latency), and get the user's go-ahead. Runner-side diagnostics/fixes are fine but keep behaviour-changing ones opt-in. See [[k1-kick-staged-training]].
