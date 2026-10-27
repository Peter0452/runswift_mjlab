# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w6_w3_60_s8_40.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.859** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.59 ± 0.52 (1.52) |
| Direction error [°] | 4.99 ± 3.19 (4.42) |
| Avg ball speed [m/s] | 1.98 ± 0.42 (2.10) |
| Peak ball speed [m/s] | 4.25 ± 1.00 (4.59) |
| Distance [m] | 1.65 ± 0.62 (1.78) |
| Path length [m] | 1.66 ± 0.62 (1.79) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.855 | 50/50 | 0 | 50 | 1.05 ± 0.22 (1.09) | 4.87 ± 3.17 (4.02) | 1.75 ± 0.43 (1.70) | 3.75 ± 0.99 (3.47) | 1.32 ± 0.57 (1.23) |
| left | p | 0.870 | 50/50 | 0 | 49 | 1.53 ± 0.35 (1.52) | 5.12 ± 3.42 (5.02) | 2.05 ± 0.39 (2.14) | 4.41 ± 0.93 (4.75) | 1.76 ± 0.57 (1.89) |
| back | p | 0.858 | 50/50 | 0 | 50 | 2.24 ± 0.26 (2.23) | 4.57 ± 2.79 (3.56) | 2.15 ± 0.36 (2.29) | 4.61 ± 0.90 (5.01) | 1.90 ± 0.61 (2.10) |
| right | p | 0.853 | 50/50 | 0 | 50 | 1.53 ± 0.35 (1.47) | 5.39 ± 3.29 (5.39) | 1.98 ± 0.40 (2.06) | 4.24 ± 0.98 (4.50) | 1.64 ± 0.58 (1.69) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.860 | 100/100 | 0 | 99 | 1.60 ± 0.53 (1.52) | 4.77 ± 3.28 (3.60) | 2.01 ± 0.41 (2.12) | 4.31 ± 0.98 (4.69) | 1.69 ± 0.62 (1.81) |
| right | p | 0.858 | 100/100 | 0 | 100 | 1.58 ± 0.51 (1.49) | 5.21 ± 3.09 (5.00) | 1.95 ± 0.44 (2.06) | 4.20 ± 1.02 (4.50) | 1.61 ± 0.62 (1.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 5.17 ± 3.33 (4.57) | 1.79 ± 0.37 (1.70) | 3.84 ± 0.87 (3.74) | 1.37 ± 0.52 (1.25) |
| forward/right | p | 0.857 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.10) | 4.57 ± 2.97 (3.81) | 1.70 ± 0.48 (1.68) | 3.66 ± 1.09 (3.47) | 1.26 ± 0.60 (1.21) |
| left/left | p | 0.864 | 25/25 | 0 | 24 | 1.42 ± 0.35 (1.46) | 5.17 ± 4.03 (3.02) | 1.97 ± 0.41 (2.10) | 4.22 ± 0.98 (4.68) | 1.64 ± 0.59 (1.81) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.64 ± 0.31 (1.62) | 5.06 ± 2.68 (5.73) | 2.13 ± 0.34 (2.22) | 4.61 ± 0.84 (4.98) | 1.88 ± 0.53 (1.95) |
| back/left | p | 0.862 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.22) | 3.94 ± 2.68 (3.32) | 2.21 ± 0.33 (2.32) | 4.73 ± 0.86 (5.14) | 1.99 ± 0.61 (2.18) |
| back/right | p | 0.855 | 25/25 | 0 | 25 | 2.22 ± 0.26 (2.24) | 5.20 ± 2.76 (5.16) | 2.10 ± 0.39 (2.24) | 4.50 ± 0.92 (4.87) | 1.81 ± 0.59 (1.98) |
| right/left | p | 0.862 | 25/25 | 0 | 25 | 1.64 ± 0.32 (1.60) | 4.79 ± 2.72 (4.49) | 2.07 ± 0.39 (2.27) | 4.47 ± 0.97 (4.99) | 1.77 ± 0.59 (1.83) |
| right/right | p | 0.843 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.42) | 5.99 ± 3.68 (5.71) | 1.88 ± 0.38 (1.88) | 4.01 ± 0.93 (4.18) | 1.50 ± 0.54 (1.41) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.880 | 4.8 | 4.94 | 2.05 |
| p | normal | 0.838 | 5.2 | 3.57 | 1.25 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.802 | 0.29 | 1.95 ± 0.64 (1.84) | 3.09 | 0.96 |
| p | medium | 16 | 0.897 | 0.83 | 0.96 ± 0.21 (1.01) | 3.08 | 0.97 |
| p | strong | 126 | 0.880 | 0.66 | - | 4.94 | 2.06 |

## Notes

- p: score 0.859, 200/200 kicked, 0 fell; worst sector right (0.853).
