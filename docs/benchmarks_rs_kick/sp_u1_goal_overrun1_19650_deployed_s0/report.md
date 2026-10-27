# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.789** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.90 ± 0.93 (1.77) |
| Direction error [°] | 17.27 ± 37.19 (4.77) |
| Avg ball speed [m/s] | 2.09 ± 0.70 (2.34) |
| Peak ball speed [m/s] | 4.50 ± 1.63 (5.30) |
| Distance [m] | 1.89 ± 0.93 (2.05) |
| Path length [m] | 1.90 ± 0.93 (2.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.782 | 48/50 | 0 | 39 | 1.37 ± 0.36 (1.36) | 9.40 ± 12.13 (4.68) | 1.93 ± 0.67 (1.95) | 4.15 ± 1.59 (3.84) | 1.64 ± 0.85 (1.46) |
| left | p | 0.819 | 49/50 | 0 | 43 | 1.90 ± 1.27 (1.78) | 15.56 ± 32.00 (5.00) | 2.16 ± 0.66 (2.39) | 4.67 ± 1.54 (5.39) | 1.98 ± 0.89 (2.22) |
| back | p | 0.751 | 49/50 | 0 | 40 | 2.58 ± 0.83 (2.50) | 29.11 ± 55.72 (5.66) | 2.13 ± 0.81 (2.44) | 4.58 ± 1.83 (5.61) | 2.00 ± 1.04 (2.28) |
| right | p | 0.804 | 48/50 | 0 | 42 | 1.73 ± 0.47 (1.76) | 14.79 ± 31.82 (3.98) | 2.15 ± 0.63 (2.40) | 4.58 ± 1.50 (5.34) | 1.94 ± 0.87 (2.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.824 | 99/100 | 0 | 88 | 1.81 ± 0.61 (1.78) | 15.58 ± 36.79 (4.30) | 2.16 ± 0.64 (2.40) | 4.65 ± 1.51 (5.39) | 1.97 ± 0.89 (2.21) |
| right | p | 0.753 | 95/100 | 0 | 76 | 1.99 ± 1.16 (1.76) | 19.03 ± 37.52 (5.00) | 2.02 ± 0.76 (2.06) | 4.34 ± 1.74 (4.77) | 1.81 ± 0.96 (1.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 23 | 1.35 ± 0.30 (1.36) | 6.60 ± 10.36 (3.63) | 2.03 ± 0.65 (2.10) | 4.37 ± 1.53 (4.15) | 1.76 ± 0.82 (1.65) |
| forward/right | p | 0.717 | 23/25 | 0 | 16 | 1.39 ± 0.41 (1.36) | 12.45 ± 13.14 (7.20) | 1.83 ± 0.68 (1.85) | 3.92 ± 1.63 (3.78) | 1.51 ± 0.87 (1.42) |
| left/left | p | 0.879 | 25/25 | 0 | 24 | 1.67 ± 0.41 (1.76) | 7.76 ± 15.33 (4.11) | 2.32 ± 0.51 (2.41) | 5.04 ± 1.22 (5.46) | 2.19 ± 0.76 (2.35) |
| left/right | p | 0.759 | 24/25 | 0 | 19 | 2.14 ± 1.73 (1.98) | 23.68 ± 41.43 (5.62) | 1.99 ± 0.76 (2.17) | 4.29 ± 1.74 (4.91) | 1.75 ± 0.95 (1.71) |
| back/left | p | 0.746 | 24/25 | 0 | 19 | 2.41 ± 0.68 (2.49) | 30.60 ± 57.20 (6.42) | 2.17 ± 0.74 (2.43) | 4.70 ± 1.69 (5.72) | 2.04 ± 1.04 (2.27) |
| back/right | p | 0.755 | 25/25 | 0 | 21 | 2.75 ± 0.93 (2.68) | 27.69 ± 54.23 (4.98) | 2.08 ± 0.88 (2.44) | 4.47 ± 1.95 (5.48) | 1.96 ± 1.05 (2.28) |
| right/left | p | 0.826 | 25/25 | 0 | 22 | 1.84 ± 0.47 (1.92) | 17.97 ± 38.87 (3.67) | 2.11 ± 0.61 (2.39) | 4.51 ± 1.49 (5.32) | 1.88 ± 0.85 (1.98) |
| right/right | p | 0.782 | 23/25 | 0 | 20 | 1.62 ± 0.44 (1.72) | 11.33 ± 21.14 (4.30) | 2.18 ± 0.64 (2.44) | 4.65 ± 1.51 (5.38) | 2.00 ± 0.88 (2.41) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.816 | 13.9 | 5.27 | 2.34 |
| p | normal | 0.761 | 20.5 | 3.74 | 1.45 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.22 | 2.13 ± 0.92 (1.96) | 3.35 | 1.19 |
| p | medium | 16 | 0.858 | 0.81 | 1.13 ± 0.20 (1.16) | 3.68 | 1.36 |
| p | strong | 126 | 0.813 | 0.68 | - | 5.13 | 2.28 |

## Notes

- p: score 0.789, 194/200 kicked, 0 fell; worst sector back (0.751).
