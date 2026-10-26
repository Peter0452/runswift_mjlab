# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 20 |
| Time to kick [s] | 2.15 ± 1.84 (1.80) |
| Direction error [°] | 17.86 ± 33.80 (5.54) |
| Avg ball speed [m/s] | 2.27 ± 0.85 (2.46) |
| Peak ball speed [m/s] | 4.81 ± 1.88 (5.57) |
| Distance [m] | 2.30 ± 1.13 (2.62) |
| Path length [m] | 2.31 ± 1.14 (2.63) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.813 | 50/50 | 0 | 45 | 1.65 ± 2.01 (1.26) | 10.50 ± 19.42 (4.81) | 2.26 ± 0.74 (2.36) | 4.83 ± 1.67 (5.47) | 2.23 ± 0.98 (2.46) |
| left | p | 0.775 | 50/50 | 0 | 41 | 2.37 ± 2.11 (1.87) | 16.28 ± 25.26 (6.46) | 2.24 ± 0.91 (2.43) | 4.74 ± 1.97 (5.39) | 2.26 ± 1.17 (2.38) |
| back | p | 0.745 | 49/50 | 0 | 41 | 2.77 ± 1.81 (2.54) | 21.76 ± 41.90 (5.91) | 2.41 ± 0.85 (2.83) | 5.11 ± 1.90 (6.19) | 2.56 ± 1.18 (3.18) |
| right | p | 0.779 | 49/50 | 0 | 39 | 1.81 ± 0.94 (1.78) | 23.08 ± 41.52 (5.72) | 2.17 ± 0.89 (2.39) | 4.57 ± 1.94 (5.36) | 2.15 ± 1.15 (2.27) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.781 | 99/100 | 0 | 80 | 2.01 ± 1.39 (1.76) | 20.42 ± 37.28 (5.72) | 2.28 ± 0.90 (2.55) | 4.85 ± 1.98 (5.82) | 2.35 ± 1.18 (2.77) |
| right | p | 0.775 | 99/100 | 0 | 86 | 2.29 ± 2.18 (1.86) | 15.30 ± 29.69 (5.43) | 2.26 ± 0.80 (2.39) | 4.78 ± 1.79 (4.91) | 2.24 ± 1.08 (2.13) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.814 | 25/25 | 0 | 22 | 1.28 ± 0.33 (1.32) | 12.79 ± 24.81 (4.87) | 2.18 ± 0.81 (2.31) | 4.64 ± 1.84 (4.41) | 2.15 ± 1.01 (1.88) |
| forward/right | p | 0.812 | 25/25 | 0 | 23 | 2.02 ± 2.77 (1.24) | 8.22 ± 11.31 (4.75) | 2.35 ± 0.66 (2.50) | 5.02 ± 1.47 (5.55) | 2.31 ± 0.93 (2.60) |
| left/left | p | 0.774 | 25/25 | 0 | 20 | 2.38 ± 2.24 (1.80) | 15.04 ± 21.10 (6.67) | 2.28 ± 0.94 (2.54) | 4.83 ± 2.01 (5.82) | 2.34 ± 1.19 (2.90) |
| left/right | p | 0.776 | 25/25 | 0 | 21 | 2.35 ± 1.98 (1.92) | 17.52 ± 28.77 (6.28) | 2.21 ± 0.87 (2.32) | 4.65 ± 1.92 (4.75) | 2.18 ± 1.15 (2.10) |
| back/left | p | 0.763 | 24/25 | 0 | 20 | 2.32 ± 0.59 (2.51) | 19.76 ± 37.11 (5.56) | 2.53 ± 0.76 (2.84) | 5.39 ± 1.68 (6.23) | 2.73 ± 1.12 (3.25) |
| back/right | p | 0.728 | 25/25 | 0 | 21 | 3.20 ± 2.39 (2.54) | 23.67 ± 45.96 (6.09) | 2.29 ± 0.92 (2.71) | 4.84 ± 2.05 (5.96) | 2.39 ± 1.21 (2.87) |
| right/left | p | 0.772 | 25/25 | 0 | 18 | 2.05 ± 1.20 (1.82) | 34.06 ± 53.36 (6.32) | 2.17 ± 1.02 (2.61) | 4.56 ± 2.22 (5.75) | 2.20 ± 1.30 (2.64) |
| right/right | p | 0.786 | 24/25 | 0 | 21 | 1.57 ± 0.41 (1.65) | 11.65 ± 17.24 (5.00) | 2.18 ± 0.72 (2.16) | 4.59 ± 1.61 (4.36) | 2.09 ± 0.96 (1.91) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.817 | 18.4 | 5.44 | 2.73 |
| p | normal | 0.740 | 17.3 | 4.18 | 1.86 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.710 | 0.16 | 2.20 ± 1.03 (2.14) | 3.68 | 1.49 |
| p | medium | 15 | 0.788 | 0.58 | 1.06 ± 0.49 (1.21) | 3.42 | 1.37 |
| p | strong | 125 | 0.810 | 0.74 | - | 5.53 | 2.80 |

## Notes

- p: score 0.778, 198/200 kicked, 0 fell; worst sector back (0.745).
