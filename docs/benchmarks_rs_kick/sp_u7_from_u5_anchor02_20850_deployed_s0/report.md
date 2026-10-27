# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.805** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.02 ± 1.65 (1.76) |
| Direction error [°] | 17.53 ± 38.32 (4.45) |
| Avg ball speed [m/s] | 2.06 ± 0.66 (2.20) |
| Peak ball speed [m/s] | 4.55 ± 1.57 (5.10) |
| Distance [m] | 1.85 ± 0.84 (1.90) |
| Path length [m] | 1.86 ± 0.84 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.793 | 50/50 | 0 | 43 | 1.86 ± 2.33 (1.35) | 9.00 ± 11.81 (5.07) | 1.97 ± 0.66 (2.05) | 4.35 ± 1.59 (4.20) | 1.73 ± 0.83 (1.67) |
| left | p | 0.835 | 50/50 | 0 | 45 | 2.03 ± 1.76 (1.78) | 15.71 ± 36.51 (3.66) | 2.10 ± 0.60 (2.23) | 4.72 ± 1.46 (5.23) | 1.90 ± 0.78 (1.94) |
| back | p | 0.781 | 50/50 | 0 | 42 | 2.34 ± 0.64 (2.42) | 28.67 ± 56.28 (5.04) | 2.10 ± 0.76 (2.31) | 4.57 ± 1.74 (5.31) | 1.95 ± 0.95 (2.16) |
| right | p | 0.809 | 50/50 | 0 | 42 | 1.86 ± 1.35 (1.76) | 16.75 ± 32.14 (3.55) | 2.06 ± 0.61 (2.21) | 4.55 ± 1.46 (5.03) | 1.83 ± 0.78 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.828 | 100/100 | 0 | 88 | 1.84 ± 1.12 (1.74) | 14.72 ± 34.40 (3.99) | 2.12 ± 0.60 (2.24) | 4.68 ± 1.43 (5.17) | 1.92 ± 0.80 (2.06) |
| right | p | 0.782 | 100/100 | 0 | 84 | 2.21 ± 2.03 (1.78) | 20.35 ± 41.68 (5.33) | 1.99 ± 0.71 (2.16) | 4.41 ± 1.69 (4.90) | 1.79 ± 0.88 (1.77) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.810 | 25/25 | 0 | 22 | 1.66 ± 1.99 (1.32) | 8.66 ± 11.31 (5.15) | 2.02 ± 0.62 (2.12) | 4.51 ± 1.53 (4.21) | 1.80 ± 0.77 (1.73) |
| forward/right | p | 0.776 | 25/25 | 0 | 21 | 2.07 ± 2.60 (1.36) | 9.33 ± 12.29 (5.00) | 1.92 ± 0.69 (1.96) | 4.19 ± 1.62 (4.19) | 1.67 ± 0.88 (1.59) |
| left/left | p | 0.879 | 25/25 | 0 | 24 | 1.61 ± 0.38 (1.68) | 6.94 ± 15.46 (3.33) | 2.22 ± 0.43 (2.20) | 4.96 ± 1.07 (5.13) | 2.02 ± 0.62 (1.94) |
| left/right | p | 0.791 | 25/25 | 0 | 21 | 2.44 ± 2.39 (1.96) | 24.48 ± 47.68 (4.15) | 1.98 ± 0.72 (2.26) | 4.47 ± 1.74 (5.27) | 1.79 ± 0.89 (1.92) |
| back/left | p | 0.810 | 25/25 | 0 | 22 | 2.32 ± 0.63 (2.40) | 22.92 ± 51.08 (4.57) | 2.26 ± 0.58 (2.39) | 4.91 ± 1.34 (5.58) | 2.12 ± 0.89 (2.51) |
| back/right | p | 0.752 | 25/25 | 0 | 20 | 2.37 ± 0.65 (2.42) | 34.43 ± 60.49 (5.52) | 1.93 ± 0.88 (2.20) | 4.23 ± 2.01 (5.16) | 1.78 ± 0.98 (1.94) |
| right/left | p | 0.812 | 25/25 | 0 | 20 | 1.77 ± 0.48 (1.86) | 20.36 ± 39.54 (3.06) | 1.99 ± 0.71 (2.20) | 4.35 ± 1.62 (4.45) | 1.73 ± 0.82 (1.88) |
| right/right | p | 0.807 | 25/25 | 0 | 22 | 1.95 ± 1.85 (1.74) | 13.15 ± 21.83 (5.48) | 2.13 ± 0.49 (2.27) | 4.75 ± 1.24 (5.29) | 1.93 ± 0.73 (1.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.836 | 16.1 | 5.21 | 2.22 |
| p | normal | 0.773 | 19.0 | 3.88 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.736 | 0.17 | 2.25 ± 0.95 (2.22) | 3.56 | 1.30 |
| p | medium | 16 | 0.819 | 0.63 | 1.16 ± 0.41 (1.29) | 3.76 | 1.46 |
| p | strong | 126 | 0.834 | 0.68 | - | 5.10 | 2.16 |

## Notes

- p: score 0.805, 200/200 kicked, 0 fell; worst sector back (0.781).
