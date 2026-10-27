# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 24 |
| Time to kick [s] | 1.89 ± 1.72 (1.48) |
| Direction error [°] | 20.13 ± 38.16 (6.37) |
| Avg ball speed [m/s] | 1.77 ± 0.62 (1.94) |
| Peak ball speed [m/s] | 3.77 ± 1.40 (4.02) |
| Distance [m] | 1.43 ± 0.72 (1.50) |
| Path length [m] | 1.43 ± 0.73 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.789 | 50/50 | 0 | 41 | 1.55 ± 1.95 (1.11) | 9.25 ± 12.52 (4.19) | 1.55 ± 0.59 (1.63) | 3.30 ± 1.28 (3.40) | 1.12 ± 0.64 (1.09) |
| left | p | 0.780 | 49/50 | 0 | 41 | 1.82 ± 1.67 (1.52) | 18.87 ± 30.97 (6.90) | 1.86 ± 0.58 (2.12) | 3.98 ± 1.35 (4.56) | 1.55 ± 0.69 (1.80) |
| back | p | 0.763 | 50/50 | 0 | 41 | 2.54 ± 1.83 (2.30) | 30.45 ± 54.40 (6.00) | 1.91 ± 0.65 (2.11) | 4.07 ± 1.47 (4.55) | 1.63 ± 0.77 (1.77) |
| right | p | 0.784 | 50/50 | 0 | 41 | 1.63 ± 1.12 (1.48) | 21.92 ± 38.88 (7.06) | 1.75 ± 0.61 (1.90) | 3.72 ± 1.35 (3.89) | 1.40 ± 0.68 (1.50) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.797 | 100/100 | 0 | 83 | 1.66 ± 1.17 (1.47) | 21.58 ± 40.64 (6.36) | 1.78 ± 0.62 (1.99) | 3.80 ± 1.38 (4.20) | 1.44 ± 0.72 (1.61) |
| right | p | 0.761 | 99/100 | 0 | 81 | 2.12 ± 2.11 (1.50) | 18.66 ± 35.42 (6.38) | 1.76 ± 0.63 (1.87) | 3.73 ± 1.41 (3.88) | 1.41 ± 0.73 (1.47) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.812 | 25/25 | 0 | 22 | 1.38 ± 1.58 (1.12) | 7.22 ± 9.62 (3.61) | 1.62 ± 0.50 (1.63) | 3.46 ± 1.08 (3.41) | 1.18 ± 0.55 (1.11) |
| forward/right | p | 0.766 | 25/25 | 0 | 19 | 1.73 ± 2.25 (1.06) | 11.28 ± 14.59 (5.90) | 1.48 ± 0.66 (1.59) | 3.14 ± 1.42 (3.29) | 1.06 ± 0.71 (1.08) |
| left/left | p | 0.834 | 25/25 | 0 | 22 | 1.36 ± 0.40 (1.46) | 15.10 ± 24.81 (7.29) | 1.90 ± 0.56 (2.13) | 4.06 ± 1.28 (4.56) | 1.60 ± 0.66 (1.78) |
| left/right | p | 0.726 | 24/25 | 0 | 19 | 2.29 ± 2.25 (1.67) | 22.80 ± 35.87 (6.90) | 1.82 ± 0.61 (2.09) | 3.90 ± 1.41 (4.58) | 1.50 ± 0.72 (1.81) |
| back/left | p | 0.773 | 25/25 | 0 | 20 | 2.38 ± 1.38 (2.26) | 32.68 ± 54.87 (7.07) | 1.90 ± 0.63 (2.06) | 4.08 ± 1.42 (4.43) | 1.62 ± 0.79 (1.77) |
| back/right | p | 0.753 | 25/25 | 0 | 21 | 2.70 ± 2.18 (2.30) | 28.22 ± 53.83 (5.17) | 1.91 ± 0.68 (2.11) | 4.05 ± 1.52 (4.58) | 1.64 ± 0.75 (1.81) |
| right/left | p | 0.770 | 25/25 | 0 | 19 | 1.51 ± 0.44 (1.52) | 31.33 ± 49.22 (7.45) | 1.69 ± 0.72 (1.91) | 3.60 ± 1.57 (4.02) | 1.37 ± 0.77 (1.57) |
| right/right | p | 0.798 | 25/25 | 0 | 22 | 1.74 ± 1.52 (1.42) | 12.50 ± 20.57 (6.54) | 1.82 ± 0.48 (1.83) | 3.84 ± 1.08 (3.88) | 1.43 ± 0.58 (1.41) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.801 | 17.4 | 4.27 | 1.69 |
| p | normal | 0.757 | 22.9 | 3.26 | 1.16 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.728 | 0.29 | 1.83 ± 1.01 (1.78) | 2.84 | 0.93 |
| p | medium | 16 | 0.841 | 0.74 | 1.00 ± 0.36 (1.15) | 3.23 | 1.14 |
| p | strong | 126 | 0.795 | 0.57 | - | 4.26 | 1.69 |

## Notes

- p: score 0.779, 199/200 kicked, 0 fell; worst sector back (0.763).
