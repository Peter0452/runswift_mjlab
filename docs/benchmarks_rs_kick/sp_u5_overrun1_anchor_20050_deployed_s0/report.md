# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.777** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 2.16 ± 1.88 (1.75) |
| Direction error [°] | 18.41 ± 37.85 (5.02) |
| Avg ball speed [m/s] | 1.89 ± 0.56 (2.05) |
| Peak ball speed [m/s] | 4.51 ± 1.39 (4.92) |
| Distance [m] | 1.75 ± 0.73 (1.88) |
| Path length [m] | 1.76 ± 0.73 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.784 | 50/50 | 0 | 42 | 1.86 ± 2.12 (1.32) | 8.92 ± 10.39 (5.37) | 1.78 ± 0.56 (1.90) | 4.26 ± 1.42 (4.37) | 1.59 ± 0.73 (1.63) |
| left | p | 0.810 | 50/50 | 0 | 42 | 2.06 ± 1.99 (1.76) | 19.12 ± 35.59 (5.05) | 1.93 ± 0.48 (2.08) | 4.64 ± 1.20 (5.12) | 1.82 ± 0.66 (1.97) |
| back | p | 0.745 | 50/50 | 0 | 42 | 2.83 ± 1.74 (2.57) | 28.05 ± 55.32 (4.34) | 1.93 ± 0.65 (2.11) | 4.56 ± 1.54 (5.00) | 1.83 ± 0.78 (1.88) |
| right | p | 0.768 | 48/50 | 0 | 40 | 1.89 ± 1.38 (1.74) | 17.49 ± 33.14 (5.76) | 1.91 ± 0.53 (2.07) | 4.59 ± 1.32 (4.95) | 1.77 ± 0.71 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 99/100 | 0 | 86 | 1.96 ± 1.40 (1.74) | 16.23 ± 35.89 (4.26) | 1.94 ± 0.52 (2.05) | 4.67 ± 1.24 (5.02) | 1.83 ± 0.70 (1.92) |
| right | p | 0.754 | 99/100 | 0 | 80 | 2.37 ± 2.23 (1.76) | 20.58 ± 39.60 (5.70) | 1.83 ± 0.60 (2.05) | 4.35 ± 1.50 (4.74) | 1.67 ± 0.75 (1.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.805 | 25/25 | 0 | 22 | 1.66 ± 1.80 (1.30) | 8.37 ± 11.63 (4.85) | 1.81 ± 0.53 (1.91) | 4.41 ± 1.31 (4.66) | 1.67 ± 0.69 (1.66) |
| forward/right | p | 0.762 | 25/25 | 0 | 20 | 2.07 ± 2.39 (1.34) | 9.47 ± 8.94 (7.32) | 1.75 ± 0.59 (1.88) | 4.10 ± 1.51 (4.26) | 1.52 ± 0.76 (1.56) |
| left/left | p | 0.848 | 25/25 | 0 | 22 | 1.60 ± 0.42 (1.70) | 12.52 ± 23.68 (4.95) | 2.00 ± 0.44 (2.08) | 4.83 ± 1.07 (5.24) | 1.92 ± 0.59 (2.08) |
| left/right | p | 0.771 | 25/25 | 0 | 20 | 2.52 ± 2.71 (1.92) | 25.73 ± 43.42 (5.14) | 1.86 ± 0.52 (2.07) | 4.44 ± 1.28 (5.10) | 1.71 ± 0.71 (1.93) |
| back/left | p | 0.772 | 25/25 | 0 | 22 | 2.76 ± 1.79 (2.52) | 22.66 ± 51.29 (4.02) | 2.07 ± 0.44 (2.16) | 4.90 ± 0.99 (5.19) | 1.99 ± 0.65 (1.90) |
| back/right | p | 0.719 | 25/25 | 0 | 20 | 2.89 ± 1.69 (2.64) | 33.44 ± 58.59 (5.09) | 1.78 ± 0.77 (2.09) | 4.21 ± 1.88 (4.70) | 1.67 ± 0.87 (1.88) |
| right/left | p | 0.771 | 24/25 | 0 | 20 | 1.81 ± 0.53 (1.80) | 21.58 ± 41.21 (4.61) | 1.88 ± 0.61 (2.02) | 4.52 ± 1.48 (4.86) | 1.75 ± 0.79 (1.88) |
| right/right | p | 0.764 | 24/25 | 0 | 20 | 1.97 ± 1.87 (1.66) | 13.40 ± 21.56 (6.13) | 1.95 ± 0.43 (2.10) | 4.66 ± 1.15 (5.11) | 1.78 ± 0.62 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.802 | 17.1 | 5.03 | 2.03 |
| p | normal | 0.751 | 19.7 | 4.00 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.708 | 0.15 | 2.34 ± 1.04 (2.11) | 3.68 | 1.32 |
| p | medium | 16 | 0.823 | 0.66 | 1.30 ± 0.23 (1.34) | 4.23 | 1.63 |
| p | strong | 126 | 0.802 | 0.66 | - | 4.93 | 1.97 |

## Notes

- p: score 0.777, 198/200 kicked, 0 fell; worst sector back (0.745).
