# Experience repository

68 experiences in `experiences.jsonl` (context, action, result, impact, lesson).
Updated by `scripts/tools/experience.py` (sync from the evolution loops; manual records via `add`).

## Objectives (every experience is read against these)

- **accuracy**: kicks on target (first touch within 15 deg, kicks within 20 deg, goals)
- **time_to_kick**: kick quickly once at the ball (first kick time / share)
- **power_by_range**: short passes stop near the target, long kicks as hard as possible
- **speed_caps**: run at the speed caps (cap use, approach speed)
- **posture**: upright ~0.52 m, no lean, smooth (height, pitch, action rate)
- **safety**: few falls in every situation, torque within limits
- **style_selection**: keep every kick style (front, inside, hop, ...) and use the best one for each situation
- **beat_bhuman**: beat B-Human convincingly on the kick league, then keep improving
- **no_regression**: never trade away an objective already built up
- **deployable**: one end-to-end policy, deployed path (runner clip, lost rule), 83 inputs

## Objective balance over all experiences

| objective | improved | worsened | mixed |
|---|---|---|---|
| accuracy | 13 | 28 | 6 |
| time_to_kick | 6 | 16 | 4 |
| power_by_range | 4 | 17 | 6 |
| speed_caps | 7 | 9 | 0 |
| posture | 4 | 6 | 0 |
| safety | 14 | 24 | 0 |
| style_selection | 2 | 5 | 2 |
| beat_bhuman | 0 | 0 | 0 |
| no_regression | 0 | 0 | 0 |
| deployable | 0 | 0 | 0 |

## What each kind of action did

| action feature | n | promoted | mean score | best | most frequent effects |
|---|---|---|---|---|---|
| gene:rsi_bhuman | 30 | 0 | 68.45 | 252.71 | bumps_goals:worse ×9, flat_goals:worse ×8, moving_goals:worse ×8, kicks_20_pct:better ×7, short_stop_m:worse ×7, first_touch_15_pct:better ×7 |
| level:L0/L1 | 28 | 0 | 0.77 | 28.31 | bumps_goals:worse ×22, moving_goals:worse ×17, h2h_long_knee_p90:worse ×15, flat_goals:worse ×14, bumps_late_falls_pct:worse ×12, latency_goals:worse ×9 |
| gene:s.far_spawn_prob | 23 | 0 | 166.7 | 252.71 | first_touch_15_pct:better ×11, fall_pct:better ×10, kicks_20_pct:better ×10, first_kick_pct:better ×8, goals_per_ep:better ×8, long_3d:better ×8 |
| gene:s.spawn_any_prob | 23 | 0 | 166.7 | 252.71 | first_touch_15_pct:better ×11, fall_pct:better ×10, kicks_20_pct:better ×10, first_kick_pct:better ×8, goals_per_ep:better ×8, long_3d:better ×8 |
| gene:desired_kl | 22 | 0 | 112.24 | 252.71 | short_stop_m:worse ×6, fall_pct:better ×6, first_touch_15_pct:better ×6, kicks_20_pct:better ×6, long_3d:better ×6, long_x_needed:better ×6 |
| gene:w.kick_rest_accuracy | 22 | 0 | 63.19 | 252.71 | bumps_goals:worse ×6, flat_goals:worse ×4, h2h_long_knee_p90:worse ×4, moving_goals:worse ×4, fall_pct:better ×4, fast_height_m:worse ×4 |
| gene:k.STYLE_MAP | 21 | 0 | 142.25 | 252.71 | kicks_20_pct:better ×7, first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:rsi_ours | 21 | 0 | 138.95 | 252.71 | first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, kicks_20_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:t.hop_power_long | 21 | 0 | 142.25 | 252.71 | kicks_20_pct:better ×7, first_touch_15_pct:better ×7, goals_per_ep:better ×6, style_selection_pct:worse ×6, fall_pct:better ×6, cap_use:better ×5 |
| gene:w.hop_kick_fall | 21 | 0 | 142.25 | 252.71 | kicks_20_pct:better ×7, first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:w.hop_kick_style | 21 | 0 | 142.25 | 252.71 | kicks_20_pct:better ×7, first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:w.inside_foot_style | 21 | 0 | 142.25 | 252.71 | kicks_20_pct:better ×7, first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:s.unknown_start_prob | 20 | 0 | 189.87 | 252.71 | first_touch_15_pct:better ×9, fall_pct:better ×8, kicks_20_pct:better ×8, cap_use:better ×7, first_kick_pct:better ×7, goals_per_ep:better ×7 |
| gene:k.STYLE_SHARE_HOP | 18 | 0 | 186.8 | 252.71 | first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, kicks_20_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:k.STYLE_SHARE_INSIDE | 18 | 0 | 186.8 | 252.71 | first_touch_15_pct:better ×7, style_selection_pct:worse ×6, fall_pct:better ×6, kicks_20_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5 |
| gene:w.long_kick_speed_linear | 17 | 0 | 186.8 | 252.71 | fall_pct:better ×6, first_touch_15_pct:better ×6, kicks_20_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5, goals_per_ep:better ×5 |
| gene:w.style_advantage | 17 | 0 | 186.8 | 252.71 | fall_pct:better ×6, first_touch_15_pct:better ×6, kicks_20_pct:better ×6, cap_use:better ×5, first_kick_pct:better ×5, goals_per_ep:better ×5 |
| gene:w.action_rate_l2 | 13 | 0 | 156.47 | 175.6 | action_rate:worse ×2, fall_pct:better ×2, fast_height_m:worse ×2, first_touch_15_pct:better ×2, goals_per_ep:better ×2, kicks_20_pct:better ×2 |
| level:L5 | 11 | 0 | 159.62 | 251.4 | first_touch_15_pct:better ×10, fall_pct:better ×8, kicks_20_pct:better ×8, first_kick_pct:better ×7, first_kick_s:worse ×6, goals_per_ep:better ×6 |
| gene:caps_near_ball_scale | 8 | 0 | None | None |  |
| gene:caps_temporal_coef | 8 | 0 | None | None |  |
| gene:k.MOMENTUM_KICK_MAX_SPEED | 8 | 0 | -2.89 | 22.86 | bumps_goals:worse ×7, h2h_long_knee_p90:worse ×6, moving_goals:worse ×6, flat_goals:worse ×5, bumps_late_falls_pct:worse ×4, h2h_aim_pct:worse ×3 |
| gene:t.far_cap_tracking | 8 | 0 | 5.14 | 12.71 | bumps_goals:worse ×6, flat_goals:worse ×3, moving_goals:worse ×3, latency_goals:worse ×3, approach_kick_pct:worse ×2, bumps_late_falls_pct:worse ×2 |
| gene:w.long_kick_power | 8 | 0 | -4.32 | 7.37 | bumps_goals:worse ×6, flat_goals:worse ×5, moving_goals:worse ×5, h2h_long_knee_p90:worse ×3, bumps_late_falls_pct:worse ×3, approach_kick_pct:worse ×3 |
| gene:t.aim_tight | 7 | 0 | 31.37 | 137.33 | bumps_goals:worse ×4, flat_goals:worse ×3, moving_goals:worse ×3, approach_kick_pct:worse ×2, bumps_late_falls_pct:worse ×2, caps_fast_vx:worse ×1 |
| gene:w.search_turn | 7 | 0 | 4.72 | 14.52 | bumps_goals:worse ×7, flat_goals:worse ×5, moving_goals:worse ×5, approach_kick_pct:worse ×3, approach_vx:worse ×3, flat_late_falls_pct:worse ×2 |
| level:- | 7 | 0 | None | None | deployment fidelity ×2, benchmark ranking confirmed on robot ×1, first_touch_15_pct:worse (deployed) ×1, first_touch_15_pct:worse (zero delay) ×1, fall_pct:worse (ball behind) ×1, champion -> sty_power_17149 ×1 |
| gene:stand_start_prob | 6 | 0 | None | None |  |
| gene:w.side_foot_strike | 6 | 0 | 2.24 | 7.37 | bumps_goals:worse ×4, bumps_late_falls_pct:worse ×4, moving_goals:worse ×3, flat_goals:worse ×2, long_x_needed:worse ×1, push_late_falls_pct:worse ×1 |
| gene:k.KICK_STYLE_AMP | 5 | 0 | -0.29 | 4.18 | long_3d:worse ×2, bumps_goals:worse ×2, flat_goals:worse ×2, moving_goals:worse ×2, short_stop_m:worse ×2, goals_per_ep:worse ×1 |
| gene:k.SUPPORT_PLANT_FACTOR | 5 | 0 | -9.17 | 4.18 | bumps_goals:worse ×3, flat_goals:worse ×3, h2h_long_knee_p90:worse ×3, moving_goals:worse ×3, bumps_late_falls_pct:worse ×3, short_stop_m:worse ×3 |
| gene:t.long_power_ramp | 5 | 0 | 55.77 | 252.71 | bumps_goals:worse ×4, flat_goals:worse ×3, moving_goals:worse ×3, approach_kick_pct:worse ×2, bumps_late_falls_pct:worse ×2, caps_fast_vx:worse ×2 |
| gene:w.kick_direction | 5 | 0 | -6.08 | 22.86 | bumps_goals:worse ×4, h2h_long_knee_p90:worse ×4, flat_goals:worse ×3, moving_goals:worse ×3, flat_late_falls_pct:worse ×3, h2h_long_3d:worse ×2 |
| gene:w.long_kick_underpower | 5 | 0 | -1.85 | 22.86 | bumps_goals:worse ×4, flat_goals:worse ×2, h2h_long_3d:worse ×2, h2h_long_knee_p90:worse ×2, long_x_needed:worse ×2, moving_goals:worse ×2 |
| gene:w.torque_over_soft_limit | 5 | 0 | -2.76 | 22.86 | bumps_goals:worse ×5, flat_goals:worse ×3, h2h_long_knee_p90:worse ×3, moving_goals:worse ×3, h2h_aim_pct:worse ×2, bumps_late_falls_pct:worse ×2 |
| level:L1@L5 | 5 | 2 | 217.1 | 279.7 | first_touch_15_pct:better ×4, fall_pct:better ×3, goal_pct:better ×3, style_selection_pct:worse ×2, kicks_20_pct:better ×2, long_3d:better ×2 |
| gene:amp_kick_data | 4 | 0 | 2.86 | 4.18 | long_3d:worse ×2, goals_per_ep:worse ×1, kicks_20_pct:better ×1, support_planted:worse ×1, bumps_goals:worse ×1, bumps_late_falls_pct:worse ×1 |
| gene:k.LONG_AIM_SIGMA2 | 4 | 0 | -13.31 | -3.52 | bumps_goals:worse ×3, flat_goals:worse ×3, h2h_long_knee_p90:worse ×3, moving_goals:worse ×3, h2h_long_3d:worse ×2, long_x_needed:worse ×2 |
| gene:s.cap_low_prob | 4 | 0 | 199.09 | 251.4 | first_touch_15_pct:better ×4, fall_pct:better ×3, goals_per_ep:worse ×3, first_kick_s:worse ×3, action_rate:better ×2, cap_use:better ×2 |
| gene:s.world_ball_prob | 4 | 0 | None | None |  |
| gene:t.upright_fast | 4 | 0 | 3.59 | 12.71 | bumps_goals:worse ×3, bumps_late_falls_pct:worse ×3, latency_goals:worse ×3, moving_goals:worse ×2, approach_vx:worse ×2, h2h_long_knee_p90:worse ×1 |
| level:L2 | 4 | 0 | None | None |  |
| level:L3 | 4 | 0 | None | None | first_touch_15_pct:better ×1, fall_pct:better ×1, goals_per_ep:worse ×1, first_kick_s:worse ×1, first_kick_pct:worse ×1 |
| gene:c.action_rate_l2 | 3 | 0 | 137.33 | 137.33 | action_rate:worse ×1, cap_use:better ×1, fall_pct:better ×1, fast_height_m:worse ×1, first_touch_15_pct:better ×1, goals_per_ep:better ×1 |
| gene:w.walk_speed_track | 3 | 0 | 199.09 | 251.4 | action_rate:better ×2, cap_use:better ×2, fall_pct:better ×2, fall_pct_behind:better ×2, first_kick_pct:better ×2, first_kick_s:worse ×2 |
| level:L1@L3 | 3 | 0 | None | None |  |
| gene:k.TRACK_BRAKE_PROFILE | 2 | 0 | 199.09 | 251.4 | action_rate:better ×2, cap_use:better ×2, fall_pct:better ×2, fall_pct_behind:better ×2, first_kick_pct:better ×2, first_kick_s:worse ×2 |
| gene:t.quick_kick | 2 | 0 | None | None | first_touch_15_pct:better ×1, goals_per_ep:better (high caps) ×1, first_kick_s:worse (low caps) ×1 |
| level:L1 | 2 | 0 | None | None | long_3d:worse ×2, goals_per_ep:worse ×1, first_kick_s:better ×1, goals_per_ep:better ×1, kicks_20_pct:better ×1, fall_pct:worse ×1 |
| level:L1@L2 | 2 | 0 | 137.33 | 137.33 | action_rate:worse ×1, cap_use:better ×1, fall_pct:better ×1, fast_height_m:worse ×1, first_touch_15_pct:better ×1, goals_per_ep:better ×1 |
| atom:ball_behind_starts | 1 | 0 | 118.83 | 118.83 | action_rate:better ×1, fall_pct:better ×1, fall_pct_behind:better ×1, first_kick_pct:better ×1, first_kick_pct:worse ×1, first_kick_s:worse ×1 |
| gene:k.PROMPT_FLOOR | 1 | 0 | None | None | first_touch_15_pct:better ×1, goals_per_ep:better (high caps) ×1, first_kick_s:worse (low caps) ×1 |
| gene:k.PROMPT_KICK_TAU | 1 | 0 | None | None | first_touch_15_pct:better ×1, goals_per_ep:better (high caps) ×1, first_kick_s:worse (low caps) ×1 |
| gene:s.ball_origin_trunk_prob | 1 | 0 | None | None |  |
| gene:style_w | 1 | 0 | 22.86 | 22.86 | bumps_goals:worse ×1, flat_late_falls_pct:worse ×1, h2h_long_knee_p90:worse ×1 |
| gene:w.kick_time_cost | 1 | 0 | None | None | first_touch_15_pct:better ×1, goals_per_ep:better (high caps) ×1, first_kick_s:worse (low caps) ×1 |
| gene:w.turn_rate_track | 1 | 0 | None | None | first_touch_15_pct:better ×1, goals_per_ep:better (high caps) ×1, first_kick_s:worse (low caps) ×1 |
| level:L0 | 1 | 1 | None | None | promotion via blending ×1 |
| level:L1/L3 | 1 | 0 | None | None | kicks_20_pct:better ×1, long_3d:worse ×1, support_planted:worse ×1 |

## Lessons (latest first)

- **promotion/h010_c2_17850_x70_2seed** (2026-10-08 11:09): A 70/30 champion blend kept the h010 child's gains without its stop-distance regression; runswift's speed gate must be judged on 6/9 m kicks (3 m passes are meant to be soft).
- **promotion/h007_c1_17650_x50_2seed** (2026-10-08 05:36): Blending a context child 50/50 with the champion was again what made the candidate promotable; the approach-speed reward (cap tracking down to 1 m) cut the low-cap time-to-kick drift to within tolerance.
- **hier/h005** (2026-10-07 23:31): Moderate time-to-kick shaping (time cost -5, promptness floor 0.25, quick kick, turn-rate) did not stop the low-cap slowdown (6.7-7.7 s vs 5.9); high-cap goals rose to ~2.1-2.2. Champion blends of the best child did not beat the parent either.
- **manual/2026-10-07_control_defaults** (2026-10-07 22:25): Training on the deployed path (target clip, delay from 0, feet origin) clearly improves deployed accuracy, power and safety; the low-cap slowness is fine-tune drift on a rare condition (low caps ~10 % of episodes), not caused by those defaults.
- **hier/h004** (2026-10-07 22:25): Low-cap slowness also without ball-behind starts.
- **hier/ctx/L5_ball_behind_starts** (2026-10-07 19:28): Best of the context: h001 blend (+161 v2, 1 regression: low-cap close-start first kick 4.30 -> 4.86 s). Large safety/accuracy gains vs a consistent low-cap time-to-kick cost.
- **hier/h003** (2026-10-07 19:28): Inside the ball-behind context every child (h001, h002, h003) lost 0.5-2 s of low-cap time to kick and low-cap goals while gaining accuracy and safety; the scenario mix itself causes it. Outcome-only styles inside that context did not restore front kicks or style selection within 500 iterations.
- **hier/h002** (2026-10-07 18:23): Training more episodes at low caps made the policy slower at low caps (goals 1.11 -> 0.75-0.89, first kick +0.7-1.0 s); low-cap time to kick is likely a technique cost (inside-foot alignment under a 0.6 rad/s turn cap), not a lack of low-cap practice.
- **manual/2026-10-07_ball_behind_early** (2026-10-07 15:02): Training with the ball at any bearing / far removed almost all ball-behind falls (36-38 % -> 1-2.5 %) and doubled near-ball first-touch accuracy; the cost is slower, fewer kicks at low caps - pair it with low-cap episodes (s.cap_low_prob).
- **bench/2026-10-07_v2_baselines** (2026-10-07 12:30): Under the deployed path the inside-foot lineage is the better policy; its weak spots (power, ball-behind falls) are the next targets.
- **bench/2026-10-07_ball_behind** (2026-10-07 11:30): Cover every start the robot can meet (ball behind, far) in training, and count falls from t = 0 in every benchmark situation.
- **bench/2026-10-07_motor_delay** (2026-10-07 10:30): A policy that only works inside its training delay range is brittle; train and test delay ranges that include zero.
- **bench/2026-10-07_runner_target_clip** (2026-10-07 10:00): Benchmark the deployed action path: any runner transform (clip, filter) must be in training and in the benchmark, or the policy learns to depend on what deployment removes (x4 pressed hip roll 0.38 rad past its stop).
- **manual/2026-10-07_torque_clip** (2026-10-07 09:00): Use loaded torque limits, not motor ratings; keep them in one table until measured on the robot.
- **manual/2026-10-07_sty_power** (2026-10-07 07:30): Power recovered only partly after the style curriculum; inside-foot passes with a hop are the remaining safety issue.
- **manual/2026-10-06_styles_k4_bundle** (2026-10-07 03:30): A rising target-angle curriculum (B-Human style) teaches the inside foot where a fixed 90 deg reward did not (1 %); do not bundle known-harmful defaults (K4) into a new experiment; free style choice collapses onto the most rewarded style (hop).
- **manual/2026-10-06_robot_g014_vs_x4** (2026-10-06 17:46): The benchmark ranking predicted the robot; keep rejecting children with regressions even if they look faster.
- **manual/2026-10-06_k4_confound** (2026-10-06 22:00): Make every default a switchable gene and record the parent's exact recipe; a default change confounds every child that inherits it.
- **manual/2026-10-05_weight_blend_x3_x4** (2026-10-06 08:40): In the flat loop, blending the champion with a near-miss child was the only route to promotion; single gene changes rarely survive the no-regression gate.

## All experiences (latest first)

| id | level | action | score | promoted | impact | objectives |
|---|---|---|---|---|---|---|
| hier/h023 | L2 | fix h022_c2_18450's two regressions (seed 1 +172.9 / seed 2 +126.5 vs champion; camera run | None |  |  |  |
| hier/h022 | L1@L3 | add template far_cap_tracking | in cold starts with the ball behind (runswift goal grid, a | None |  |  |  |
| hier/ctx/021_L3 | L3 | context: world-model ball (2026-10-09): the runswift harness (truth inputs) and v2 'world' |  |  |  |  |
| hier/h021 | L1@L3 | add template aim_tight | in world-model ball (2026-10-09): the runswift harness (truth inp | None |  |  |  |
| hier/h020 | L1@L3 | add template aim_tight | in world-model ball (2026-10-09): the runswift harness (truth inp | None |  |  |  |
| hier/h019 | L3 | world-model ball (2026-10-09): the runswift harness (truth inputs) and v2 'world' percepti | None |  |  |  |
| hier/h018 | L3 | cold starts with the ball behind (runswift goal grid, aligned fixture: every miss of h014  | None |  |  |  |
| hier/h017 | L1@L2 | add template quick_kick | in smooth near the ball (user 2026-10-08): CAPS on the determini | None |  |  |  |
| hier/h016 | L2 | smooth near the ball (user 2026-10-08): CAPS on the deterministic action, temporal 1.3, ne | None |  |  |  |
| hier/h015 | L1@L5 | add template far_cap_tracking | in keep h011 long power (3D 4.4-4.5 m/s) and fix its high- | None |  |  |  |
| hier/ctx/014_L2 | L2 | context: smooth + stable actions (user 2026-10-08): action_rate held at 0.75x the parent l |  |  |  |  |
| hier/h014 | L1@L2 | add template aim_tight | in smooth + stable actions (user 2026-10-08): action_rate held at | 137.33 |  | +21 / -7 | accuracy better, power_by_range mixed, safety better, speed_caps better, posture worse, style_selection worse |
| hier/h013 | L2 | smooth + stable actions (user 2026-10-08): action_rate held at 0.75x the parent level by d | None |  |  |  |
| hier/h012 | L5 | keep h011 long power (3D 4.4-4.5 m/s) and fix its high-cap regressions: smoother actions ( | 175.6 |  | +27 / -5 | accuracy better, time_to_kick better, power_by_range mixed, safety better, posture worse, style_selection worse |
| hier/h011 | L1@L5 | add template long_power_ramp | in power + styles v2 from h009 child: style_advantage 1500, | 252.71 |  | +27 / -3 | accuracy better, time_to_kick better, power_by_range better, safety better, speed_caps better, posture worse, style_selection mixed |
| promotion/h010_c2_17850_x70_2seed | L1@L5 | power + styles v2 (style_advantage 1500, short-pass stop 1000, long uncapped 800, KL 0.004 | 118.9 | yes | fall_pct:better, goal_pct:better, first_touch_15_pct:better, long_3d:better | safety better, accuracy better, power_by_range better |
| hier/h010 | L5 | power + styles v2 from h009 child: style_advantage 1500, short-pass stop reward 1000, long | 186.4 |  | +23 / -2 | accuracy better, time_to_kick better, power_by_range mixed, safety better, speed_caps better, posture worse, style_selection better |
| hier/h009 | L5 | power + learned style choice, small policy steps (KL 0.004), from the new champion | 209.5 |  | +19 / -5 | accuracy better, time_to_kick better, power_by_range mixed, safety better, speed_caps better, posture worse, style_selection worse |
| hier/h008 | L5 | conservative fine-tune: desired_kl 0.004 (smaller policy steps, less drift of the champion | 251.4 |  | +43 / -9 | accuracy mixed, time_to_kick mixed, power_by_range mixed, safety better, speed_caps better, posture better, style_selection better |
| promotion/h007_c1_17650_x50_2seed | L1@L5 | approach-speed context (track the vx cap with braking to 1 m, walk_speed_track 6, 15 % low | 279.7 | yes | fall_pct:better, goal_pct:better, first_touch_15_pct:better, first_kick_cens:better (high caps) | safety better, accuracy better, time_to_kick better |
| hier/h007 | L5 | approach speed: track the vx cap with the braking profile down to 1 m (k.TRACK_BRAKE_PROFI | 146.77 |  | +24 / -6 | accuracy mixed, time_to_kick mixed, power_by_range mixed, safety better, speed_caps better, posture better, style_selection mixed |
| hier/h006 | L5 | power + learned style choice: style forcing off, style_advantage 600, long uncapped 800, R | 159.28 |  | +24 / -4 | accuracy better, time_to_kick mixed, safety better, speed_caps better, posture better, style_selection worse |
| hier/h005 | L5 | time to kick T1 (moderate): time cost, promptness floor 0.25 / tau 1.0, quick kick, turn-r |  |  | first_touch_15_pct:better, goals_per_ep:better (high caps), first_kick_s:worse (low caps) | accuracy better, time_to_kick worse |
| manual/2026-10-07_control_defaults | - | control: champion recipe 500 it. with today's training defaults (A) vs without (B: no targ |  |  | first_touch_15_pct:better, long_x_needed:better, fall_pct_behind:better, first_kick_s:worse | accuracy better, power_by_range better, safety better, time_to_kick worse |
| hier/h004 | L5 | situational styles from the champion (no ball-behind), outcome-only + RSI front/inside |  |  | first_touch_15_pct:better, first_kick_s:worse, goals_per_ep:worse | accuracy mixed, time_to_kick worse |
| hier/ctx/L5_ball_behind_starts | L5 | context closed: ball_behind_starts (spawn_any 0.3, far 0.3) |  |  |  |  |
| hier/h003 | L1@L5 | situational styles: outcome-only rewards (no style shares / bonuses, hop_power_long off),  |  |  | first_touch_15_pct:better, goals_per_ep:mixed, first_kick_s:worse, style_selection_pct:worse | accuracy better, time_to_kick worse, style_selection worse |
| hier/h002 | L3 | s.cap_low_prob 0.3 inside ball_behind_starts (fix low-cap time-to-kick regression of h001  |  |  | first_touch_15_pct:better, fall_pct:better, goals_per_ep:worse, first_kick_s:worse | accuracy mixed, safety better, time_to_kick worse |
| hier/h001 | L5 | atom ball_behind_starts: spawn the ball at any bearing and far (v2 approach falls with the | 118.83 |  | +22 / -9 | accuracy mixed, time_to_kick mixed, power_by_range better, safety better, posture better |
| manual/2026-10-07_ball_behind_early | L5 | ball-behind and far starts (s.spawn_any_prob 0.3, s.far_spawn_prob 0.3), ~1350 iterations  | 29.2 |  | fall_pct:better, fall_pct_behind:better, first_touch_15_pct:better, kicks_20_pct:better | safety better, accuracy mixed, time_to_kick worse |
| evolve/evo_g021_x50 | L0/L1 | gene child evo_g021_x50 | -11.13 |  | latency_goals:worse | accuracy worse |
| evolve/evo_g021_14600 | L0/L1 | gene child evo_g021_14600 | 28.31 |  | bumps_goals:worse, bumps_late_falls_pct:worse, flat_late_falls_pct:worse, h2h_long_knee_p90:worse | accuracy worse, safety worse, time_to_kick worse |
| evolve/sty_free_14950 | L0/L1 | gene child sty_free_14950 | 9.12 |  | approach_kick_pct:worse, approach_vx:worse, bumps_late_falls_pct:worse, h2h_long_knee_p90:worse | time_to_kick worse, speed_caps worse, safety worse, accuracy worse |
| evolve/sty_range_x50 | L0/L1 | gene child sty_range_x50 | 8.44 |  | bumps_goals:worse, h2h_long_knee_p90:worse, h2h_support_planted_short_pct:worse, latency_goals:worse | accuracy worse, safety worse, power_by_range worse |
| evolve/sty_range_14450 | L0/L1 | gene child sty_range_14450 | 21.81 |  | approach_first_s:worse, bumps_goals:worse, bumps_late_falls_pct:worse, caps_fast_vx:worse | accuracy worse, safety worse, speed_caps worse, time_to_kick worse |
| evolve/evo_g017_x50 | L0/L1 | gene child evo_g017_x50 | 4.94 |  | approach_vx:worse, bumps_goals:worse, latency_goals:worse | speed_caps worse, accuracy worse |
| evolve/evo_g017_14450 | L0/L1 | gene child evo_g017_14450 | 12.71 |  | approach_first_s:worse, approach_kick_pct:worse, approach_vx:worse, bumps_goals:worse | time_to_kick worse, speed_caps worse, accuracy worse, safety worse |
| evolve/evo_g016_x70 | L0/L1 | gene child evo_g016_x70 | 4.87 |  | bumps_goals:worse | accuracy worse |
| evolve/evo_g016_14400 | L0/L1 | gene child evo_g016_14400 | -2.68 |  | bumps_goals:worse, flat_goals:worse, h2h_aim_pct:worse, h2h_long_knee_p90:worse | accuracy worse, safety worse, power_by_range worse |
| evolve/evo_g015_x50 | L0/L1 | gene child evo_g015_x50 | -1.78 |  | bumps_late_falls_pct:worse, h2h_first_kick_pct:worse | safety worse, time_to_kick worse |
| evolve/evo_g015_14700 | L0/L1 | gene child evo_g015_14700 | -1.51 |  | bumps_goals:worse, bumps_late_falls_pct:worse, h2h_long_knee_p90:worse, latency_goals:worse | accuracy worse, safety worse |
| evolve/evo_g014_x50 | L0/L1 | gene child evo_g014_x50 | 1.27 |  | bumps_goals:worse, flat_goals:worse, moving_goals:worse | accuracy worse |
| evolve/evo_g014_14550 | L0/L1 | gene child evo_g014_14550 | 7.23 |  | approach_kick_pct:worse, bumps_goals:worse, bumps_late_falls_pct:worse, caps_fast_vx:worse | time_to_kick worse, accuracy worse, safety worse, speed_caps worse, power_by_range worse |
| evolve/evo_g013_x50 | L0/L1 | gene child evo_g013_x50 | 3.63 |  | bumps_goals:worse | accuracy worse |
| evolve/evo_g013_14500 | L0/L1 | gene child evo_g013_14500 | 7.37 |  | approach_kick_pct:worse, bumps_goals:worse, bumps_late_falls_pct:worse, flat_goals:worse | time_to_kick worse, accuracy worse, safety worse |
| evolve/evo_g011_x50 | L0/L1 | gene child evo_g011_x50 | 4.18 |  | search_turn_rad:worse | accuracy worse |
| evolve/evo_g011_14700 | L0/L1 | gene child evo_g011_14700 | 1.55 |  | bumps_goals:worse, bumps_late_falls_pct:worse, flat_goals:worse, long_x_needed:worse | accuracy worse, safety worse, power_by_range worse |
| evolve/evo_g009_14600 | L0/L1 | gene child evo_g009_14600 | -6.6 |  | approach_first_s:worse, approach_kick_pct:worse, approach_vx:worse, bumps_goals:worse | time_to_kick worse, speed_caps worse, accuracy worse, safety worse, power_by_range worse |
| evolve/evo_g008_14450 | L0/L1 | gene child evo_g008_14450 | 22.86 |  | bumps_goals:worse, flat_late_falls_pct:worse, h2h_long_knee_p90:worse | accuracy worse, safety worse |
| evolve/evo_g006_14700 | L0/L1 | gene child evo_g006_14700 | -3.9 |  | bumps_late_falls_pct:worse, h2h_long_knee_p90:worse, short_stop_m:worse | safety worse, power_by_range worse |
| evolve/evo_g005_14600 | L0/L1 | gene child evo_g005_14600 | 14.52 |  | bumps_goals:worse, flat_goals:worse, flat_late_falls_pct:worse, h2h_first_kick_s:worse | accuracy worse, safety worse, time_to_kick worse, power_by_range worse |
| evolve/evo_g004_14300 | L0/L1 | gene child evo_g004_14300 | -3.52 |  | bumps_goals:worse, flat_goals:worse, flat_late_falls_pct:worse, h2h_aim_pct:worse | accuracy worse, safety worse, power_by_range worse |
| evolve/evo_g003_14700 | L0/L1 | gene child evo_g003_14700 | -14.88 |  | bumps_late_falls_pct:worse, flat_late_falls_pct:worse, h2h_long_3d:worse, long_x_needed:worse | safety worse, power_by_range worse |
| evolve/evo_g003_14450 | L0/L1 | gene child evo_g003_14450 | -28.25 |  | bumps_goals:worse, caps_fast_vx:worse, flat_goals:worse, h2h_first_kick_s:worse | accuracy worse, speed_caps worse, time_to_kick worse, power_by_range worse, safety worse, posture worse |
| evolve/evo_g002_14700 | L0/L1 | gene child evo_g002_14700 | -21.5 |  | bumps_aim_pct:worse, bumps_goals:worse, bumps_late_falls_pct:worse, flat_goals:worse | accuracy worse, safety worse, power_by_range worse |
| evolve/evo_g002_14450 | L0/L1 | gene child evo_g002_14450 | -26.17 |  | bumps_goals:worse, flat_goals:worse, h2h_aim_pct:worse, h2h_long_3d:worse | accuracy worse, power_by_range worse, safety worse |
| evolve/evo_g001_14700 | L0/L1 | gene child evo_g001_14700 | -11.21 |  | bumps_goals:worse, caps_fast_vx:worse, flat_goals:worse, h2h_aim_pct:worse | accuracy worse, speed_caps worse, power_by_range worse |
| evolve/evo_g001_14450 | L0/L1 | gene child evo_g001_14450 | 1.96 |  | bumps_goals:worse, caps_fast_vx:worse, flat_goals:worse, h2h_long_3d:worse | accuracy worse, speed_caps worse, power_by_range worse, safety worse |
| bench/2026-10-07_v2_baselines | - | benchmark v2 on x4, sty_power_17149, B-Human |  |  | champion -> sty_power_17149 |  |
| bench/2026-10-07_ball_behind | - | found why x4 fell in 34/90 goal-grid approaches |  |  | fall_pct:worse (ball behind) | safety worse |
| bench/2026-10-07_motor_delay | - | motor delay 10-40 ms (training) vs 0 (runswift fixture) |  |  | first_touch_15_pct:worse (zero delay) | accuracy worse |
| bench/2026-10-07_runner_target_clip | - | bisected the runswift-vs-ours accuracy gap (torque, feet, model, integrator, delay, I/O, O |  |  | first_touch_15_pct:worse (deployed), deployment fidelity | accuracy worse |
| manual/2026-10-07_torque_clip | - | hard leg torque clip at B-Human's 50/50/30/60/30/30 N·m (user) |  |  | deployment fidelity |  |
| manual/2026-10-07_sty_power | L1 | sty_power: K4 off, t.hop_power_long 800, w.long_kick_power 4000, 1000 it. |  |  | first_kick_s:better, goals_per_ep:better, kicks_20_pct:better, long_3d:worse | time_to_kick better, accuracy better, power_by_range worse, safety worse |
| manual/2026-10-06_styles_k4_bundle | L1/L3 | style runs sty_range / sty_free: inside foot (curriculum 20->90 deg) + hop, bundled with K |  |  | kicks_20_pct:better, long_3d:worse, support_planted:worse | accuracy better, power_by_range worse, safety worse |
| manual/2026-10-06_robot_g014_vs_x4 | - | robot test of the benchmark-rejected g014 and the champion x4 |  |  | benchmark ranking confirmed on robot |  |
| manual/2026-10-06_k4_confound | L1 | children silently inherited K4 defaults (kick clips in AMP data, style near the ball, RSI  |  |  | goals_per_ep:worse, long_3d:worse | accuracy worse, power_by_range worse |
| manual/2026-10-05_weight_blend_x3_x4 | L0 | weight-space blend of the champion with an evolution child (x3 = blend g003 0.6; x4 = 0.7  |  | yes | promotion via blending |  |
