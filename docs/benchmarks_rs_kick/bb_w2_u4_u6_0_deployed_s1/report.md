# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w2_u4_u6.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.857** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.84 ± 0.57 (1.75) |
| Direction error [°] | 6.42 ± 13.45 (4.41) |
| Avg ball speed [m/s] | 2.51 ± 0.59 (2.68) |
| Peak ball speed [m/s] | 5.35 ± 1.41 (6.02) |
| Distance [m] | 2.61 ± 0.99 (2.91) |
| Path length [m] | 2.62 ± 0.99 (2.93) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.881 | 50/50 | 0 | 50 | 1.27 ± 0.26 (1.28) | 4.47 ± 3.09 (3.48) | 2.46 ± 0.47 (2.63) | 5.32 ± 1.19 (6.02) | 2.51 ± 0.85 (2.80) |
| left | p | 0.873 | 50/50 | 0 | 49 | 1.77 ± 0.37 (1.72) | 5.48 ± 3.49 (4.38) | 2.53 ± 0.46 (2.68) | 5.40 ± 1.20 (5.84) | 2.61 ± 0.91 (2.83) |
| back | p | 0.810 | 50/50 | 0 | 47 | 2.56 ± 0.31 (2.54) | 10.41 ± 24.45 (6.49) | 2.61 ± 0.79 (2.96) | 5.53 ± 1.76 (6.41) | 2.85 ± 1.16 (3.45) |
| right | p | 0.862 | 50/50 | 0 | 49 | 1.77 ± 0.35 (1.75) | 5.33 ± 9.06 (3.33) | 2.42 ± 0.55 (2.59) | 5.17 ± 1.39 (5.86) | 2.46 ± 0.96 (2.77) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 98 | 1.84 ± 0.58 (1.69) | 5.46 ± 3.64 (4.57) | 2.57 ± 0.47 (2.68) | 5.50 ± 1.20 (6.04) | 2.70 ± 0.92 (2.92) |
| right | p | 0.858 | 100/100 | 0 | 97 | 1.85 ± 0.55 (1.81) | 7.39 ± 18.62 (4.14) | 2.44 ± 0.68 (2.66) | 5.20 ± 1.58 (5.92) | 2.52 ± 1.05 (2.87) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.879 | 25/25 | 0 | 25 | 1.23 ± 0.25 (1.26) | 4.42 ± 3.20 (3.50) | 2.43 ± 0.44 (2.61) | 5.26 ± 1.18 (6.03) | 2.48 ± 0.84 (2.80) |
| forward/right | p | 0.884 | 25/25 | 0 | 25 | 1.30 ± 0.26 (1.30) | 4.52 ± 2.98 (3.41) | 2.50 ± 0.49 (2.65) | 5.38 ± 1.21 (5.84) | 2.54 ± 0.87 (2.79) |
| left/left | p | 0.871 | 25/25 | 0 | 24 | 1.67 ± 0.34 (1.62) | 6.11 ± 3.72 (5.46) | 2.57 ± 0.42 (2.70) | 5.51 ± 1.13 (6.02) | 2.70 ± 0.88 (2.85) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.88 ± 0.38 (1.84) | 4.85 ± 3.13 (4.14) | 2.50 ± 0.49 (2.62) | 5.28 ± 1.26 (5.73) | 2.52 ± 0.94 (2.71) |
| back/left | p | 0.810 | 25/25 | 0 | 24 | 2.59 ± 0.28 (2.54) | 7.41 ± 3.76 (7.32) | 2.82 ± 0.49 (3.01) | 5.95 ± 1.20 (6.57) | 3.12 ± 0.94 (3.52) |
| back/right | p | 0.810 | 25/25 | 0 | 23 | 2.54 ± 0.33 (2.52) | 13.41 ± 34.11 (6.42) | 2.40 ± 0.95 (2.87) | 5.11 ± 2.10 (6.29) | 2.58 ± 1.28 (3.21) |
| right/left | p | 0.862 | 25/25 | 0 | 25 | 1.86 ± 0.35 (1.80) | 3.90 ± 2.65 (3.22) | 2.47 ± 0.42 (2.58) | 5.29 ± 1.16 (5.85) | 2.50 ± 0.87 (2.76) |
| right/right | p | 0.862 | 25/25 | 0 | 24 | 1.68 ± 0.32 (1.62) | 6.77 ± 12.37 (3.70) | 2.37 ± 0.66 (2.62) | 5.05 ± 1.58 (6.00) | 2.42 ± 1.04 (3.07) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.891 | 7.8 | 6.19 | 3.21 |
| p | normal | 0.823 | 5.1 | 4.51 | 2.00 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.763 | 0.10 | 2.46 ± 0.91 (2.38) | 3.78 | 1.47 |
| p | medium | 20 | 0.889 | 0.75 | 1.25 ± 0.13 (1.26) | 3.99 | 1.59 |
| p | strong | 126 | 0.892 | 0.83 | - | 6.24 | 3.26 |

## Notes

- p: score 0.857, 200/200 kicked, 0 fell; worst sector back (0.810).
