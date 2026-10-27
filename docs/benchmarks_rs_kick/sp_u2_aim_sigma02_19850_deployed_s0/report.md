# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-08-39_u2_aim_sigma02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.769** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 1.99 ± 1.36 (1.75) |
| Direction error [°] | 17.31 ± 35.77 (5.85) |
| Avg ball speed [m/s] | 2.08 ± 0.61 (2.25) |
| Peak ball speed [m/s] | 4.60 ± 1.45 (5.11) |
| Distance [m] | 1.81 ± 0.76 (1.95) |
| Path length [m] | 1.82 ± 0.76 (1.97) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.779 | 48/50 | 0 | 42 | 1.59 ± 1.52 (1.34) | 8.05 ± 10.30 (5.08) | 2.02 ± 0.63 (2.17) | 4.44 ± 1.48 (4.45) | 1.71 ± 0.81 (1.80) |
| left | p | 0.795 | 48/50 | 0 | 42 | 1.70 ± 0.49 (1.77) | 18.01 ± 35.29 (5.45) | 2.09 ± 0.63 (2.24) | 4.66 ± 1.52 (5.10) | 1.83 ± 0.77 (1.96) |
| back | p | 0.723 | 49/50 | 0 | 42 | 2.69 ± 1.37 (2.60) | 25.27 ± 49.16 (8.51) | 2.14 ± 0.56 (2.27) | 4.76 ± 1.32 (5.19) | 1.90 ± 0.70 (2.06) |
| right | p | 0.778 | 49/50 | 0 | 42 | 1.96 ± 1.48 (1.74) | 17.74 ± 34.32 (5.03) | 2.08 ± 0.63 (2.28) | 4.54 ± 1.47 (5.12) | 1.80 ± 0.76 (1.87) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 98/100 | 0 | 89 | 1.79 ± 0.63 (1.74) | 15.78 ± 35.19 (5.49) | 2.14 ± 0.50 (2.27) | 4.73 ± 1.22 (5.15) | 1.87 ± 0.67 (1.96) |
| right | p | 0.740 | 96/100 | 0 | 79 | 2.19 ± 1.80 (1.76) | 18.87 ± 36.29 (5.97) | 2.02 ± 0.70 (2.24) | 4.47 ± 1.65 (5.06) | 1.76 ± 0.84 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.809 | 24/25 | 0 | 23 | 1.32 ± 0.33 (1.31) | 6.40 ± 9.71 (3.29) | 2.17 ± 0.47 (2.34) | 4.77 ± 1.13 (5.25) | 1.86 ± 0.63 (2.14) |
| forward/right | p | 0.749 | 24/25 | 0 | 19 | 1.86 ± 2.09 (1.35) | 9.71 ± 10.61 (5.36) | 1.87 ± 0.72 (1.89) | 4.12 ± 1.70 (4.04) | 1.57 ± 0.93 (1.51) |
| left/left | p | 0.848 | 25/25 | 0 | 23 | 1.64 ± 0.42 (1.76) | 12.43 ± 25.32 (5.32) | 2.13 ± 0.48 (2.18) | 4.74 ± 1.18 (5.03) | 1.85 ± 0.64 (1.85) |
| left/right | p | 0.742 | 23/25 | 0 | 19 | 1.77 ± 0.56 (1.98) | 24.08 ± 42.79 (5.61) | 2.05 ± 0.76 (2.34) | 4.57 ± 1.82 (5.42) | 1.81 ± 0.88 (2.13) |
| back/left | p | 0.724 | 24/25 | 0 | 21 | 2.42 ± 0.70 (2.53) | 26.14 ± 50.85 (8.54) | 2.17 ± 0.50 (2.30) | 4.84 ± 1.22 (5.30) | 1.94 ± 0.71 (2.03) |
| back/right | p | 0.722 | 25/25 | 0 | 21 | 2.95 ± 1.76 (2.64) | 24.43 ± 47.47 (7.81) | 2.10 ± 0.61 (2.24) | 4.69 ± 1.40 (5.18) | 1.86 ± 0.70 (2.06) |
| right/left | p | 0.809 | 25/25 | 0 | 22 | 1.80 ± 0.46 (1.74) | 18.20 ± 37.89 (4.43) | 2.10 ± 0.56 (2.30) | 4.59 ± 1.33 (5.14) | 1.82 ± 0.70 (2.03) |
| right/right | p | 0.747 | 24/25 | 0 | 20 | 2.14 ± 2.05 (1.70) | 17.26 ± 30.15 (5.68) | 2.04 ± 0.69 (2.20) | 4.48 ± 1.60 (5.04) | 1.78 ± 0.82 (1.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.797 | 15.7 | 5.18 | 2.10 |
| p | normal | 0.740 | 18.9 | 4.04 | 1.54 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.714 | 0.16 | 2.43 ± 0.96 (2.34) | 3.89 | 1.44 |
| p | medium | 16 | 0.776 | 0.62 | 1.34 ± 0.25 (1.36) | 4.35 | 1.73 |
| p | strong | 126 | 0.793 | 0.66 | - | 4.97 | 2.00 |

## Notes

- p: score 0.769, 194/200 kicked, 0 fell; worst sector back (0.723).
