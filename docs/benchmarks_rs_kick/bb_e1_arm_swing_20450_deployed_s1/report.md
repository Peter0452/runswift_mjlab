# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-03-35_e1_arm_swing/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.806** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 178 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.87 ± 1.05 (1.70) |
| Direction error [°] | 12.36 ± 26.55 (5.06) |
| Avg ball speed [m/s] | 2.07 ± 0.56 (2.13) |
| Peak ball speed [m/s] | 4.93 ± 1.39 (5.49) |
| Distance [m] | 2.20 ± 0.82 (2.33) |
| Path length [m] | 2.21 ± 0.82 (2.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.827 | 49/50 | 0 | 45 | 1.26 ± 0.29 (1.28) | 7.42 ± 11.42 (3.96) | 1.97 ± 0.60 (2.12) | 4.79 ± 1.51 (5.57) | 2.06 ± 0.83 (2.20) |
| left | p | 0.827 | 49/50 | 0 | 44 | 1.71 ± 0.42 (1.70) | 10.44 ± 22.06 (4.17) | 2.12 ± 0.46 (2.14) | 5.04 ± 1.19 (5.37) | 2.25 ± 0.75 (2.27) |
| back | p | 0.758 | 49/50 | 0 | 44 | 2.69 ± 1.53 (2.50) | 20.82 ± 41.90 (7.03) | 2.14 ± 0.62 (2.30) | 5.12 ± 1.50 (5.81) | 2.40 ± 0.90 (2.79) |
| right | p | 0.811 | 50/50 | 0 | 45 | 1.83 ± 0.86 (1.85) | 10.81 ± 18.75 (5.04) | 2.05 ± 0.51 (2.09) | 4.78 ± 1.30 (5.01) | 2.11 ± 0.75 (2.12) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 99/100 | 0 | 91 | 1.88 ± 0.94 (1.74) | 11.99 ± 26.22 (4.65) | 2.07 ± 0.59 (2.15) | 4.93 ± 1.44 (5.58) | 2.22 ± 0.84 (2.46) |
| right | p | 0.799 | 98/100 | 0 | 87 | 1.86 ± 1.15 (1.69) | 12.73 ± 26.87 (5.77) | 2.08 ± 0.52 (2.12) | 4.93 ± 1.34 (5.36) | 2.19 ± 0.80 (2.21) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 23 | 1.26 ± 0.31 (1.28) | 6.82 ± 11.20 (3.61) | 1.94 ± 0.64 (2.10) | 4.73 ± 1.60 (5.57) | 2.04 ± 0.88 (2.46) |
| forward/right | p | 0.807 | 24/25 | 0 | 22 | 1.26 ± 0.27 (1.30) | 8.03 ± 11.62 (4.32) | 2.01 ± 0.56 (2.13) | 4.86 ± 1.41 (5.57) | 2.08 ± 0.76 (2.15) |
| left/left | p | 0.844 | 24/25 | 0 | 24 | 1.71 ± 0.31 (1.62) | 3.78 ± 2.93 (2.31) | 2.24 ± 0.29 (2.20) | 5.31 ± 0.77 (5.51) | 2.41 ± 0.52 (2.43) |
| left/right | p | 0.810 | 25/25 | 0 | 20 | 1.71 ± 0.49 (1.74) | 16.83 ± 29.35 (6.47) | 2.02 ± 0.55 (2.08) | 4.78 ± 1.43 (4.57) | 2.09 ± 0.89 (1.98) |
| back/left | p | 0.764 | 25/25 | 0 | 22 | 2.52 ± 1.08 (2.40) | 23.14 ± 41.56 (9.17) | 2.16 ± 0.67 (2.45) | 5.08 ± 1.54 (5.87) | 2.40 ± 0.95 (2.81) |
| back/right | p | 0.751 | 24/25 | 0 | 22 | 2.87 ± 1.87 (2.54) | 18.40 ± 42.11 (6.28) | 2.13 ± 0.57 (2.22) | 5.16 ± 1.46 (5.80) | 2.39 ± 0.85 (2.56) |
| right/left | p | 0.796 | 25/25 | 0 | 22 | 2.05 ± 1.13 (1.98) | 13.90 ± 25.33 (3.78) | 1.94 ± 0.61 (2.08) | 4.63 ± 1.55 (5.15) | 2.03 ± 0.84 (2.15) |
| right/right | p | 0.826 | 25/25 | 0 | 23 | 1.62 ± 0.34 (1.60) | 7.71 ± 6.48 (5.58) | 2.15 ± 0.36 (2.09) | 4.94 ± 0.97 (4.86) | 2.19 ± 0.63 (2.10) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.834 | 10.9 | 5.41 | 2.49 |
| p | normal | 0.778 | 13.8 | 4.45 | 1.92 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.729 | 0.08 | 2.58 ± 1.04 (2.48) | 3.97 | 1.60 |
| p | medium | 20 | 0.866 | 0.66 | 1.29 ± 0.24 (1.33) | 4.14 | 1.69 |
| p | strong | 126 | 0.829 | 0.73 | - | 5.48 | 2.55 |

## Notes

- p: score 0.806, 197/200 kicked, 0 fell; worst sector back (0.758).
