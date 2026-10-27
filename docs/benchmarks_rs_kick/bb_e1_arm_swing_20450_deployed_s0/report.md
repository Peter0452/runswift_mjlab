# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-03-35_e1_arm_swing/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 158 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.89 ± 1.28 (1.71) |
| Direction error [°] | 20.51 ± 37.92 (7.83) |
| Avg ball speed [m/s] | 2.35 ± 0.80 (2.60) |
| Peak ball speed [m/s] | 4.89 ± 1.74 (5.69) |
| Distance [m] | 2.37 ± 1.13 (2.72) |
| Path length [m] | 2.38 ± 1.14 (2.72) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.775 | 49/50 | 0 | 40 | 1.68 ± 1.89 (1.32) | 9.91 ± 11.95 (5.95) | 2.23 ± 0.71 (2.14) | 4.65 ± 1.56 (4.27) | 2.15 ± 1.00 (1.87) |
| left | p | 0.818 | 50/50 | 0 | 40 | 1.89 ± 1.45 (1.74) | 18.25 ± 31.68 (8.17) | 2.47 ± 0.77 (2.81) | 5.17 ± 1.69 (6.09) | 2.54 ± 1.10 (3.07) |
| back | p | 0.752 | 50/50 | 0 | 39 | 2.31 ± 0.65 (2.39) | 35.51 ± 57.27 (9.93) | 2.35 ± 0.94 (2.78) | 4.89 ± 2.02 (6.02) | 2.47 ± 1.31 (2.99) |
| right | p | 0.791 | 49/50 | 0 | 39 | 1.68 ± 0.45 (1.72) | 18.11 ± 30.70 (6.77) | 2.34 ± 0.76 (2.61) | 4.86 ± 1.61 (5.57) | 2.31 ± 1.05 (2.72) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 100/100 | 0 | 83 | 1.73 ± 0.61 (1.67) | 19.91 ± 39.52 (6.70) | 2.36 ± 0.77 (2.56) | 4.91 ± 1.67 (5.65) | 2.37 ± 1.09 (2.72) |
| right | p | 0.760 | 98/100 | 0 | 75 | 2.06 ± 1.70 (1.74) | 21.12 ± 36.20 (8.87) | 2.33 ± 0.84 (2.62) | 4.87 ± 1.81 (5.69) | 2.37 ± 1.18 (2.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.816 | 25/25 | 0 | 21 | 1.35 ± 0.50 (1.28) | 9.65 ± 12.64 (5.72) | 2.24 ± 0.73 (2.17) | 4.70 ± 1.62 (4.42) | 2.19 ± 1.02 (1.94) |
| forward/right | p | 0.734 | 24/25 | 0 | 19 | 2.03 ± 2.61 (1.32) | 10.18 ± 11.17 (6.73) | 2.21 ± 0.68 (2.12) | 4.60 ± 1.50 (4.27) | 2.11 ± 0.98 (1.85) |
| left/left | p | 0.856 | 25/25 | 0 | 21 | 1.60 ± 0.37 (1.66) | 10.60 ± 15.11 (5.77) | 2.63 ± 0.57 (2.82) | 5.46 ± 1.28 (6.14) | 2.71 ± 0.91 (3.14) |
| left/right | p | 0.780 | 25/25 | 0 | 19 | 2.17 ± 1.97 (1.96) | 25.91 ± 40.76 (8.93) | 2.30 ± 0.90 (2.79) | 4.88 ± 1.97 (6.07) | 2.37 ± 1.23 (3.03) |
| back/left | p | 0.757 | 25/25 | 0 | 20 | 2.21 ± 0.69 (2.40) | 39.29 ± 62.49 (8.99) | 2.33 ± 0.90 (2.76) | 4.83 ± 1.93 (6.01) | 2.40 ± 1.30 (2.96) |
| back/right | p | 0.747 | 25/25 | 0 | 19 | 2.41 ± 0.60 (2.38) | 31.74 ± 51.26 (11.51) | 2.37 ± 0.97 (2.82) | 4.96 ± 2.10 (6.02) | 2.54 ± 1.32 (3.02) |
| right/left | p | 0.804 | 25/25 | 0 | 21 | 1.76 ± 0.46 (1.78) | 20.10 ± 37.24 (6.28) | 2.24 ± 0.78 (2.39) | 4.66 ± 1.67 (5.33) | 2.16 ± 1.00 (2.69) |
| right/right | p | 0.778 | 24/25 | 0 | 18 | 1.59 ± 0.42 (1.68) | 16.02 ± 21.70 (7.31) | 2.44 ± 0.73 (2.76) | 5.07 ± 1.52 (5.81) | 2.47 ± 1.08 (3.00) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.817 | 17.8 | 5.75 | 2.98 |
| p | normal | 0.750 | 23.2 | 4.03 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.17 | 2.31 ± 1.07 (2.30) | 3.57 | 1.41 |
| p | medium | 16 | 0.807 | 0.66 | 1.17 ± 0.37 (1.23) | 3.77 | 1.55 |
| p | strong | 126 | 0.814 | 0.75 | - | 5.64 | 2.91 |

## Notes

- p: score 0.784, 198/200 kicked, 0 fell; worst sector back (0.752).
