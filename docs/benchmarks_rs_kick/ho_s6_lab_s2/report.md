# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s6_ctl7_30_n7_70.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.841** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.58 ± 0.55 (1.56) |
| Direction error [°] | 6.00 ± 3.64 (6.04) |
| Avg ball speed [m/s] | 2.14 ± 0.33 (2.13) |
| Peak ball speed [m/s] | 4.54 ± 0.76 (4.59) |
| Distance [m] | 1.94 ± 0.52 (1.95) |
| Path length [m] | 1.95 ± 0.53 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.829 | 50/50 | 0 | 50 | 1.03 ± 0.24 (1.01) | 6.75 ± 3.63 (7.08) | 1.99 ± 0.31 (1.93) | 4.23 ± 0.67 (4.07) | 1.70 ± 0.46 (1.54) |
| left | p | 0.851 | 50/50 | 0 | 49 | 1.48 ± 0.36 (1.50) | 5.39 ± 3.61 (5.40) | 2.14 ± 0.32 (2.25) | 4.55 ± 0.76 (4.79) | 1.95 ± 0.52 (2.09) |
| back | p | 0.827 | 50/50 | 0 | 49 | 2.30 ± 0.28 (2.28) | 6.07 ± 3.39 (6.04) | 2.26 ± 0.28 (2.30) | 4.80 ± 0.70 (5.03) | 2.13 ± 0.47 (2.22) |
| right | p | 0.856 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.59) | 5.81 ± 3.79 (5.70) | 2.16 ± 0.34 (2.20) | 4.59 ± 0.80 (4.80) | 1.98 ± 0.55 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 99 | 1.58 ± 0.54 (1.57) | 5.84 ± 3.28 (5.81) | 2.18 ± 0.34 (2.26) | 4.65 ± 0.80 (4.93) | 2.01 ± 0.55 (2.11) |
| right | p | 0.833 | 100/100 | 0 | 99 | 1.58 ± 0.56 (1.54) | 6.17 ± 3.97 (6.19) | 2.09 ± 0.30 (2.06) | 4.44 ± 0.71 (4.41) | 1.87 ± 0.49 (1.81) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.823 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.02) | 7.00 ± 3.42 (7.29) | 2.00 ± 0.36 (1.92) | 4.22 ± 0.75 (3.91) | 1.70 ± 0.51 (1.49) |
| forward/right | p | 0.835 | 25/25 | 0 | 25 | 1.02 ± 0.25 (0.96) | 6.50 ± 3.82 (6.14) | 1.97 ± 0.25 (1.94) | 4.24 ± 0.58 (4.35) | 1.71 ± 0.40 (1.68) |
| left/left | p | 0.856 | 25/25 | 0 | 25 | 1.38 ± 0.33 (1.36) | 5.81 ± 3.44 (5.69) | 2.14 ± 0.31 (2.29) | 4.58 ± 0.75 (5.00) | 1.97 ± 0.51 (2.16) |
| left/right | p | 0.845 | 25/25 | 0 | 24 | 1.57 ± 0.36 (1.56) | 4.96 ± 3.73 (4.55) | 2.13 ± 0.32 (2.18) | 4.52 ± 0.77 (4.59) | 1.94 ± 0.53 (1.93) |
| back/left | p | 0.839 | 25/25 | 0 | 24 | 2.29 ± 0.29 (2.30) | 5.92 ± 3.20 (5.81) | 2.35 ± 0.28 (2.37) | 5.03 ± 0.68 (5.23) | 2.28 ± 0.46 (2.39) |
| back/right | p | 0.815 | 25/25 | 0 | 25 | 2.31 ± 0.28 (2.26) | 6.21 ± 3.57 (6.08) | 2.16 ± 0.25 (2.11) | 4.57 ± 0.64 (4.66) | 1.98 ± 0.43 (2.15) |
| right/left | p | 0.874 | 25/25 | 0 | 25 | 1.61 ± 0.32 (1.62) | 4.63 ± 2.52 (4.82) | 2.24 ± 0.32 (2.34) | 4.75 ± 0.77 (4.95) | 2.10 ± 0.55 (2.29) |
| right/right | p | 0.837 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.54) | 6.99 ± 4.43 (6.60) | 2.09 ± 0.33 (2.13) | 4.42 ± 0.79 (4.52) | 1.86 ± 0.52 (1.84) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.871 | 5.8 | 5.00 | 2.25 |
| p | normal | 0.811 | 6.2 | 4.08 | 1.64 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.767 | 0.17 | 2.25 ± 0.69 (2.06) | 3.70 | 1.39 |
| p | medium | 15 | 0.897 | 0.81 | 1.19 ± 0.11 (1.18) | 3.90 | 1.48 |
| p | strong | 125 | 0.869 | 0.67 | - | 5.02 | 2.26 |

## Notes

- p: score 0.841, 200/200 kicked, 0 fell; worst sector back (0.827).
