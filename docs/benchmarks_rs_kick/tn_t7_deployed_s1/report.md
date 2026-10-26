# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_01-33-49_t7_n7_lowcap03/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.797** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 176 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.91 ± 0.82 (1.76) |
| Direction error [°] | 13.72 ± 31.75 (4.99) |
| Avg ball speed [m/s] | 1.87 ± 0.50 (1.98) |
| Peak ball speed [m/s] | 4.75 ± 1.30 (5.02) |
| Distance [m] | 2.00 ± 0.72 (2.05) |
| Path length [m] | 2.01 ± 0.73 (2.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.796 | 48/50 | 0 | 43 | 1.46 ± 0.47 (1.48) | 7.38 ± 7.29 (5.13) | 1.85 ± 0.46 (1.93) | 4.69 ± 1.19 (4.95) | 1.92 ± 0.65 (1.92) |
| left | p | 0.817 | 49/50 | 0 | 45 | 1.74 ± 0.39 (1.74) | 15.32 ± 34.96 (5.01) | 1.88 ± 0.51 (1.97) | 4.74 ± 1.27 (5.02) | 2.02 ± 0.75 (2.06) |
| back | p | 0.750 | 48/50 | 0 | 41 | 2.50 ± 1.04 (2.49) | 23.76 ± 48.21 (3.45) | 1.81 ± 0.61 (2.01) | 4.66 ± 1.60 (5.13) | 1.96 ± 0.82 (2.18) |
| right | p | 0.824 | 50/50 | 0 | 47 | 1.93 ± 0.84 (1.83) | 8.61 ± 16.99 (5.41) | 1.95 ± 0.41 (2.00) | 4.90 ± 1.07 (4.91) | 2.10 ± 0.65 (2.03) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 99/100 | 0 | 88 | 1.94 ± 0.99 (1.76) | 14.08 ± 30.34 (5.32) | 1.88 ± 0.54 (2.01) | 4.74 ± 1.38 (5.02) | 2.02 ± 0.77 (2.10) |
| right | p | 0.791 | 96/100 | 0 | 88 | 1.87 ± 0.60 (1.76) | 13.36 ± 33.14 (4.73) | 1.87 ± 0.46 (1.97) | 4.76 ± 1.21 (4.98) | 1.99 ± 0.67 (2.00) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 22 | 1.36 ± 0.32 (1.36) | 8.19 ± 8.39 (4.86) | 1.85 ± 0.51 (1.84) | 4.69 ± 1.30 (4.93) | 1.94 ± 0.75 (1.90) |
| forward/right | p | 0.760 | 23/25 | 0 | 21 | 1.57 ± 0.56 (1.58) | 6.50 ± 5.72 (5.34) | 1.84 ± 0.41 (1.95) | 4.69 ± 1.07 (4.97) | 1.90 ± 0.51 (1.94) |
| left/left | p | 0.817 | 24/25 | 0 | 24 | 1.74 ± 0.33 (1.66) | 6.57 ± 2.87 (6.85) | 2.08 ± 0.32 (2.08) | 5.17 ± 0.80 (5.31) | 2.29 ± 0.56 (2.31) |
| left/right | p | 0.817 | 25/25 | 0 | 21 | 1.74 ± 0.44 (1.76) | 23.73 ± 47.36 (4.52) | 1.70 ± 0.58 (1.89) | 4.33 ± 1.49 (4.44) | 1.76 ± 0.82 (1.90) |
| back/left | p | 0.761 | 25/25 | 0 | 20 | 2.52 ± 1.32 (2.50) | 29.70 ± 51.72 (4.64) | 1.72 ± 0.70 (2.02) | 4.40 ± 1.81 (5.14) | 1.84 ± 0.90 (2.10) |
| back/right | p | 0.739 | 23/25 | 0 | 21 | 2.48 ± 0.59 (2.38) | 17.31 ± 43.16 (3.38) | 1.90 ± 0.48 (2.00) | 4.94 ± 1.27 (5.12) | 2.09 ± 0.69 (2.21) |
| right/left | p | 0.800 | 25/25 | 0 | 22 | 2.14 ± 1.10 (1.96) | 11.55 ± 23.52 (4.96) | 1.87 ± 0.52 (1.87) | 4.71 ± 1.30 (4.81) | 2.01 ± 0.75 (2.01) |
| right/right | p | 0.848 | 25/25 | 0 | 25 | 1.72 ± 0.32 (1.76) | 5.66 ± 2.67 (5.77) | 2.04 ± 0.23 (2.03) | 5.09 ± 0.72 (5.19) | 2.20 ± 0.52 (2.09) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.812 | 13.2 | 5.25 | 2.27 |
| p | normal | 0.782 | 14.2 | 4.27 | 1.74 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.734 | 0.11 | 2.55 ± 1.07 (2.44) | 3.93 | 1.54 |
| p | medium | 20 | 0.870 | 0.67 | 1.31 ± 0.20 (1.32) | 4.19 | 1.70 |
| p | strong | 126 | 0.812 | 0.69 | - | 5.20 | 2.26 |

## Notes

- p: score 0.797, 195/200 kicked, 0 fell; worst sector back (0.750).
