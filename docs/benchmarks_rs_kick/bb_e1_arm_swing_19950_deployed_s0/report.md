# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-03-35_e1_arm_swing/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.775** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.96 ± 1.41 (1.76) |
| Direction error [°] | 17.39 ± 34.68 (5.76) |
| Avg ball speed [m/s] | 2.11 ± 0.63 (2.30) |
| Peak ball speed [m/s] | 4.57 ± 1.44 (5.02) |
| Distance [m] | 1.83 ± 0.78 (1.93) |
| Path length [m] | 1.84 ± 0.79 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.799 | 50/50 | 0 | 44 | 1.83 ± 2.15 (1.32) | 7.90 ± 10.74 (4.65) | 2.02 ± 0.60 (2.09) | 4.34 ± 1.43 (4.33) | 1.66 ± 0.75 (1.67) |
| left | p | 0.784 | 48/50 | 0 | 38 | 1.65 ± 0.48 (1.78) | 20.07 ± 35.42 (5.07) | 2.09 ± 0.68 (2.29) | 4.58 ± 1.57 (5.17) | 1.84 ± 0.83 (2.08) |
| back | p | 0.731 | 48/50 | 0 | 41 | 2.47 ± 0.63 (2.55) | 24.57 ± 47.90 (7.26) | 2.27 ± 0.63 (2.40) | 4.83 ± 1.40 (5.46) | 2.06 ± 0.80 (2.22) |
| right | p | 0.785 | 49/50 | 0 | 42 | 1.90 ± 1.47 (1.76) | 17.41 ± 32.30 (5.51) | 2.09 ± 0.56 (2.26) | 4.53 ± 1.32 (5.15) | 1.78 ± 0.71 (1.92) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 99/100 | 0 | 85 | 1.77 ± 0.64 (1.76) | 16.49 ± 35.47 (4.84) | 2.16 ± 0.61 (2.32) | 4.66 ± 1.41 (5.05) | 1.89 ± 0.78 (1.98) |
| right | p | 0.741 | 96/100 | 0 | 80 | 2.16 ± 1.87 (1.76) | 18.31 ± 33.82 (7.03) | 2.07 ± 0.63 (2.29) | 4.47 ± 1.47 (4.86) | 1.78 ± 0.78 (1.93) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.840 | 25/25 | 0 | 23 | 1.32 ± 0.34 (1.28) | 6.81 ± 11.89 (2.61) | 2.08 ± 0.61 (2.27) | 4.51 ± 1.45 (4.60) | 1.76 ± 0.75 (1.70) |
| forward/right | p | 0.759 | 25/25 | 0 | 21 | 2.34 ± 2.93 (1.34) | 8.98 ± 9.31 (5.97) | 1.95 ± 0.57 (2.08) | 4.17 ± 1.39 (4.24) | 1.56 ± 0.73 (1.64) |
| left/left | p | 0.840 | 25/25 | 0 | 20 | 1.57 ± 0.42 (1.74) | 13.25 ± 22.46 (4.84) | 2.17 ± 0.67 (2.29) | 4.74 ± 1.52 (5.21) | 1.96 ± 0.81 (2.06) |
| left/right | p | 0.728 | 23/25 | 0 | 18 | 1.74 ± 0.53 (1.92) | 27.47 ± 44.32 (6.76) | 2.00 ± 0.69 (2.23) | 4.40 ± 1.61 (5.12) | 1.71 ± 0.82 (2.09) |
| back/left | p | 0.737 | 24/25 | 0 | 21 | 2.41 ± 0.70 (2.49) | 25.28 ± 51.06 (6.50) | 2.36 ± 0.52 (2.44) | 4.97 ± 1.16 (5.38) | 2.13 ± 0.76 (2.25) |
| back/right | p | 0.724 | 24/25 | 0 | 20 | 2.54 ± 0.54 (2.60) | 23.86 ± 44.50 (8.15) | 2.18 ± 0.72 (2.35) | 4.69 ± 1.60 (5.47) | 1.99 ± 0.83 (2.18) |
| right/left | p | 0.816 | 25/25 | 0 | 21 | 1.80 ± 0.50 (1.80) | 20.98 ± 40.43 (4.85) | 2.03 ± 0.59 (2.26) | 4.42 ± 1.42 (5.19) | 1.70 ± 0.74 (1.87) |
| right/right | p | 0.755 | 24/25 | 0 | 21 | 2.00 ± 2.03 (1.65) | 13.70 ± 19.99 (7.08) | 2.15 ± 0.51 (2.26) | 4.64 ± 1.19 (5.04) | 1.86 ± 0.66 (1.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.809 | 13.6 | 5.20 | 2.16 |
| p | normal | 0.741 | 21.1 | 3.95 | 1.52 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.710 | 0.18 | 2.30 ± 1.03 (2.22) | 3.59 | 1.30 |
| p | medium | 16 | 0.784 | 0.66 | 1.32 ± 0.20 (1.34) | 4.26 | 1.69 |
| p | strong | 126 | 0.804 | 0.68 | - | 5.07 | 2.10 |

## Notes

- p: score 0.775, 195/200 kicked, 0 fell; worst sector back (0.731).
