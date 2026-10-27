# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_05-06-31_u4c_u4b_lowcap03/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 184 |
| Weak kicks (< 0.3 m) | 8 |
| Time to kick [s] | 1.78 ± 0.53 (1.68) |
| Direction error [°] | 9.90 ± 20.46 (6.48) |
| Avg ball speed [m/s] | 2.73 ± 0.75 (3.02) |
| Peak ball speed [m/s] | 5.50 ± 1.58 (6.26) |
| Distance [m] | 2.81 ± 1.08 (3.25) |
| Path length [m] | 2.82 ± 1.08 (3.27) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.856 | 50/50 | 0 | 48 | 1.28 ± 0.22 (1.32) | 6.30 ± 8.28 (4.80) | 2.51 ± 0.83 (2.80) | 5.16 ± 1.80 (5.92) | 2.56 ± 1.18 (3.02) |
| left | p | 0.867 | 50/50 | 0 | 47 | 1.70 ± 0.35 (1.66) | 7.48 ± 4.67 (7.05) | 2.89 ± 0.50 (3.04) | 5.83 ± 1.10 (6.28) | 3.00 ± 0.88 (3.31) |
| back | p | 0.791 | 50/50 | 0 | 43 | 2.42 ± 0.41 (2.42) | 19.21 ± 37.94 (8.40) | 2.70 ± 0.97 (3.14) | 5.42 ± 1.98 (6.42) | 2.85 ± 1.25 (3.48) |
| right | p | 0.847 | 50/50 | 0 | 46 | 1.72 ± 0.33 (1.69) | 6.60 ± 5.33 (5.78) | 2.81 ± 0.55 (3.02) | 5.61 ± 1.18 (6.25) | 2.82 ± 0.92 (3.22) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.839 | 100/100 | 0 | 91 | 1.76 ± 0.53 (1.66) | 11.77 ± 25.48 (7.04) | 2.72 ± 0.78 (3.03) | 5.48 ± 1.64 (6.31) | 2.81 ± 1.10 (3.32) |
| right | p | 0.842 | 100/100 | 0 | 93 | 1.80 ± 0.52 (1.69) | 8.03 ± 13.46 (5.84) | 2.74 ± 0.71 (3.00) | 5.53 ± 1.52 (6.23) | 2.81 ± 1.06 (3.24) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 23 | 1.28 ± 0.21 (1.32) | 8.23 ± 10.80 (6.12) | 2.51 ± 0.87 (2.82) | 5.14 ± 1.89 (6.02) | 2.57 ± 1.20 (3.10) |
| forward/right | p | 0.866 | 25/25 | 0 | 25 | 1.28 ± 0.24 (1.34) | 4.38 ± 3.61 (3.14) | 2.51 ± 0.78 (2.65) | 5.17 ± 1.72 (5.78) | 2.56 ± 1.16 (2.77) |
| left/left | p | 0.871 | 25/25 | 0 | 24 | 1.59 ± 0.34 (1.62) | 6.44 ± 4.31 (5.82) | 2.81 ± 0.47 (3.03) | 5.60 ± 1.06 (5.93) | 2.83 ± 0.84 (3.19) |
| left/right | p | 0.863 | 25/25 | 0 | 23 | 1.82 ± 0.32 (1.82) | 8.53 ± 4.78 (8.85) | 2.98 ± 0.50 (3.15) | 6.05 ± 1.10 (6.59) | 3.17 ± 0.88 (3.52) |
| back/left | p | 0.790 | 25/25 | 0 | 21 | 2.36 ± 0.50 (2.34) | 25.16 ± 46.82 (8.74) | 2.68 ± 1.03 (3.12) | 5.41 ± 2.10 (6.43) | 2.88 ± 1.32 (3.58) |
| back/right | p | 0.793 | 25/25 | 0 | 22 | 2.47 ± 0.28 (2.46) | 13.27 ± 24.84 (7.38) | 2.73 ± 0.90 (3.14) | 5.42 ± 1.85 (6.36) | 2.82 ± 1.17 (3.42) |
| right/left | p | 0.849 | 25/25 | 0 | 23 | 1.82 ± 0.33 (1.78) | 7.25 ± 5.37 (7.45) | 2.88 ± 0.58 (3.15) | 5.76 ± 1.22 (6.43) | 2.95 ± 0.95 (3.48) |
| right/right | p | 0.845 | 25/25 | 0 | 23 | 1.62 ± 0.29 (1.60) | 5.95 ± 5.20 (3.49) | 2.73 ± 0.51 (2.89) | 5.46 ± 1.11 (5.96) | 2.70 ± 0.88 (2.98) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 7.8 | 6.54 | 3.56 |
| p | normal | 0.795 | 12.0 | 4.47 | 2.06 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.744 | 0.08 | 2.32 ± 1.10 (2.23) | 3.66 | 1.48 |
| p | medium | 16 | 0.873 | 0.66 | 1.22 ± 0.34 (1.28) | 3.96 | 1.63 |
| p | strong | 126 | 0.880 | 0.87 | - | 6.55 | 3.57 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector back (0.791).
