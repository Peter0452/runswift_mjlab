# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.56 ± 0.53 (1.48) |
| Direction error [°] | 4.92 ± 3.40 (4.75) |
| Avg ball speed [m/s] | 2.02 ± 0.35 (2.10) |
| Peak ball speed [m/s] | 4.43 ± 0.84 (4.68) |
| Distance [m] | 1.77 ± 0.54 (1.86) |
| Path length [m] | 1.78 ± 0.54 (1.87) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.854 | 50/50 | 0 | 49 | 1.03 ± 0.26 (1.06) | 5.29 ± 3.82 (5.13) | 1.90 ± 0.38 (1.91) | 4.17 ± 0.84 (4.19) | 1.57 ± 0.54 (1.59) |
| left | p | 0.864 | 50/50 | 0 | 50 | 1.48 ± 0.34 (1.40) | 5.30 ± 3.28 (5.07) | 1.98 ± 0.34 (2.07) | 4.34 ± 0.86 (4.59) | 1.73 ± 0.54 (1.82) |
| back | p | 0.862 | 50/50 | 0 | 50 | 2.23 ± 0.29 (2.22) | 3.76 ± 2.54 (3.14) | 2.19 ± 0.26 (2.24) | 4.80 ± 0.70 (5.01) | 2.01 ± 0.46 (2.13) |
| right | p | 0.846 | 50/50 | 0 | 49 | 1.48 ± 0.34 (1.48) | 5.35 ± 3.57 (4.78) | 2.01 ± 0.31 (2.10) | 4.39 ± 0.81 (4.75) | 1.76 ± 0.52 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.849 | 100/100 | 0 | 99 | 1.55 ± 0.53 (1.40) | 5.42 ± 3.54 (5.09) | 2.02 ± 0.38 (2.11) | 4.44 ± 0.89 (4.71) | 1.78 ± 0.58 (1.90) |
| right | p | 0.864 | 100/100 | 0 | 99 | 1.56 ± 0.53 (1.54) | 4.43 ± 3.19 (3.69) | 2.02 ± 0.31 (2.08) | 4.42 ± 0.78 (4.55) | 1.76 ± 0.50 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.01 ± 0.26 (1.00) | 5.93 ± 3.92 (5.25) | 1.87 ± 0.41 (1.88) | 4.11 ± 0.88 (3.95) | 1.56 ± 0.57 (1.53) |
| forward/right | p | 0.861 | 25/25 | 0 | 24 | 1.04 ± 0.26 (1.12) | 4.64 ± 3.60 (4.25) | 1.92 ± 0.36 (1.92) | 4.23 ± 0.80 (4.29) | 1.59 ± 0.50 (1.67) |
| left/left | p | 0.867 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.34) | 5.14 ± 3.22 (4.80) | 1.99 ± 0.39 (2.11) | 4.39 ± 0.98 (4.88) | 1.76 ± 0.62 (1.91) |
| left/right | p | 0.862 | 25/25 | 0 | 25 | 1.56 ± 0.32 (1.56) | 5.45 ± 3.33 (5.32) | 1.96 ± 0.27 (2.02) | 4.29 ± 0.71 (4.39) | 1.70 ± 0.45 (1.80) |
| back/left | p | 0.852 | 25/25 | 0 | 25 | 2.24 ± 0.24 (2.22) | 4.41 ± 2.78 (4.76) | 2.20 ± 0.26 (2.24) | 4.83 ± 0.68 (5.01) | 2.02 ± 0.44 (2.12) |
| back/right | p | 0.871 | 25/25 | 0 | 25 | 2.23 ± 0.32 (2.22) | 3.11 ± 2.08 (2.63) | 2.19 ± 0.27 (2.24) | 4.77 ± 0.72 (5.02) | 2.01 ± 0.49 (2.13) |
| right/left | p | 0.829 | 25/25 | 0 | 24 | 1.56 ± 0.33 (1.48) | 6.17 ± 3.85 (5.46) | 2.02 ± 0.35 (2.10) | 4.41 ± 0.86 (4.71) | 1.78 ± 0.56 (1.92) |
| right/right | p | 0.862 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.48) | 4.53 ± 3.06 (3.58) | 2.01 ± 0.28 (2.16) | 4.38 ± 0.77 (4.78) | 1.74 ± 0.48 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.877 | 4.9 | 4.93 | 2.08 |
| p | normal | 0.836 | 5.0 | 3.92 | 1.46 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.776 | 0.18 | 2.20 ± 0.67 (2.04) | 3.44 | 1.16 |
| p | medium | 20 | 0.922 | 0.83 | 1.16 ± 0.14 (1.15) | 3.70 | 1.32 |
| p | strong | 126 | 0.880 | 0.66 | - | 4.96 | 2.10 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector right (0.846).
