# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u5_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.53 (1.50) |
| Direction error [°] | 5.35 ± 12.44 (3.83) |
| Avg ball speed [m/s] | 2.16 ± 0.36 (2.14) |
| Peak ball speed [m/s] | 4.63 ± 0.85 (4.70) |
| Distance [m] | 1.99 ± 0.58 (2.01) |
| Path length [m] | 2.00 ± 0.58 (2.02) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.854 | 50/50 | 0 | 50 | 1.02 ± 0.21 (1.02) | 4.72 ± 3.42 (4.08) | 1.99 ± 0.31 (1.97) | 4.29 ± 0.74 (4.05) | 1.75 ± 0.53 (1.57) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.51 ± 0.32 (1.50) | 4.61 ± 3.39 (3.67) | 2.21 ± 0.32 (2.26) | 4.76 ± 0.78 (5.00) | 2.08 ± 0.54 (2.26) |
| back | p | 0.844 | 50/50 | 0 | 49 | 2.26 ± 0.33 (2.26) | 7.67 ± 24.09 (3.90) | 2.27 ± 0.42 (2.28) | 4.80 ± 1.00 (5.09) | 2.14 ± 0.64 (2.29) |
| right | p | 0.856 | 50/50 | 0 | 50 | 1.51 ± 0.31 (1.52) | 4.39 ± 2.94 (3.97) | 2.18 ± 0.32 (2.25) | 4.66 ± 0.77 (4.93) | 2.00 ± 0.53 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.859 | 100/100 | 0 | 100 | 1.58 ± 0.54 (1.54) | 4.29 ± 3.12 (3.69) | 2.17 ± 0.33 (2.15) | 4.65 ± 0.80 (4.80) | 2.00 ± 0.57 (2.04) |
| right | p | 0.850 | 100/100 | 0 | 99 | 1.56 ± 0.53 (1.50) | 6.40 ± 17.25 (4.03) | 2.15 ± 0.39 (2.12) | 4.60 ± 0.91 (4.65) | 1.98 ± 0.60 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.858 | 25/25 | 0 | 25 | 1.03 ± 0.21 (1.02) | 4.50 ± 3.11 (3.73) | 2.01 ± 0.32 (2.01) | 4.33 ± 0.76 (4.07) | 1.77 ± 0.56 (1.61) |
| forward/right | p | 0.850 | 25/25 | 0 | 25 | 1.01 ± 0.21 (1.04) | 4.95 ± 3.69 (4.42) | 1.97 ± 0.29 (1.96) | 4.24 ± 0.71 (3.88) | 1.72 ± 0.50 (1.53) |
| left/left | p | 0.867 | 25/25 | 0 | 25 | 1.42 ± 0.31 (1.48) | 4.45 ± 3.62 (2.72) | 2.18 ± 0.32 (2.25) | 4.71 ± 0.78 (4.99) | 2.04 ± 0.53 (2.22) |
| left/right | p | 0.862 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.54) | 4.76 ± 3.15 (3.94) | 2.23 ± 0.32 (2.26) | 4.80 ± 0.78 (5.13) | 2.12 ± 0.55 (2.28) |
| back/left | p | 0.861 | 25/25 | 0 | 25 | 2.29 ± 0.32 (2.24) | 3.76 ± 2.23 (3.57) | 2.31 ± 0.29 (2.25) | 4.90 ± 0.79 (5.10) | 2.18 ± 0.58 (2.35) |
| back/right | p | 0.826 | 25/25 | 0 | 24 | 2.23 ± 0.34 (2.28) | 11.58 ± 33.54 (4.11) | 2.22 ± 0.52 (2.30) | 4.71 ± 1.17 (5.08) | 2.10 ± 0.69 (2.20) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.59 ± 0.28 (1.58) | 4.47 ± 3.30 (4.14) | 2.17 ± 0.30 (2.25) | 4.65 ± 0.75 (4.99) | 2.00 ± 0.52 (2.13) |
| right/right | p | 0.860 | 25/25 | 0 | 25 | 1.42 ± 0.31 (1.36) | 4.32 ± 2.52 (3.81) | 2.19 ± 0.34 (2.13) | 4.66 ± 0.79 (4.71) | 2.00 ± 0.55 (1.95) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.896 | 3.6 | 5.17 | 2.35 |
| p | normal | 0.813 | 7.1 | 4.08 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.763 | 0.12 | 2.34 ± 0.70 (2.40) | 3.73 | 1.39 |
| p | medium | 18 | 0.894 | 0.77 | 1.22 ± 0.16 (1.21) | 3.89 | 1.47 |
| p | strong | 124 | 0.891 | 0.69 | - | 5.15 | 2.35 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.844).
