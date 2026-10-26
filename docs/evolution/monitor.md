# Monitor log: hierarchical evolution (L0-L5)

Supervisor: Claude (user, 2026-10-07: "monitor this system; intervene if it starts
regressing the objectives; make changes if needed, and note them down").

Watch on every frame: champion v2 metrics vs the objectives (accuracy, time to kick,
power by range, caps, posture, safety, B-Human), promotions (two seeds, no
regressions), loop health (crashes, stalls, disk, GPU), proposer sanity (L4 output),
experience repository (`docs/experience/README.md`) objective balance.

Intervene when: a promotion worsens a primary objective beyond noise; repeated
crashes / no checkpoints; a level keeps proposing the same failing change; L4 output
invalid or harmful; benchmark / fitness bug. Every intervention: what, why, evidence.

## Entries

- 2026-10-07 13:05 start: hierarchy rebuilt (contexts + stall-based escalation, experience
  repository wired in: every frame recorded, L4 digest + L1 weights from experience stats).
  Champion sty_power_17149 (v2). First context: L5 atom ball_behind_starts. Earlier run
  (round-robin, frame h001 at 20 min) stopped and discarded for the rebuild.
- 2026-10-07 15:00 INTERVENTION (bug): `evolve_kick.train_child` waited for checkpoints at
  parent + step (17149 + 150 = 17299 ...), but checkpoints are saved at multiples of 50, so
  frame h001's children ran ~1350 iterations and would have ended with "no checkpoints" at
  the 150-min deadline (every frame from a parent not on a multiple of 50 would fail). Fix:
  round expected checkpoints up to multiples of 50 (17299 -> 17300). Loop and h001 children
  stopped (2 h of GPU lost), L5 context ball_behind_starts reset to its full budget and
  the loop restarted. The flat loop never hit this because its parents were on multiples of 50.
- 2026-10-07 15:15 evidence: the overrun h001 child (ball-behind + far starts, ~1350 it.) screened
  +29.2 vs champion: approach falls 20/13 % -> 0.4/1.2 %, ball-behind falls 38/36 % -> 1/2.5 %,
  near-grid first touch <= 15 deg 44/14 % -> 82/85 %, but low-cap loop goals 1.17 -> 0.82 and
  slower first kicks at low caps (5 screen regressions). Recorded in the experience repository.
  No intervention: the loop re-runs this context with the proper 500-it protocol; if it again
  fails only on low caps, consider queueing s.cap_low_prob inside the context.
- 2026-10-07 16:55 frame h001 result (L5 ball_behind_starts): child c0/17300 v2 +118.8 with 9
  low-cap regressions; blend 50/50 with champion +161.2 with ONE regression (close-start
  first kick at low caps 4.30 -> 4.86 s). Huge gains: approach falls 21 -> 2 %, ball-behind
  falls 43-45 -> 7-10 %, zero-delay falls 25-33 -> 2-3 %, goal grid 59 -> 73 % (high caps),
  near-grid first touch <= 15 deg 57/18 -> 73/61 %. Gate NOT overridden (time to kick is a
  primary objective; user: never trade one away).
  INTERVENTION (structure): contexts restarted every inner frame from the champion, so the
  +161 blend was thrown away. Added inheritance: inside a context, children start from the
  context's best candidate (child or blend; `context_parent`, `install_parent`). Set the
  h001 blend as the L5 context best and opened a nested L3 context `s.cap_low_prob 0.3`
  (budget 2) aimed at the remaining low-cap time-to-kick regression. h002 (reshape
  hop_power_long, 1 min in) aborted and its budget returned.
  Process slip: one restart command killed its own shell (pkill pattern matched the same
  command line) - children were then stopped by PID; no state lost.
- 2026-10-07 17:40 user observation: the blend side-kicks (not exactly 90 deg) and has forgotten
  the front kick. Measured: front kicks 2 % (aim <= 20 deg only 14-38 %), inside foot 89 % of
  short/medium and 49 % of long kicks, hop 73 % of long. Cause: STYLE_MAP "range" (short /
  medium kicks lose half their quality unless inside-foot; hop bonus on long; nothing rewards
  front) - the style was dictated by range, not learned per situation.
  INTERVENTION (objective + measurement): new objective "use the best kick style for each
  situation" (memory, experience OBJECTIVES); benchmark v2 now records style x situation
  (range x redirect angle) with aim and speed / needed per cell, `style_selection_pct`
  (share of kicks using the best-performing style per situation) and `style_repertoire`;
  fitness_v2 gates style_selection (weight 1, tol 10). Blend measured: selection 37-46 %,
  front kicks ~0.
  PLANNED (after frame h002, STOP_AFTER_FRAME set): context "situational styles" inside the
  ball-behind context, from the context best: STYLE_MAP free with style shares / bonuses 0,
  hop_power_long off (long power through the style-agnostic long_kick_power), hop fall
  penalty kept, RSI 15 % our front kicks + 10 % B-Human inside kicks so no style is forgotten.
- 2026-10-07 18:35 INTERVENTION (user: "if it is not improving, then move on"): frame h002
  (nested L3 s.cap_low_prob 0.3 from the blend) stopped after screens: accuracy / falls up again
  (near-grid 81/77 %, approach falls 0.4-3 %) but its target got worse - low-cap loop goals
  1.11 -> 0.75-0.89, low-cap first kick 5.9 -> 6.6-6.9 s, approach low-cap kick share 73 -> 60 %.
  Context closed as failed (L3 stall +1), lesson recorded. Pushed the "situational styles"
  context inside the ball-behind context (parent = h001 blend): STYLE_MAP free, style shares /
  bonuses 0, hop_power_long off, hop fall penalty kept, RSI 15 % front / 10 % B-Human inside.
  Champion and blend full-loop re-measured with style metrics: selection 44/31 % and 56/42 %
  (low/high caps), 4 styles in use.
- 2026-10-07 19:28 INTERVENTION (move on): h003 (styles outcome-only inside the ball-behind context,
  from the blend) stopped after screens: vs its parent, low-cap goals 1.11 -> 0.74-1.06, low-cap
  first kick 5.9 -> 6.1-8.0 s, style selection not better; high-cap goals up (to 2.08).
  Finding: all three ball-behind-context frames lost 0.5-2 s of low-cap time to kick -> the
  scenario mix causes it. Closed the L5 ball-behind context (best: h001 blend +161, 1 regression).
  Next, isolating tests from the champion: h004 = situational styles WITHOUT ball-behind (does
  outcome-only + front-kick RSI restore front kicks / power / style choice?); queued = milder
  ball-behind (spawn_any 0.15, far 0.1) (does a smaller share keep the safety gain without the
  low-cap cost?). Decision for the user flagged: accept the blend's trade-off or not.
- 2026-10-07 19:50 user decision: the h001 blend is good but NOT accepted with its low-cap
  time-to-kick cost - keep searching, priority: bring down the time to kick.
  Change: new genes for time to kick - `w.kick_time_cost` (per-step cost until the next kick;
  term existed but unused), `k.PROMPT_KICK_TAU`, `k.PROMPT_FLOOR` (promptness floor was
  hard-coded 0.5). STOP_AFTER_FRAME set; after h004 the queue gets, from the blend:
  A {t.quick_kick 400, k.PROMPT_KICK_TAU 0.8}, B {w.kick_time_cost -5, k.PROMPT_FLOOR 0.25},
  then the milder ball-behind context.
- 2026-10-07 20:15-20:45 runswift's own benchmarks re-run (unchanged harness) on the new models:
  near-ball first strike <= 15 deg: sty_power 54/41, h001 blend 66/50 of 108 (x4 22/20, B-Human
  102/101); goal grid goals: sty 31/30, blend 41/34 of 90, falls 46/46 and 36/37 (x4 45/53 and
  34/34; B-Human 80/85, 0 falls). Falls: 33/36 with the ball behind. Bisection: runner torque
  limits not the cause (34 falls); camera vision -> 1 fall but 10 goals (no search). Found a
  RUNNER BUG: never-seen ball -> slots (0, 0), age 0, no lost rule; training treats an unknown
  ball as lost (virtual ball). FIXED in k1_policy_runner (never seen -> virtual ball, age 0):
  goals 10 -> 33, but falls 49 (turning in that engine at zero delay). GPU check: world ball +
  zero delay -> 25.6 % falls / 50 % goals (close to runswift). Benchmark v2 now adds goal_grid
  world/zero, goal_grid unknown-start and approach unknown-start (gated); env gene
  s.unknown_start_prob. GPU unknown-start goal grid for the blend: 80/79 % goals, 0-1 % falls.
- 2026-10-07 20:45 h004 (styles from the champion) stopped: low-cap first kick 5.6 -> 6.5-7.6 s
  again, goals down. Low-cap slowness appears in EVERY child trained today (with or without
  ball-behind), so the earlier attribution to the ball-behind mix was wrong / incomplete.
  Control experiment running: ctrlA = champion recipe + today's training defaults (target clip,
  delay from 0, feet origin); ctrlB = same with those three off; both screened under the
  deployed path. Loop paused until the cause is known.
- 2026-10-07 22:25 control result: both ctrlA (today's defaults) and ctrlB (without) got slower at low
  caps (loop first kick 5.6 -> 6.5-7.3 s) -> fine-tune drift on a rare condition, NOT the defaults.
  The defaults clearly help deployed accuracy / power / safety (A vs B: near-grid 84-89/75 vs
  37-66/18-42 %, speed/needed 0.81-0.94 vs 0.70, ball-behind falls 18 vs 29-44 %): kept.
  User direction applied: (1) never-seen ball = zeros / age 0 in BOTH training (new never_seen
  state on unknown starts) and the runner (my virtual-ball runner change reverted); lost rule
  only for seen-then-lost balls. (2) new reward turn_rate_track (turn at the yaw cap toward the
  kick line near the ball; gene w.turn_rate_track). (3) delay stays 0-40 ms + time-to-kick
  rewards. (4) contexts from the blend: T1 moderate (time cost -5, floor 0.25, tau 1.0, quick
  kick 400, turn 5, 15 % low caps, 15 % unknown starts, mild ball-behind) running as h005; T2
  strong queued. Normal / high caps stay in training and in the gate.
  Also: control waiter hung on model_17650 (last checkpoint is 17649 with max-iterations 501) -
  screened directly.
- 2026-10-07 23:31 OVERNIGHT SETUP (user: 10 h, keep improving, beat the bench and B-Human):
  user decisions: long >= 8 m uncapped (new reward long_kick_speed_linear, 3D speed / 8 m/s up to
  2x, sharp aim), air balls fine (k.LOFT_PENALTY 0), 4-8 m stays matched, heavy ball in the
  benchmark (near grid camera / perfect-zero, close start; gated) and in training (mass DR up to
  0.30 kg), runswift = proxy soft gate at promotion (falls +4/180, first strike -6/216, kick
  speed -0.15 m/s tolerance vs champion; harness in .cache/runswift_harness), style choice
  learned from outcomes (new style_advantage reward from running per-situation statistics).
  Global champion genes now: k.LOFT_PENALTY 0, ball_mass_alpha_max 0.55, w.long_kick_speed_linear 600.
  Loop changes: early stop (child must beat the parent's screen, after trying 70/30 and 50/50
  champion blends), fixed fall_before_contact metric, L4 objectives text updated.
  h005 (T1 time-to-kick) closed: +63.9 vs parent +75.7, blends +50/+47, low-cap first kick
  still 6.7-7.7 s. Now: h006 = context P (power + learned styles) from the blend; queued T2.
  Running under scripts/tools/hier_supervisor.sh (restarts on crash, max 6, logs here).
- 2026-10-08 00:30 h006 (power + learned styles) screens: best +51.3 vs parent +75.7; long 3D
  unchanged (3.7-4.0 m/s), low-cap first kick 6.5-7.6 s, accuracy and ball-behind falls held
  (best 1-3 % behind falls), style selection up to 42-45 % in one checkpoint. Loop handles it
  (champion blends, then move on to T2). No intervention.
  Open problem (all frames today): low-cap time to kick drifts 0.5-2 s slower in every fine-tune,
  whatever the reward; walking speed is not the cause (blend cap use 0.60 vs champion 0.44 at
  low caps), so the extra time is near the ball (alignment / dithering at the 0.6 rad/s turn
  cap) - likely an accuracy-vs-time trade the children make (kicks <= 20 deg 97-99 %).
- 2026-10-08 01:46 supervisor: loop stopped (flag or time), not restarting
- 2026-10-08 01:50 CORRECTION + INTERVENTION: lowcap_timing.py (new tool) shows the extra low-cap
  time is mostly the WALK to the ball, not near-ball alignment: time to 1 m 3.36 s (champion) vs
  4.08 (ctrlA) / 3.82 (ctrlB) / 3.54 (blend); near-ball time 1.82 vs 1.94-2.02 s; aim equal.
  (My 00:30 note "walking speed is not the cause" was wrong - it used the approach-track cap use
  for balls > 2.5 m away.) Cause: walk_speed_track only rewards cap tracking beyond 2.5 m, and loop
  balls start 1-4 m away. Fixes: walk_speed_track reads TRACK_CAP_MIN_DIST at call time (gene now
  effective); new context h007 "approach speed" from the h001 blend: k.TRACK_BRAKE_PROFILE 1
  (track the cap, brake to ~1 m) + w.walk_speed_track 6 + 15 % low caps. T2 and P (power +
  styles, 2 frames left) queued after it. Loop gained inject.json support (contexts queued
  without a stop).
  h006 result: its champion blend scored +159.3 on full v2 (4 regressions: time to first kick
  approach-high / loop-low, style selection low/high) - not promotable; h001 blend (+161, 1
  regression) remains the best candidate.
- 2026-10-08 02:55 h007 (approach speed) screens: best +69.3 vs parent +75.7 (not improving); low-cap
  loop first kick 6.2-6.7 s (better than earlier frames 6.5-7.7, still behind blend 5.9 / champion
  5.6). Resume check: action std 0.60 before / after, LR adaptive - no reset artefact found.
  INTERVENTION: injected a context "conservative fine-tune" (desired_kl 0.004 + approach speed +
  15 % low caps, from the blend) via inject.json - smaller policy steps to limit drift of the
  low-cap approach speed. Runs at the next frame boundary.
- 2026-10-08 04:50 NEW BEST CANDIDATE h007_c1_17650_x50 (h007 child 50/50 with champion): full v2
  +168.9 vs champion, 1 regression (loop first kick low caps 5.64 -> 6.10 s); close-start first kick
  4.49/3.93 s (h001 blend 4.86/4.20, champion 4.30/3.90), loop goals 1.08/1.90, style selection
  44/59 %. Became the h007 context best. Not promotable (1 regression).
  FIX (fitness): heavy-ball metric keys were wrong ("<track>/camera/typical/heavy"; the benchmark
  writes "<track>/heavy/camera/typical") so heavy metrics were silently not scored - corrected.
- 2026-10-08 05:20 FITNESS FIX (review please): time-to-kick gates now use a CENSORED time (robots that
  never kick count as the full episode: p * mean + (1 - p) * T, from stored first_kick_pct and
  first_kick_s). The old first_kick_s averaged only robots that kicked, so kicking MORE often
  (incl. harder cases) looked slower - e.g. unknown-start approach: 58 -> 86 % kicking but
  9.5 -> 10.7 s. Also filled the champion's missing v2 runs (heavy, world/zero, unknown) and fixed
  the heavy keys. Re-score: h007_c1_17650_x50 = +279.7 vs champion, NO regressions (censored first
  kick low caps loop 6.70 vs 6.35 s, within 0.4 s; high caps faster everywhere), beats B-Human on 9
  kick-league metrics. Running confirm_and_install manually (seed-2 v2 + runswift soft gate +
  install / ONNX). STOP_AFTER_FRAME set so the loop reloads the fixed fitness after h008.
- 2026-10-08 05:34 NEW CHAMPION h007_c1_17650_x50_2seed (first promotion of the hierarchy). v2 seeds
  +279.7 / +261.6 vs sty_power_17149, no regressions; runswift soft gate passed and better on all
  critical features: goal-grid falls 92 -> 60/180, goals 61 -> 103/180, first strike <= 15 deg
  95 -> 99/216, kick speed 3.04 -> 3.06 m/s. ONNX k1_kick_loop_h007_c1_17650_x50.onnx (robot test
  candidate). Champion genes now include the approach-speed / scenario genes (spawn_any 0.15,
  far 0.1, unknown 0.15, TRACK_BRAKE_PROFILE, walk_speed_track 6, cap_low 0.15) so children
  inherit the recipe.
- 2026-10-08 06:16 supervisor: loop stopped (flag or time), not restarting
- 2026-10-08 06:20 h008 (conservative KL) vs the NEW champion: child +141 (12 regressions), blend +96 (3:
  short-pass stop distance, style selection) - not promotable; but both beat B-Human on 12 kick-league
  metrics (champion 9). Loop restarted with the corrected fitness; stack = "power + learned styles,
  KL 0.004" from the new champion; T2 queued. ~3 h left (supervisor 11500 s).
- 2026-10-08 07:17 h009 (power + learned styles, KL 0.004, from the new champion) screens: best +58.1 vs
  champion. Long-kick 3D 3.55/3.66 -> 4.2-4.4 m/s, speed/needed 0.73/0.76 -> 0.84-0.91 (first real power
  gain), near-grid first touch <= 15 deg 59/43 -> 84-93/80-90 %, high-cap goals 1.91 -> 1.95-2.19,
  high-cap first kick 4.20 -> 3.95-4.07 s; but style selection 61/57 -> 16-47/8-37 % (gated): the
  policy converges on one strong style - style_advantage too weak vs the power rewards. Loop is
  running the full v2 on c0_17500; no intervention.
- 2026-10-08 08:25 supervisor: loop stopped (flag or time), not restarting
- 2026-10-08 08:30 METRIC FIX: style_selection_pct now counts a kick as a good choice when its style
  scores within 5 % of the best style in that situation (near-ties were counted as mistakes);
  recomputed from stored style tables in fitness_v2 and in the benchmark. Values: old champion 59/39,
  h001 blend 83/73, champion 78/68, h009 child 65/71 %.
  h009 final: child +214.3 (3 regr.: short stop low 3.09 -> 4.71 m, action rate high, style selection
  low), beats B-Human on 13 kick-league metrics (most so far); blend +161 (1 regr.: short stop low).
  Next context "power + styles v2" from the h009 child: style_advantage 1500, kick_rest_accuracy
  1000, long uncapped 800, KL 0.004. Supervisor extended 5 h (user: keep iterating).
- 2026-10-08 10:25 h010 (power + styles v2): c2_17850 full v2 +186.4 vs champion, 1 regression (short stop
  low caps); loop now benching its 70/30 blend. INTERVENTION: c0_17950 had the best screen stop distance
  (3.16/2.67 m vs champion 3.17/3.12) but is not the top screen -> full v2 started on it in parallel
  (manual), as a likely clean promotion candidate.
- 2026-10-08 10:55 h010 results vs champion: c0_17950 +223.6 (4 regr.: style selection low/high, heavy
  long 3D high, action rate high); c2_17850 +186.4 (1 regr.: short stop low); c2_17850_x70 (70 %
  champion) +118.9 with NO regressions -> loop's promotion check (seed 2 + runswift gate) running.
- 2026-10-08 11:09 GATE CHANGE (user-approved): runswift kick-speed gate now uses the 6/9 m tasks only
  (median strongest foot-linked speed); 3 m passes are meant to be soft. NEW CHAMPION
  h010_c2_17850_x70_2seed (70 % h007 champion + 30 % h010 c2_17850): v2 +118.9 / +122.4, no
  regressions; runswift falls 60 -> 44/180, first strike 99 -> 106/216, goals 103 -> 119/180, 6/9 m kick
  speed 3.04 -> 3.00 (within 0.15). Champion genes now carry the power + styles v2 recipe. ONNX
  k1_kick_loop_h010_c2_17850_x70.onnx. STOP_AFTER_FRAME set to restart the loop on the new gate code.
- 2026-10-08 13:14 supervisor: loop stopped (flag or time), not restarting
- 2026-10-08 13:35 Claude: restart after the h010 promotion. Re-scored h011 against h010: h011_c2_17750
  +174.5 with long 3D 4.4-4.5 m/s (champion 3.6) but regressions action_rate:high and
  style_selection_pct:high. Changes: (1) genes now also set base reward weights (w.action_rate_l2 etc.);
  (2) blends also try 30 % champion / 70 % child; (3) full v2 benches of h011_c2_17750_x30 / _x40
  started by hand; (4) injected context from h011_c2_17750 with action_rate -0.15, stack cleared.
- 2026-10-08 15:10 Claude: h011_c2_17750 blends scored vs h010 champion. x30 (30 % champion) +123.6,
  regressions style_selection_pct low+high; x40 +110.3, style_selection_pct:high. Blending removes the
  action_rate regression but not style selection (full_loop high caps: champion 68 %, h011 57 %, x30 57 %,
  x40 52 %). Power is diluted by blending (close_any camera long 3D high: 3.61 / 4.46 / 4.08 / 3.68).
  Not promoted. h012 context (from h011_c2_17750, style_advantage 1500) continues.
- 2026-10-08 15:20 Claude (user: "keep training, keep action rate stable and smooth while not
  compromising"): (1) fitness_v2: action_rate is now a safety metric (x2) with tolerance 0.006 on
  full_loop, close_any and approach (was full_loop only, 0.01, x1); any CI-separated rise blocks
  promotion. Rescored: h011_c2_17750 +157.8 with 4 action_rate regressions. (2) inject.json: L2 context
  c.action_rate_l2 = 0.75 (dual-ascent constraint, lam0 0.15) on top of the h012 power + styles genes.
  (3) STOP_AFTER_FRAME after h012 so the loop restarts with the new fitness; a restart watcher clears
  the flag and relaunches the supervisor.
- 2026-10-08 16:21 supervisor: loop stopped (flag or time), not restarting
- 2026-10-08 16:21 restart watcher: relaunching supervisor on new fitness
- 2026-10-08 20:45 Claude: h013 (c.action_rate_l2 0.75 constraint) and h014 did not smooth the policy:
  the multiplier rose 0.15 -> 0.40 but the action_rate cost stayed ~14.5 per episode. Cause: the
  action_rate_l2 reward is computed on sampled actions and the action std is fixed at 0.6, so it is
  dominated by exploration noise the policy cannot change. Smoothness of the deployed (deterministic)
  action is set by CAPS in the PPO update (temporal 1.0 / spatial 0.4, x0.5 within 0.8 m of the ball),
  which is exactly where the regressions are (close_any, high caps).
  Changes: (1) rl_cfg: genes caps_temporal_coef / caps_spatial_coef / caps_near_ball_scale; evolve_kick
  GENES gains caps_temporal_coef (0.8-2.0) and caps_near_ball_scale (0.4-1.0) for L0 mutation.
  (2) inject.json: L2 context from h012_c1_18000 (+170.3 under the new fitness, regressions only
  close_any action_rate:high and heavy long_3d:high), CAPS temporal 1.3, near-ball 0.8, constraint
  dropped. Starts after h015.
  Note: the h011 context's best kept its old score (+252.7 vs h007), so h013-h015 trained from
  h011_c2_17750 rather than the better h012_c1_18000; the new context sets its parent explicitly.
- 2026-10-08 20:58 Claude: wrote docs/evolution/HANDOFF.md (system, objectives, current state, runbook,
  gotchas, pending items) for the next agent session. Added scripts/tools/hier_relaunch.sh and started
  it on supervisor PID 3820386 (ends ~23:21): it relaunches the supervisor for 12 h unless
  STOP_AFTER_FRAME is set (user: "keep training").
- 2026-10-08 21:10 Claude (user: "kick faster, more accurate, more powerful than B-Human for diverse ball
  sizes, without sacrificing stability / no falls / smooth action"; loud steps on the robot, "foot_flat
  slapping is likely the cause, fix it; randomise ball size 0.07-0.13 and mass; keep improving"):
  (1) Quiet steps. foot_flat (pitch^2 from the first contact frame, -200) made the cheapest landing a
  flat sole slapped down at once. Now `settle_s` = 60 ms: the first 60 ms of each contact are exempt, so
  the foot can land heel first and roll flat (smoke from the champion: foot_flat -1.17 -> -0.1 per s, i.e.
  ~90 % of the cost was in those first 60 ms). New term touchdown_speed (-50): squared downward foot
  speed in the last 3 cm before touchdown. Landing force was 300 N (1.55x body weight), the same as the
  AMP walk (286-293 N), so the slap came with the walk. Genes foot_flat_settle_s, w.touchdown_speed
  (added to evolve_kick GENES for L0).
  (2) Ball size. New event mdp.ball_size_mass under the old key "ball_mass" (tools that pop it still
  get the nominal ball): radius U(0.07, 0.13) m, mass 0.1 kg x e^{2a}, a in (-0.347, 0.752) =
  0.05-0.45 kg (was 0.05-0.30), independent; shell inertia 2/3 m r^2. Spawns and RSI read the radius
  back from the model (approach.ball_radius); a larger ball in an RSI clip is pushed away by the extra
  radius. Gene ball_mass_alpha_max now only raises the ceiling; new gene ball_radius_max. Visual mesh
  stays 0.08 m in the viewer. Checked: spawn height error no worse than the fixed ball's (RSI clips
  already put balls up to 0.47 m in the air).
  (3) Judge. bench v2 tracks near_grid/large, close_any/large (0.13 m / 0.45 kg), near_grid/small
  (0.07 m / 0.05 kg), full_loop/landing; metrics touchdown_speed, landing_force on every track.
  fitness_v2: large/small primary metrics, close_any/large fall_pct safety, touchdown_speed safety
  (tol 0.02 m/s), landing_force rest. They score only once the champion has them: champion bench of the
  new tracks running (docs/benchmarks_v2/champ_newtracks_2026-10-08.log, backup of the old json in the
  session scratchpad), then B-Human on the same tracks (bhuman_newtracks_2026-10-08.log).
  Reach: env/reward changes apply to every child started from now (h015_c2 if it runs trains on the new
  env, unlike c0/c1); fitness and evolve_kick changes apply after the 23:20 supervisor relaunch.
- 2026-10-08 23:33 supervisor: loop stopped (flag or time), not restarting
- 2026-10-08 23:34 relaunch watcher: supervisor 3820386 ended, relaunching for 43200s
- 2026-10-08 23:55 Claude (user goal 23:45: monitor 7 h, intervene on dead ends, outperform B-Human
  convincingly). Diagnosis: no promotion since h010 (h011-h016). The runswift harness, where B-Human
  wins every row, is only a non-regression gate; the gap there is precision (first-strike heading 15 deg
  vs 2 deg, 3 m target hits 3-6 vs 59-73/108) and power. Training kick_dir_err ~0.27 rad: the main aim
  reward kick_direction uses KICK_AIM_SIGMA 0.35 rad (a 15 deg miss still pays 58 %); B-Human anneals
  to 0.05. h012_c1_18000 is the best lineage on exactly these (near_grid perfect aim 5-6 deg vs
  champion 8-11, 99 % within 15 deg, long 3D 4.6-4.8 vs 3.3-3.9, short stop 2.1 vs 3.4 m), blocked by
  close_any action_rate high 0.129 vs 0.123 (tol 0.006) and heavy long high 3.34 vs 3.86.
  Changes: (1) the screen now includes near_grid/large (ball sizes are an objective; children trained
  with size DR got no credit for it); evolve_kick.screen() re-runs a cached screen missing tracks
  (SCREEN_KEYS, applies after the next restart); cached champion and h012 screens moved aside so they
  are recomputed with the new track now. (2) runswift proxy on h012_c1_18000 running (CPU) to check its
  precision transfers. Next: a precision context from h012 (k.KICK_AIM_SIGMA tighter) if it does.
- 2026-10-09 00:10 Claude: FINDING - runswift's lead for B-Human is mostly its foot model. The harness
  loads ../k1_policy_runner/assets/k1_22dof_scene.xml, whose feet collide only through five 1 cm
  sole capsules (no foot body); training (whirlwind K1) collides with the full Left/Right_Foot mesh.
  Our runswift misses are systematic, not noise: aim 0, ball y -0.12 -> +16..24 deg, y +0.12 ->
  -16..26, centred -> +-20..30 (the stick under the ball sets the deflection). h012 (best v2 aim) gets
  96/216 on-direction there vs champion 106. Same harness with the training mesh feet
  (scratchpad rsw_meshfoot, both policies): champion 98/98 on-direction of 108 (was 53/53), heading
  10 deg; B-Human 97/99 (was 107/108), 5 deg; target hits B-Human 6/6 (was 59/73), ours 0. h012 with
  mesh feet: heavy-large 104/108, 3.9 deg (better than B-Human), light-small 87, 9.4 deg. Remaining
  real gaps vs B-Human in the runner sim: first-strike speed 1.1-1.6 vs 2.4-2.5 m/s, launch 1.15-1.4
  vs 1.03 s, precision on the light ball. Not changing the official fixture (runswift's); asking the
  user. Screening the recent candidates on the mesh-foot fixture now.
- 2026-10-09 00:05 Claude: FINDING 2 - the runswift harness also feeds our policy the ball relative to
  the PELVIS (compare.py: body_xy(ball, qpos[:3])), while training observes it from the point between
  the soles (gene ball_origin "feet") and the harness gives B-Human the soles midpoint. Diagnostic flag
  KC_BALL_FEET=1 added to our harness copy (.cache/runswift_harness/compare.py; backup in session
  scratchpad). Champion, near grid: mesh feet + soles origin -> light-small 108/108 on-direction,
  4.6 deg, first strike 2.1 m/s; heavy-large 91, 6.6 deg, 2.3 m/s (B-Human 97/99, 4.7/5.4 deg,
  2.5/2.4 m/s). Capsule feet + soles origin: 69/45, 12/16 deg, first strike 3.5 m/s (> B-Human 3.35).
  So the official fixture's verdict is mostly two fixture artifacts that hit only our policy. Next:
  screen candidates on the aligned fixture (mesh feet + soles origin; scratchpad al_*), then goal grid.
- 2026-10-09 00:26 Claude: aligned fixture (mesh feet + soles ball origin), all candidates, near grid:
  h012/h014/h016 lineages 108/108 on-direction on both balls, 2.8-4.6 deg (B-Human 97/99, 4.7/5.4);
  launch 1.2-1.3 s vs 1.03; first strike 1.5-2.3 vs 2.4-2.5 m/s (3 m passes are meant soft). Goal grid
  aligned (runner default caps 0.5/0.3/0.6 = bench low caps): B-Human 88-89/90, 0 falls; h014 62,
  h012_x30 52-54, champion 42-44, falls 9-13, misses = ball never touched. At high caps (KC_CAPS
  2.0,1.5,1.5) h014 73-74/90: timeouts gone, every remaining miss is a fall within 0.8 s of a STANDING
  start with the ball ~10 m behind ("away" starts; trace: lurches forward ~1 m/s while spinning).
  Training reset only from moving motion clips. Changes: mdp.stand_start reset event after the motion
  reset (with_stand_start, gene stand_start_prob, default 0.25; checked: ~18 % of envs start still in
  the default pose, upright; bench pops it); GENES stand_start_prob. inject.json: L3 context "cold
  starts with the ball behind" (stand 0.35, spawn_any 0.3, far 0.2, CAPS defaults) from h012_c1_18000.
  Applies to every child from now (stand_start default on) and the context opens after h017.
- 2026-10-09 01:00 Claude: the runner's default caps (0.5/0.3/0.6) also slow us in the harness (B-Human's walk is
  uncapped). Aligned fixture at high caps (KC_CAPS 2.0,1.5,1.5), h017_c0_18500 (quick_kick, in the
  CAPS context): near grid 107/107 on-direction, 3.7/4.8 deg, launch 1.00 s, first strike 2.30/2.49,
  strongest 3.20/3.28 m/s vs B-Human 97/99, 4.7/5.4, 1.03 s, 2.50/2.42, 3.01/2.94 -> ahead on the near
  grid. Goal grid: 67/63 goals, 12 falls (cold start, ball behind), 8-12 out; median time to goal 14.4 s
  vs B-Human 30.5 s (88-89 goals, 0 falls). The cold-start falls are the remaining gap (context queued).
- 2026-10-09 01:52 Claude: COLLAPSE in h018 (cold-start context). h018_c0 trained normally to ~18225, then from 18250
  every episode ends in ~35 steps on illegal_contact (deliberate early termination); h018_c1 task reward
  -72/episode (h017_c0 +13). Cause: the harder scenarios (stand 0.35, ball behind 0.3, far 0.2) cut the
  kick reward rate while penalties stayed, and my touchdown_speed term cost -1.3..-1.6 per s (the smoke
  run's -0.36 estimate was far too low), so staying alive paid negative (same failure as stage3_v2).
  Fixes: TOUCHDOWN_SPEED_WEIGHT 50 -> 15 (GENES range -40..-5, default -15); killed h018_c0 (PID 147637)
  so c2 starts on the corrected weight. h018_c1 (still on -50) watched. Aligned check at 18300: c1 goal
  grid 71/70 goals, 9 falls (h014 13, h017_c0 12); c0 0/90 (collapsed).
- 2026-10-09 01:55 Claude: h018_c1 collapsed the same way at ~18445 (episode length 1400 -> 112, illegal_contact
  0.1 -> 63); killed (PID 147636). Root cause: dying (fall = is_terminated -1000, ~-20 per episode) paid
  more than living through a hard-scenario episode (task reward -50..-72). Fix: reward term "alive"
  (mdp.is_alive, +2 per s, gene w.alive), the same for every policy that stays up, so surviving always
  pays; touchdown_speed already at -15. h018_c2 and later children train with both.
- 2026-10-09 02:28 Claude: cold start with the ball behind reproduces in our sim (scratchpad coldbehind.py: stand,
  ball 10 m behind +-30 deg, perfect ball, high caps, falls in 3 s): champion v2 track 32-40 % (all in
  the first 2 s); h012 4.7, h014 5.9, h015_c0 7.0, h016_c0 0.2 (18150) / 3.1 (18500), h017_c0 31-37
  (quick_kick), h018_c1 40 (18350), h018_c2 15.8 / 62.1 / 5.9 (18200 / 18450 / 18500): it swings between
  neighbouring checkpoints. New bench v2 track approach/behind/world/typical (stand, ball 8-10 m within
  30 deg of straight behind, 6 s; full n=512, screen n=256) with fall_pct as safety (tol 3) in
  fitness_v2; SCREEN_KEYS updated; champion benched on it (falls 39.8 / 31.6 %); cached champion / h012
  screens moved aside again so the next frame recomputes them. Aligned goal grid of the low-fall
  checkpoints h016_c0_18150 and h018_c2_18500 running.
- 2026-10-09 02:36 Claude: runner-only falls explained. Not self-collision (runner has it, training not: removing it
  in the aligned fixture moved h017_c0 falls 12 -> 10) and not the cold start alone (h016_c0_18150 has
  0.2 % cold-behind falls in our camera-ball sim but 14 runner falls). Observation diff, runner vs sim,
  same start: the runner (truth inputs, has_ball always) reports the ball at (-10.3, -1.4) m as SEEN;
  training never showed a seen ball far behind (world_ball_prob 0: camera view, memory, or the lost
  virtual ball at ~5 m). The new v2 track approach/behind/world/typical uses world perception, i.e.
  the same input, which is why the champion falls 32-40 % there. inject.json: L3 context
  s.world_ball_prob 0.3 on top of the cold-start context, parent h012_c1_18000.
- 2026-10-09 03:00 Claude: h019_c1 collapsed at ~18100 (episode length ~60, illegal_contact) with genes equal to c0 (L0 changed only w.kick_direction 900 -> 902): a training instability under the cold-start / world-ball scenarios, not a gene; killed (PID 222585). c0 healthy (length ~1200, task reward > 0).
- 2026-10-09 03:03 Claude: h019_c0 collapsed too (~18140). Collapses so far: h018_c0, h018_c1, h019_c1, h019_c0 - all with stand_start_prob 0.35 (contexts before stand_start never collapsed; h018_c2 survived). Killed h019_c0 (PID 222586). Control run exp_nostand (outside the loop, free GPU slot): h019 genes with stand_start_prob 0, from h012_c1_18000, 300 iterations; if it stays healthy, stand_start is the trigger.
- 2026-10-09 03:11 Claude: h019_c2 collapsed at ~18089 like the others (killed). exp_nostand (same genes, stand_start 0) healthy through 18100 (episode length ~1350), the window where all five stand-start children collapsed. stand_start disabled in with_stand_start (prob 0, gene ignored). h020 (L1 aim_tight in the world-ball context) had started 03:10 with stand 0.35: killed h020_c0/c1 (PIDs 239986/239985) so the frame continues with c2 on the fixed config.
- 2026-10-09 03:50 Claude: KEY RESULT. The runner harness's default for our policy is truth inputs (has_ball always,
  ball reported seen at any bearing / distance = a perfect world model). With the harness's camera
  perception (KC_VISION=1: what our deployed runner actually gets) h014_c1_18000 on the aligned fixture
  (mesh feet, soles origin, caps 2.0/1.5/1.5) scores 87/87 goals with 1/0 falls (truth inputs: 73/74,
  13/13 falls) vs B-Human 88/89, 0 falls (truth inputs; its port has no vision path). The cold-start
  falls are the policy meeting a seen ball far behind, which camera-only training never produced.
  exp_nostand_18299 (world ball 0.3, 300 it, no stand starts): truth-input goal grid 68/72, 10 falls,
  near grid 108/104 on-direction, 2.7/3.9 deg; its cold-behind sim falls 50 % (no fix yet). Camera-vision
  near+goal for h014, h017_c0, exp_nostand, h012_x30 and the champion running (scratchpad alvis_*).
- 2026-10-09 03:58 Claude: camera-vision aligned results (KC_VISION=1, mesh feet, soles origin, caps 2.0/1.5/1.5): goal grid exp_nostand_18299 90/89 goals 0/0 falls, h012_x30 87/89, h014 87/87, champion 87/87, h017_c0 82/81; median time to goal ~19-20 s for all vs B-Human 30.5 s (88/89, truth inputs). Started exp_world2: exp_nostand_18299 + world_ball 0.5, 500 it, 2048 envs (free GPU slot), to fix the truth-input ball-behind falls (~10/90).
- 2026-10-09 05:06 Claude: exp_world2 (world ball 0.5, +500 it from exp_nostand_18299, 2048 envs): aligned truth-input
  goal grid 73/73 with 14 falls (18550: 74/74, 8 falls); camera vision 76/83, 10/1 falls (worse than
  exp_nostand's 90/89, 0 falls); near grid stays excellent (105-108 on-direction, 3.0-3.8 deg). World-ball
  training at this budget does not fix the truth-input ball-behind falls -> dead end for tonight; the
  world-ball context should not be extended without a different approach (e.g. stand starts fixed
  first, or a curriculum on turning from standstill). exp_nostand v2 vs champion +85.0 with regressions
  approach first_kick_pct low, late_detect / robust goals low, behind fall_pct high.
- 2026-10-09 05:14 Claude: h021 (L1 aim_tight in the world-ball context) camera-vision aligned at 18450: c0 87/89 goals,
  0 falls; c1 87/88, 0 falls; near grid (camera) 68-96 on-direction. exp_world2_18798 cold-behind sim
  falls 50 %.
  SUMMARY OF THE NIGHT (for the user):
  * Not promoted: h015-h021 (gate: v2 regressions vs champion h010_c2_17850_x70_2seed).
  * runswift official fixture misjudges our policy three ways (sole-capsule feet, pelvis ball origin,
    runner default caps 0.5/0.3/0.6) and feeds truth inputs our camera-trained policy never saw.
    Aligned + camera perception (deployed path): goal grid exp_nostand_18299 90/89, h021_c0_18450
    87/89, h012_x30 87/89, h014 87/87, champion 87/87 - all with 0-1 falls, median time to goal ~19-20 s;
    B-Human 88/89 (truth inputs), 0 falls, 30.5 s. Near grid with truth inputs (B-Human's only mode):
    exp_nostand 108/104 on-direction, 2.7/3.9 deg, h017_c0 107/107 3.7/4.8 deg, launch 1.00 s vs
    B-Human 97/99, 4.7/5.4 deg, 1.03 s.
  * Open: truth-input ball-behind cold-start falls (~10/90; world-ball training did not fix them);
    stand_start collapses training (disabled, cause unknown); decide whether the official runswift
    fixture should adopt mesh feet / soles origin / caps / vision for our policy.
- 2026-10-09 05:41 Claude: exp_world2_18798 v2 vs champion +109.4, regressions full_loop short_stop_m low+high, robust goals low, action_rate high (full_loop, close_any). h021 c0/c1 best screens +51.7 / +44.9 (parent +77.5 at the previous frame); c2 training.
- 2026-10-09 06:18 Claude: h021 closed (best screen +68.9, blend +60.6 vs parent +77.5); world-ball context closed without promotion. h022 (L1 far_cap_tracking in the cold-start context; stand_start is off in code, so effectively ball behind 0.3 / far 0.2) started. End of the 7 h monitoring window; loop left running (supervisor until ~11:30).
- 2026-10-09 07:58 Claude: h022 closed (best +56.3 vs parent +77.5). Pattern: since h016 every frame's children (best +50..+69) fail the early-stop gate against h012_c1_18000's single screen (+67.5 / +77.5 / +81.8 as tracks were added); the parent bar is one screen draw while children get 5 checkpoints each - worth a decision (e.g. re-screen the parent with a second seed, or compare against the parent's mean of 2 screens). Not changed unattended. h023 (L1 long_power_ramp) started.
- 2026-10-09 08:34 Claude (user: "that's unacceptable" - no progress): correction - the early-stop gate is not unfair
  (each child's best of 5 screens vs one parent screen favours children); fine-tunes from h012 in the
  recent contexts are genuinely worse on the screen. Actions: (1) blends h012_c1_18000_x15 / _x20 (85/80 %
  h012) on full v2 to find one without h012's two marginal regressions (action_rate close_any high, heavy
  long high) and without x30's style-selection loss; promote through confirm_and_install if one passes.
  (2) New gene s.ball_origin_trunk_prob (per-episode trunk vs feet ball frame; checked) and inject.json
  L3 context with 0.3 from h012, for runswift's pelvis-frame harness.
- 2026-10-09 08:44 Claude: h022_c2_18450 (quietest post-fix candidate in screens: touchdown 0.197 m/s, landing 270 N vs champion 0.242 / 333) - camera-vision aligned runswift: goal grid 90/90 and 90/90, 0 falls (B-Human 88/89); near (camera) 86/103 on-direction, 6.5/2.9 deg. Its full v2 run died of GPU OOM after 3 tracks (my fault: 3 benches + 2 trainings); killed the x20 blend bench to protect the loop's h023 screens; x15 continues, then x20 and h022 resume one at a time.
- 2026-10-09 08:49 supervisor: loop stopped (flag or time), not restarting
- 2026-10-09 08:49 Claude (user: good performance needed within 1 h): paused the loop (STOP_AFTER_FRAME set, evolve_hier killed during h023 screens; supervisor ended) to free the GPU. Parallel: h022_c2_18450 full v2 seed 1 and seed 2 (confirm_and_install inputs), blends x15 / x20, official runswift proxy for h022 (CPU).
- 2026-10-09 08:51 Claude (user: keep iterating): ft_h022 - fine-tune from h022_c2_18450 with h022 genes + reward program h022_c2.json + s.ball_origin_trunk_prob 0.3, 500 it, 4096 envs. ONNX of h022_c2_18450 exported to k1_policy_runner/kick_loop_models/k1_kick_loop_h022_c2_18450.onnx.
- 2026-10-09 10:06 Claude: h022_c2_18450 full v2 both seeds: +172.9 / +126.5, regressions on both: approach first_kick_pct low (61-62 vs 69-72 %), action_rate high (close_any 0.130 vs 0.123, full_loop 0.137 vs 0.131); seed 1 also style_selection low. Official runswift: near 144/216 (champion 106), falls 36 (44), goals 92 (119). x15 blend +189 with heavy long high + style_selection regressions. Not promoted (gate). Benching ft_h022_18949 (both seeds); loop relaunched (12 h) with L2 context from h022_c2_18450 targeting its two regressions (walk_speed_track 8, CAPS temporal 1.3, trunk ball frame 0.3).
- 2026-10-09 10:22 Claude: USER PROMOTED h022_c2_18450 -> champion h022_c2_18450_2seed (run dir *_champ_h022_c2_18450, benches copied, runswift ref copied, state backup state_before_h022_*.json). start_kick.sh model -> kick_loop_models/k1_kick_loop_h022_c2_18450.onnx (speed limits unchanged 1.5,1.5,2.0). Next: deep review of B-Human's method vs ours.
- 2026-10-09 10:27 Claude: B-HUMAN REVIEW (MachineLearning/IsaacGymRL/envs/K1_Ball.yaml vs ours). Integrated already:
  momentum kicks, B-Human torque clip (soft limit), heavier balls (now size+mass DR), 3D long power, RSI
  from B-Human kicks, AMP, KL 0.004. Not integrated: (1) final-stage tight kick-direction sigma (theirs
  1 -> 0.05 rad, ours 0.35) and wrong-direction factor 3; (2) speed-per-range sigma scale 1 -> 0.5 with a
  continuous 0.5-20 m range (ours 3 bins, rest-miss scale 2 m); (3) target sole yaw 90 deg (side foot);
  (4) ball freeze at kick 20 %, incoming balls 0-7.5 m/s, rare immovable ball (needs ball velocity input
  for best use - 83-input rule); (5) ground friction 0.3-1.5 / compliance / restitution 0.1-0.9, terrain
  random 7.5 cm; (6) energy costs (power -2e-3, torque tiredness). Remaining gaps vs B-Human in v2 map
  to (1) aim with a perfect ball 3.7 vs ~5 deg and (2) short-pass stop 1.3 vs 2.5 m.
  Done: reward term joint_power (mdp.joint_power_penalty, legs, actuators aligned; checked ~50 W standing;
  weight 0 unless gene w.joint_power, added to GENES). inject.json: L2 "B-Human final-stage precision" from
  the champion: k.KICK_AIM_SIGMA 0.2, k.REST_MISS_SCALE 1.0, w.joint_power -2e-3 (after the running frame).
- 2026-10-09 11:20 Claude: ft_h022_18949 (h022 + trunk ball frame 0.3, +500 it) is far worse: vs h022 champion -110 / -113 (goals, short stop, robust/moving/late goals, style selection). Trunk-frame mixing hurts -> off in bh_prec (restarted as bh_prec2: aim sigma 0.2, rest scale 1.0, power -2e-3) and forced 0 in the queued B-Human context. torque_tiredness term removed (whirlwind actuators expose no force_limit, term saturates).
- 2026-10-09 11:26 Claude: gene foot_capsules (_use_foot_capsules: the runner/runswift scene's five 1 cm sole capsules replace the foot mesh collider; same link frame and mesh in both models; friction/condim carried over; checked: geoms compile, zero-action fall rate 84 % vs 83 % mesh from motion resets). Fine-tune capfoot from the champion (champion genes + foot_capsules, 500 it, 2048 envs) to learn kicks that stay straight on the stick feet of the official runswift fixture. STOP_AFTER_FRAME set: the loop stops after h023 to leave the GPU to bh_prec2 and capfoot.
- 2026-10-09 13:30 Claude: RUNNER FIX (k1_policy_runner kick_loop_policy.py, uncommitted, backup in session scratchpad):
  fov_gate (default on) ignores a ball detection at a bearing the camera can never see (|bearing| > head
  yaw limit 0.85 + half horizontal FOV = 66 deg), as training only ever reports camera-visible balls.
  Official runswift fixture, champion h022_c2_18450: goal-attempt falls 36 -> 0, goals 92 -> 95, near grid
  unchanged (144/216). Remaining misses at the runner's default caps 0.5/0.3/0.6: 44 timeouts (median
  time to goal 44 s) + 40 out. Same fixture with KC_CAPS 1.5,1.5,1.5 (start_kick.sh deploys 1.5,1.5,2.0):
  142/180 goals, 0 falls, 36 out, median 19.5 s (B-Human 165, 0 falls, 30.5 s). capfoot 118 (60 out),
  bh_prec2 127 (6 falls, 47 out). v2 vs champion: bh_prec2 +47/+37 (regressions short_stop, action rate,
  landing force), capfoot -35/-32. Remaining gap: shots out of bounds.
- 2026-10-09 13:31 Claude: official goal-grid misses after the FOV gate are shots just wide (|y| 1.2-2.9 m vs goal half-width 1.25) or out the side, 15 of them single long shots from ~11.5 m (needs < ~6 deg). Long aim sigma2 is 0.05 rad^2 (~13 deg; B-Human final 0.05 rad). Fine-tune aimlong from the champion: k.LONG_AIM_SIGMA2 0.015, k.KICK_AIM_SIGMA 0.25, 500 it, 4096 envs.
- 2026-10-09 13:52 supervisor: loop stopped (flag or time), not restarting
- 2026-10-09 14:03 Claude: aimlong (k.LONG_AIM_SIGMA2 0.015, KICK_AIM_SIGMA 0.25) official goal grid (FOV gate, caps 1.5): 18650 137 goals / 16 falls / 27 out; 18949 128 / 4 / 42 (champion 142 / 0 / 36) - not better. Added sim2real recorder to k1_policy_runner (run_recorder.py, kick_record_fields.py, kick_record_analyze.py, --kick-record; uncommitted). Screening all candidates on the official goal grid with the FOV gate and caps 1.5.
- 2026-10-09 14:09 Claude: candidate screen, official goal grid with FOV gate + caps 1.5 (goals/180, falls, out): h012_c1_18000_x30 159/8/13 (t 21.9 s), h014 147/0/33, exp_nostand 144/4/32, champion h022 142/0/36, h012 137/0/43, aimlong_18650 137/16/27, h021_c0 136/19/22, h016_c0_18150 131/0/49, bh_prec2 127, h017_c0 127, capfoot 118, exp_world2 91/52 falls. B-Human 165/0. Testing blends around x30 (x15, x20, x50, x30+h022, x30+h014).
- 2026-10-09 14:18 Claude: OFFICIAL GOAL GRID ABOVE B-HUMAN. Runner soft start added (kick_loop_policy cap_ramp_s=4.0
  default: caps ramp from 0.5/0.3/0.6 to the configured caps over 4 s after enable; trace showed a fall
  3.6 s in when a robot turning on the spot sprinted at once). Blends h012_c1_18000_x30/_x50 (70/50 %
  h012 + old champion) screened: official goal grid, FOV gate, no ramp: x50 160 (caps 1.5x3), 163
  (1.5,1.5,1.0), 162 (1.2,1.0,1.2 / 1.5,1.2,0.8 / 1.2,1.0,1.0), 158 (2.0,1.5,1.0); x30 159, x20 156,
  x15 151, x30+h022 154, x30+h014 156. With soft start: x50 at caps 1.5,1.5,1.0 -> 170/180 goals, 4
  falls, 6 out, median 27.3 s (B-Human 165, 0 falls, 30.5 s); x30 same caps 165/2/13; x50 at 1.5x3 with
  ramp 143 (28 falls) - sensitive to wz. Official near grid x50 (caps 1.5,1.5,1.0): on-direction
  63/56 of 108, 12-14 deg (B-Human 107/108) - single kicks off the stick feet still lose.
- 2026-10-09 14:49 Claude: h012_c1_18000_x50 full v2 vs champion h022: -47.2 / -47.1, regressions long_3d and long_x_needed (both caps), touchdown_speed and landing_force (both caps; x50 predates the landing fix), style selection high (seed 1). Trade-off: x50 best on the official runswift goal grid (170/180 with FOV gate + soft start + caps 1.5,1.5,1.0), h022 better on long power and quiet landings. Not promoted. Real-robot recordings analysed: docs/K1_REAL2SIM_2026-10-09.md.
- 2026-10-09 14:49 Claude: combined fine-tunes from h012_c1_18000_x50 (installed as 2026-10-09_14-49-48_ctx_x50): ft_x50a = champion genes + current env (landing fix, ball sizes, power settings, reward program h022_c2), ft_x50b = same + walk_speed_track 8, CAPS temporal 1.3; 600 it, 4096 envs each. Goal: keep x50's runswift shooting, recover long power and quiet landings.
- 2026-10-09 16:34 Claude: ft_x50a/b (fine-tunes of the x50 blend in the current env, 600 it) failed: official goal grid 80 / 98 (x50 170), v2 vs champion -89 / -67..-83. Blends do not fine-tune well. Trying h022 blended with the old champion h010 (x50, x30) - the x50 recipe on the landing-fixed lineage, no training.
- 2026-10-09 17:07 Claude: same config (FOV gate + soft start, caps 1.5,1.5,1.0) official goal grid: champion h022 141/4 falls/35 out; h022_x50 (h022 + 50 % old champion) 155/6/17, v2 -61/-73 (long power regressions, landing_force low; touchdown speed kept); h012_x50 170/4/6, v2 -47. Blending with h010 consistently trades long power (v2) for runswift shooting accuracy.
- 2026-10-09 21:14 Claude (user: long kicks as air balls at 7-10 m/s, kick faster, no regressions): fine-tunes from the champion h022, 800 it, 4096 envs. pow_a: w.long_kick_speed_linear 2500 (800), foot/speed bands 8-9.5 / 8-10 m/s (6.5-7.5 / 7-8), LONG_KICK_VEL_REF 9 (7.5), underpower -600 from 100 % of the need (-300, 80 %), MOMENTUM_KICK_MAX_SPEED 1.5 (1.0), loft penalty off. pow_b: pow_a + t.quick_kick 400, PROMPT_FLOOR 0.25, PROMPT_KICK_TAU 1.0. Safety terms unchanged. Evaluated after training: official goal grid + v2 both seeds vs champion.
- 2026-10-09 23:14 Claude: pow_a / pow_b results. Long 3D (close_any) 4.56 / 4.69 m/s vs champion 4.22 (perfect ball 4.62 / 4.78 vs 5.06); time to kick 1.77 / 1.65 s vs 1.62; official goal grid (FOV gate + ramp, caps 1.5,1.5,1.0) 133 / 103 goals vs champion 141 (out 39 / 77 vs 35). Reward weights alone do not reach 7-10 m/s in 800 it and harder kicks go out more. Eval jobs hit the 3 h background limit at 24-25/28 tracks; benches resumed detached. Next per plan: teach the momentum side-foot long kick (more B-Human RSI, side-foot reward on long range), longer training.

## 2026-10-26 night: fine-tune toward the runswift-spec kick benchmark (B-Human as target)

- 2026-10-26 00:30 Claude (user goal, 8 h, unattended): train/fine-tune the kick with the runswift-spec benchmark (`k1/eval/rs_kick.py`, the user's schema) and B-Human as reference/target, through the new interface (cards, proposals with forecasts, `rsw design check`, recipes, `rsw recipe check`, `rsw train`).
  Baselines (score; seeds 0 / 1): B-Human pretrained 0.925 / 0.931 (0.921 with its obs noise). h022 deployed path (camera, 10-40 ms delay) 0.834 / 0.854; h022 lab (perfect perception, zero delay, as B-Human runs) 0.936-0.942 / 0.940. So in matched lab conditions h022 already beats B-Human slightly; the deficit is the deployed path: 22 kicks > 45 deg off (touches 0.7-1.2 s in, ball 0.36-0.6 m away, side/back targets) and 10 no-kicks. Cause found: training never spawns the ball closer than 1.0 m (ball_distance_range 1-4 m); every benchmark trial is 0.35-1.0 m.
- 00:34 card `near_ball_starts` (environment; reuses the v52 side drill with target 0-180 deg either side, ball 0.35-1.0 m). Proposals near_ball 0.25 / 0.4 checked (expected gain +4.8 on bench v2 each). Started night_n1_near025 and night_n2_near04 from h022_c2_18450, 600 iterations (~5.1 s/it), tensorboard logging. Judge: rs_kick deployed + lab, seeds 0 and 1, every ~150 iterations; bench v2 quick screen on the best before any promotion.
- 01:15 Claude: cause of the deployed-path wrong-way kicks (h022, rs_kick seed 0, delay zero): camera 0.834 / 28 wrong-way; wide FOV with camera noise 0.938 / 1; camera FOV without noise, dropout, vision delay and jitter 0.939 / 0; both on (control) 0.837 / 28. Delay alone (perfect perception, typical delay) 0.935 / 2 wrong-way but doubles kicks slower than 2.3 s (27 -> 53). So a close ball (0.36-0.6 m) at the bottom edge of the view (head pitch max 47 deg + half FOV 21 deg = 68 deg below horizontal; ball at 0.4 m is ~65 deg down) flickers with noise, the lost rule fires (0.5 s in view without detection), the virtual ball appears at 1.6 rad and the robot turns into the real ball (~0.8 s). Same geometry and rule on the robot: the policy has to keep a close ball in view (step back / stop). near_ball 18750: deployed 0.848 / 0.854 (n1 / n2), lab 0.937 / 0.944; no-kicks 9 -> 1 / 5, wrong-way still 29 / 24.

### 2026-10-26 07:55 — near-ball round 1 verdict; round 2 launched

- Lost ~6 h: the judge waited for `model_19050.pt`, but a 600-iteration resume
  from 18450 ends at `model_19049.pt`. Waiters now wait for the training
  process to exit and take the newest checkpoint.
- rsjudge at 19049 (score; paired vs B-Human / vs h022, 95 % CI):

  | run | deployed s0 / s1 | lab s0 / s1 |
  |---|---|---|
  | n1 side_drill 0.25 | 0.852 / 0.879 (vs h022 +0.017 [-0.005,+0.040] / +0.025 [+0.005,+0.045]) | 0.945 / 0.948 (vs B-Human +0.020 [+0.011,+0.030] / +0.017 [+0.008,+0.026]) |
  | n2 side_drill 0.4 | 0.841 / 0.866 | 0.934 / 0.924 (vs B-Human +0.009 / -0.007) |

  n1 wins; n2 dropped. Lab: n1 beats B-Human on both seeds, but not by the
  substantial 0.05. Deployed: still ~-0.06 vs B-Human's lab score.
- Round 2 (400 it each, from n1 19049): `kick_n3_aim025` (KICK_AIM_SIGMA 0.25,
  inbox proposal, expected gain +4.2) and `kick_n4_cont` (same genes, control
  for the continuation effect). Bench v2 quick screen of n1 19049 in parallel.
- 08:08 bench v2 quick (seed 1) of n1 19049: score +38.8 vs h022, **no
  regressions**, B-Human beaten on 12 metric-caps (close_any camera kicks_20 /
  first_kick / falls, near_grid first_touch). Single seed: confirm on seed 2.

### 2026-10-26 08:40 — round 2 verdict; round 3 launched

| run (19448) | deployed s0 / s1 | lab s0 / s1 | lab vs B-Human |
|---|---|---|---|
| n4 continue n1 | 0.856 / 0.875 (vs h022 +0.021 / +0.021, CIs > 0) | 0.954 / 0.950 | +0.029 [+0.021,+0.037] / +0.019 [+0.009,+0.028] |
| n3 aim sigma 0.25 | 0.850 / 0.876 | 0.939 / 0.939 | +0.014 / +0.008 |

- n3 rejected: aim sigma 0.25 did not cut direction error; lab fell vs n1.
- n4 is the night's best: better than h022 in all four mode-seeds, 0 falls.
- Deployed loss is now one failure: all 21 wrong-way kicks (s0) have the ball
  0.36-0.64 m away; lab mode has 1. Camera bottom-edge loss + lost rule.
- Round 3 from n4 19448 (400 it each, via inbox -> InboxDesigner -> recipe):
  `kick_n5_close` (side_drill distance 0.35-1.0 -> 0.35-0.65, gain +6.6) and
  `kick_n6_avoid15` (ball_avoidance -5 -> -15, gain +4.9).
- 08:55 bench v2 quick of n4 19448: +37.4 vs h022 but **regression**
  full_loop/camera short_stop_m high cap 3.91 m [3.58,4.23] vs h022 2.92
  [2.60,3.22] (n1 3.55, not flagged): the near-ball line over-powers short
  passes. n4 not promotable as is; n1 19049 remains the clean candidate.
- 09:00 my mistakes: (1) killed n5's trainer instead of n6's (PIDs listed
  together); (2) the judge waiter's `kill -0` on all PIDs fired when any one
  died. n5 stopped at 19550; n6 (ball_avoidance -15) dropped for a better use
  of the slot. Now one PID per launch (`$!`) and one waiter per run.
- Round 3b: `kick_n5b_close` (n5 resumed 19550 -> 19849) and `kick_n7_rest15`
  (from n4, w.kick_rest_accuracy 1000 -> 1500). n7 is a **worth-gate override**:
  the gate scored it +1.7 (< 4) because it prices gain only, not removing a
  regression that blocks promotion. Step 10 gap: give regression fixes a gain.

### 2026-10-26 09:30 — round 3b verdict; n1 to full confirmation

| run | deployed s0 / s1 | lab s0 / s1 | bench v2 quick |
|---|---|---|---|
| n5b close 0.35-0.65 (19849) | 0.854 / 0.876 | 0.945 / 0.946 | short_stop_m regress low+high |
| n7 rest x1.5 (19847) | 0.876 / 0.880 (vs h022 +0.042/+0.025) | 0.937 / 0.939 | short_stop_m regress high |

- Short-pass overshoot grows with near-ball training (n1 < n4 < n7 < n5b);
  rest accuracy x1.5 did not fix it. Root cause open (side_drill keeps the
  target bins; maybe close starts reward quick hard first touches).
- Only clean candidate: n1 19049. Running `rsw judge --confirm` (bench v2
  full, seeds 1+2). Use records u024-u026.

### 2026-10-26 10:15 — n1 fails the full confirmation; h022 stays champion

`rsw judge --confirm` (bench v2 full, seeds 1+2) of n1 19049: score +26.0
(18.4 / 7.6) but regressions on both seeds: full_loop/camera goals_per_ep (high
cap 1.86/1.87 vs h022 2.07/2.02; also low cap, moving, robust, late_detect),
short_stop_m (3.7-4.1 m vs 2.9-3.1), goal_grid/unknown goal_pct (seed 2 high cap
64 % vs 84 %). The near-ball fine-tune wins rs_kick but loses the full loop.
Not promoted. Pose probe (foot contact at kick, rs_kick rollouts): sole strike,
toes up ~37 deg, sole rolled ~50 deg inward; pose variation within this kick does
not change rs_kick outcomes except flat-foot toe touches (accidental, -0.11..-0.16).

### 2026-10-26 — kick pose study (h022, n1, B-Human; bench v2 full_loop + close_any, camera)

Pose at foot-ball contact per kick (scratchpad pose_v2.py over kick_bench2.measure).
- Ours (h022/n1): inner sole strike, foot toe-out ~56-60 deg vs the kick line,
  sole rolled ~45-50 deg inward, toes up ~27-31 deg. Kicking leg pinned at joint
  limits: ankle roll -0.345 in 100 % of kicks, hip roll -0.40 in 66-72 %, ankle
  pitch near -0.87 in 15 %. Knee nearly straight (0.55).
- B-Human: inside-of-foot sweep (76 %), toe-out ~90 deg, flat foot, hip roll
  +0.89 abducted, knee 1.25; no joint at a limit; power from hip roll (p90 32 Nm).
- Outcomes (full_loop): short passes B-Human rest miss 1.4 m at 1.2-1.3x needed
  speed vs ours 3.5-4.4 m at 1.5-1.6x; ours more accurate (3.4-4.8 vs 6.9-12.2
  deg), more long power (0.89-1.01 vs 0.71 x needed).
- Within ours, short-pass speed/needed is ~1.5 for every pose: the overshoot is
  power modulation, not pose. Long power rises with toe-out (40-55: 0.61x,
  55-70: 0.97x, 70-85: 1.33x) and toes-up >= 35 deg.
- Real robot (dribble_1019): reaches the ankle/hip roll limits; ankle roll tracks
  well at extremes (0.04 rad), hip roll and ankle pitch poorly (0.23-0.24 rad).
Use: short-pass overpower target from B-Human (~1.25x needed) is the lever for
the short_stop regression; don't train toward B-Human's pose (costs accuracy and
long power; u-record kick.md: inside-foot cut long power 6.99 -> 4.70); robot
check of contact pose before any limit-margin change (needs robot evidence).

### 2026-10-26 ~12:00 — short_kick_overpower doses from h022

Term added (4a96e34, off by default). Halfway (18750, full-loop pose probe):
o1 -300 drifted (short 1.60x needed, miss 4.14 m, goals 1.43); o2 -600 held or
improved the aims (long 1.00x / 5.2 m/s, aim 3.7 deg, near-ball 2.56 s, goals
1.63) but short passes barely moved (1.51x, miss 3.33 m). o1 stopped at ~18760;
o3 -1500 launched in its slot. Judging per run on exit: rs_kick both seeds/modes,
pose probe, bench v2 quick.
- 12:05 final (19049): short_kick_overpower did not change short-pass power.
  o2 -600: short 1.56x needed, miss 3.52 m, long 0.96x, aim 4.6 deg, near-ball
  2.64 s, goals 1.49/robot; rs_kick lab 0.927/0.928 (vs h022 -0.009/-0.012),
  deployed 0.834/0.879; bench v2 quick +12.3, no regressions. o3 -1500: short
  1.56x, miss 3.46 m, long 0.89x, aim 4.4, near 2.78 s, goals 1.44; rs_kick lab
  0.935/0.923, deployed 0.838/0.871; bench v2 quick +28.2, no regressions.
  Neither promoted (no gain on speed / accuracy / time to kick).
  Cause: within a range class kick speed is uncorrelated with the needed speed
  (corr ~0 for h022, o3 and B-Human; p10-p90 1.5-4.7 m/s). The policy sees only
  the range one-hot (< 4 / 4-8 / >= 8 m), so "short" spans 0.8-2.5 m/s needed and
  it kicks for the far end (short targets reached 93-95 % vs B-Human 67 %).
  Overshoot is an input limit (deployment contract), not reward or pose.

### 2026-10-26 — rs_kick power scored by kick class (user request)
User: power should follow each kick's intended design (strong, small, medium). `rs_kick.power_score`: strong (range ≥ 8 m, every 20 m trial) = min(1, peak / 7.5 m/s), the training long-kick reference; small (< 4 m) / medium (4–8 m) = 1 − |peak / need − 1|, need = √(2 · 0.95 · range), our training roll deceleration (was clip(peak / √(2 · 0.3 · range)) for all, which capped at ~3.5 m/s and never charged overshoot). Edges / decel / reference are asserted equal to kick_loop's. `rs_judge` rescores reference CSVs on load (`rs_kick.rescore`); `bench_bhuman_kick_v2` uses the shared score. Old report.md files keep the old scores.
Rescored (lab s0/s1 old → new): B-Human 0.925/0.931 → 0.854/0.861; h022 0.936/0.940 → 0.841/0.845; n4 0.954/0.950 → 0.855/0.855; n5b → 0.854/0.858; n1 → 0.850/0.852; n7 → 0.843/0.845. Deployed: h022 0.754/0.771, n7 0.795/0.803, n5b 0.774/0.809. Power lab s1 (small / medium / strong): h022 0.25 / 0.91 / 0.56 (small at 1.9× need), B-Human 0.73 / 0.53 / 0.57 (small 0.76×, medium 0.51×). B-Human now leads h022 in lab by ~0.015; small-kick overshoot is the whole gap (range input, u027).
