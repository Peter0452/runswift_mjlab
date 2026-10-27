# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.773** |
| Kicked / fell | 191 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.88 ± 0.89 (1.76) |
| Direction error [°] | 17.57 ± 35.73 (5.82) |
| Avg ball speed [m/s] | 1.98 ± 0.63 (2.18) |
| Peak ball speed [m/s] | 4.47 ± 1.58 (5.20) |
| Distance [m] | 1.70 ± 0.85 (1.86) |
| Path length [m] | 1.70 ± 0.85 (1.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.780 | 48/50 | 0 | 42 | 1.51 ± 1.27 (1.38) | 9.41 ± 10.19 (6.88) | 1.93 ± 0.66 (1.81) | 4.26 ± 1.61 (3.71) | 1.60 ± 0.87 (1.24) |
| left | p | 0.800 | 48/50 | 0 | 40 | 1.72 ± 0.52 (1.82) | 19.26 ± 34.95 (5.82) | 2.02 ± 0.64 (2.24) | 4.64 ± 1.64 (5.43) | 1.77 ± 0.89 (2.03) |
| back | p | 0.714 | 47/50 | 0 | 40 | 2.52 ± 0.71 (2.64) | 26.33 ± 51.30 (5.75) | 2.00 ± 0.65 (2.15) | 4.49 ± 1.60 (5.20) | 1.72 ± 0.85 (1.93) |
| right | p | 0.798 | 48/50 | 0 | 42 | 1.76 ± 0.49 (1.79) | 15.46 ± 32.06 (4.29) | 1.98 ± 0.55 (2.21) | 4.49 ± 1.45 (5.22) | 1.69 ± 0.78 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.801 | 98/100 | 0 | 88 | 1.91 ± 1.07 (1.79) | 16.02 ± 35.01 (5.82) | 2.03 ± 0.54 (2.19) | 4.58 ± 1.38 (5.27) | 1.74 ± 0.77 (1.95) |
| right | p | 0.745 | 93/100 | 0 | 76 | 1.84 ± 0.66 (1.76) | 19.20 ± 36.40 (5.69) | 1.93 ± 0.70 (2.14) | 4.35 ± 1.77 (5.06) | 1.65 ± 0.92 (1.72) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 24 | 1.66 ± 1.72 (1.38) | 7.72 ± 9.55 (5.91) | 2.05 ± 0.56 (2.18) | 4.55 ± 1.36 (5.40) | 1.74 ± 0.78 (2.09) |
| forward/right | p | 0.732 | 23/25 | 0 | 18 | 1.35 ± 0.31 (1.38) | 11.25 ± 10.53 (7.25) | 1.79 ± 0.72 (1.65) | 3.95 ± 1.79 (3.48) | 1.46 ± 0.95 (1.14) |
| left/left | p | 0.854 | 25/25 | 0 | 22 | 1.64 ± 0.43 (1.80) | 12.40 ± 22.11 (5.81) | 2.07 ± 0.52 (2.23) | 4.72 ± 1.36 (5.37) | 1.81 ± 0.74 (1.95) |
| left/right | p | 0.746 | 23/25 | 0 | 18 | 1.81 ± 0.59 (1.96) | 26.71 ± 43.72 (6.16) | 1.97 ± 0.74 (2.31) | 4.55 ± 1.90 (5.59) | 1.73 ± 1.02 (2.17) |
| back/left | p | 0.698 | 23/25 | 0 | 20 | 2.52 ± 0.79 (2.64) | 26.12 ± 52.23 (6.79) | 2.09 ± 0.49 (2.18) | 4.65 ± 1.23 (5.20) | 1.79 ± 0.76 (1.93) |
| back/right | p | 0.729 | 24/25 | 0 | 20 | 2.51 ± 0.62 (2.67) | 26.53 ± 50.41 (5.06) | 1.91 ± 0.76 (2.15) | 4.33 ± 1.88 (5.32) | 1.65 ± 0.91 (1.89) |
| right/left | p | 0.821 | 25/25 | 0 | 22 | 1.87 ± 0.51 (1.90) | 18.63 ± 39.14 (4.25) | 1.92 ± 0.57 (2.20) | 4.40 ± 1.51 (5.26) | 1.62 ± 0.78 (1.95) |
| right/right | p | 0.774 | 23/25 | 0 | 20 | 1.65 ± 0.44 (1.62) | 12.01 ± 21.36 (5.08) | 2.03 ± 0.52 (2.23) | 4.58 ± 1.38 (5.18) | 1.76 ± 0.77 (1.79) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.786 | 17.0 | 5.28 | 2.14 |
| p | normal | 0.760 | 18.1 | 3.68 | 1.27 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.723 | 0.27 | 2.02 ± 0.78 (1.81) | 3.19 | 0.99 |
| p | medium | 16 | 0.825 | 0.78 | 1.13 ± 0.22 (1.14) | 3.66 | 1.27 |
| p | strong | 126 | 0.790 | 0.69 | - | 5.17 | 2.08 |

## Notes

- p: score 0.773, 191/200 kicked, 0 fell; worst sector back (0.714).
