# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.857** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.58 ± 0.54 (1.50) |
| Direction error [°] | 6.32 ± 11.97 (4.73) |
| Avg ball speed [m/s] | 2.12 ± 0.47 (2.28) |
| Peak ball speed [m/s] | 4.51 ± 1.09 (4.98) |
| Distance [m] | 1.96 ± 0.72 (2.21) |
| Path length [m] | 1.97 ± 0.72 (2.22) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.863 | 50/50 | 0 | 49 | 1.03 ± 0.26 (1.10) | 5.28 ± 3.93 (4.21) | 1.98 ± 0.43 (2.10) | 4.27 ± 1.01 (4.65) | 1.76 ± 0.66 (1.87) |
| left | p | 0.868 | 50/50 | 0 | 48 | 1.53 ± 0.36 (1.45) | 5.66 ± 3.94 (4.67) | 2.14 ± 0.40 (2.27) | 4.55 ± 0.99 (5.02) | 1.98 ± 0.67 (2.23) |
| back | p | 0.845 | 50/50 | 0 | 49 | 2.25 ± 0.28 (2.23) | 8.76 ± 22.89 (5.43) | 2.22 ± 0.57 (2.45) | 4.71 ± 1.26 (5.26) | 2.13 ± 0.77 (2.38) |
| right | p | 0.851 | 50/50 | 0 | 50 | 1.51 ± 0.36 (1.52) | 5.58 ± 3.17 (5.25) | 2.15 ± 0.44 (2.34) | 4.53 ± 1.03 (5.09) | 1.97 ± 0.71 (2.29) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 99 | 1.59 ± 0.54 (1.42) | 5.58 ± 3.36 (4.90) | 2.17 ± 0.45 (2.32) | 4.61 ± 1.04 (5.05) | 2.02 ± 0.71 (2.27) |
| right | p | 0.859 | 100/100 | 0 | 97 | 1.57 ± 0.54 (1.54) | 7.06 ± 16.55 (4.43) | 2.08 ± 0.49 (2.21) | 4.42 ± 1.13 (4.80) | 1.90 ± 0.72 (2.12) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.861 | 25/25 | 0 | 24 | 1.04 ± 0.28 (1.10) | 5.48 ± 4.45 (4.28) | 1.97 ± 0.45 (2.16) | 4.24 ± 1.05 (4.71) | 1.76 ± 0.69 (1.81) |
| forward/right | p | 0.866 | 25/25 | 0 | 25 | 1.02 ± 0.25 (1.10) | 5.08 ± 3.31 (4.14) | 1.99 ± 0.42 (2.10) | 4.30 ± 0.97 (4.63) | 1.77 ± 0.64 (1.88) |
| left/left | p | 0.871 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.38) | 5.73 ± 3.33 (4.81) | 2.17 ± 0.44 (2.33) | 4.65 ± 1.05 (5.13) | 2.05 ± 0.71 (2.34) |
| left/right | p | 0.864 | 25/25 | 0 | 23 | 1.62 ± 0.36 (1.60) | 5.59 ± 4.46 (4.43) | 2.11 ± 0.36 (2.20) | 4.45 ± 0.91 (4.78) | 1.91 ± 0.63 (2.15) |
| back/left | p | 0.845 | 25/25 | 0 | 25 | 2.27 ± 0.24 (2.24) | 5.53 ± 2.81 (5.48) | 2.32 ± 0.39 (2.46) | 4.91 ± 0.90 (5.25) | 2.23 ± 0.62 (2.40) |
| back/right | p | 0.845 | 25/25 | 0 | 24 | 2.23 ± 0.31 (2.20) | 11.99 ± 31.92 (5.37) | 2.12 ± 0.69 (2.45) | 4.50 ± 1.52 (5.28) | 2.04 ± 0.88 (2.37) |
| right/left | p | 0.839 | 25/25 | 0 | 25 | 1.61 ± 0.36 (1.56) | 5.59 ± 2.54 (5.90) | 2.20 ± 0.45 (2.39) | 4.64 ± 1.04 (5.17) | 2.04 ± 0.72 (2.31) |
| right/right | p | 0.862 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.50) | 5.57 ± 3.69 (4.11) | 2.10 ± 0.43 (2.32) | 4.43 ± 1.01 (5.02) | 1.89 ± 0.69 (2.19) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.881 | 6.7 | 5.20 | 2.41 |
| p | normal | 0.833 | 6.0 | 3.83 | 1.51 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.780 | 0.22 | 2.07 ± 0.69 (1.99) | 3.23 | 1.10 |
| p | medium | 20 | 0.906 | 0.88 | 1.07 ± 0.14 (1.04) | 3.41 | 1.21 |
| p | strong | 126 | 0.882 | 0.70 | - | 5.24 | 2.45 |

## Notes

- p: score 0.857, 200/200 kicked, 0 fell; worst sector back (0.845).
