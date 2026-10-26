# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.56 ± 0.52 (1.52) |
| Direction error [°] | 6.74 ± 15.65 (4.60) |
| Avg ball speed [m/s] | 1.95 ± 0.37 (1.98) |
| Peak ball speed [m/s] | 4.21 ± 0.87 (4.26) |
| Distance [m] | 1.62 ± 0.53 (1.60) |
| Path length [m] | 1.63 ± 0.53 (1.61) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.855 | 50/50 | 0 | 49 | 1.01 ± 0.22 (1.03) | 4.81 ± 3.37 (3.87) | 1.79 ± 0.31 (1.79) | 3.89 ± 0.73 (3.73) | 1.39 ± 0.46 (1.29) |
| left | p | 0.850 | 50/50 | 0 | 50 | 1.49 ± 0.32 (1.51) | 5.57 ± 3.56 (4.74) | 2.02 ± 0.28 (2.05) | 4.36 ± 0.70 (4.46) | 1.70 ± 0.44 (1.70) |
| back | p | 0.826 | 50/50 | 0 | 48 | 2.23 ± 0.31 (2.22) | 11.50 ± 30.25 (5.59) | 2.07 ± 0.47 (2.18) | 4.43 ± 1.11 (4.83) | 1.82 ± 0.62 (1.84) |
| right | p | 0.842 | 50/50 | 0 | 50 | 1.50 ± 0.30 (1.54) | 5.08 ± 3.25 (4.84) | 1.93 ± 0.33 (1.95) | 4.15 ± 0.78 (4.18) | 1.58 ± 0.47 (1.54) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.849 | 100/100 | 0 | 99 | 1.56 ± 0.52 (1.55) | 6.32 ± 15.27 (4.15) | 1.96 ± 0.37 (2.00) | 4.22 ± 0.88 (4.34) | 1.63 ± 0.55 (1.61) |
| right | p | 0.837 | 100/100 | 0 | 98 | 1.55 ± 0.53 (1.51) | 7.16 ± 16.02 (4.97) | 1.95 ± 0.37 (1.97) | 4.20 ± 0.86 (4.24) | 1.62 ± 0.51 (1.60) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 25 | 1.02 ± 0.22 (1.02) | 4.15 ± 2.45 (3.37) | 1.77 ± 0.33 (1.74) | 3.82 ± 0.81 (3.49) | 1.36 ± 0.51 (1.10) |
| forward/right | p | 0.846 | 25/25 | 0 | 24 | 1.00 ± 0.22 (1.06) | 5.48 ± 3.98 (4.41) | 1.82 ± 0.28 (1.84) | 3.95 ± 0.65 (3.90) | 1.43 ± 0.41 (1.42) |
| left/left | p | 0.851 | 25/25 | 0 | 25 | 1.38 ± 0.29 (1.40) | 5.46 ± 3.86 (4.23) | 1.98 ± 0.27 (2.07) | 4.30 ± 0.71 (4.52) | 1.65 ± 0.43 (1.74) |
| left/right | p | 0.849 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.54) | 5.68 ± 3.23 (4.83) | 2.05 ± 0.28 (1.99) | 4.43 ± 0.68 (4.39) | 1.75 ± 0.45 (1.67) |
| back/left | p | 0.837 | 25/25 | 0 | 24 | 2.24 ± 0.31 (2.20) | 11.05 ± 29.56 (4.42) | 2.09 ± 0.46 (2.16) | 4.46 ± 1.09 (4.84) | 1.85 ± 0.65 (1.83) |
| back/right | p | 0.816 | 25/25 | 0 | 24 | 2.22 ± 0.31 (2.24) | 11.95 ± 30.92 (6.23) | 2.05 ± 0.49 (2.18) | 4.39 ± 1.12 (4.82) | 1.80 ± 0.60 (1.87) |
| right/left | p | 0.846 | 25/25 | 0 | 25 | 1.59 ± 0.27 (1.60) | 4.61 ± 2.67 (4.73) | 1.99 ± 0.30 (2.05) | 4.30 ± 0.74 (4.60) | 1.66 ± 0.47 (1.63) |
| right/right | p | 0.839 | 25/25 | 0 | 25 | 1.40 ± 0.30 (1.34) | 5.54 ± 3.68 (5.49) | 1.87 ± 0.34 (1.76) | 4.01 ± 0.80 (3.86) | 1.49 ± 0.46 (1.37) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.870 | 6.3 | 4.64 | 1.87 |
| p | normal | 0.817 | 7.2 | 3.78 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.768 | 0.18 | 2.15 ± 0.69 (2.14) | 3.43 | 1.17 |
| p | medium | 18 | 0.905 | 0.82 | 1.12 ± 0.17 (1.16) | 3.58 | 1.23 |
| p | strong | 124 | 0.870 | 0.62 | - | 4.66 | 1.89 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector back (0.826).
