# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.866** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.52 (1.54) |
| Direction error [°] | 4.93 ± 3.31 (4.26) |
| Avg ball speed [m/s] | 1.91 ± 0.46 (2.07) |
| Peak ball speed [m/s] | 4.16 ± 1.09 (4.61) |
| Distance [m] | 1.58 ± 0.66 (1.77) |
| Path length [m] | 1.59 ± 0.66 (1.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.861 | 50/50 | 0 | 48 | 1.07 ± 0.24 (1.09) | 4.86 ± 3.63 (4.08) | 1.63 ± 0.47 (1.56) | 3.57 ± 1.08 (3.27) | 1.20 ± 0.60 (1.08) |
| left | p | 0.881 | 50/50 | 0 | 50 | 1.55 ± 0.35 (1.53) | 4.85 ± 3.54 (4.16) | 2.00 ± 0.40 (2.18) | 4.38 ± 0.97 (4.88) | 1.72 ± 0.58 (1.95) |
| back | p | 0.858 | 50/50 | 0 | 50 | 2.26 ± 0.26 (2.27) | 5.21 ± 2.56 (5.07) | 2.10 ± 0.41 (2.29) | 4.57 ± 1.01 (5.11) | 1.86 ± 0.66 (2.09) |
| right | p | 0.864 | 50/50 | 0 | 50 | 1.56 ± 0.34 (1.54) | 4.79 ± 3.38 (3.73) | 1.89 ± 0.44 (2.06) | 4.12 ± 1.04 (4.57) | 1.54 ± 0.61 (1.72) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.864 | 100/100 | 0 | 99 | 1.61 ± 0.52 (1.59) | 5.00 ± 3.34 (4.16) | 1.92 ± 0.44 (2.09) | 4.20 ± 1.05 (4.62) | 1.60 ± 0.65 (1.80) |
| right | p | 0.868 | 100/100 | 0 | 99 | 1.61 ± 0.52 (1.53) | 4.85 ± 3.28 (4.38) | 1.89 ± 0.49 (2.06) | 4.12 ± 1.13 (4.59) | 1.56 ± 0.67 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.861 | 25/25 | 0 | 24 | 1.07 ± 0.24 (1.08) | 5.01 ± 4.01 (2.62) | 1.66 ± 0.41 (1.73) | 3.64 ± 1.01 (3.89) | 1.23 ± 0.57 (1.27) |
| forward/right | p | 0.861 | 25/25 | 0 | 24 | 1.07 ± 0.24 (1.10) | 4.72 ± 3.20 (4.13) | 1.60 ± 0.52 (1.56) | 3.50 ± 1.14 (3.24) | 1.17 ± 0.62 (1.01) |
| left/left | p | 0.875 | 25/25 | 0 | 25 | 1.44 ± 0.35 (1.48) | 5.17 ± 3.54 (4.16) | 1.92 ± 0.42 (2.11) | 4.19 ± 1.01 (4.71) | 1.60 ± 0.59 (1.84) |
| left/right | p | 0.887 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.70) | 4.52 ± 3.51 (3.64) | 2.09 ± 0.36 (2.24) | 4.58 ± 0.89 (4.95) | 1.85 ± 0.54 (1.99) |
| back/left | p | 0.854 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.28) | 5.23 ± 2.70 (4.69) | 2.13 ± 0.36 (2.27) | 4.64 ± 0.94 (5.10) | 1.91 ± 0.64 (2.13) |
| back/right | p | 0.862 | 25/25 | 0 | 25 | 2.25 ± 0.26 (2.26) | 5.19 ± 2.42 (5.40) | 2.07 ± 0.45 (2.30) | 4.51 ± 1.07 (5.11) | 1.81 ± 0.68 (2.06) |
| right/left | p | 0.865 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.60) | 4.61 ± 2.91 (3.74) | 1.99 ± 0.41 (2.20) | 4.34 ± 1.00 (4.80) | 1.68 ± 0.60 (1.83) |
| right/right | p | 0.864 | 25/25 | 0 | 25 | 1.44 ± 0.32 (1.46) | 4.97 ± 3.79 (3.11) | 1.79 ± 0.45 (1.81) | 3.89 ± 1.04 (4.09) | 1.41 ± 0.60 (1.40) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.877 | 4.8 | 4.87 | 1.99 |
| p | normal | 0.855 | 5.1 | 3.45 | 1.17 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.822 | 0.39 | 1.79 ± 0.62 (1.67) | 2.83 | 0.81 |
| p | medium | 16 | 0.909 | 0.87 | 0.92 ± 0.14 (0.95) | 3.00 | 0.91 |
| p | strong | 126 | 0.881 | 0.66 | - | 4.92 | 2.02 |

## Notes

- p: score 0.866, 200/200 kicked, 0 fell; worst sector back (0.858).
