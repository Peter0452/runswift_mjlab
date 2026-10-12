# Hierarchical evolution report

| level | frames | promoted | best screen |
|---|---|---|---|
| L2 | 3 | 0 | +49.8 |
| L3 | 3 | 0 | +42.0 |
| L5 | 9 | 0 | +88.7 |

| id | level | change | screen | v2 score | regressions | promoted |
|---|---|---|---|---|---|---|
| h001 | L5 | atom ball_behind_starts: spawn the ball at any bearing and far (v2 approach falls with the ball behind 23-45 %) | +55.4 | 118.83 | 9 |  |
| h002 | L3 | s.cap_low_prob 0.3 inside ball_behind_starts (fix low-cap time-to-kick regression of h001 blend) | +42.0 | — | 0 |  |
| h003 | L1@L5 | situational styles: outcome-only rewards (no style shares / bonuses, hop_power_long off), RSI 15 % front + 10 % B-Human inside so no style is forgotten | +63.9 | — | 0 |  |
| h004 | L5 | situational styles from the champion (no ball-behind) | +35.6 | — | 0 |  |
| h005 | L5 | time to kick T1 (moderate): time cost, promptness floor 0.25 / tau 1.0, quick kick, turn-rate, 15 % low caps, 15 % unknown starts, mild ball-behind | +63.9 | — | 0 |  |
| h006 | L5 | power + learned style choice: style forcing off, style_advantage 600, long uncapped 800, RSI front 15 % / inside 10 %, loft free, heavy balls | +51.3 | 159.28 | 4 |  |
| h007 | L5 | approach speed: track the vx cap with the braking profile down to 1 m (k.TRACK_BRAKE_PROFILE 1, w.walk_speed_track 6) - children walk to the ball 0.5-0.7 s slower at low caps | +69.3 | 146.77 | 5 |  |
| h008 | L5 | conservative fine-tune: desired_kl 0.004 (smaller policy steps, less drift of the champion's low-cap speed) + approach speed (brake profile, walk_speed_track 6) + 15 % low caps | +88.7 | 251.4 | 9 |  |
| h009 | L5 | power + learned style choice, small policy steps (KL 0.004), from the new champion | +58.1 | 209.5 | 4 |  |
| h010 | L5 | power + styles v2 from h009 child: style_advantage 1500, short-pass stop reward 1000, long uncapped 800, KL 0.004 | +68.6 | 186.4 | 1 |  |
| h011 | L1@L5 | add template long_power_ramp | in power + styles v2 from h009 child: style_advantage 1500, short-pass stop reward 1000, long uncapped 800, KL 0.004 | +85.0 | 252.71 | 3 |  |
| h012 | L5 | keep h011 long power (3D 4.4-4.5 m/s) and fix its high-cap regressions: smoother actions (action_rate -0.15), style_advantage kept | +69.2 | 175.6 | 1 |  |
| h013 | L2 | smooth + stable actions (user 2026-10-08): action_rate held at 0.75x the parent level by dual ascent, power + style_advantage kept | +47.4 | — | 0 |  |
| h014 | L1@L2 | add template aim_tight | in smooth + stable actions (user 2026-10-08): action_rate held at 0.75x the parent level by dual ascent, power + style_advantage kept | +61.8 | 137.33 | 5 |  |
| h015 | L1@L5 | add template far_cap_tracking | in keep h011 long power (3D 4.4-4.5 m/s) and fix its high-cap regressions: smoother actions (action_rate -0.15), style_advantage kept | +52.3 | — | 0 |  |
| h016 | L2 | smooth near the ball (user 2026-10-08): CAPS on the deterministic action, temporal 1.3, near-ball scale 0.5 -> 0.8; drop the action_rate constraint (noise-dominated); from h012_c1_18000 (power kept, close_any action_rate:high + heavy long regressions); env since 2026-10-08 21:30: ball 0.07-0.13 m / 0.05-0.45 kg, foot_flat settle 60 ms, touchdown_speed -50 (quiet steps) | +49.8 | — | 0 |  |
| h017 | L1@L2 | add template quick_kick | in smooth near the ball (user 2026-10-08): CAPS on the deterministic action, temporal 1.3, near-ball scale 0.5 -> 0.8; drop the action_rate constraint (noise-dominated); from h012_c1_18000 (power kept, close_any action_rate:high + heavy long regressions); env since 2026-10-08 21:30: ball 0.07-0.13 m / 0.05-0.45 kg, foot_flat settle 60 ms, touchdown_speed -50 (quiet steps) | +54.5 | — | 0 |  |
| h018 | L3 | cold starts with the ball behind (runswift goal grid, aligned fixture: every miss of h014 at high caps is a fall within 0.8 s of a standing start with the ball ~10 m behind; training only reset from moving motion clips): stand_start 0.35, spawn_any 0.3, far spawn 0.2; CAPS back to defaults; from h012_c1_18000 | +17.9 | — | 0 |  |
| h019 | L3 | world-model ball (2026-10-09): the runswift harness (truth inputs) and v2 'world' perception report a ball 10 m behind as seen; training never did (world_ball_prob 0: only camera view, memory, or the lost virtual ball), and the champion falls 32-40 % in exactly that start. s.world_ball_prob 0.3 with the cold starts (stand 0.35, ball behind 0.3, far 0.2), alive +2/s, touchdown -15; from h012_c1_18000 | -1000000000.0 | — | 0 |  |
| h020 | L1@L3 | add template aim_tight | in world-model ball (2026-10-09): the runswift harness (truth inputs) and v2 'world' perception report a ball 10 m behind as seen; training never did (world_ball_prob 0: only camera view, memory, or the lost virtual ball), and the champion falls 32-40 % in exactly that start. s.world_ball_prob 0.3 with the cold starts (stand 0.35, ball behind 0.3, far 0.2), alive +2/s, touchdown -15; from h012_c1_18000 | +59.1 | — | 0 |  |
| h021 | L1@L3 | add template aim_tight | in world-model ball (2026-10-09): the runswift harness (truth inputs) and v2 'world' perception report a ball 10 m behind as seen; training never did (world_ball_prob 0: only camera view, memory, or the lost virtual ball), and the champion falls 32-40 % in exactly that start. s.world_ball_prob 0.3 with the cold starts (stand 0.35, ball behind 0.3, far 0.2), alive +2/s, touchdown -15; from h012_c1_18000 | +68.9 | — | 0 |  |
| h022 | L1@L3 | add template far_cap_tracking | in cold starts with the ball behind (runswift goal grid, aligned fixture: every miss of h014 at high caps is a fall within 0.8 s of a standing start with the ball ~10 m behind; training only reset from moving motion clips): stand_start 0.35, spawn_any 0.3, far spawn 0.2; CAPS back to defaults; from h012_c1_18000 | +56.3 | — | 0 |  |
| h023 | L2 | fix h022_c2_18450's two regressions (seed 1 +172.9 / seed 2 +126.5 vs champion; camera runswift 90/90 goals 0 falls; quietest landings): low-cap approach first-kick 61 % vs 70 % (walk at the cap: walk_speed_track 6 -> 8) and action_rate high +0.007 (CAPS temporal 1.3); ball frame trunk 0.3; from h022_c2_18450 | +41.2 | — | 0 |  |
