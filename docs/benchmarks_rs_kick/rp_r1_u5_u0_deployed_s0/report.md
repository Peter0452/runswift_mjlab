# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r1_u5_u0.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.804** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 1.94 ± 1.32 (1.76) |
| Direction error [°] | 19.30 ± 39.19 (5.56) |
| Avg ball speed [m/s] | 2.36 ± 0.88 (2.60) |
| Peak ball speed [m/s] | 4.92 ± 1.89 (5.77) |
| Distance [m] | 2.41 ± 1.24 (2.84) |
| Path length [m] | 2.42 ± 1.24 (2.85) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.822 | 50/50 | 0 | 44 | 1.65 ± 1.76 (1.33) | 7.50 ± 12.29 (3.10) | 2.28 ± 0.77 (2.26) | 4.72 ± 1.68 (4.38) | 2.21 ± 1.12 (1.84) |
| left | p | 0.814 | 49/50 | 0 | 43 | 1.91 ± 1.29 (1.82) | 17.30 ± 33.98 (6.01) | 2.43 ± 0.77 (2.66) | 5.13 ± 1.71 (5.93) | 2.53 ± 1.14 (2.97) |
| back | p | 0.761 | 50/50 | 0 | 38 | 2.31 ± 0.64 (2.44) | 36.75 ± 58.45 (7.95) | 2.36 ± 1.07 (2.91) | 4.92 ± 2.27 (6.28) | 2.53 ± 1.45 (3.27) |
| right | p | 0.819 | 50/50 | 0 | 42 | 1.90 ± 1.26 (1.76) | 15.60 ± 30.83 (4.76) | 2.37 ± 0.86 (2.62) | 4.91 ± 1.81 (5.91) | 2.38 ± 1.18 (2.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.829 | 100/100 | 0 | 87 | 1.77 ± 0.60 (1.74) | 17.78 ± 38.99 (5.15) | 2.42 ± 0.81 (2.65) | 5.04 ± 1.78 (5.78) | 2.48 ± 1.18 (2.86) |
| right | p | 0.779 | 99/100 | 0 | 80 | 2.11 ± 1.76 (1.76) | 20.83 ± 39.32 (5.87) | 2.31 ± 0.93 (2.56) | 4.79 ± 1.99 (5.63) | 2.34 ± 1.29 (2.61) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.856 | 25/25 | 0 | 23 | 1.30 ± 0.29 (1.28) | 6.25 ± 12.08 (3.01) | 2.31 ± 0.77 (2.39) | 4.79 ± 1.69 (4.47) | 2.25 ± 1.10 (1.96) |
| forward/right | p | 0.788 | 25/25 | 0 | 21 | 1.99 ± 2.42 (1.38) | 8.74 ± 12.38 (3.14) | 2.25 ± 0.78 (2.22) | 4.65 ± 1.67 (4.29) | 2.17 ± 1.14 (1.84) |
| left/left | p | 0.871 | 25/25 | 0 | 24 | 1.65 ± 0.39 (1.78) | 9.04 ± 15.91 (6.01) | 2.56 ± 0.57 (2.69) | 5.40 ± 1.31 (6.03) | 2.68 ± 0.93 (3.03) |
| left/right | p | 0.756 | 24/25 | 0 | 19 | 2.17 ± 1.76 (2.01) | 25.91 ± 44.14 (5.97) | 2.31 ± 0.91 (2.57) | 4.84 ± 2.01 (5.66) | 2.37 ± 1.31 (2.67) |
| back/left | p | 0.768 | 25/25 | 0 | 19 | 2.31 ± 0.68 (2.46) | 37.41 ± 60.59 (8.79) | 2.46 ± 0.97 (3.04) | 5.13 ± 2.10 (6.47) | 2.66 ± 1.41 (3.56) |
| back/right | p | 0.755 | 25/25 | 0 | 19 | 2.31 ± 0.61 (2.38) | 36.09 ± 56.23 (7.21) | 2.26 ± 1.14 (2.89) | 4.70 ± 2.41 (6.25) | 2.40 ± 1.47 (3.27) |
| right/left | p | 0.820 | 25/25 | 0 | 21 | 1.83 ± 0.48 (1.84) | 18.40 ± 37.62 (4.56) | 2.34 ± 0.87 (2.77) | 4.85 ± 1.86 (5.99) | 2.34 ± 1.17 (2.85) |
| right/right | p | 0.819 | 25/25 | 0 | 21 | 1.97 ± 1.72 (1.74) | 12.80 ± 21.68 (4.96) | 2.41 ± 0.86 (2.56) | 4.96 ± 1.77 (5.83) | 2.42 ± 1.18 (2.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.849 | 14.6 | 5.89 | 3.10 |
| p | normal | 0.759 | 23.9 | 3.95 | 1.73 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.16 | 2.19 ± 1.17 (2.11) | 3.37 | 1.32 |
| p | medium | 16 | 0.810 | 0.62 | 1.20 ± 0.38 (1.28) | 3.89 | 1.63 |
| p | strong | 126 | 0.842 | 0.77 | - | 5.76 | 3.02 |

## Notes

- p: score 0.804, 199/200 kicked, 0 fell; worst sector back (0.761).
