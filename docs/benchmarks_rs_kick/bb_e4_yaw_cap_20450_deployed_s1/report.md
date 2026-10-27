# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-47-18_e4_yaw_cap/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.81 ± 0.57 (1.68) |
| Direction error [°] | 6.51 ± 4.81 (5.67) |
| Avg ball speed [m/s] | 2.65 ± 0.45 (2.72) |
| Peak ball speed [m/s] | 5.55 ± 1.09 (6.01) |
| Distance [m] | 2.75 ± 0.81 (3.05) |
| Path length [m] | 2.76 ± 0.81 (3.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.872 | 50/50 | 0 | 49 | 1.24 ± 0.25 (1.25) | 5.05 ± 3.99 (3.36) | 2.60 ± 0.42 (2.65) | 5.51 ± 1.03 (5.88) | 2.67 ± 0.75 (2.93) |
| left | p | 0.859 | 50/50 | 0 | 49 | 1.74 ± 0.35 (1.69) | 6.58 ± 6.35 (4.93) | 2.61 ± 0.54 (2.72) | 5.44 ± 1.27 (6.01) | 2.69 ± 0.90 (3.04) |
| back | p | 0.809 | 50/50 | 0 | 48 | 2.55 ± 0.33 (2.53) | 7.39 ± 3.68 (7.89) | 2.81 ± 0.39 (2.89) | 5.84 ± 0.97 (6.30) | 3.01 ± 0.76 (3.36) |
| right | p | 0.837 | 50/50 | 0 | 48 | 1.70 ± 0.35 (1.66) | 7.01 ± 4.41 (6.79) | 2.59 ± 0.37 (2.61) | 5.40 ± 0.99 (5.88) | 2.64 ± 0.76 (2.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 97 | 1.80 ± 0.57 (1.67) | 6.45 ± 5.47 (5.08) | 2.65 ± 0.46 (2.72) | 5.55 ± 1.10 (6.08) | 2.77 ± 0.80 (3.11) |
| right | p | 0.846 | 100/100 | 0 | 97 | 1.81 ± 0.57 (1.68) | 6.56 ± 4.04 (6.04) | 2.66 ± 0.42 (2.65) | 5.54 ± 1.07 (5.96) | 2.74 ± 0.82 (2.99) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.866 | 25/25 | 0 | 24 | 1.21 ± 0.25 (1.24) | 5.01 ± 4.56 (3.04) | 2.54 ± 0.36 (2.54) | 5.43 ± 0.94 (5.78) | 2.60 ± 0.65 (2.84) |
| forward/right | p | 0.879 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.30) | 5.08 ± 3.32 (4.39) | 2.65 ± 0.47 (2.66) | 5.59 ± 1.12 (5.95) | 2.74 ± 0.84 (2.98) |
| left/left | p | 0.848 | 25/25 | 0 | 24 | 1.66 ± 0.35 (1.56) | 7.98 ± 8.28 (6.11) | 2.61 ± 0.64 (2.72) | 5.43 ± 1.43 (6.03) | 2.72 ± 0.95 (3.13) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.81 ± 0.35 (1.80) | 5.17 ± 2.85 (4.42) | 2.62 ± 0.41 (2.70) | 5.44 ± 1.09 (6.00) | 2.66 ± 0.84 (3.00) |
| back/left | p | 0.814 | 25/25 | 0 | 24 | 2.54 ± 0.29 (2.54) | 6.95 ± 3.38 (7.67) | 2.83 ± 0.41 (2.89) | 5.89 ± 0.96 (6.30) | 3.06 ± 0.77 (3.38) |
| back/right | p | 0.804 | 25/25 | 0 | 24 | 2.56 ± 0.36 (2.48) | 7.84 ± 3.91 (8.28) | 2.79 ± 0.37 (2.90) | 5.80 ± 0.98 (6.31) | 2.97 ± 0.76 (3.35) |
| right/left | p | 0.843 | 25/25 | 0 | 25 | 1.80 ± 0.36 (1.76) | 5.86 ± 3.71 (5.01) | 2.61 ± 0.33 (2.71) | 5.47 ± 0.93 (5.99) | 2.69 ± 0.71 (2.98) |
| right/right | p | 0.832 | 25/25 | 0 | 23 | 1.61 ± 0.31 (1.58) | 8.15 ± 4.74 (7.54) | 2.57 ± 0.41 (2.55) | 5.33 ± 1.04 (5.62) | 2.59 ± 0.80 (2.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.889 | 6.5 | 6.27 | 3.29 |
| p | normal | 0.800 | 6.5 | 4.83 | 2.21 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.738 | 0.05 | 2.77 ± 0.86 (2.57) | 4.32 | 1.82 |
| p | medium | 20 | 0.856 | 0.67 | 1.33 ± 0.16 (1.36) | 4.26 | 1.80 |
| p | strong | 126 | 0.888 | 0.84 | - | 6.28 | 3.30 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector back (0.809).
