# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_16-13-42_u14_u6_overpower600/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 2.03 ± 1.63 (1.76) |
| Direction error [°] | 17.41 ± 36.37 (4.90) |
| Avg ball speed [m/s] | 2.11 ± 0.63 (2.25) |
| Peak ball speed [m/s] | 4.57 ± 1.48 (5.12) |
| Distance [m] | 1.90 ± 0.81 (2.00) |
| Path length [m] | 1.90 ± 0.82 (2.02) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.779 | 49/50 | 0 | 41 | 1.75 ± 1.96 (1.36) | 8.64 ± 11.09 (5.10) | 2.02 ± 0.64 (2.13) | 4.37 ± 1.53 (4.26) | 1.78 ± 0.84 (1.72) |
| left | p | 0.805 | 49/50 | 0 | 42 | 1.86 ± 1.49 (1.80) | 19.39 ± 36.28 (5.05) | 2.13 ± 0.60 (2.25) | 4.67 ± 1.44 (5.23) | 1.94 ± 0.79 (2.13) |
| back | p | 0.758 | 50/50 | 0 | 43 | 2.80 ± 1.88 (2.56) | 24.99 ± 51.30 (4.79) | 2.20 ± 0.71 (2.34) | 4.71 ± 1.59 (5.45) | 2.03 ± 0.87 (2.24) |
| right | p | 0.789 | 48/50 | 0 | 40 | 1.69 ± 0.45 (1.76) | 16.44 ± 32.36 (3.63) | 2.08 ± 0.53 (2.19) | 4.53 ± 1.30 (4.95) | 1.82 ± 0.71 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.811 | 100/100 | 0 | 86 | 1.93 ± 1.40 (1.76) | 17.25 ± 37.43 (4.90) | 2.14 ± 0.58 (2.26) | 4.67 ± 1.39 (5.21) | 1.94 ± 0.77 (2.06) |
| right | p | 0.754 | 96/100 | 0 | 80 | 2.13 ± 1.84 (1.76) | 17.57 ± 35.22 (4.91) | 2.07 ± 0.67 (2.22) | 4.47 ± 1.55 (4.80) | 1.85 ± 0.85 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.811 | 25/25 | 0 | 21 | 1.63 ± 1.73 (1.32) | 8.06 ± 11.12 (4.91) | 2.13 ± 0.60 (2.16) | 4.62 ± 1.42 (4.37) | 1.91 ± 0.79 (1.89) |
| forward/right | p | 0.747 | 24/25 | 0 | 20 | 1.88 ± 2.16 (1.36) | 9.25 ± 11.02 (5.82) | 1.91 ± 0.67 (1.95) | 4.11 ± 1.59 (4.00) | 1.63 ± 0.88 (1.55) |
| left/left | p | 0.853 | 25/25 | 0 | 23 | 1.60 ± 0.41 (1.76) | 11.84 ± 22.58 (4.96) | 2.23 ± 0.49 (2.25) | 4.90 ± 1.19 (5.31) | 2.07 ± 0.69 (2.20) |
| left/right | p | 0.756 | 24/25 | 0 | 19 | 2.13 ± 2.05 (1.91) | 27.26 ± 45.12 (5.11) | 2.02 ± 0.67 (2.24) | 4.44 ± 1.62 (5.18) | 1.81 ± 0.86 (2.11) |
| back/left | p | 0.765 | 25/25 | 0 | 21 | 2.72 ± 1.90 (2.56) | 28.80 ± 56.29 (4.87) | 2.17 ± 0.64 (2.36) | 4.72 ± 1.47 (5.46) | 1.99 ± 0.83 (2.25) |
| back/right | p | 0.751 | 25/25 | 0 | 22 | 2.89 ± 1.85 (2.68) | 21.18 ± 45.45 (4.22) | 2.24 ± 0.77 (2.32) | 4.71 ± 1.70 (5.25) | 2.08 ± 0.91 (2.23) |
| right/left | p | 0.815 | 25/25 | 0 | 21 | 1.79 ± 0.47 (1.84) | 20.31 ± 39.32 (3.88) | 2.05 ± 0.58 (2.25) | 4.46 ± 1.42 (5.10) | 1.79 ± 0.76 (1.93) |
| right/right | p | 0.763 | 23/25 | 0 | 19 | 1.58 ± 0.40 (1.70) | 12.24 ± 21.69 (3.57) | 2.11 ± 0.47 (2.13) | 4.61 ± 1.14 (4.92) | 1.86 ± 0.65 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.808 | 15.3 | 5.20 | 2.25 |
| p | normal | 0.757 | 19.5 | 3.96 | 1.55 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.16 | 2.31 ± 0.97 (2.23) | 3.65 | 1.37 |
| p | medium | 16 | 0.845 | 0.70 | 1.26 ± 0.22 (1.24) | 4.08 | 1.63 |
| p | strong | 126 | 0.805 | 0.68 | - | 5.07 | 2.18 |

## Notes

- p: score 0.783, 196/200 kicked, 0 fell; worst sector back (0.758).
