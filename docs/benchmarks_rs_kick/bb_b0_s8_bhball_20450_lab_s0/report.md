# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 191 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.60 ± 0.58 (1.51) |
| Direction error [°] | 8.08 ± 22.30 (4.41) |
| Avg ball speed [m/s] | 1.83 ± 0.34 (1.83) |
| Peak ball speed [m/s] | 4.63 ± 0.82 (4.76) |
| Distance [m] | 1.92 ± 0.53 (1.82) |
| Path length [m] | 1.93 ± 0.54 (1.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.802 | 50/50 | 0 | 45 | 1.25 ± 0.76 (1.09) | 14.60 ± 36.91 (4.79) | 1.63 ± 0.32 (1.58) | 4.19 ± 0.72 (4.05) | 1.58 ± 0.44 (1.53) |
| left | p | 0.873 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.51) | 4.96 ± 3.29 (4.52) | 1.92 ± 0.32 (1.91) | 4.87 ± 0.75 (5.05) | 2.08 ± 0.51 (2.04) |
| back | p | 0.858 | 50/50 | 0 | 48 | 2.18 ± 0.25 (2.14) | 7.11 ± 23.17 (2.63) | 1.95 ± 0.35 (1.98) | 4.85 ± 0.91 (5.16) | 2.11 ± 0.55 (2.23) |
| right | p | 0.838 | 50/50 | 0 | 48 | 1.48 ± 0.33 (1.44) | 5.66 ± 4.54 (4.87) | 1.84 ± 0.29 (1.82) | 4.60 ± 0.70 (4.36) | 1.90 ± 0.45 (1.78) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 97 | 1.63 ± 0.61 (1.52) | 7.63 ± 20.72 (4.66) | 1.85 ± 0.30 (1.85) | 4.68 ± 0.71 (4.80) | 1.94 ± 0.49 (1.89) |
| right | p | 0.841 | 100/100 | 0 | 94 | 1.57 ± 0.55 (1.47) | 8.54 ± 23.78 (4.24) | 1.82 ± 0.38 (1.78) | 4.58 ± 0.91 (4.54) | 1.90 ± 0.58 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.798 | 25/25 | 0 | 23 | 1.34 ± 0.86 (1.12) | 16.56 ± 39.70 (4.88) | 1.64 ± 0.28 (1.62) | 4.29 ± 0.58 (4.05) | 1.63 ± 0.40 (1.54) |
| forward/right | p | 0.807 | 25/25 | 0 | 22 | 1.15 ± 0.64 (1.06) | 12.65 ± 33.79 (4.61) | 1.61 ± 0.35 (1.57) | 4.09 ± 0.83 (4.03) | 1.53 ± 0.47 (1.52) |
| left/left | p | 0.869 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.46) | 5.13 ± 3.75 (4.72) | 1.88 ± 0.31 (1.88) | 4.77 ± 0.76 (4.93) | 1.99 ± 0.50 (1.95) |
| left/right | p | 0.877 | 25/25 | 0 | 25 | 1.60 ± 0.29 (1.58) | 4.79 ± 2.75 (4.31) | 1.96 ± 0.32 (1.94) | 4.98 ± 0.72 (5.15) | 2.17 ± 0.51 (2.14) |
| back/left | p | 0.860 | 25/25 | 0 | 25 | 2.22 ± 0.25 (2.14) | 3.79 ± 2.62 (2.99) | 1.95 ± 0.22 (1.96) | 4.89 ± 0.62 (5.11) | 2.11 ± 0.46 (2.20) |
| back/right | p | 0.856 | 25/25 | 0 | 23 | 2.15 ± 0.25 (2.10) | 10.43 ± 32.32 (2.58) | 1.96 ± 0.44 (2.04) | 4.81 ± 1.12 (5.23) | 2.12 ± 0.63 (2.33) |
| right/left | p | 0.851 | 25/25 | 0 | 24 | 1.57 ± 0.30 (1.58) | 5.03 ± 3.57 (4.68) | 1.91 ± 0.29 (1.89) | 4.77 ± 0.70 (5.07) | 2.02 ± 0.43 (2.07) |
| right/right | p | 0.825 | 25/25 | 0 | 24 | 1.39 ± 0.33 (1.40) | 6.28 ± 5.26 (5.09) | 1.77 ± 0.27 (1.71) | 4.44 ± 0.65 (4.26) | 1.79 ± 0.43 (1.64) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.881 | 5.0 | 5.05 | 2.15 |
| p | normal | 0.805 | 11.2 | 4.21 | 1.68 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.745 | 0.10 | 2.40 ± 0.80 (2.21) | 3.81 | 1.44 |
| p | medium | 16 | 0.881 | 0.78 | 1.22 ± 0.14 (1.23) | 3.95 | 1.52 |
| p | strong | 126 | 0.883 | 0.68 | - | 5.09 | 2.19 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector forward (0.802).
