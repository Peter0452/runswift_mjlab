# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.796** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 1.91 ± 1.40 (1.71) |
| Direction error [°] | 18.79 ± 38.40 (5.68) |
| Avg ball speed [m/s] | 2.42 ± 0.86 (2.69) |
| Peak ball speed [m/s] | 5.04 ± 1.88 (5.94) |
| Distance [m] | 2.52 ± 1.28 (2.99) |
| Path length [m] | 2.53 ± 1.28 (3.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.796 | 49/50 | 0 | 42 | 1.60 ± 1.69 (1.32) | 9.06 ± 13.50 (4.51) | 2.29 ± 0.77 (2.18) | 4.74 ± 1.71 (4.19) | 2.25 ± 1.14 (1.84) |
| left | p | 0.809 | 48/50 | 0 | 42 | 1.67 ± 0.45 (1.74) | 15.45 ± 29.74 (5.95) | 2.53 ± 0.84 (2.83) | 5.31 ± 1.84 (6.37) | 2.70 ± 1.24 (3.35) |
| back | p | 0.774 | 50/50 | 0 | 41 | 2.47 ± 1.46 (2.40) | 32.81 ± 58.09 (7.26) | 2.42 ± 0.97 (2.87) | 5.05 ± 2.12 (6.34) | 2.60 ± 1.42 (3.44) |
| right | p | 0.803 | 49/50 | 0 | 42 | 1.88 ± 1.45 (1.74) | 17.48 ± 33.15 (5.85) | 2.45 ± 0.82 (2.64) | 5.08 ± 1.79 (5.78) | 2.53 ± 1.24 (2.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.819 | 100/100 | 0 | 87 | 1.91 ± 1.40 (1.70) | 18.95 ± 40.82 (4.96) | 2.45 ± 0.82 (2.71) | 5.10 ± 1.83 (6.00) | 2.54 ± 1.24 (3.12) |
| right | p | 0.772 | 96/100 | 0 | 80 | 1.91 ± 1.39 (1.73) | 18.63 ± 35.71 (6.01) | 2.39 ± 0.90 (2.64) | 4.99 ± 1.94 (5.86) | 2.49 ± 1.31 (2.91) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 22 | 1.61 ± 1.70 (1.30) | 8.03 ± 14.51 (2.76) | 2.33 ± 0.76 (2.27) | 4.88 ± 1.72 (4.46) | 2.34 ± 1.12 (2.00) |
| forward/right | p | 0.758 | 24/25 | 0 | 20 | 1.59 ± 1.67 (1.32) | 10.14 ± 12.27 (5.78) | 2.24 ± 0.77 (2.13) | 4.59 ± 1.68 (4.12) | 2.15 ± 1.15 (1.81) |
| left/left | p | 0.855 | 25/25 | 0 | 23 | 1.60 ± 0.38 (1.68) | 10.34 ± 15.60 (6.07) | 2.56 ± 0.79 (2.82) | 5.38 ± 1.81 (6.36) | 2.77 ± 1.19 (3.27) |
| left/right | p | 0.763 | 23/25 | 0 | 19 | 1.74 ± 0.51 (1.96) | 21.01 ± 39.02 (5.88) | 2.49 ± 0.88 (2.85) | 5.23 ± 1.88 (6.39) | 2.63 ± 1.28 (3.36) |
| back/left | p | 0.767 | 25/25 | 0 | 20 | 2.67 ± 1.96 (2.46) | 37.54 ± 64.14 (5.56) | 2.40 ± 0.91 (2.86) | 5.04 ± 2.02 (6.31) | 2.54 ± 1.42 (3.42) |
| back/right | p | 0.782 | 25/25 | 0 | 21 | 2.28 ± 0.59 (2.34) | 28.09 ± 50.89 (7.61) | 2.43 ± 1.03 (3.02) | 5.07 ± 2.21 (6.52) | 2.66 ± 1.43 (3.67) |
| right/left | p | 0.821 | 25/25 | 0 | 22 | 1.78 ± 0.46 (1.76) | 19.89 ± 39.45 (6.55) | 2.48 ± 0.79 (2.64) | 5.08 ± 1.71 (5.78) | 2.52 ± 1.17 (2.91) |
| right/right | p | 0.785 | 24/25 | 0 | 20 | 1.99 ± 2.01 (1.71) | 14.97 ± 24.68 (5.80) | 2.42 ± 0.85 (2.64) | 5.08 ± 1.86 (5.73) | 2.54 ± 1.31 (2.80) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.822 | 18.7 | 5.89 | 3.16 |
| p | normal | 0.770 | 18.9 | 4.20 | 1.87 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.732 | 0.16 | 2.37 ± 1.01 (2.32) | 3.69 | 1.49 |
| p | medium | 16 | 0.809 | 0.69 | 1.25 ± 0.23 (1.27) | 4.04 | 1.68 |
| p | strong | 126 | 0.823 | 0.77 | - | 5.79 | 3.09 |

## Notes

- p: score 0.796, 196/200 kicked, 0 fell; worst sector back (0.774).
