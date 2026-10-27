# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.857** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.58 ± 0.51 (1.59) |
| Direction error [°] | 7.53 ± 19.75 (4.58) |
| Avg ball speed [m/s] | 2.07 ± 0.52 (2.23) |
| Peak ball speed [m/s] | 4.44 ± 1.18 (4.91) |
| Distance [m] | 1.88 ± 0.74 (2.08) |
| Path length [m] | 1.89 ± 0.74 (2.09) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.863 | 50/50 | 0 | 50 | 1.07 ± 0.25 (1.06) | 5.17 ± 2.77 (4.60) | 1.98 ± 0.46 (2.06) | 4.30 ± 1.05 (4.57) | 1.75 ± 0.70 (1.86) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.52 ± 0.37 (1.54) | 4.87 ± 2.99 (4.51) | 2.10 ± 0.43 (2.25) | 4.49 ± 1.01 (4.92) | 1.90 ± 0.68 (2.11) |
| back | p | 0.826 | 50/50 | 0 | 46 | 2.19 ± 0.32 (2.19) | 14.90 ± 38.27 (5.00) | 2.06 ± 0.66 (2.33) | 4.43 ± 1.49 (5.09) | 1.93 ± 0.84 (2.27) |
| right | p | 0.872 | 50/50 | 0 | 50 | 1.54 ± 0.34 (1.61) | 5.17 ± 2.65 (4.58) | 2.13 ± 0.47 (2.29) | 4.55 ± 1.07 (5.03) | 1.94 ± 0.72 (2.16) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.864 | 100/100 | 0 | 98 | 1.58 ± 0.51 (1.60) | 6.50 ± 13.41 (4.60) | 2.09 ± 0.53 (2.30) | 4.52 ± 1.21 (4.98) | 1.94 ± 0.75 (2.18) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.58 ± 0.52 (1.56) | 8.56 ± 24.46 (4.58) | 2.04 ± 0.50 (2.15) | 4.37 ± 1.14 (4.79) | 1.82 ± 0.73 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.865 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.06) | 4.58 ± 2.21 (4.24) | 1.94 ± 0.46 (2.06) | 4.21 ± 1.08 (4.51) | 1.69 ± 0.70 (1.91) |
| forward/right | p | 0.862 | 25/25 | 0 | 25 | 1.07 ± 0.26 (0.98) | 5.76 ± 3.13 (6.42) | 2.01 ± 0.45 (2.09) | 4.39 ± 1.02 (4.63) | 1.80 ± 0.70 (1.80) |
| left/left | p | 0.876 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.40) | 4.89 ± 3.07 (4.23) | 2.09 ± 0.45 (2.34) | 4.50 ± 1.06 (4.97) | 1.91 ± 0.69 (2.21) |
| left/right | p | 0.854 | 25/25 | 0 | 25 | 1.63 ± 0.37 (1.60) | 4.84 ± 2.91 (4.89) | 2.10 ± 0.40 (2.21) | 4.48 ± 0.97 (4.87) | 1.89 ± 0.67 (2.03) |
| back/left | p | 0.838 | 25/25 | 0 | 23 | 2.20 ± 0.31 (2.24) | 10.87 ± 25.93 (4.42) | 2.11 ± 0.69 (2.36) | 4.56 ± 1.54 (5.22) | 2.02 ± 0.82 (2.29) |
| back/right | p | 0.814 | 25/25 | 0 | 23 | 2.19 ± 0.32 (2.14) | 18.92 ± 47.17 (5.03) | 2.02 ± 0.62 (2.29) | 4.30 ± 1.42 (5.03) | 1.83 ± 0.84 (2.20) |
| right/left | p | 0.875 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.66) | 5.63 ± 2.61 (5.16) | 2.23 ± 0.44 (2.33) | 4.79 ± 1.01 (5.20) | 2.11 ± 0.70 (2.38) |
| right/right | p | 0.869 | 25/25 | 0 | 25 | 1.43 ± 0.32 (1.52) | 4.71 ± 2.60 (4.45) | 2.03 ± 0.47 (2.16) | 4.32 ± 1.08 (4.74) | 1.77 ± 0.69 (1.96) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 6.6 | 5.21 | 2.36 |
| p | normal | 0.829 | 8.4 | 3.68 | 1.39 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.794 | 0.28 | 1.94 ± 0.68 (1.84) | 3.18 | 1.06 |
| p | medium | 15 | 0.892 | 0.81 | 1.01 ± 0.26 (1.03) | 3.26 | 1.12 |
| p | strong | 125 | 0.882 | 0.69 | - | 5.19 | 2.36 |

## Notes

- p: score 0.857, 200/200 kicked, 0 fell; worst sector back (0.826).
