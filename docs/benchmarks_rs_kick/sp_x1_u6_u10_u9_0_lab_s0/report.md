# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/x1_u6_u10_u9.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.53 (1.48) |
| Direction error [°] | 5.12 ± 3.24 (4.48) |
| Avg ball speed [m/s] | 1.79 ± 0.35 (1.93) |
| Peak ball speed [m/s] | 4.00 ± 0.87 (4.31) |
| Distance [m] | 1.38 ± 0.48 (1.47) |
| Path length [m] | 1.38 ± 0.48 (1.47) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.859 | 50/50 | 0 | 50 | 1.02 ± 0.23 (1.07) | 4.15 ± 2.96 (3.47) | 1.56 ± 0.40 (1.50) | 3.41 ± 0.89 (3.18) | 1.06 ± 0.47 (0.98) |
| left | p | 0.867 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.51) | 5.31 ± 3.52 (4.14) | 1.86 ± 0.30 (1.95) | 4.19 ± 0.77 (4.49) | 1.47 ± 0.43 (1.55) |
| back | p | 0.835 | 50/50 | 0 | 50 | 2.25 ± 0.29 (2.22) | 5.88 ± 3.02 (6.09) | 1.96 ± 0.23 (2.05) | 4.40 ± 0.67 (4.70) | 1.62 ± 0.39 (1.70) |
| right | p | 0.852 | 50/50 | 0 | 50 | 1.49 ± 0.34 (1.46) | 5.13 ± 3.19 (4.30) | 1.80 ± 0.31 (1.92) | 3.99 ± 0.81 (4.40) | 1.36 ± 0.42 (1.41) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.57 ± 0.53 (1.48) | 5.41 ± 3.37 (4.82) | 1.80 ± 0.32 (1.91) | 4.00 ± 0.81 (4.27) | 1.38 ± 0.45 (1.46) |
| right | p | 0.859 | 100/100 | 0 | 100 | 1.56 ± 0.53 (1.48) | 4.83 ± 3.08 (4.08) | 1.79 ± 0.38 (1.96) | 3.99 ± 0.93 (4.38) | 1.37 ± 0.50 (1.48) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.08) | 4.26 ± 2.91 (3.24) | 1.58 ± 0.34 (1.54) | 3.45 ± 0.74 (3.21) | 1.07 ± 0.42 (0.97) |
| forward/right | p | 0.865 | 25/25 | 0 | 25 | 1.01 ± 0.23 (1.04) | 4.04 ± 3.02 (3.71) | 1.53 ± 0.44 (1.46) | 3.37 ± 1.03 (3.10) | 1.04 ± 0.52 (0.99) |
| left/left | p | 0.854 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.44) | 6.05 ± 4.13 (4.14) | 1.79 ± 0.29 (1.89) | 4.01 ± 0.74 (4.23) | 1.37 ± 0.42 (1.42) |
| left/right | p | 0.881 | 25/25 | 0 | 25 | 1.60 ± 0.29 (1.62) | 4.56 ± 2.58 (4.14) | 1.93 ± 0.30 (2.07) | 4.37 ± 0.75 (4.76) | 1.57 ± 0.42 (1.66) |
| back/left | p | 0.832 | 25/25 | 0 | 25 | 2.27 ± 0.26 (2.24) | 6.16 ± 3.10 (6.81) | 2.00 ± 0.19 (2.04) | 4.45 ± 0.58 (4.70) | 1.66 ± 0.37 (1.70) |
| back/right | p | 0.839 | 25/25 | 0 | 25 | 2.23 ± 0.31 (2.22) | 5.60 ± 2.92 (5.48) | 1.93 ± 0.27 (2.06) | 4.34 ± 0.75 (4.69) | 1.59 ± 0.41 (1.69) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.58 ± 0.30 (1.56) | 5.15 ± 2.85 (5.46) | 1.82 ± 0.31 (1.94) | 4.10 ± 0.82 (4.51) | 1.42 ± 0.41 (1.48) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.41 ± 0.35 (1.46) | 5.10 ± 3.50 (3.82) | 1.77 ± 0.32 (1.87) | 3.88 ± 0.79 (3.98) | 1.30 ± 0.41 (1.33) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.863 | 5.3 | 4.52 | 1.65 |
| p | normal | 0.843 | 4.9 | 3.47 | 1.11 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.811 | 0.32 | 1.90 ± 0.64 (1.74) | 3.03 | 0.88 |
| p | medium | 16 | 0.914 | 0.85 | 0.97 ± 0.17 (0.99) | 3.14 | 0.94 |
| p | strong | 126 | 0.865 | 0.61 | - | 4.55 | 1.66 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector back (0.835).
