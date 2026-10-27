# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.80 ± 0.55 (1.72) |
| Direction error [°] | 5.44 ± 10.77 (4.42) |
| Avg ball speed [m/s] | 2.30 ± 0.28 (2.32) |
| Peak ball speed [m/s] | 5.10 ± 0.80 (5.40) |
| Distance [m] | 2.13 ± 0.48 (2.12) |
| Path length [m] | 2.14 ± 0.48 (2.14) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.859 | 50/50 | 0 | 50 | 1.23 ± 0.22 (1.26) | 3.80 ± 2.55 (3.11) | 2.26 ± 0.28 (2.24) | 4.99 ± 0.84 (5.20) | 2.04 ± 0.52 (1.89) |
| left | p | 0.881 | 50/50 | 0 | 50 | 1.72 ± 0.34 (1.76) | 4.51 ± 2.65 (3.90) | 2.34 ± 0.23 (2.37) | 5.24 ± 0.71 (5.56) | 2.19 ± 0.45 (2.33) |
| back | p | 0.813 | 50/50 | 0 | 49 | 2.51 ± 0.32 (2.45) | 8.19 ± 20.69 (5.00) | 2.34 ± 0.34 (2.36) | 5.14 ± 0.88 (5.45) | 2.20 ± 0.50 (2.25) |
| right | p | 0.845 | 50/50 | 0 | 49 | 1.72 ± 0.34 (1.71) | 5.26 ± 3.33 (4.76) | 2.28 ± 0.24 (2.24) | 5.03 ± 0.74 (5.20) | 2.09 ± 0.44 (1.97) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.849 | 100/100 | 0 | 99 | 1.80 ± 0.56 (1.76) | 6.35 ± 14.89 (4.59) | 2.31 ± 0.31 (2.33) | 5.11 ± 0.85 (5.44) | 2.15 ± 0.51 (2.27) |
| right | p | 0.850 | 100/100 | 0 | 99 | 1.79 ± 0.55 (1.72) | 4.53 ± 2.93 (4.10) | 2.30 ± 0.25 (2.31) | 5.08 ± 0.75 (5.36) | 2.11 ± 0.46 (2.04) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.868 | 25/25 | 0 | 25 | 1.25 ± 0.23 (1.28) | 3.62 ± 2.15 (3.13) | 2.27 ± 0.29 (2.24) | 5.02 ± 0.87 (5.20) | 2.06 ± 0.55 (1.91) |
| forward/right | p | 0.850 | 25/25 | 0 | 25 | 1.22 ± 0.21 (1.24) | 3.99 ± 2.89 (2.94) | 2.25 ± 0.28 (2.28) | 4.95 ± 0.81 (5.21) | 2.02 ± 0.48 (1.89) |
| left/left | p | 0.875 | 25/25 | 0 | 25 | 1.63 ± 0.34 (1.70) | 4.85 ± 2.90 (4.47) | 2.35 ± 0.25 (2.38) | 5.21 ± 0.77 (5.59) | 2.22 ± 0.47 (2.38) |
| left/right | p | 0.887 | 25/25 | 0 | 25 | 1.82 ± 0.31 (1.84) | 4.17 ± 2.34 (3.70) | 2.32 ± 0.21 (2.34) | 5.27 ± 0.65 (5.54) | 2.16 ± 0.43 (2.14) |
| back/left | p | 0.810 | 25/25 | 0 | 24 | 2.52 ± 0.34 (2.46) | 10.88 ± 28.91 (5.29) | 2.29 ± 0.41 (2.35) | 5.07 ± 0.99 (5.44) | 2.16 ± 0.54 (2.24) |
| back/right | p | 0.817 | 25/25 | 0 | 25 | 2.50 ± 0.29 (2.40) | 5.49 ± 2.49 (4.73) | 2.38 ± 0.24 (2.37) | 5.20 ± 0.75 (5.50) | 2.23 ± 0.45 (2.26) |
| right/left | p | 0.843 | 25/25 | 0 | 25 | 1.83 ± 0.31 (1.84) | 6.05 ± 2.79 (5.37) | 2.32 ± 0.25 (2.28) | 5.15 ± 0.74 (5.46) | 2.16 ± 0.45 (2.29) |
| right/right | p | 0.848 | 25/25 | 0 | 24 | 1.62 ± 0.33 (1.62) | 4.48 ± 3.62 (2.73) | 2.23 ± 0.22 (2.23) | 4.92 ± 0.73 (5.11) | 2.01 ± 0.43 (1.97) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.891 | 4.7 | 5.63 | 2.40 |
| p | normal | 0.809 | 6.2 | 4.57 | 1.86 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.754 | 0.06 | 2.63 ± 0.86 (2.44) | 4.15 | 1.63 |
| p | medium | 16 | 0.873 | 0.69 | 1.31 ± 0.12 (1.32) | 4.26 | 1.71 |
| p | strong | 126 | 0.891 | 0.75 | - | 5.65 | 2.41 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector back (0.813).
