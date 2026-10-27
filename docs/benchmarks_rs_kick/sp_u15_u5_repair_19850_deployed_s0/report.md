# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-26-24_u15_u5_repair/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.806** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.89 ± 1.31 (1.70) |
| Direction error [°] | 18.58 ± 38.35 (5.16) |
| Avg ball speed [m/s] | 2.34 ± 0.86 (2.67) |
| Peak ball speed [m/s] | 4.91 ± 1.88 (5.80) |
| Distance [m] | 2.40 ± 1.21 (2.78) |
| Path length [m] | 2.41 ± 1.22 (2.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.809 | 50/50 | 0 | 42 | 1.61 ± 1.71 (1.31) | 8.90 ± 12.86 (4.27) | 2.28 ± 0.74 (2.24) | 4.73 ± 1.64 (4.33) | 2.23 ± 1.07 (1.91) |
| left | p | 0.833 | 49/50 | 0 | 42 | 1.67 ± 0.45 (1.78) | 14.49 ± 30.05 (5.68) | 2.43 ± 0.78 (2.73) | 5.14 ± 1.74 (6.05) | 2.54 ± 1.13 (3.01) |
| back | p | 0.765 | 50/50 | 0 | 37 | 2.45 ± 1.28 (2.44) | 34.51 ± 58.60 (7.59) | 2.32 ± 1.06 (2.80) | 4.88 ± 2.28 (6.21) | 2.49 ± 1.45 (3.30) |
| right | p | 0.818 | 50/50 | 0 | 42 | 1.84 ± 1.27 (1.73) | 16.35 ± 31.61 (4.88) | 2.34 ± 0.82 (2.61) | 4.89 ± 1.75 (5.79) | 2.34 ± 1.13 (2.69) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.828 | 100/100 | 0 | 86 | 1.72 ± 0.58 (1.69) | 17.18 ± 37.64 (5.72) | 2.41 ± 0.81 (2.67) | 5.04 ± 1.78 (5.83) | 2.47 ± 1.18 (2.81) |
| right | p | 0.785 | 99/100 | 0 | 77 | 2.06 ± 1.75 (1.76) | 20.00 ± 39.00 (4.69) | 2.28 ± 0.91 (2.62) | 4.78 ± 1.96 (5.74) | 2.32 ± 1.24 (2.71) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.843 | 25/25 | 0 | 22 | 1.28 ± 0.29 (1.28) | 7.87 ± 13.05 (3.94) | 2.33 ± 0.76 (2.31) | 4.85 ± 1.69 (4.47) | 2.31 ± 1.09 (2.00) |
| forward/right | p | 0.776 | 25/25 | 0 | 20 | 1.93 ± 2.36 (1.32) | 9.93 ± 12.58 (5.44) | 2.24 ± 0.72 (2.21) | 4.62 ± 1.57 (4.31) | 2.14 ± 1.05 (1.86) |
| left/left | p | 0.860 | 25/25 | 0 | 23 | 1.59 ± 0.37 (1.66) | 9.84 ± 16.48 (6.00) | 2.48 ± 0.73 (2.73) | 5.20 ± 1.68 (6.05) | 2.58 ± 1.07 (3.04) |
| left/right | p | 0.806 | 24/25 | 0 | 19 | 1.76 ± 0.51 (1.86) | 19.33 ± 38.91 (3.48) | 2.39 ± 0.83 (2.72) | 5.08 ± 1.81 (5.98) | 2.49 ± 1.20 (2.94) |
| back/left | p | 0.790 | 25/25 | 0 | 19 | 2.27 ± 0.64 (2.50) | 31.78 ± 58.45 (7.26) | 2.45 ± 0.96 (2.81) | 5.15 ± 2.08 (6.28) | 2.65 ± 1.42 (3.35) |
| back/right | p | 0.740 | 25/25 | 0 | 18 | 2.63 ± 1.68 (2.36) | 37.25 ± 58.63 (7.94) | 2.19 ± 1.14 (2.78) | 4.60 ± 2.44 (6.14) | 2.34 ± 1.47 (3.19) |
| right/left | p | 0.818 | 25/25 | 0 | 22 | 1.75 ± 0.45 (1.76) | 19.22 ± 38.08 (5.67) | 2.37 ± 0.74 (2.38) | 4.94 ± 1.60 (5.28) | 2.35 ± 1.05 (2.59) |
| right/right | p | 0.818 | 25/25 | 0 | 20 | 1.93 ± 1.73 (1.70) | 13.47 ± 23.06 (3.97) | 2.31 ± 0.89 (2.77) | 4.83 ± 1.88 (5.89) | 2.33 ± 1.20 (2.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.851 | 16.9 | 5.74 | 3.00 |
| p | normal | 0.762 | 20.2 | 4.07 | 1.79 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.15 | 2.29 ± 1.12 (2.16) | 3.50 | 1.39 |
| p | medium | 16 | 0.815 | 0.71 | 1.26 ± 0.21 (1.25) | 4.06 | 1.68 |
| p | strong | 126 | 0.846 | 0.75 | - | 5.66 | 2.95 |

## Notes

- p: score 0.806, 199/200 kicked, 0 fell; worst sector back (0.765).
