# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.66 ± 0.57 (1.58) |
| Direction error [°] | 5.23 ± 12.07 (3.09) |
| Avg ball speed [m/s] | 1.73 ± 0.29 (1.70) |
| Peak ball speed [m/s] | 4.07 ± 0.73 (4.02) |
| Distance [m] | 1.51 ± 0.43 (1.45) |
| Path length [m] | 1.51 ± 0.43 (1.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.844 | 50/50 | 0 | 49 | 1.16 ± 0.48 (1.10) | 5.22 ± 4.11 (3.93) | 1.59 ± 0.27 (1.57) | 3.78 ± 0.66 (3.66) | 1.31 ± 0.40 (1.24) |
| left | p | 0.852 | 50/50 | 0 | 50 | 1.55 ± 0.33 (1.54) | 4.92 ± 3.50 (4.16) | 1.77 ± 0.26 (1.78) | 4.15 ± 0.66 (4.28) | 1.57 ± 0.40 (1.49) |
| back | p | 0.846 | 50/50 | 0 | 49 | 2.34 ± 0.35 (2.33) | 6.32 ± 23.29 (2.29) | 1.81 ± 0.34 (1.82) | 4.25 ± 0.84 (4.48) | 1.63 ± 0.45 (1.65) |
| right | p | 0.845 | 50/50 | 0 | 50 | 1.59 ± 0.37 (1.60) | 4.45 ± 3.09 (3.66) | 1.74 ± 0.24 (1.73) | 4.08 ± 0.64 (4.13) | 1.52 ± 0.38 (1.49) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 100 | 1.66 ± 0.58 (1.58) | 4.58 ± 3.05 (3.36) | 1.73 ± 0.28 (1.72) | 4.08 ± 0.69 (4.03) | 1.51 ± 0.43 (1.43) |
| right | p | 0.846 | 100/100 | 0 | 98 | 1.66 ± 0.57 (1.58) | 5.87 ± 16.77 (3.02) | 1.72 ± 0.31 (1.69) | 4.05 ± 0.77 (3.99) | 1.50 ± 0.42 (1.45) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.851 | 25/25 | 0 | 25 | 1.18 ± 0.54 (1.06) | 4.47 ± 3.09 (3.43) | 1.59 ± 0.27 (1.57) | 3.80 ± 0.69 (3.58) | 1.30 ± 0.42 (1.16) |
| forward/right | p | 0.838 | 25/25 | 0 | 24 | 1.14 ± 0.41 (1.14) | 5.97 ± 4.82 (3.96) | 1.58 ± 0.26 (1.62) | 3.76 ± 0.63 (3.70) | 1.31 ± 0.38 (1.28) |
| left/left | p | 0.844 | 25/25 | 0 | 25 | 1.46 ± 0.30 (1.50) | 5.71 ± 3.26 (5.33) | 1.76 ± 0.28 (1.78) | 4.14 ± 0.68 (4.04) | 1.56 ± 0.42 (1.40) |
| left/right | p | 0.860 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.64) | 4.13 ± 3.56 (2.57) | 1.78 ± 0.25 (1.81) | 4.17 ± 0.65 (4.33) | 1.58 ± 0.39 (1.65) |
| back/left | p | 0.858 | 25/25 | 0 | 25 | 2.36 ± 0.34 (2.32) | 2.98 ± 1.67 (2.41) | 1.85 ± 0.27 (1.81) | 4.30 ± 0.63 (4.27) | 1.64 ± 0.40 (1.66) |
| back/right | p | 0.833 | 25/25 | 0 | 24 | 2.32 ± 0.35 (2.40) | 9.66 ± 32.55 (2.17) | 1.78 ± 0.40 (1.86) | 4.21 ± 1.01 (4.66) | 1.62 ± 0.49 (1.65) |
| right/left | p | 0.836 | 25/25 | 0 | 25 | 1.64 ± 0.28 (1.68) | 5.16 ± 3.19 (4.68) | 1.74 ± 0.25 (1.77) | 4.10 ± 0.66 (4.20) | 1.55 ± 0.41 (1.60) |
| right/right | p | 0.854 | 25/25 | 0 | 25 | 1.55 ± 0.43 (1.54) | 3.73 ± 2.81 (3.13) | 1.73 ± 0.24 (1.69) | 4.05 ± 0.62 (4.09) | 1.49 ± 0.33 (1.46) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.862 | 4.6 | 4.48 | 1.72 |
| p | normal | 0.832 | 5.8 | 3.65 | 1.29 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.791 | 0.20 | 2.11 ± 0.67 (2.08) | 3.34 | 1.12 |
| p | medium | 18 | 0.911 | 0.85 | 1.08 ± 0.15 (1.12) | 3.46 | 1.17 |
| p | strong | 124 | 0.863 | 0.60 | - | 4.49 | 1.74 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector forward (0.844).
