# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.788** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 7 |
| Time to kick [s] | 2.03 ± 1.65 (1.76) |
| Direction error [°] | 16.10 ± 33.56 (5.08) |
| Avg ball speed [m/s] | 2.06 ± 0.58 (2.18) |
| Peak ball speed [m/s] | 4.64 ± 1.42 (5.14) |
| Distance [m] | 1.80 ± 0.79 (1.86) |
| Path length [m] | 1.81 ± 0.79 (1.87) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.807 | 50/50 | 0 | 44 | 1.95 ± 2.46 (1.34) | 7.34 ± 10.25 (4.04) | 1.98 ± 0.58 (2.01) | 4.41 ± 1.44 (4.07) | 1.65 ± 0.79 (1.49) |
| left | p | 0.803 | 48/50 | 0 | 40 | 1.69 ± 0.45 (1.79) | 16.28 ± 30.67 (4.96) | 2.13 ± 0.56 (2.25) | 4.88 ± 1.39 (5.45) | 1.93 ± 0.77 (2.04) |
| back | p | 0.737 | 48/50 | 0 | 42 | 2.64 ± 1.40 (2.56) | 21.41 ± 45.18 (6.02) | 2.16 ± 0.52 (2.28) | 4.84 ± 1.24 (5.19) | 1.94 ± 0.75 (1.79) |
| right | p | 0.804 | 50/50 | 0 | 42 | 1.87 ± 1.42 (1.76) | 19.60 ± 36.48 (5.10) | 1.98 ± 0.64 (2.16) | 4.44 ± 1.54 (5.09) | 1.68 ± 0.80 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.818 | 100/100 | 0 | 87 | 1.86 ± 1.09 (1.76) | 16.62 ± 36.62 (4.74) | 2.09 ± 0.56 (2.18) | 4.69 ± 1.36 (5.07) | 1.82 ± 0.76 (1.88) |
| right | p | 0.758 | 96/100 | 0 | 81 | 2.21 ± 2.06 (1.78) | 15.56 ± 30.03 (5.39) | 2.04 ± 0.61 (2.17) | 4.58 ± 1.48 (5.18) | 1.78 ± 0.81 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 23 | 1.65 ± 1.89 (1.32) | 5.98 ± 9.70 (3.93) | 2.09 ± 0.49 (2.11) | 4.66 ± 1.25 (4.93) | 1.77 ± 0.72 (1.60) |
| forward/right | p | 0.774 | 25/25 | 0 | 21 | 2.24 ± 2.90 (1.34) | 8.69 ± 10.60 (4.10) | 1.88 ± 0.64 (1.83) | 4.15 ± 1.57 (3.99) | 1.54 ± 0.83 (1.36) |
| left/left | p | 0.856 | 25/25 | 0 | 22 | 1.61 ± 0.39 (1.70) | 9.82 ± 15.86 (4.77) | 2.21 ± 0.43 (2.18) | 5.02 ± 1.08 (5.36) | 2.00 ± 0.63 (2.03) |
| left/right | p | 0.750 | 23/25 | 0 | 18 | 1.78 ± 0.50 (1.92) | 23.30 ± 39.94 (5.15) | 2.04 ± 0.66 (2.44) | 4.72 ± 1.64 (5.59) | 1.85 ± 0.89 (2.21) |
| back/left | p | 0.774 | 25/25 | 0 | 22 | 2.41 ± 0.67 (2.58) | 24.43 ± 50.74 (5.74) | 2.14 ± 0.48 (2.27) | 4.82 ± 1.17 (5.19) | 1.91 ± 0.74 (1.83) |
| back/right | p | 0.699 | 23/25 | 0 | 20 | 2.88 ± 1.87 (2.54) | 18.12 ± 37.95 (6.46) | 2.18 ± 0.55 (2.30) | 4.86 ± 1.30 (5.18) | 1.97 ± 0.77 (1.69) |
| right/left | p | 0.801 | 25/25 | 0 | 20 | 1.77 ± 0.46 (1.78) | 26.26 ± 46.15 (4.77) | 1.90 ± 0.73 (2.15) | 4.24 ± 1.73 (4.47) | 1.59 ± 0.87 (1.66) |
| right/right | p | 0.807 | 25/25 | 0 | 22 | 1.97 ± 1.95 (1.58) | 12.94 ± 21.06 (5.93) | 2.06 ± 0.53 (2.24) | 4.63 ± 1.28 (5.29) | 1.78 ± 0.70 (1.95) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 14.0 | 5.33 | 2.18 |
| p | normal | 0.753 | 18.2 | 3.94 | 1.42 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.713 | 0.19 | 2.24 ± 0.88 (2.11) | 3.54 | 1.18 |
| p | medium | 16 | 0.795 | 0.76 | 1.21 ± 0.18 (1.27) | 3.90 | 1.40 |
| p | strong | 126 | 0.821 | 0.70 | - | 5.23 | 2.13 |

## Notes

- p: score 0.788, 196/200 kicked, 0 fell; worst sector back (0.737).
