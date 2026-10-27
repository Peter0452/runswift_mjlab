# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r6_u5_75_u0_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.777** |
| Kicked / fell | 192 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 1.94 ± 1.26 (1.75) |
| Direction error [°] | 15.91 ± 35.41 (4.30) |
| Avg ball speed [m/s] | 2.07 ± 0.58 (2.25) |
| Peak ball speed [m/s] | 4.60 ± 1.42 (5.03) |
| Distance [m] | 1.79 ± 0.74 (1.88) |
| Path length [m] | 1.80 ± 0.74 (1.89) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.790 | 49/50 | 0 | 43 | 1.70 ± 1.82 (1.34) | 7.72 ± 10.63 (3.42) | 2.05 ± 0.59 (2.13) | 4.48 ± 1.43 (4.33) | 1.74 ± 0.76 (1.72) |
| left | p | 0.809 | 48/50 | 0 | 43 | 1.71 ± 0.48 (1.77) | 14.84 ± 30.84 (4.41) | 2.08 ± 0.58 (2.27) | 4.71 ± 1.47 (5.20) | 1.82 ± 0.73 (1.97) |
| back | p | 0.722 | 47/50 | 0 | 41 | 2.63 ± 1.40 (2.56) | 24.71 ± 52.71 (4.78) | 2.11 ± 0.58 (2.29) | 4.65 ± 1.36 (4.96) | 1.82 ± 0.70 (1.87) |
| right | p | 0.785 | 48/50 | 0 | 41 | 1.71 ± 0.48 (1.76) | 16.72 ± 32.89 (4.04) | 2.06 ± 0.57 (2.21) | 4.55 ± 1.40 (4.99) | 1.78 ± 0.77 (1.92) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 99/100 | 0 | 88 | 1.87 ± 1.13 (1.74) | 15.49 ± 35.52 (4.06) | 2.10 ± 0.51 (2.27) | 4.67 ± 1.28 (5.04) | 1.81 ± 0.69 (1.91) |
| right | p | 0.742 | 93/100 | 0 | 80 | 2.00 ± 1.39 (1.76) | 16.36 ± 35.28 (4.40) | 2.04 ± 0.64 (2.24) | 4.51 ± 1.55 (4.98) | 1.77 ± 0.79 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 23 | 1.66 ± 1.94 (1.30) | 6.04 ± 8.83 (2.59) | 2.15 ± 0.47 (2.28) | 4.75 ± 1.18 (5.05) | 1.84 ± 0.65 (1.94) |
| forward/right | p | 0.748 | 24/25 | 0 | 20 | 1.75 ± 1.68 (1.36) | 9.47 ± 11.97 (3.93) | 1.95 ± 0.67 (1.98) | 4.21 ± 1.60 (4.03) | 1.63 ± 0.84 (1.55) |
| left/left | p | 0.855 | 25/25 | 0 | 23 | 1.62 ± 0.42 (1.72) | 11.36 ± 22.05 (4.42) | 2.10 ± 0.47 (2.27) | 4.73 ± 1.24 (5.15) | 1.82 ± 0.64 (1.91) |
| left/right | p | 0.763 | 23/25 | 0 | 20 | 1.81 ± 0.51 (1.96) | 18.63 ± 37.80 (4.40) | 2.05 ± 0.67 (2.34) | 4.69 ± 1.69 (5.52) | 1.82 ± 0.82 (2.19) |
| back/left | p | 0.752 | 24/25 | 0 | 21 | 2.41 ± 0.71 (2.53) | 23.99 ± 52.25 (4.35) | 2.16 ± 0.45 (2.30) | 4.82 ± 1.13 (5.11) | 1.87 ± 0.66 (1.88) |
| back/right | p | 0.692 | 23/25 | 0 | 20 | 2.86 ± 1.84 (2.56) | 25.46 ± 53.18 (4.86) | 2.06 ± 0.67 (2.26) | 4.47 ± 1.54 (4.90) | 1.78 ± 0.73 (1.84) |
| right/left | p | 0.807 | 25/25 | 0 | 21 | 1.81 ± 0.51 (1.80) | 20.91 ± 40.07 (4.06) | 2.01 ± 0.62 (2.14) | 4.40 ± 1.48 (4.95) | 1.72 ± 0.79 (1.92) |
| right/right | p | 0.764 | 23/25 | 0 | 20 | 1.61 ± 0.43 (1.74) | 12.16 ± 21.74 (3.26) | 2.11 ± 0.50 (2.22) | 4.71 ± 1.29 (5.08) | 1.84 ± 0.73 (1.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.798 | 13.8 | 5.28 | 2.13 |
| p | normal | 0.755 | 17.9 | 3.94 | 1.46 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.15 | 2.29 ± 0.98 (2.13) | 3.62 | 1.30 |
| p | medium | 16 | 0.813 | 0.71 | 1.25 ± 0.21 (1.30) | 4.04 | 1.53 |
| p | strong | 126 | 0.802 | 0.68 | - | 5.13 | 2.05 |

## Notes

- p: score 0.777, 192/200 kicked, 0 fell; worst sector back (0.722).
