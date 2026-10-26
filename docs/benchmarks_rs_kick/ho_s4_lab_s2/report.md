# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.59 ± 0.57 (1.54) |
| Direction error [°] | 5.59 ± 5.48 (4.69) |
| Avg ball speed [m/s] | 1.97 ± 0.40 (2.02) |
| Peak ball speed [m/s] | 4.54 ± 0.79 (4.62) |
| Distance [m] | 1.98 ± 0.70 (1.90) |
| Path length [m] | 2.01 ± 0.71 (1.93) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.836 | 50/50 | 0 | 49 | 1.06 ± 0.43 (0.99) | 5.95 ± 4.11 (5.37) | 1.83 ± 0.31 (1.83) | 4.19 ± 0.72 (4.17) | 1.69 ± 0.69 (1.57) |
| left | p | 0.840 | 50/50 | 0 | 47 | 1.52 ± 0.42 (1.50) | 6.66 ± 8.81 (4.85) | 1.94 ± 0.43 (1.96) | 4.60 ± 0.77 (4.72) | 2.10 ± 0.75 (2.09) |
| back | p | 0.848 | 50/50 | 0 | 50 | 2.24 ± 0.28 (2.24) | 4.57 ± 2.86 (4.91) | 2.15 ± 0.36 (2.17) | 4.87 ± 0.69 (5.11) | 2.19 ± 0.55 (2.24) |
| right | p | 0.854 | 50/50 | 0 | 48 | 1.52 ± 0.36 (1.56) | 5.21 ± 3.90 (4.20) | 1.95 ± 0.41 (2.02) | 4.49 ± 0.81 (4.63) | 1.92 ± 0.70 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 98 | 1.57 ± 0.54 (1.56) | 5.12 ± 3.82 (4.03) | 2.02 ± 0.39 (2.09) | 4.63 ± 0.79 (4.82) | 2.03 ± 0.66 (2.09) |
| right | p | 0.835 | 100/100 | 0 | 96 | 1.60 ± 0.59 (1.52) | 6.07 ± 6.72 (5.03) | 1.91 ± 0.40 (1.93) | 4.45 ± 0.78 (4.25) | 1.92 ± 0.74 (1.71) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.841 | 25/25 | 0 | 25 | 1.01 ± 0.25 (1.00) | 5.57 ± 3.83 (5.30) | 1.86 ± 0.31 (1.92) | 4.20 ± 0.78 (4.27) | 1.71 ± 0.73 (1.68) |
| forward/right | p | 0.831 | 25/25 | 0 | 24 | 1.11 ± 0.54 (0.98) | 6.33 ± 4.34 (5.95) | 1.80 ± 0.30 (1.83) | 4.18 ± 0.66 (3.96) | 1.66 ± 0.65 (1.47) |
| left/left | p | 0.853 | 25/25 | 0 | 24 | 1.38 ± 0.33 (1.36) | 5.81 ± 4.23 (4.74) | 1.89 ± 0.45 (1.96) | 4.59 ± 0.74 (4.84) | 2.07 ± 0.69 (2.09) |
| left/right | p | 0.828 | 25/25 | 0 | 23 | 1.66 ± 0.46 (1.54) | 7.50 ± 11.65 (4.95) | 1.99 ± 0.41 (1.96) | 4.61 ± 0.80 (4.59) | 2.14 ± 0.81 (1.97) |
| back/left | p | 0.862 | 25/25 | 0 | 25 | 2.23 ± 0.28 (2.30) | 4.10 ± 2.86 (3.37) | 2.23 ± 0.30 (2.31) | 4.98 ± 0.62 (5.20) | 2.22 ± 0.43 (2.25) |
| back/right | p | 0.834 | 25/25 | 0 | 25 | 2.25 ± 0.28 (2.22) | 5.04 ± 2.78 (5.59) | 2.06 ± 0.39 (2.11) | 4.77 ± 0.74 (4.84) | 2.17 ± 0.65 (2.20) |
| right/left | p | 0.860 | 25/25 | 0 | 24 | 1.65 ± 0.36 (1.60) | 5.02 ± 3.98 (3.98) | 2.10 ± 0.34 (2.17) | 4.74 ± 0.78 (5.08) | 2.12 ± 0.63 (2.14) |
| right/right | p | 0.849 | 25/25 | 0 | 24 | 1.38 ± 0.32 (1.44) | 5.39 ± 3.82 (4.62) | 1.79 ± 0.42 (1.83) | 4.24 ± 0.76 (3.97) | 1.73 ± 0.70 (1.48) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.877 | 5.1 | 4.96 | 2.30 |
| p | normal | 0.812 | 6.1 | 4.11 | 1.65 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.760 | 0.16 | 2.27 ± 0.70 (2.15) | 3.75 | 1.39 |
| p | medium | 15 | 0.902 | 0.79 | 1.13 ± 0.19 (1.16) | 3.68 | 1.35 |
| p | strong | 125 | 0.878 | 0.67 | - | 5.02 | 2.33 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector forward (0.836).
