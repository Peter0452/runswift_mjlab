# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_01-26-16_t6_n7_control_s7/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.772** |
| Kicked / fell | 192 / 0 |
| Kicks within 15° | 153 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.71 ± 1.18 (1.56) |
| Direction error [°] | 22.13 ± 41.00 (6.01) |
| Avg ball speed [m/s] | 2.37 ± 0.91 (2.58) |
| Peak ball speed [m/s] | 4.97 ± 1.98 (5.67) |
| Distance [m] | 2.47 ± 1.28 (2.80) |
| Path length [m] | 2.48 ± 1.28 (2.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.777 | 48/50 | 0 | 39 | 1.31 ± 0.73 (1.24) | 10.92 ± 15.58 (4.74) | 2.24 ± 0.89 (2.32) | 4.71 ± 1.93 (4.67) | 2.27 ± 1.23 (2.05) |
| left | p | 0.781 | 48/50 | 0 | 37 | 1.49 ± 0.46 (1.57) | 22.78 ± 36.39 (7.21) | 2.37 ± 0.90 (2.59) | 5.00 ± 1.96 (5.67) | 2.49 ± 1.27 (2.83) |
| back | p | 0.739 | 48/50 | 0 | 38 | 2.49 ± 1.97 (2.25) | 36.79 ± 60.85 (5.97) | 2.36 ± 1.03 (2.79) | 4.96 ± 2.25 (6.16) | 2.54 ± 1.42 (3.14) |
| right | p | 0.790 | 48/50 | 0 | 39 | 1.55 ± 0.42 (1.57) | 18.03 ± 33.12 (5.55) | 2.49 ± 0.80 (2.79) | 5.20 ± 1.71 (6.04) | 2.60 ± 1.14 (3.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 99/100 | 0 | 79 | 1.67 ± 1.15 (1.52) | 24.36 ± 44.71 (6.14) | 2.40 ± 0.94 (2.67) | 5.03 ± 2.03 (6.03) | 2.53 ± 1.30 (3.03) |
| right | p | 0.741 | 93/100 | 0 | 74 | 1.76 ± 1.22 (1.56) | 19.75 ± 36.49 (5.97) | 2.33 ± 0.88 (2.46) | 4.90 ± 1.92 (4.88) | 2.42 ± 1.25 (2.42) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 21 | 1.23 ± 0.34 (1.24) | 8.79 ± 15.12 (3.42) | 2.42 ± 0.75 (2.42) | 5.06 ± 1.67 (4.83) | 2.48 ± 1.08 (2.22) |
| forward/right | p | 0.715 | 23/25 | 0 | 18 | 1.40 ± 0.99 (1.28) | 13.24 ± 15.75 (7.91) | 2.05 ± 0.98 (2.19) | 4.32 ± 2.11 (4.39) | 2.05 ± 1.34 (1.88) |
| left/left | p | 0.827 | 25/25 | 0 | 20 | 1.41 ± 0.39 (1.52) | 18.39 ± 26.19 (7.72) | 2.47 ± 0.93 (2.71) | 5.16 ± 2.02 (6.14) | 2.65 ± 1.30 (3.10) |
| left/right | p | 0.735 | 23/25 | 0 | 17 | 1.58 ± 0.50 (1.66) | 27.55 ± 44.43 (6.86) | 2.26 ± 0.85 (2.49) | 4.83 ± 1.86 (5.42) | 2.31 ± 1.22 (2.72) |
| back/left | p | 0.720 | 24/25 | 0 | 17 | 2.40 ± 2.04 (2.17) | 50.08 ± 68.15 (8.47) | 2.23 ± 1.14 (2.89) | 4.74 ± 2.48 (6.37) | 2.42 ± 1.57 (3.34) |
| back/right | p | 0.759 | 24/25 | 0 | 21 | 2.57 ± 1.89 (2.32) | 23.50 ± 49.07 (4.94) | 2.49 ± 0.89 (2.73) | 5.18 ± 1.96 (5.97) | 2.65 ± 1.25 (3.05) |
| right/left | p | 0.825 | 25/25 | 0 | 21 | 1.65 ± 0.44 (1.70) | 21.22 ± 40.27 (4.19) | 2.48 ± 0.88 (2.77) | 5.15 ± 1.84 (6.07) | 2.56 ± 1.20 (3.28) |
| right/right | p | 0.754 | 23/25 | 0 | 18 | 1.43 ± 0.35 (1.50) | 14.56 ± 22.45 (7.07) | 2.50 ± 0.71 (2.81) | 5.25 ± 1.55 (6.02) | 2.64 ± 1.07 (2.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.798 | 19.6 | 5.77 | 3.05 |
| p | normal | 0.746 | 24.6 | 4.20 | 1.92 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.699 | 0.17 | 2.29 ± 1.21 (2.19) | 3.62 | 1.52 |
| p | medium | 16 | 0.804 | 0.61 | 1.34 ± 0.25 (1.35) | 4.33 | 1.91 |
| p | strong | 126 | 0.801 | 0.76 | - | 5.69 | 3.00 |

## Notes

- p: score 0.772, 192/200 kicked, 0 fell; worst sector back (0.739).
