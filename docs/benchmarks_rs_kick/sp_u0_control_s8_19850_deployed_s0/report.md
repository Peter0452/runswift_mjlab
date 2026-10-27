# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u0_control_s8/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 1.96 ± 1.35 (1.75) |
| Direction error [°] | 18.44 ± 36.38 (5.88) |
| Avg ball speed [m/s] | 2.35 ± 0.88 (2.61) |
| Peak ball speed [m/s] | 4.91 ± 1.91 (5.83) |
| Distance [m] | 2.39 ± 1.24 (2.90) |
| Path length [m] | 2.40 ± 1.24 (2.92) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.800 | 50/50 | 0 | 42 | 1.69 ± 1.96 (1.34) | 10.79 ± 17.66 (4.43) | 2.19 ± 0.88 (2.22) | 4.56 ± 1.92 (4.39) | 2.13 ± 1.20 (1.82) |
| left | p | 0.808 | 48/50 | 0 | 42 | 1.71 ± 0.50 (1.80) | 15.91 ± 31.32 (4.27) | 2.41 ± 0.80 (2.71) | 5.09 ± 1.78 (6.08) | 2.49 ± 1.17 (3.04) |
| back | p | 0.740 | 50/50 | 0 | 40 | 2.69 ± 1.47 (2.58) | 30.37 ± 52.65 (8.71) | 2.41 ± 0.98 (2.98) | 5.01 ± 2.07 (6.35) | 2.53 ± 1.35 (3.37) |
| right | p | 0.788 | 48/50 | 0 | 40 | 1.74 ± 0.48 (1.75) | 16.49 ± 31.51 (5.20) | 2.39 ± 0.82 (2.64) | 5.00 ± 1.81 (5.90) | 2.43 ± 1.18 (3.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.814 | 100/100 | 0 | 87 | 1.89 ± 1.13 (1.78) | 17.59 ± 37.04 (5.67) | 2.42 ± 0.85 (2.69) | 5.05 ± 1.86 (6.08) | 2.47 ± 1.23 (2.97) |
| right | p | 0.754 | 96/100 | 0 | 77 | 2.03 ± 1.54 (1.74) | 19.31 ± 35.67 (5.92) | 2.28 ± 0.90 (2.57) | 4.77 ± 1.95 (5.71) | 2.31 ± 1.24 (2.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 23 | 1.31 ± 0.28 (1.28) | 6.98 ± 10.80 (3.41) | 2.38 ± 0.82 (2.39) | 4.96 ± 1.79 (4.55) | 2.38 ± 1.19 (2.10) |
| forward/right | p | 0.748 | 25/25 | 0 | 19 | 2.06 ± 2.70 (1.34) | 14.60 ± 21.86 (6.24) | 2.00 ± 0.91 (2.12) | 4.15 ± 1.96 (4.19) | 1.88 ± 1.15 (1.76) |
| left/left | p | 0.857 | 25/25 | 0 | 23 | 1.62 ± 0.43 (1.76) | 11.95 ± 23.16 (4.12) | 2.46 ± 0.83 (2.72) | 5.17 ± 1.81 (6.10) | 2.56 ± 1.18 (3.16) |
| left/right | p | 0.758 | 23/25 | 0 | 19 | 1.81 ± 0.55 (1.96) | 20.22 ± 37.79 (4.65) | 2.36 ± 0.76 (2.70) | 5.00 ± 1.74 (5.93) | 2.41 ± 1.16 (2.97) |
| back/left | p | 0.740 | 25/25 | 0 | 21 | 2.80 ± 1.84 (2.58) | 31.68 ± 55.33 (8.73) | 2.47 ± 0.87 (3.02) | 5.15 ± 1.86 (6.43) | 2.57 ± 1.29 (3.39) |
| back/right | p | 0.741 | 25/25 | 0 | 19 | 2.57 ± 0.96 (2.58) | 29.06 ± 49.81 (7.18) | 2.34 ± 1.07 (2.95) | 4.87 ± 2.25 (6.22) | 2.48 ± 1.40 (3.35) |
| right/left | p | 0.807 | 25/25 | 0 | 20 | 1.85 ± 0.50 (1.82) | 19.77 ± 37.78 (5.43) | 2.36 ± 0.90 (2.81) | 4.92 ± 1.96 (6.22) | 2.39 ± 1.24 (3.18) |
| right/right | p | 0.768 | 23/25 | 0 | 20 | 1.62 ± 0.44 (1.72) | 12.93 ± 22.28 (5.14) | 2.42 ± 0.73 (2.61) | 5.09 ± 1.62 (5.82) | 2.47 ± 1.10 (3.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.812 | 18.8 | 5.69 | 2.98 |
| p | normal | 0.756 | 18.0 | 4.13 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.717 | 0.15 | 2.32 ± 1.12 (2.25) | 3.61 | 1.42 |
| p | medium | 16 | 0.789 | 0.69 | 1.26 ± 0.23 (1.28) | 4.07 | 1.66 |
| p | strong | 126 | 0.814 | 0.75 | - | 5.61 | 2.93 |

## Notes

- p: score 0.784, 196/200 kicked, 0 fell; worst sector back (0.740).
