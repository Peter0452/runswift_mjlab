# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.55 ± 0.54 (1.48) |
| Direction error [°] | 5.38 ± 3.40 (4.90) |
| Avg ball speed [m/s] | 1.91 ± 0.36 (1.94) |
| Peak ball speed [m/s] | 4.13 ± 0.85 (4.16) |
| Distance [m] | 1.54 ± 0.52 (1.49) |
| Path length [m] | 1.55 ± 0.52 (1.50) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.852 | 50/50 | 0 | 49 | 1.01 ± 0.26 (1.10) | 5.12 ± 3.98 (3.78) | 1.71 ± 0.38 (1.70) | 3.72 ± 0.85 (3.65) | 1.27 ± 0.50 (1.20) |
| left | p | 0.856 | 50/50 | 0 | 50 | 1.48 ± 0.36 (1.39) | 6.02 ± 3.44 (5.62) | 1.88 ± 0.33 (1.85) | 4.07 ± 0.80 (4.16) | 1.50 ± 0.49 (1.41) |
| back | p | 0.850 | 50/50 | 0 | 50 | 2.24 ± 0.27 (2.20) | 4.74 ± 2.01 (5.03) | 2.15 ± 0.26 (2.21) | 4.65 ± 0.68 (4.89) | 1.88 ± 0.43 (2.00) |
| right | p | 0.839 | 50/50 | 0 | 50 | 1.48 ± 0.34 (1.49) | 5.65 ± 3.69 (4.30) | 1.89 ± 0.30 (1.81) | 4.07 ± 0.77 (3.77) | 1.51 ± 0.47 (1.36) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.55 ± 0.54 (1.41) | 5.21 ± 3.39 (4.52) | 1.92 ± 0.37 (2.00) | 4.16 ± 0.86 (4.31) | 1.56 ± 0.53 (1.57) |
| right | p | 0.850 | 100/100 | 0 | 99 | 1.56 ± 0.54 (1.52) | 5.55 ± 3.40 (5.05) | 1.89 ± 0.35 (1.89) | 4.09 ± 0.83 (3.98) | 1.52 ± 0.51 (1.43) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 0.99 ± 0.25 (1.00) | 5.05 ± 3.39 (4.22) | 1.67 ± 0.32 (1.57) | 3.64 ± 0.76 (3.41) | 1.22 ± 0.42 (1.06) |
| forward/right | p | 0.851 | 25/25 | 0 | 24 | 1.02 ± 0.26 (1.10) | 5.19 ± 4.48 (3.21) | 1.75 ± 0.42 (1.80) | 3.80 ± 0.93 (3.89) | 1.33 ± 0.57 (1.36) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.40 ± 0.35 (1.34) | 5.70 ± 3.92 (5.09) | 1.86 ± 0.36 (2.00) | 4.05 ± 0.87 (4.29) | 1.49 ± 0.51 (1.55) |
| left/right | p | 0.850 | 25/25 | 0 | 25 | 1.56 ± 0.34 (1.56) | 6.33 ± 2.84 (7.31) | 1.89 ± 0.30 (1.77) | 4.09 ± 0.74 (3.69) | 1.52 ± 0.47 (1.31) |
| back/left | p | 0.848 | 25/25 | 0 | 25 | 2.25 ± 0.24 (2.20) | 4.56 ± 2.36 (4.43) | 2.19 ± 0.27 (2.21) | 4.71 ± 0.66 (4.93) | 1.93 ± 0.42 (1.99) |
| back/right | p | 0.851 | 25/25 | 0 | 25 | 2.24 ± 0.30 (2.20) | 4.92 ± 1.57 (5.05) | 2.12 ± 0.25 (2.21) | 4.59 ± 0.68 (4.89) | 1.84 ± 0.43 (2.04) |
| right/left | p | 0.830 | 25/25 | 0 | 25 | 1.56 ± 0.33 (1.50) | 5.53 ± 3.57 (4.45) | 1.96 ± 0.32 (2.02) | 4.25 ± 0.79 (4.44) | 1.62 ± 0.50 (1.75) |
| right/right | p | 0.849 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.48) | 5.76 ± 3.80 (4.14) | 1.82 ± 0.27 (1.75) | 3.89 ± 0.70 (3.71) | 1.39 ± 0.41 (1.29) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.864 | 5.2 | 4.55 | 1.78 |
| p | normal | 0.834 | 5.6 | 3.70 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.783 | 0.24 | 2.12 ± 0.72 (1.92) | 3.30 | 1.05 |
| p | medium | 20 | 0.919 | 0.86 | 1.07 ± 0.16 (1.06) | 3.43 | 1.14 |
| p | strong | 126 | 0.866 | 0.61 | - | 4.59 | 1.81 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector right (0.839).
