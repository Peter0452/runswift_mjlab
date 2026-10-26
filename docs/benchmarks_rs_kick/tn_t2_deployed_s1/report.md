# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t2_control_s7/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.785** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 20 |
| Time to kick [s] | 1.97 ± 1.36 (1.64) |
| Direction error [°] | 15.49 ± 28.47 (6.68) |
| Avg ball speed [m/s] | 2.01 ± 0.63 (2.19) |
| Peak ball speed [m/s] | 4.38 ± 1.48 (4.88) |
| Distance [m] | 1.74 ± 0.75 (1.83) |
| Path length [m] | 1.75 ± 0.76 (1.84) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.796 | 50/50 | 0 | 40 | 1.61 ± 1.62 (1.27) | 9.98 ± 12.36 (6.76) | 1.95 ± 0.73 (2.19) | 4.26 ± 1.70 (4.54) | 1.70 ± 0.82 (1.82) |
| left | p | 0.813 | 50/50 | 0 | 43 | 1.84 ± 1.28 (1.60) | 14.13 ± 25.74 (5.77) | 2.01 ± 0.58 (2.16) | 4.38 ± 1.39 (4.62) | 1.72 ± 0.72 (1.79) |
| back | p | 0.728 | 50/50 | 0 | 42 | 2.73 ± 1.48 (2.54) | 25.06 ± 42.36 (9.53) | 2.06 ± 0.64 (2.24) | 4.49 ± 1.47 (5.00) | 1.82 ± 0.76 (1.98) |
| right | p | 0.803 | 50/50 | 0 | 42 | 1.71 ± 0.43 (1.70) | 12.80 ± 22.36 (5.18) | 2.03 ± 0.56 (2.13) | 4.38 ± 1.33 (4.58) | 1.73 ± 0.70 (1.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.781 | 100/100 | 0 | 83 | 1.93 ± 1.23 (1.60) | 16.82 ± 30.38 (6.44) | 1.99 ± 0.63 (2.19) | 4.36 ± 1.49 (4.97) | 1.72 ± 0.74 (1.88) |
| right | p | 0.789 | 100/100 | 0 | 84 | 2.01 ± 1.49 (1.69) | 14.16 ± 26.34 (6.69) | 2.03 ± 0.63 (2.17) | 4.39 ± 1.47 (4.57) | 1.77 ± 0.76 (1.81) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.807 | 25/25 | 0 | 19 | 1.30 ± 0.47 (1.24) | 11.17 ± 14.53 (7.28) | 1.98 ± 0.73 (2.22) | 4.35 ± 1.71 (4.93) | 1.75 ± 0.81 (1.87) |
| forward/right | p | 0.785 | 25/25 | 0 | 21 | 1.92 ± 2.20 (1.34) | 8.79 ± 9.57 (6.75) | 1.91 ± 0.73 (2.15) | 4.17 ± 1.68 (4.40) | 1.65 ± 0.82 (1.75) |
| left/left | p | 0.833 | 25/25 | 0 | 23 | 1.99 ± 1.72 (1.60) | 9.46 ± 19.12 (4.95) | 2.11 ± 0.51 (2.20) | 4.63 ± 1.24 (5.04) | 1.85 ± 0.66 (2.03) |
| left/right | p | 0.793 | 25/25 | 0 | 20 | 1.69 ± 0.53 (1.74) | 18.80 ± 30.27 (7.86) | 1.91 ± 0.62 (2.03) | 4.14 ± 1.48 (4.13) | 1.60 ± 0.76 (1.58) |
| back/left | p | 0.712 | 25/25 | 0 | 20 | 2.64 ± 1.31 (2.54) | 28.36 ± 44.74 (10.01) | 1.96 ± 0.59 (2.15) | 4.33 ± 1.41 (4.99) | 1.68 ± 0.71 (1.89) |
| back/right | p | 0.745 | 25/25 | 0 | 22 | 2.82 ± 1.63 (2.54) | 21.75 ± 39.57 (9.15) | 2.15 ± 0.67 (2.32) | 4.64 ± 1.51 (5.18) | 1.95 ± 0.78 (2.14) |
| right/left | p | 0.772 | 25/25 | 0 | 21 | 1.81 ± 0.47 (1.82) | 18.31 ± 29.88 (5.64) | 1.91 ± 0.65 (2.17) | 4.14 ± 1.53 (4.38) | 1.60 ± 0.75 (1.82) |
| right/right | p | 0.833 | 25/25 | 0 | 21 | 1.60 ± 0.35 (1.52) | 7.30 ± 6.84 (4.76) | 2.14 ± 0.43 (2.08) | 4.62 ± 1.04 (4.79) | 1.86 ± 0.63 (1.80) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.810 | 15.2 | 4.76 | 1.94 |
| p | normal | 0.760 | 15.8 | 4.00 | 1.55 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.711 | 0.15 | 2.35 ± 0.98 (2.24) | 3.65 | 1.34 |
| p | medium | 20 | 0.855 | 0.73 | 1.26 ± 0.14 (1.29) | 4.06 | 1.55 |
| p | strong | 126 | 0.806 | 0.63 | - | 4.74 | 1.95 |

## Notes

- p: score 0.785, 200/200 kicked, 0 fell; worst sector back (0.728).
