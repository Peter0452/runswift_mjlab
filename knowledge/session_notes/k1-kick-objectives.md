---
name: k1-kick-objectives
description: "User's objectives for the K1 kick-loop policy (runswift_mjlab stage3) — kick quick, power by range, run at the speed cap, upright 0.52 m"
metadata:
  node_type: memory
  type: project
  originSessionId: 03a30a32-4b87-4b76-ade4-979cf900f3dd
  modified: 2026-10-08T09:56:08.836Z
---

K1 kick-loop policy objectives (stated by the user, refined 2026-10-03):
- (2026-10-08) Headline: kick **faster, more accurate and more powerful than B-Human across diverse ball sizes** (not just mass), without sacrificing stability, no falls, smooth actions. User also reports the real robot's stepping is too loud (open issue).
- (2026-10-07) Long >= 8 m: no speed cap, as strong as or stronger than B-Human, **air balls fine** (no loft penalty); 4-8 m stays distance-matched; evaluate light AND heavy ball; runswift's fixture is a proxy soft gate (may be a bit worse where its ideal assumptions matter, must not be worse on falls / accuracy / kick speed); current priority: time to kick (esp. low caps) and long power without losing accuracy/safety; style choice must be learned from outcomes (speed, accuracy), not forced by range.
- Kick **quickly** once at the ball; **power matched to range**: short 1–4 m soft/accurate, medium 4–8 m, long ≥ 8 m as hard as possible (7–8 m/s goal; fastest reliable kick if out of reach).
- **Run according to the speed caps** (caps for ball play, not commands): |vx| ≤ 2.0 fwd / 1.75 back, |vy| ≤ 1.5, |wz| ≤ 1.5 — the policy should actually reach them.
- Upright, no lean even at speed, height ~0.52 m, no crouch / knock-knee / wide arms / head up, flat feet; gait as smooth as the gold AMP walk (model_9950).
- **One end-to-end kick policy** (no policy switching / walk–kick hybrids for now, user 2026-10-06); external methods (B-Human etc.) only enter through data, scenarios, rewards, constraints, training algorithm or distillation into this policy. Approach-level (L5) loop runs every few hours / ≤ half a day, earlier when lower loops finish.
- **Kick styles** (user 2026-10-05/07): keep several styles (front, inside foot, hop, ...) in the repertoire and let the policy choose the best one for each situation — not a style forced by range. Measured by benchmark v2 `style_selection_pct` / `style_repertoire`.
- Accuracy, few falls, sim-to-real fidelity; 83 inputs fixed; one fine-tune lineage, never compromise built-up objectives; truthful reporting.

**Why:** soccer competition deployment on the real K1.
**How to apply:** judge every run against all of these (eval_kick_loop modes, range_hesitation.py, cap_compliance.py, lean_vs_speed.py, runner bench); one change per run, keep the peak checkpoint. Related: [[k1-kick-staged-training]], [[kick-dr-from-amp-walk]]
