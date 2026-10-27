# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_23-01-41_q3_speed_fastmix/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.07 ± 1.78 (1.70) |
| Direction error [°] | 19.71 ± 39.29 (5.10) |
| Avg ball speed [m/s] | 2.03 ± 0.66 (2.23) |
| Peak ball speed [m/s] | 4.60 ± 1.65 (5.16) |
| Distance [m] | 1.79 ± 0.85 (1.90) |
| Path length [m] | 1.80 ± 0.85 (1.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.791 | 50/50 | 0 | 41 | 1.88 ± 2.20 (1.35) | 8.47 ± 10.60 (4.38) | 2.00 ± 0.70 (2.04) | 4.48 ± 1.72 (4.20) | 1.73 ± 0.89 (1.56) |
| left | p | 0.820 | 50/50 | 0 | 43 | 2.05 ± 1.99 (1.73) | 18.58 ± 35.05 (5.21) | 2.13 ± 0.59 (2.32) | 4.88 ± 1.52 (5.51) | 1.93 ± 0.82 (2.07) |
| back | p | 0.725 | 49/50 | 0 | 40 | 2.56 ± 1.48 (2.52) | 33.70 ± 57.35 (7.45) | 2.04 ± 0.68 (2.24) | 4.58 ± 1.66 (5.06) | 1.81 ± 0.84 (1.94) |
| right | p | 0.797 | 49/50 | 0 | 40 | 1.80 ± 1.09 (1.70) | 18.33 ± 35.41 (2.39) | 1.97 ± 0.66 (2.23) | 4.47 ± 1.65 (5.20) | 1.68 ± 0.81 (1.78) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.804 | 100/100 | 0 | 84 | 1.90 ± 1.36 (1.70) | 19.46 ± 39.55 (4.58) | 2.04 ± 0.63 (2.23) | 4.63 ± 1.57 (5.16) | 1.79 ± 0.81 (1.86) |
| right | p | 0.763 | 98/100 | 0 | 80 | 2.24 ± 2.10 (1.73) | 19.96 ± 39.03 (5.88) | 2.03 ± 0.70 (2.24) | 4.57 ± 1.72 (4.99) | 1.79 ± 0.89 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.812 | 25/25 | 0 | 21 | 1.56 ± 1.48 (1.30) | 8.78 ± 12.13 (4.30) | 2.08 ± 0.63 (2.20) | 4.64 ± 1.56 (4.40) | 1.80 ± 0.83 (1.77) |
| forward/right | p | 0.771 | 25/25 | 0 | 20 | 2.20 ± 2.70 (1.38) | 8.16 ± 8.81 (4.55) | 1.92 ± 0.75 (1.92) | 4.31 ± 1.85 (4.10) | 1.65 ± 0.94 (1.47) |
| left/left | p | 0.864 | 25/25 | 0 | 23 | 1.58 ± 0.40 (1.64) | 11.24 ± 22.32 (4.54) | 2.19 ± 0.49 (2.36) | 5.02 ± 1.30 (5.60) | 2.00 ± 0.71 (2.14) |
| left/right | p | 0.776 | 25/25 | 0 | 20 | 2.52 ± 2.71 (1.96) | 25.91 ± 43.02 (6.59) | 2.07 ± 0.68 (2.32) | 4.75 ± 1.71 (5.45) | 1.87 ± 0.90 (2.05) |
| back/left | p | 0.727 | 25/25 | 0 | 20 | 2.74 ± 1.97 (2.54) | 36.17 ± 58.64 (8.18) | 1.99 ± 0.65 (2.23) | 4.50 ± 1.57 (5.06) | 1.73 ± 0.78 (1.84) |
| back/right | p | 0.723 | 24/25 | 0 | 20 | 2.36 ± 0.60 (2.45) | 31.13 ± 55.85 (7.14) | 2.08 ± 0.71 (2.27) | 4.65 ± 1.74 (5.08) | 1.89 ± 0.90 (1.94) |
| right/left | p | 0.814 | 25/25 | 0 | 20 | 1.73 ± 0.47 (1.74) | 21.64 ± 41.30 (2.39) | 1.91 ± 0.69 (2.15) | 4.34 ± 1.74 (4.47) | 1.62 ± 0.84 (1.78) |
| right/right | p | 0.780 | 24/25 | 0 | 20 | 1.88 ± 1.48 (1.66) | 14.89 ± 27.55 (2.83) | 2.03 ± 0.62 (2.23) | 4.59 ± 1.55 (5.36) | 1.75 ± 0.77 (1.77) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.812 | 17.5 | 5.27 | 2.13 |
| p | normal | 0.755 | 21.9 | 3.94 | 1.45 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.714 | 0.15 | 2.24 ± 1.03 (2.12) | 3.51 | 1.22 |
| p | medium | 16 | 0.827 | 0.68 | 1.27 ± 0.22 (1.29) | 4.14 | 1.59 |
| p | strong | 126 | 0.810 | 0.69 | - | 5.17 | 2.08 |

## Notes

- p: score 0.783, 198/200 kicked, 0 fell; worst sector back (0.725).
