# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-01-05_u12_u6_seed23/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.55 ± 0.52 (1.48) |
| Direction error [°] | 5.62 ± 3.63 (5.23) |
| Avg ball speed [m/s] | 1.83 ± 0.38 (1.94) |
| Peak ball speed [m/s] | 3.96 ± 0.85 (4.19) |
| Distance [m] | 1.39 ± 0.49 (1.42) |
| Path length [m] | 1.40 ± 0.49 (1.43) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.856 | 50/50 | 0 | 49 | 1.02 ± 0.23 (1.04) | 4.58 ± 3.41 (3.56) | 1.58 ± 0.44 (1.73) | 3.39 ± 0.90 (3.51) | 1.06 ± 0.49 (1.10) |
| left | p | 0.861 | 50/50 | 0 | 50 | 1.49 ± 0.32 (1.51) | 5.53 ± 4.02 (4.56) | 1.90 ± 0.33 (1.96) | 4.14 ± 0.78 (4.45) | 1.48 ± 0.47 (1.54) |
| back | p | 0.828 | 50/50 | 0 | 49 | 2.22 ± 0.26 (2.18) | 6.56 ± 3.00 (6.63) | 2.01 ± 0.25 (2.07) | 4.35 ± 0.64 (4.57) | 1.64 ± 0.39 (1.74) |
| right | p | 0.840 | 50/50 | 0 | 49 | 1.47 ± 0.33 (1.46) | 5.82 ± 3.72 (5.63) | 1.83 ± 0.31 (1.93) | 3.97 ± 0.75 (4.27) | 1.38 ± 0.41 (1.40) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.842 | 100/100 | 0 | 99 | 1.55 ± 0.52 (1.51) | 5.70 ± 3.62 (5.25) | 1.84 ± 0.34 (1.93) | 3.97 ± 0.79 (4.09) | 1.39 ± 0.47 (1.39) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.54 ± 0.52 (1.47) | 5.55 ± 3.64 (5.18) | 1.82 ± 0.41 (1.96) | 3.96 ± 0.91 (4.27) | 1.39 ± 0.51 (1.49) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 24 | 1.03 ± 0.23 (1.06) | 5.02 ± 3.61 (3.74) | 1.65 ± 0.35 (1.80) | 3.50 ± 0.74 (3.75) | 1.12 ± 0.43 (1.25) |
| forward/right | p | 0.867 | 25/25 | 0 | 25 | 1.00 ± 0.23 (1.04) | 4.13 ± 3.14 (3.13) | 1.51 ± 0.51 (1.61) | 3.27 ± 1.02 (3.33) | 1.00 ± 0.54 (1.07) |
| left/left | p | 0.848 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.46) | 6.01 ± 4.41 (4.86) | 1.81 ± 0.34 (1.89) | 3.92 ± 0.78 (4.05) | 1.36 ± 0.45 (1.35) |
| left/right | p | 0.874 | 25/25 | 0 | 25 | 1.58 ± 0.29 (1.58) | 5.05 ± 3.53 (4.26) | 1.99 ± 0.31 (2.04) | 4.36 ± 0.72 (4.58) | 1.61 ± 0.44 (1.63) |
| back/left | p | 0.827 | 25/25 | 0 | 25 | 2.23 ± 0.24 (2.16) | 6.63 ± 2.91 (7.47) | 2.01 ± 0.24 (2.07) | 4.33 ± 0.64 (4.56) | 1.64 ± 0.42 (1.74) |
| back/right | p | 0.830 | 25/25 | 0 | 24 | 2.21 ± 0.28 (2.20) | 6.49 ± 3.08 (6.61) | 2.02 ± 0.26 (2.07) | 4.37 ± 0.64 (4.62) | 1.65 ± 0.37 (1.70) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.56 ± 0.30 (1.54) | 5.13 ± 3.13 (5.17) | 1.89 ± 0.29 (2.00) | 4.12 ± 0.75 (4.41) | 1.46 ± 0.41 (1.51) |
| right/right | p | 0.831 | 25/25 | 0 | 24 | 1.38 ± 0.34 (1.40) | 6.51 ± 4.12 (5.80) | 1.78 ± 0.32 (1.92) | 3.82 ± 0.73 (4.16) | 1.31 ± 0.39 (1.31) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.858 | 5.7 | 4.45 | 1.65 |
| p | normal | 0.835 | 5.5 | 3.47 | 1.14 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.803 | 0.30 | 1.93 ± 0.65 (1.77) | 3.09 | 0.94 |
| p | medium | 16 | 0.896 | 0.82 | 0.94 ± 0.21 (0.97) | 3.04 | 0.87 |
| p | strong | 126 | 0.860 | 0.60 | - | 4.48 | 1.67 |

## Notes

- p: score 0.846, 200/200 kicked, 0 fell; worst sector back (0.828).
