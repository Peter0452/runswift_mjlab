# K1 kick styles in one policy: inside foot (B-Human) + hop kick

2026-10-06, user: "I want hop_kick, B-Human style inside foot kick in the
current model tonight. That leaves the question of when to use it, explore
the option." One end-to-end policy, 83 inputs, warm-started from the
champion (x4_g004_70 / model_14200).

## Evidence before training (kick_anatomy, ball 0.4–1.5 m, any bearing, perfect perception)

| | x4 champion | B-Human |
|---|---|---|
| long kicks: hop (both feet up) share | 12 % | 6 % |
| long, hop: ball 3D p50 / aim ≤ 20° | **5.93 m/s** / 95 % | 4.01 / 88 % |
| long, planted: ball 3D p50 / aim ≤ 20° | 5.09 / 95 % | 5.74 / 98 % |
| inside-foot share (foot yaw 60–120° to the kick line) | 1 % | 97 % |
| short/medium ball 3D p50 / aim ≤ 20° | 3.87 / 93 % | 2.57 / 99 % |
| short/medium support planted | 89 % | 100 % |

Reading: for us the hop is the more powerful long kick at equal aim; B-Human's
inside foot is the accurate, softer pass (matches "power by range").

## Mechanism (kick_loop.py, STYLE_MAP)

- Detected at contact: `kick_inside` (signed toe-out yaw of the kicking foot vs
  the kick line, Gaussian match to a curriculum target) and `kick_hop` (no foot
  on the ground).
- Inside-foot target rises 20° → 90° in 8.6° steps whenever 40 % of styled kicks
  match (B-Human raised its sole-yaw target 0 → 90° by hand; our fixed-90° ramp
  reward found only 1 % side-foot kicks).
- `STYLE_SHARE_*`: part of a styled kick's quality (all kick rewards) depends on
  the mapped style (B-Human: direction reward × (0.5 + 0.5 × sole match)).
- Rewards: `inside_foot_style`, `hop_kick_style` (power-gated: a weak hop earns
  nothing), `hop_kick_fall` (falls within 2 s of a hop).
- Default `STYLE_MAP = "off"`: the champion recipe is unchanged.

## When to use which: options

| # | Rule | Inputs | Status |
|---|---|---|---|
| A | **Range-mapped**: short/medium → inside foot, long → hop (range one-hot already observed) | unchanged | training (`sty_range`, `sty_range_strong`) |
| B | **Free choice**: both styles paid in every range; outcome rewards (aim, speed match, rest accuracy, goals, falls) pick | unchanged | training (`sty_free`) |
| C | **Situation-mapped**: inside foot when the kick must be redirected (kick direction far from the approach heading) or the ball is beside the robot; hop only when aligned, long, and running in | unchanged (ball xy + direction observed) | next, if A/B show the styles are learnable |
| D | **Commanded**: style slot from the runner / behaviour (`--kick-style auto/inside/hop`) | +1–3 dims, runner change | needs user approval |
| E | **Learned selector + archive**: per-situation benchmark cells (range × bearing × speed), keep the best style per cell (QD) | unchanged | later; uses the C/D machinery |

Judged on the fixed benchmark plus the style metrics
(`style_inside_short_pct`, `style_hop_long_pct`, `h2h_support_planted_short_pct`,
`hop_fall_pct`). Overall `h2h_support_planted_pct` will drop by design when long
kicks hop; it is reported, and the short/medium planted share replaces it for
styled runs.

## Runs (2026-10-06 night)

All from x4/14200 with the champion genes, plus `rsi_bhuman 0.15`, kick clips in
the AMP data, `KICK_STYLE_AMP 1`, `w.inside_foot_style 300`, `w.hop_kick_style 300`,
`w.hop_kick_fall -1000`, 2000 iterations.

- `sty_range`: STYLE_MAP range, inside share 0.5, hop share 0.
- `sty_free`: STYLE_MAP free.
- `sty_range_strong`: range, inside share 0.7, `w.inside_foot_style 600`, `rsi_bhuman 0.3`.

Results: (pending)

## Overnight loop alignment (2026-10-06, user: optimise accuracy, time to kick, power; beat B-Human convincingly; keep iterating)

- One fitness for both loops (`evolve_kick.score`): tolerance-normalised gains over the
  champion, primary objectives (accuracy, time to kick, power: `kick_benchmark.PRIMARY`) x3,
  other head-to-head x2, the rest x1; +2 per head-to-head metric newly beating B-Human by
  at least its tolerance (`convincing_beats`). Every metric remains a no-regression gate.
- L1 (genes / weights): style genes added, incl. the categorical `k.STYLE_MAP`
  (off / range / free), style weights, style shares, curriculum step.
- L2 (reward structure): new grammar signals `kick_inside`, `kick_hop`, `kick_near_time`;
  templates `quick_kick` (time to kick), `hop_power_long` (power), `inside_accurate_short`
  (accuracy). Template weights are genes, so structure added by L2 is then tuned by L1.
- Screen adds time to first kick (x2 weight).
- `h2h_support_planted_pct` is reported, not gated (hops by design);
  `h2h_support_planted_short_pct` and `hop_fall_pct` gate instead.
- `scripts/tools/styles_then_evolve.sh`: waits for the style runs, measures style metrics
  for the champion and B-Human, queues the style runs as candidates
  (`docs/evolution/seed_runs.json`), then runs evolution for 14 h.

### First results (2026-10-07 03:30, quick screen, 512 envs)

| | champion | sty_range 14450 | sty_range 16150 | sty_free 16150 |
|---|---|---|---|---|
| bumps aim ≤ 20° | 89 % | 91 % | 94 % | 91 % |
| close-start aim ≤ 20° | 92 % | 94 % | 97 % | 93 % |
| late falls | 0.4 % | 0.0 | 0.0 | 0.0 |
| long 3D p50 | 6.99 | 6.62 | 4.70 | 6.22 |
| goals / episode | 1.09 | 1.01 | 0.93 | 1.07 |
| first kick p50 | 3.78 s | 3.64 | 3.96 | 3.68 |

- Inside-foot curriculum reached 89° in sty_range (first time the inside foot was learned);
  accuracy and falls improve, long-kick power collapses with training, the hop does not
  deliver power under `hop_kick_style` (pays only up to the needed speed).
- Confound: these runs also carried the K4 bundle (kick clips in AMP, style near the
  ball, RSI B-Human 0.15), which cost goals / power in v59. Queued next:
  range styles without K4 + `t.hop_power_long` 800 (pays 3D speed 5 → 9 m/s on hops).

### Full benchmarks (2026-10-07 05:00) and the 16150 anatomy

- sty_range_14450 (early; inside foot not yet learned, 1 %): +21.8 score, convincingly beats
  B-Human on first-kick time, first-kick aim, all-kick aim, long aim (camera); 9 regressions
  (knee torque 78 Nm, short planted 71 %, goals, latency goals, approach time, caps).
- sty_range_x50 (blend with champion): +8.4, 5 regressions.
- sty_free_14950: +9.1, hops 97 % of long kicks and short planted 6 %: free choice = hop
  everything; 6 regressions.
- **sty_range/16150 (no RSI in eval): short/medium inside foot 88 % (B-Human 92 %), aim
  99 %, short ball 3.5 m/s; long hop 76 %, aim 99 %, falls after hop 0 / 440; but long
  ball 3D p50 3.97 m/s (champion ~5.1-5.9)** - the inside foot is learned, power is lost.
  (The training curriculum metric was right; my RSI-contamination suspicion was wrong.)
- Next: `sty_power` fine-tune from sty_range/16150, K4 bundle off, `t.hop_power_long` 800,
  `w.long_kick_power` 4000, 1000 iterations (parallel to evolution g021).

### sty_power/17149 full benchmark (2026-10-07 07:30)

Best style model so far on the user's priorities: first kick 3.34 s (champion 3.73,
B-Human 4.49), perfect-perception first kick 2.88 s (beats B-Human 3.0), goals bumps / flat /
moving / latency 1.24 / 1.30 / 1.16 / 1.13 (champion 1.105 / 1.105 / 1.045 / 1.00), aim
first / all / long 91 / 92 / 96 % (champion 84.5 / 89.5 / 92.5). Inside foot 97 % of short /
medium kicks, hop 85 % of long kicks, 0 falls after a hop.
Not promotable (7): long 3D 5.72 (6.9), knee p90 61 (55), short planted 44 % (92: it hops
into passes too), late falls bumps 1.8 % (0.35) and push 2.1 % (1.25), long speed / needed 0.82.
Next: `sty_power2` (hop power 1500, underpower -600) then `sty_power3` with
`k.SHORT_PLANT_FACTOR 0.4` (new: a short / medium kick without the support foot planted
keeps 40 % of its quality; long hops untouched). evo_g021_14600 (clean range rule from the
champion): +28.3 but 8 regressions.

## Torque regime change (2026-10-07 ~09:00, user)

"Use B-Human torque; the provided torques are for the motors without any weight; exact
numbers not known yet." Stage 3 now hard-clips leg torque at B-Human's kick clip
(`env_cfgs.LEG_TORQUE_CLIP`: hip pitch / roll 50, hip yaw 30, knee 60, ankle pitch / roll
30 N·m; was knee 112, hip roll 76, hip pitch 68, hip yaw / ankle 38.3). Verified in the
compiled model (actuator_forcerange). Gene `torque_clip` 0 restores the old limits.
All earlier benchmark numbers are without the clip; baselines re-run under it
(`bhuman` (old kept as `bhuman_noclip`), `x4_clip` + `x4_clip_s2`, `v56d_13450`).
Adaptation runs: `clip_champ` (champion recipe, 1000 it.) and `sty_clip`
(sty_power2/18148 + `k.SHORT_PLANT_FACTOR` 0.4, 1000 it.). Evolution resumes against the
clipped champion. sty_power2/18148 was not benchmarked (stopped mid-run, regime change).
