# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-47-18_e4_yaw_cap/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.57 ± 0.52 (1.48) |
| Direction error [°] | 6.18 ± 11.24 (4.85) |
| Avg ball speed [m/s] | 1.73 ± 0.35 (1.77) |
| Peak ball speed [m/s] | 3.86 ± 0.86 (3.87) |
| Distance [m] | 1.29 ± 0.45 (1.29) |
| Path length [m] | 1.30 ± 0.46 (1.30) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 50 | 1.02 ± 0.23 (1.05) | 4.35 ± 2.98 (3.17) | 1.43 ± 0.36 (1.36) | 3.14 ± 0.80 (2.94) | 0.90 ± 0.42 (0.76) |
| left | p | 0.856 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.50) | 5.62 ± 3.56 (4.96) | 1.79 ± 0.27 (1.77) | 4.03 ± 0.68 (4.01) | 1.37 ± 0.38 (1.31) |
| back | p | 0.829 | 50/50 | 0 | 49 | 2.23 ± 0.26 (2.19) | 8.84 ± 21.40 (5.75) | 1.89 ± 0.31 (1.96) | 4.23 ± 0.80 (4.48) | 1.52 ± 0.39 (1.63) |
| right | p | 0.838 | 50/50 | 0 | 49 | 1.50 ± 0.35 (1.47) | 5.90 ± 3.90 (4.80) | 1.81 ± 0.27 (1.86) | 4.04 ± 0.72 (4.06) | 1.38 ± 0.37 (1.31) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.837 | 100/100 | 0 | 99 | 1.58 ± 0.54 (1.50) | 5.81 ± 3.72 (5.29) | 1.76 ± 0.29 (1.78) | 3.91 ± 0.75 (3.87) | 1.32 ± 0.41 (1.32) |
| right | p | 0.850 | 100/100 | 0 | 99 | 1.55 ± 0.51 (1.47) | 6.55 ± 15.45 (4.59) | 1.70 ± 0.40 (1.75) | 3.81 ± 0.96 (3.87) | 1.27 ± 0.50 (1.27) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.840 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.08) | 5.02 ± 3.25 (4.15) | 1.53 ± 0.30 (1.41) | 3.30 ± 0.65 (3.06) | 0.99 ± 0.37 (0.83) |
| forward/right | p | 0.863 | 25/25 | 0 | 25 | 1.01 ± 0.23 (1.02) | 3.68 ± 2.51 (2.97) | 1.34 ± 0.39 (1.30) | 2.98 ± 0.90 (2.86) | 0.82 ± 0.44 (0.70) |
| left/left | p | 0.844 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.46) | 6.16 ± 3.83 (4.29) | 1.73 ± 0.25 (1.73) | 3.87 ± 0.63 (3.83) | 1.28 ± 0.36 (1.23) |
| left/right | p | 0.868 | 25/25 | 0 | 25 | 1.60 ± 0.29 (1.60) | 5.09 ± 3.17 (5.12) | 1.85 ± 0.27 (1.92) | 4.20 ± 0.68 (4.45) | 1.47 ± 0.38 (1.51) |
| back/left | p | 0.818 | 25/25 | 0 | 25 | 2.27 ± 0.27 (2.20) | 6.77 ± 3.57 (6.97) | 1.93 ± 0.19 (1.92) | 4.28 ± 0.55 (4.42) | 1.54 ± 0.31 (1.60) |
| back/right | p | 0.840 | 25/25 | 0 | 24 | 2.20 ± 0.24 (2.12) | 10.90 ± 29.91 (4.86) | 1.86 ± 0.39 (2.04) | 4.17 ± 0.98 (4.65) | 1.49 ± 0.45 (1.70) |
| right/left | p | 0.846 | 25/25 | 0 | 24 | 1.60 ± 0.33 (1.58) | 5.28 ± 3.91 (4.30) | 1.87 ± 0.24 (1.94) | 4.20 ± 0.71 (4.47) | 1.45 ± 0.35 (1.42) |
| right/right | p | 0.830 | 25/25 | 0 | 25 | 1.40 ± 0.35 (1.42) | 6.51 ± 3.79 (6.46) | 1.76 ± 0.28 (1.72) | 3.88 ± 0.71 (3.84) | 1.31 ± 0.39 (1.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.853 | 5.6 | 4.26 | 1.49 |
| p | normal | 0.834 | 6.8 | 3.46 | 1.10 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.801 | 0.30 | 1.94 ± 0.69 (1.76) | 3.08 | 0.92 |
| p | medium | 16 | 0.910 | 0.84 | 0.99 ± 0.19 (1.01) | 3.21 | 0.98 |
| p | strong | 126 | 0.855 | 0.57 | - | 4.30 | 1.51 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector back (0.829).
