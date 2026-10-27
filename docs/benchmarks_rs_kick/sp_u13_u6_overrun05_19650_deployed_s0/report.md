# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-32-24_u13_u6_overrun05/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.774** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.92 ± 1.19 (1.76) |
| Direction error [°] | 17.45 ± 35.92 (5.72) |
| Avg ball speed [m/s] | 2.04 ± 0.61 (2.19) |
| Peak ball speed [m/s] | 4.55 ± 1.49 (5.07) |
| Distance [m] | 1.83 ± 0.79 (1.90) |
| Path length [m] | 1.84 ± 0.79 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 49/50 | 0 | 42 | 1.60 ± 1.54 (1.36) | 8.57 ± 10.54 (5.70) | 1.97 ± 0.64 (2.02) | 4.36 ± 1.58 (4.16) | 1.73 ± 0.84 (1.61) |
| left | p | 0.795 | 49/50 | 0 | 42 | 1.89 ± 1.47 (1.76) | 19.58 ± 36.07 (5.73) | 2.02 ± 0.63 (2.16) | 4.55 ± 1.52 (5.20) | 1.82 ± 0.81 (1.94) |
| back | p | 0.728 | 48/50 | 0 | 41 | 2.45 ± 0.65 (2.54) | 25.48 ± 50.82 (6.76) | 2.15 ± 0.60 (2.26) | 4.75 ± 1.44 (5.26) | 1.99 ± 0.76 (2.13) |
| right | p | 0.787 | 48/50 | 0 | 41 | 1.73 ± 0.48 (1.77) | 16.30 ± 32.24 (4.43) | 2.03 ± 0.54 (2.19) | 4.52 ± 1.37 (4.93) | 1.78 ± 0.72 (1.85) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.806 | 99/100 | 0 | 88 | 1.80 ± 0.65 (1.74) | 16.18 ± 35.07 (5.57) | 2.09 ± 0.55 (2.19) | 4.66 ± 1.36 (5.06) | 1.88 ± 0.75 (1.90) |
| right | p | 0.742 | 95/100 | 0 | 78 | 2.04 ± 1.56 (1.76) | 18.77 ± 36.74 (5.81) | 1.99 ± 0.66 (2.19) | 4.42 ± 1.60 (5.08) | 1.77 ± 0.83 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 23 | 1.36 ± 0.40 (1.32) | 6.79 ± 10.53 (4.67) | 2.08 ± 0.61 (2.08) | 4.63 ± 1.53 (4.26) | 1.88 ± 0.82 (1.70) |
| forward/right | p | 0.735 | 24/25 | 0 | 19 | 1.85 ± 2.13 (1.37) | 10.43 ± 10.23 (6.41) | 1.86 ± 0.65 (1.93) | 4.08 ± 1.57 (4.08) | 1.57 ± 0.83 (1.60) |
| left/left | p | 0.847 | 25/25 | 0 | 23 | 1.61 ± 0.42 (1.64) | 12.53 ± 22.88 (5.30) | 2.13 ± 0.47 (2.24) | 4.81 ± 1.14 (5.24) | 1.95 ± 0.64 (1.94) |
| left/right | p | 0.743 | 24/25 | 0 | 19 | 2.18 ± 2.02 (1.94) | 26.92 ± 44.78 (6.24) | 1.90 ± 0.74 (2.13) | 4.27 ± 1.80 (5.14) | 1.69 ± 0.93 (1.97) |
| back/left | p | 0.733 | 24/25 | 0 | 21 | 2.43 ± 0.70 (2.54) | 25.75 ± 51.47 (6.76) | 2.17 ± 0.46 (2.22) | 4.81 ± 1.14 (5.20) | 1.98 ± 0.72 (2.02) |
| back/right | p | 0.724 | 24/25 | 0 | 20 | 2.48 ± 0.60 (2.54) | 25.20 ± 50.17 (7.07) | 2.12 ± 0.71 (2.29) | 4.70 ± 1.70 (5.32) | 2.00 ± 0.80 (2.27) |
| right/left | p | 0.807 | 25/25 | 0 | 21 | 1.83 ± 0.50 (1.86) | 20.01 ± 38.58 (4.46) | 1.98 ± 0.62 (2.16) | 4.40 ± 1.52 (4.50) | 1.72 ± 0.79 (1.84) |
| right/right | p | 0.766 | 23/25 | 0 | 20 | 1.62 ± 0.44 (1.74) | 12.27 ± 22.81 (4.43) | 2.08 ± 0.44 (2.19) | 4.66 ± 1.17 (5.15) | 1.84 ± 0.64 (1.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.797 | 15.0 | 5.22 | 2.18 |
| p | normal | 0.751 | 19.8 | 3.90 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.16 | 2.30 ± 0.99 (2.17) | 3.63 | 1.34 |
| p | medium | 16 | 0.806 | 0.67 | 1.18 ± 0.34 (1.29) | 3.81 | 1.46 |
| p | strong | 126 | 0.797 | 0.68 | - | 5.07 | 2.10 |

## Notes

- p: score 0.774, 194/200 kicked, 0 fell; worst sector back (0.728).
