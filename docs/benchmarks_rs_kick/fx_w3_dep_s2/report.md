# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.88 ± 0.56 (1.86) |
| Direction error [°] | 7.01 ± 16.96 (4.40) |
| Avg ball speed [m/s] | 2.38 ± 0.57 (2.53) |
| Peak ball speed [m/s] | 5.09 ± 1.36 (5.74) |
| Distance [m] | 2.37 ± 0.92 (2.66) |
| Path length [m] | 2.38 ± 0.93 (2.67) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.878 | 50/50 | 0 | 50 | 1.32 ± 0.25 (1.29) | 4.39 ± 3.15 (3.54) | 2.28 ± 0.47 (2.35) | 4.96 ± 1.19 (5.48) | 2.21 ± 0.81 (2.32) |
| left | p | 0.867 | 50/50 | 0 | 49 | 1.81 ± 0.38 (1.84) | 5.28 ± 3.80 (5.12) | 2.44 ± 0.56 (2.61) | 5.17 ± 1.33 (5.83) | 2.43 ± 0.98 (2.62) |
| back | p | 0.793 | 50/50 | 0 | 46 | 2.55 ± 0.41 (2.53) | 13.41 ± 32.48 (5.44) | 2.38 ± 0.72 (2.70) | 5.06 ± 1.67 (6.02) | 2.43 ± 1.03 (2.97) |
| right | p | 0.877 | 50/50 | 0 | 48 | 1.82 ± 0.35 (1.88) | 4.95 ± 3.96 (3.69) | 2.43 ± 0.48 (2.62) | 5.17 ± 1.17 (5.79) | 2.42 ± 0.84 (2.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.857 | 100/100 | 0 | 95 | 1.86 ± 0.56 (1.84) | 7.63 ± 18.50 (4.21) | 2.41 ± 0.60 (2.62) | 5.16 ± 1.41 (5.86) | 2.44 ± 0.94 (2.83) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.89 ± 0.57 (1.87) | 6.38 ± 15.23 (4.79) | 2.35 ± 0.54 (2.50) | 5.01 ± 1.30 (5.62) | 2.31 ± 0.90 (2.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.875 | 25/25 | 0 | 25 | 1.32 ± 0.26 (1.30) | 4.11 ± 2.89 (3.40) | 2.25 ± 0.44 (2.32) | 4.87 ± 1.20 (5.23) | 2.17 ± 0.82 (2.31) |
| forward/right | p | 0.881 | 25/25 | 0 | 25 | 1.33 ± 0.25 (1.26) | 4.66 ± 3.37 (3.63) | 2.31 ± 0.49 (2.51) | 5.04 ± 1.18 (5.67) | 2.24 ± 0.80 (2.34) |
| left/left | p | 0.873 | 25/25 | 0 | 24 | 1.69 ± 0.36 (1.70) | 5.73 ± 4.26 (5.20) | 2.48 ± 0.54 (2.64) | 5.24 ± 1.27 (5.95) | 2.50 ± 0.94 (2.97) |
| left/right | p | 0.861 | 25/25 | 0 | 25 | 1.93 ± 0.36 (1.94) | 4.83 ± 3.20 (5.09) | 2.39 ± 0.57 (2.53) | 5.09 ± 1.39 (5.79) | 2.37 ± 1.01 (2.50) |
| back/left | p | 0.792 | 25/25 | 0 | 22 | 2.51 ± 0.45 (2.54) | 16.10 ± 35.08 (5.65) | 2.41 ± 0.83 (2.78) | 5.15 ± 1.87 (6.07) | 2.54 ± 1.10 (2.99) |
| back/right | p | 0.793 | 25/25 | 0 | 24 | 2.60 ± 0.35 (2.52) | 10.72 ± 29.42 (5.39) | 2.34 ± 0.59 (2.49) | 4.96 ± 1.45 (5.57) | 2.32 ± 0.94 (2.74) |
| right/left | p | 0.889 | 25/25 | 0 | 24 | 1.93 ± 0.33 (2.00) | 4.59 ± 3.97 (3.09) | 2.49 ± 0.46 (2.68) | 5.37 ± 1.15 (5.93) | 2.54 ± 0.83 (2.91) |
| right/right | p | 0.865 | 25/25 | 0 | 24 | 1.71 ± 0.33 (1.72) | 5.30 ± 3.93 (4.16) | 2.37 ± 0.48 (2.48) | 4.97 ± 1.17 (5.57) | 2.30 ± 0.83 (2.61) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.887 | 6.8 | 5.99 | 2.98 |
| p | normal | 0.820 | 7.2 | 4.18 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.780 | 0.18 | 2.21 ± 0.68 (2.05) | 3.64 | 1.35 |
| p | medium | 15 | 0.897 | 0.77 | 1.06 ± 0.29 (1.16) | 3.44 | 1.26 |
| p | strong | 125 | 0.884 | 0.80 | - | 5.98 | 2.99 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.793).
