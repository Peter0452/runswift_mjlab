# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 185 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.76 ± 0.57 (1.71) |
| Direction error [°] | 8.25 ± 13.35 (6.93) |
| Avg ball speed [m/s] | 2.75 ± 0.62 (2.93) |
| Peak ball speed [m/s] | 5.75 ± 1.42 (6.42) |
| Distance [m] | 2.94 ± 1.09 (3.30) |
| Path length [m] | 2.95 ± 1.09 (3.32) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.879 | 50/50 | 0 | 48 | 1.20 ± 0.26 (1.23) | 4.92 ± 3.86 (4.11) | 2.59 ± 0.51 (2.72) | 5.51 ± 1.27 (6.01) | 2.68 ± 0.95 (2.90) |
| left | p | 0.856 | 50/50 | 0 | 46 | 1.71 ± 0.35 (1.73) | 7.68 ± 4.83 (7.25) | 2.80 ± 0.55 (2.96) | 5.83 ± 1.27 (6.48) | 3.00 ± 1.03 (3.37) |
| back | p | 0.804 | 50/50 | 0 | 43 | 2.45 ± 0.41 (2.37) | 13.43 ± 24.83 (9.33) | 2.89 ± 0.81 (3.29) | 6.00 ± 1.73 (6.94) | 3.23 ± 1.21 (3.86) |
| right | p | 0.846 | 50/50 | 0 | 48 | 1.70 ± 0.36 (1.71) | 6.97 ± 4.32 (6.82) | 2.73 ± 0.55 (2.87) | 5.65 ± 1.31 (6.32) | 2.84 ± 1.06 (3.31) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 94 | 1.76 ± 0.56 (1.70) | 6.77 ± 4.39 (6.54) | 2.76 ± 0.56 (2.89) | 5.79 ± 1.28 (6.39) | 2.95 ± 1.03 (3.28) |
| right | p | 0.843 | 100/100 | 0 | 91 | 1.76 ± 0.58 (1.74) | 9.73 ± 18.25 (7.15) | 2.74 ± 0.68 (2.95) | 5.70 ± 1.55 (6.47) | 2.92 ± 1.14 (3.44) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.885 | 25/25 | 0 | 25 | 1.18 ± 0.26 (1.22) | 3.59 ± 2.63 (3.30) | 2.51 ± 0.45 (2.62) | 5.38 ± 1.18 (5.83) | 2.56 ± 0.86 (2.89) |
| forward/right | p | 0.873 | 25/25 | 0 | 23 | 1.22 ± 0.26 (1.24) | 6.26 ± 4.39 (5.41) | 2.67 ± 0.55 (2.81) | 5.63 ± 1.34 (6.33) | 2.79 ± 1.01 (3.13) |
| left/left | p | 0.861 | 25/25 | 0 | 23 | 1.64 ± 0.34 (1.62) | 7.74 ± 4.39 (7.92) | 2.86 ± 0.53 (3.12) | 5.98 ± 1.23 (6.60) | 3.12 ± 1.00 (3.50) |
| left/right | p | 0.851 | 25/25 | 0 | 23 | 1.78 ± 0.36 (1.84) | 7.61 ± 5.23 (6.77) | 2.75 ± 0.56 (2.88) | 5.68 ± 1.30 (6.34) | 2.87 ± 1.05 (3.26) |
| back/left | p | 0.816 | 25/25 | 0 | 22 | 2.46 ± 0.27 (2.38) | 9.06 ± 4.02 (8.25) | 2.99 ± 0.60 (3.30) | 6.21 ± 1.31 (7.00) | 3.34 ± 1.07 (3.86) |
| back/right | p | 0.792 | 25/25 | 0 | 21 | 2.43 ± 0.51 (2.34) | 17.81 ± 34.33 (9.89) | 2.79 ± 0.96 (3.28) | 5.80 ± 2.06 (6.92) | 3.13 ± 1.33 (3.85) |
| right/left | p | 0.839 | 25/25 | 0 | 24 | 1.77 ± 0.36 (1.80) | 6.71 ± 4.28 (5.70) | 2.70 ± 0.52 (2.81) | 5.60 ± 1.23 (6.25) | 2.77 ± 0.98 (2.99) |
| right/right | p | 0.854 | 25/25 | 0 | 24 | 1.62 ± 0.34 (1.62) | 7.22 ± 4.33 (7.84) | 2.77 ± 0.57 (2.99) | 5.70 ± 1.39 (6.54) | 2.90 ± 1.13 (3.58) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.890 | 7.7 | 6.74 | 3.69 |
| p | normal | 0.803 | 8.8 | 4.75 | 2.18 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.739 | 0.07 | 2.62 ± 0.89 (2.56) | 4.06 | 1.63 |
| p | medium | 20 | 0.857 | 0.66 | 1.24 ± 0.32 (1.27) | 3.95 | 1.61 |
| p | strong | 126 | 0.891 | 0.90 | - | 6.75 | 3.71 |

## Notes

- p: score 0.846, 200/200 kicked, 0 fell; worst sector back (0.804).
