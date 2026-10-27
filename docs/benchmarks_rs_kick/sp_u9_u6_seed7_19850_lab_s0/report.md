# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u9_u6_seed7/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.55 ± 0.50 (1.46) |
| Direction error [°] | 6.36 ± 12.55 (4.90) |
| Avg ball speed [m/s] | 1.86 ± 0.41 (1.87) |
| Peak ball speed [m/s] | 4.05 ± 0.97 (4.02) |
| Distance [m] | 1.45 ± 0.55 (1.42) |
| Path length [m] | 1.45 ± 0.56 (1.43) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 49 | 1.04 ± 0.22 (1.06) | 5.15 ± 3.66 (4.21) | 1.69 ± 0.43 (1.59) | 3.61 ± 0.95 (3.37) | 1.19 ± 0.55 (1.04) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.49) | 5.52 ± 3.66 (5.35) | 1.90 ± 0.38 (2.02) | 4.17 ± 0.89 (4.33) | 1.50 ± 0.53 (1.54) |
| back | p | 0.839 | 50/50 | 0 | 49 | 2.18 ± 0.24 (2.14) | 9.26 ± 23.99 (6.24) | 2.02 ± 0.41 (2.18) | 4.40 ± 1.01 (4.86) | 1.68 ± 0.54 (1.83) |
| right | p | 0.844 | 50/50 | 0 | 49 | 1.50 ± 0.32 (1.45) | 5.52 ± 4.00 (4.29) | 1.85 ± 0.35 (1.86) | 4.02 ± 0.87 (3.90) | 1.42 ± 0.47 (1.42) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 99 | 1.55 ± 0.49 (1.49) | 7.45 ± 17.29 (5.90) | 1.86 ± 0.43 (1.98) | 4.06 ± 1.01 (4.18) | 1.46 ± 0.56 (1.50) |
| right | p | 0.853 | 100/100 | 0 | 98 | 1.56 ± 0.50 (1.46) | 5.28 ± 3.67 (4.40) | 1.87 ± 0.39 (1.82) | 4.05 ± 0.94 (3.93) | 1.43 ± 0.54 (1.33) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 25 | 1.04 ± 0.21 (1.06) | 5.44 ± 3.51 (4.44) | 1.69 ± 0.43 (1.51) | 3.62 ± 0.93 (3.10) | 1.20 ± 0.57 (0.91) |
| forward/right | p | 0.857 | 25/25 | 0 | 24 | 1.04 ± 0.24 (1.06) | 4.85 ± 3.79 (3.81) | 1.70 ± 0.44 (1.71) | 3.61 ± 0.96 (3.45) | 1.17 ± 0.53 (1.07) |
| left/left | p | 0.851 | 25/25 | 0 | 25 | 1.39 ± 0.32 (1.44) | 6.21 ± 4.06 (5.87) | 1.88 ± 0.42 (2.09) | 4.11 ± 0.95 (4.44) | 1.47 ± 0.56 (1.64) |
| left/right | p | 0.869 | 25/25 | 0 | 25 | 1.60 ± 0.30 (1.58) | 4.83 ± 3.05 (4.48) | 1.92 ± 0.33 (1.88) | 4.24 ± 0.81 (4.19) | 1.52 ± 0.51 (1.53) |
| back/left | p | 0.829 | 25/25 | 0 | 24 | 2.17 ± 0.25 (2.12) | 12.69 ± 33.45 (6.81) | 1.97 ± 0.45 (2.05) | 4.30 ± 1.09 (4.43) | 1.64 ± 0.55 (1.78) |
| back/right | p | 0.849 | 25/25 | 0 | 25 | 2.18 ± 0.24 (2.20) | 5.84 ± 2.93 (5.70) | 2.06 ± 0.35 (2.21) | 4.50 ± 0.91 (4.97) | 1.72 ± 0.54 (1.89) |
| right/left | p | 0.854 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.56) | 5.44 ± 3.35 (4.94) | 1.91 ± 0.36 (2.00) | 4.19 ± 0.90 (4.47) | 1.51 ± 0.48 (1.55) |
| right/right | p | 0.835 | 25/25 | 0 | 24 | 1.40 ± 0.32 (1.44) | 5.61 ± 4.55 (2.99) | 1.79 ± 0.33 (1.72) | 3.85 ± 0.81 (3.59) | 1.32 ± 0.43 (1.20) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.865 | 5.5 | 4.63 | 1.75 |
| p | normal | 0.832 | 7.2 | 3.48 | 1.14 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.802 | 0.29 | 1.94 ± 0.71 (1.84) | 3.04 | 0.91 |
| p | medium | 16 | 0.893 | 0.82 | 1.01 ± 0.21 (1.09) | 3.26 | 1.03 |
| p | strong | 126 | 0.865 | 0.62 | - | 4.62 | 1.74 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector back (0.839).
