# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.768** |
| Kicked / fell | 191 / 0 |
| Kicks within 15° | 160 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.90 ± 1.02 (1.78) |
| Direction error [°] | 19.10 ± 37.59 (5.56) |
| Avg ball speed [m/s] | 1.98 ± 0.70 (2.24) |
| Peak ball speed [m/s] | 4.36 ± 1.70 (5.16) |
| Distance [m] | 1.75 ± 0.95 (1.94) |
| Path length [m] | 1.76 ± 0.95 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.774 | 46/50 | 0 | 41 | 1.31 ± 0.31 (1.36) | 7.65 ± 9.12 (5.46) | 1.90 ± 0.70 (1.76) | 4.17 ± 1.68 (3.54) | 1.62 ± 0.93 (1.28) |
| left | p | 0.768 | 47/50 | 0 | 39 | 1.69 ± 0.54 (1.76) | 20.83 ± 36.06 (5.68) | 1.99 ± 0.66 (2.27) | 4.40 ± 1.62 (5.16) | 1.77 ± 0.92 (1.94) |
| back | p | 0.738 | 50/50 | 0 | 40 | 2.75 ± 1.52 (2.68) | 30.05 ± 53.71 (6.22) | 1.99 ± 0.75 (2.29) | 4.38 ± 1.82 (5.36) | 1.81 ± 0.99 (2.11) |
| right | p | 0.793 | 48/50 | 0 | 40 | 1.77 ± 0.51 (1.80) | 16.98 ± 31.71 (4.74) | 2.02 ± 0.66 (2.32) | 4.49 ± 1.64 (5.33) | 1.81 ± 0.93 (2.15) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.805 | 99/100 | 0 | 85 | 1.93 ± 1.20 (1.80) | 17.25 ± 35.74 (5.55) | 2.00 ± 0.65 (2.24) | 4.44 ± 1.62 (5.16) | 1.78 ± 0.91 (1.94) |
| right | p | 0.731 | 92/100 | 0 | 75 | 1.87 ± 0.79 (1.76) | 21.09 ± 39.38 (5.89) | 1.95 ± 0.74 (2.11) | 4.28 ± 1.78 (4.58) | 1.73 ± 0.99 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 24/25 | 0 | 23 | 1.33 ± 0.33 (1.31) | 6.03 ± 9.32 (3.74) | 2.04 ± 0.67 (2.02) | 4.50 ± 1.66 (4.48) | 1.80 ± 0.94 (1.66) |
| forward/right | p | 0.716 | 22/25 | 0 | 18 | 1.29 ± 0.28 (1.36) | 9.43 ± 8.56 (6.99) | 1.75 ± 0.69 (1.59) | 3.80 ± 1.62 (3.38) | 1.43 ± 0.88 (1.10) |
| left/left | p | 0.842 | 25/25 | 0 | 22 | 1.60 ± 0.44 (1.72) | 13.02 ± 22.05 (5.68) | 1.96 ± 0.63 (2.13) | 4.36 ± 1.54 (5.08) | 1.72 ± 0.83 (1.90) |
| left/right | p | 0.693 | 22/25 | 0 | 17 | 1.80 ± 0.61 (1.88) | 29.70 ± 45.58 (6.39) | 2.03 ± 0.70 (2.33) | 4.45 ± 1.71 (5.43) | 1.82 ± 1.00 (2.07) |
| back/left | p | 0.745 | 25/25 | 0 | 20 | 2.86 ± 1.95 (2.64) | 28.23 ± 52.47 (7.42) | 2.07 ± 0.61 (2.35) | 4.58 ± 1.54 (5.38) | 1.89 ± 0.93 (2.24) |
| back/right | p | 0.731 | 25/25 | 0 | 20 | 2.64 ± 0.88 (2.70) | 31.86 ± 54.86 (5.94) | 1.90 ± 0.87 (2.28) | 4.19 ± 2.04 (5.33) | 1.72 ± 1.04 (1.99) |
| right/left | p | 0.802 | 25/25 | 0 | 20 | 1.89 ± 0.53 (1.96) | 21.27 ± 38.21 (5.53) | 1.93 ± 0.67 (2.26) | 4.33 ± 1.71 (5.29) | 1.71 ± 0.91 (2.03) |
| right/right | p | 0.784 | 23/25 | 0 | 20 | 1.64 ± 0.45 (1.70) | 12.30 ± 21.68 (3.76) | 2.12 ± 0.63 (2.48) | 4.67 ± 1.53 (5.68) | 1.92 ± 0.93 (2.18) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.778 | 18.2 | 5.20 | 2.25 |
| p | normal | 0.758 | 19.9 | 3.56 | 1.28 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.723 | 0.31 | 1.91 ± 0.78 (1.78) | 3.02 | 0.95 |
| p | medium | 16 | 0.828 | 0.82 | 1.07 ± 0.20 (1.12) | 3.47 | 1.21 |
| p | strong | 126 | 0.781 | 0.68 | - | 5.10 | 2.20 |

## Notes

- p: score 0.768, 191/200 kicked, 0 fell; worst sector back (0.738).
