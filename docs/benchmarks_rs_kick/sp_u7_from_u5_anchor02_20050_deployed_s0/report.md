# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 2.02 ± 1.65 (1.72) |
| Direction error [°] | 17.98 ± 37.00 (5.27) |
| Avg ball speed [m/s] | 2.12 ± 0.65 (2.32) |
| Peak ball speed [m/s] | 4.62 ± 1.52 (5.24) |
| Distance [m] | 1.92 ± 0.84 (1.98) |
| Path length [m] | 1.93 ± 0.84 (1.99) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.791 | 49/50 | 0 | 44 | 1.87 ± 2.31 (1.32) | 7.78 ± 10.57 (4.34) | 2.20 ± 0.58 (2.23) | 4.72 ± 1.36 (4.35) | 1.97 ± 0.82 (1.75) |
| left | p | 0.796 | 48/50 | 0 | 40 | 1.65 ± 0.48 (1.73) | 17.67 ± 32.15 (5.10) | 2.07 ± 0.69 (2.33) | 4.55 ± 1.64 (5.41) | 1.88 ± 0.85 (2.16) |
| back | p | 0.745 | 49/50 | 0 | 40 | 2.66 ± 1.65 (2.50) | 29.12 ± 54.95 (5.93) | 2.13 ± 0.74 (2.39) | 4.61 ± 1.70 (5.33) | 1.98 ± 0.91 (2.16) |
| right | p | 0.787 | 49/50 | 0 | 42 | 1.88 ± 1.40 (1.72) | 17.36 ± 32.81 (5.52) | 2.08 ± 0.55 (2.23) | 4.57 ± 1.34 (4.97) | 1.85 ± 0.75 (1.86) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 99/100 | 0 | 86 | 1.82 ± 1.03 (1.70) | 16.88 ± 35.81 (5.23) | 2.15 ± 0.59 (2.33) | 4.68 ± 1.41 (5.32) | 1.95 ± 0.81 (2.09) |
| right | p | 0.751 | 96/100 | 0 | 80 | 2.21 ± 2.09 (1.73) | 19.12 ± 38.16 (5.44) | 2.09 ± 0.70 (2.28) | 4.54 ± 1.62 (5.16) | 1.89 ± 0.87 (1.98) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 24 | 1.64 ± 1.71 (1.28) | 6.75 ± 9.42 (4.10) | 2.26 ± 0.49 (2.38) | 4.89 ± 1.23 (5.39) | 2.04 ± 0.73 (1.88) |
| forward/right | p | 0.749 | 24/25 | 0 | 20 | 2.12 ± 2.78 (1.36) | 8.86 ± 11.54 (4.46) | 2.14 ± 0.66 (2.11) | 4.55 ± 1.46 (4.21) | 1.89 ± 0.89 (1.70) |
| left/left | p | 0.836 | 25/25 | 0 | 21 | 1.54 ± 0.43 (1.62) | 15.21 ± 25.12 (5.78) | 2.04 ± 0.69 (2.33) | 4.48 ± 1.64 (5.40) | 1.85 ± 0.84 (2.24) |
| left/right | p | 0.755 | 23/25 | 0 | 19 | 1.76 ± 0.50 (1.96) | 20.34 ± 38.17 (4.87) | 2.09 ± 0.69 (2.34) | 4.63 ± 1.65 (5.41) | 1.90 ± 0.86 (2.14) |
| back/left | p | 0.754 | 24/25 | 0 | 20 | 2.35 ± 0.69 (2.46) | 24.86 ± 51.50 (5.98) | 2.27 ± 0.54 (2.40) | 4.91 ± 1.28 (5.37) | 2.12 ± 0.83 (2.41) |
| back/right | p | 0.737 | 25/25 | 0 | 20 | 2.95 ± 2.17 (2.50) | 33.20 ± 57.78 (5.76) | 1.99 ± 0.87 (2.39) | 4.32 ± 1.98 (5.22) | 1.85 ± 0.97 (2.15) |
| right/left | p | 0.810 | 25/25 | 0 | 21 | 1.79 ± 0.51 (1.76) | 21.02 ± 40.34 (4.85) | 2.04 ± 0.57 (2.23) | 4.47 ± 1.39 (4.97) | 1.78 ± 0.77 (1.86) |
| right/right | p | 0.763 | 24/25 | 0 | 21 | 1.97 ± 1.93 (1.68) | 13.55 ± 21.78 (6.19) | 2.13 ± 0.53 (2.24) | 4.68 ± 1.28 (5.18) | 1.92 ± 0.73 (1.97) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.809 | 16.8 | 5.21 | 2.25 |
| p | normal | 0.751 | 19.1 | 4.02 | 1.59 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.707 | 0.18 | 2.30 ± 0.94 (2.22) | 3.64 | 1.38 |
| p | medium | 16 | 0.806 | 0.69 | 1.28 ± 0.21 (1.31) | 4.13 | 1.64 |
| p | strong | 126 | 0.810 | 0.68 | - | 5.12 | 2.20 |

## Notes

- p: score 0.780, 195/200 kicked, 0 fell; worst sector back (0.745).
