# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_23-01-41_q3_speed_fastmix/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.97 ± 1.56 (1.72) |
| Direction error [°] | 18.09 ± 36.46 (5.53) |
| Avg ball speed [m/s] | 2.08 ± 0.63 (2.25) |
| Peak ball speed [m/s] | 4.57 ± 1.52 (4.98) |
| Distance [m] | 1.82 ± 0.82 (1.93) |
| Path length [m] | 1.83 ± 0.82 (1.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.785 | 49/50 | 0 | 41 | 1.63 ± 1.69 (1.34) | 8.38 ± 10.86 (4.08) | 2.04 ± 0.67 (2.12) | 4.43 ± 1.57 (4.27) | 1.75 ± 0.85 (1.70) |
| left | p | 0.792 | 48/50 | 0 | 41 | 1.66 ± 0.50 (1.74) | 19.25 ± 35.26 (5.60) | 2.08 ± 0.61 (2.25) | 4.64 ± 1.51 (5.27) | 1.84 ± 0.81 (2.05) |
| back | p | 0.747 | 49/50 | 0 | 41 | 2.55 ± 1.47 (2.50) | 26.97 ± 52.52 (6.67) | 2.16 ± 0.61 (2.32) | 4.74 ± 1.47 (5.14) | 1.94 ± 0.79 (1.99) |
| right | p | 0.793 | 50/50 | 0 | 42 | 2.03 ± 1.95 (1.72) | 17.77 ± 32.05 (5.69) | 2.05 ± 0.63 (2.21) | 4.47 ± 1.51 (4.91) | 1.76 ± 0.80 (1.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.809 | 100/100 | 0 | 86 | 1.88 ± 1.30 (1.66) | 16.74 ± 35.09 (5.47) | 2.13 ± 0.60 (2.26) | 4.67 ± 1.47 (5.16) | 1.87 ± 0.80 (2.05) |
| right | p | 0.750 | 96/100 | 0 | 79 | 2.06 ± 1.78 (1.74) | 19.48 ± 37.79 (5.59) | 2.04 ± 0.66 (2.22) | 4.47 ± 1.57 (4.78) | 1.77 ± 0.83 (1.84) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 22 | 1.51 ± 1.25 (1.32) | 7.25 ± 10.96 (2.89) | 2.12 ± 0.59 (2.25) | 4.62 ± 1.41 (4.68) | 1.83 ± 0.75 (1.84) |
| forward/right | p | 0.750 | 24/25 | 0 | 19 | 1.76 ± 2.04 (1.34) | 9.56 ± 10.62 (5.38) | 1.97 ± 0.73 (2.00) | 4.24 ± 1.71 (4.12) | 1.68 ± 0.94 (1.60) |
| left/left | p | 0.854 | 25/25 | 0 | 23 | 1.57 ± 0.42 (1.64) | 11.51 ± 21.29 (5.18) | 2.16 ± 0.52 (2.28) | 4.80 ± 1.33 (5.34) | 1.93 ± 0.73 (2.12) |
| left/right | p | 0.729 | 23/25 | 0 | 18 | 1.75 ± 0.56 (1.94) | 27.65 ± 44.35 (6.10) | 1.99 ± 0.68 (2.23) | 4.47 ± 1.66 (5.19) | 1.73 ± 0.87 (2.01) |
| back/left | p | 0.764 | 25/25 | 0 | 21 | 2.74 ± 1.96 (2.50) | 25.00 ± 50.51 (7.18) | 2.27 ± 0.49 (2.26) | 4.99 ± 1.22 (5.14) | 2.07 ± 0.75 (2.07) |
| back/right | p | 0.730 | 24/25 | 0 | 20 | 2.35 ± 0.59 (2.46) | 29.03 ± 54.46 (5.07) | 2.05 ± 0.70 (2.35) | 4.47 ± 1.65 (5.09) | 1.80 ± 0.81 (1.94) |
| right/left | p | 0.797 | 25/25 | 0 | 20 | 1.70 ± 0.47 (1.72) | 23.20 ± 39.65 (6.39) | 1.96 ± 0.74 (2.20) | 4.27 ± 1.75 (4.68) | 1.67 ± 0.89 (2.08) |
| right/right | p | 0.789 | 25/25 | 0 | 22 | 2.35 ± 2.68 (1.72) | 12.34 ± 20.59 (5.34) | 2.14 ± 0.48 (2.22) | 4.68 ± 1.17 (4.98) | 1.85 ± 0.68 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 16.6 | 5.21 | 2.16 |
| p | normal | 0.754 | 19.6 | 3.95 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.722 | 0.16 | 2.29 ± 0.96 (2.20) | 3.62 | 1.30 |
| p | medium | 16 | 0.798 | 0.67 | 1.27 ± 0.25 (1.28) | 4.10 | 1.60 |
| p | strong | 126 | 0.803 | 0.68 | - | 5.08 | 2.09 |

## Notes

- p: score 0.779, 196/200 kicked, 0 fell; worst sector back (0.747).
