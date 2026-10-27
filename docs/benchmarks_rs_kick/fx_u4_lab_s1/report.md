# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.864** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.63 ± 0.56 (1.57) |
| Direction error [°] | 6.04 ± 11.87 (4.84) |
| Avg ball speed [m/s] | 1.94 ± 0.54 (2.12) |
| Peak ball speed [m/s] | 4.24 ± 1.25 (4.79) |
| Distance [m] | 1.69 ± 0.76 (1.93) |
| Path length [m] | 1.70 ± 0.77 (1.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.864 | 50/50 | 0 | 49 | 1.04 ± 0.28 (1.11) | 5.38 ± 3.77 (4.03) | 1.76 ± 0.50 (1.93) | 3.92 ± 1.14 (4.28) | 1.44 ± 0.67 (1.62) |
| left | p | 0.879 | 50/50 | 0 | 50 | 1.58 ± 0.39 (1.52) | 5.10 ± 3.55 (4.70) | 1.96 ± 0.51 (2.23) | 4.26 ± 1.21 (5.00) | 1.71 ± 0.75 (2.03) |
| back | p | 0.846 | 50/50 | 0 | 49 | 2.31 ± 0.26 (2.32) | 8.97 ± 22.68 (5.87) | 2.10 ± 0.56 (2.38) | 4.58 ± 1.32 (5.32) | 1.94 ± 0.80 (2.27) |
| right | p | 0.866 | 50/50 | 0 | 50 | 1.57 ± 0.38 (1.58) | 4.71 ± 3.31 (4.08) | 1.93 ± 0.52 (2.21) | 4.19 ± 1.21 (4.93) | 1.66 ± 0.75 (2.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.859 | 100/100 | 0 | 100 | 1.63 ± 0.57 (1.52) | 5.24 ± 3.34 (4.69) | 1.97 ± 0.53 (2.22) | 4.31 ± 1.23 (4.95) | 1.73 ± 0.76 (2.04) |
| right | p | 0.869 | 100/100 | 0 | 98 | 1.62 ± 0.55 (1.59) | 6.84 ± 16.41 (5.04) | 1.91 ± 0.54 (2.10) | 4.17 ± 1.26 (4.70) | 1.65 ± 0.77 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.866 | 25/25 | 0 | 25 | 1.05 ± 0.29 (1.10) | 5.29 ± 3.41 (4.64) | 1.75 ± 0.54 (1.93) | 3.89 ± 1.23 (4.29) | 1.44 ± 0.71 (1.61) |
| forward/right | p | 0.862 | 25/25 | 0 | 24 | 1.04 ± 0.26 (1.12) | 5.47 ± 4.10 (3.28) | 1.78 ± 0.46 (1.94) | 3.94 ± 1.04 (4.23) | 1.44 ± 0.62 (1.62) |
| left/left | p | 0.871 | 25/25 | 0 | 25 | 1.48 ± 0.37 (1.42) | 5.62 ± 3.92 (4.77) | 1.93 ± 0.52 (2.00) | 4.22 ± 1.20 (4.35) | 1.68 ± 0.72 (1.76) |
| left/right | p | 0.887 | 25/25 | 0 | 25 | 1.69 ± 0.37 (1.72) | 4.59 ± 3.06 (4.26) | 1.98 ± 0.50 (2.30) | 4.30 ± 1.23 (5.08) | 1.74 ± 0.77 (2.20) |
| back/left | p | 0.849 | 25/25 | 0 | 25 | 2.33 ± 0.24 (2.38) | 5.41 ± 2.16 (5.46) | 2.19 ± 0.49 (2.46) | 4.77 ± 1.19 (5.42) | 2.05 ± 0.75 (2.36) |
| back/right | p | 0.843 | 25/25 | 0 | 24 | 2.28 ± 0.28 (2.24) | 12.53 ± 31.60 (6.76) | 2.01 ± 0.61 (2.33) | 4.39 ± 1.41 (5.07) | 1.84 ± 0.83 (2.11) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.68 ± 0.38 (1.60) | 4.65 ± 3.54 (2.89) | 2.00 ± 0.47 (2.23) | 4.34 ± 1.12 (4.96) | 1.75 ± 0.72 (2.11) |
| right/right | p | 0.883 | 25/25 | 0 | 25 | 1.46 ± 0.34 (1.54) | 4.76 ± 3.05 (4.23) | 1.86 ± 0.56 (2.13) | 4.03 ± 1.28 (4.78) | 1.57 ± 0.77 (1.95) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.876 | 6.7 | 5.07 | 2.19 |
| p | normal | 0.851 | 5.4 | 3.40 | 1.18 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.811 | 0.38 | 1.74 ± 0.61 (1.71) | 2.70 | 0.75 |
| p | medium | 20 | 0.920 | 0.86 | 0.95 ± 0.15 (0.93) | 3.04 | 0.94 |
| p | strong | 126 | 0.878 | 0.68 | - | 5.09 | 2.21 |

## Notes

- p: score 0.864, 200/200 kicked, 0 fell; worst sector back (0.846).
