# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_16-13-42_u14_u6_overpower600/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 192 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.91 ± 1.34 (1.72) |
| Direction error [°] | 16.06 ± 34.35 (4.72) |
| Avg ball speed [m/s] | 1.97 ± 0.56 (2.10) |
| Peak ball speed [m/s] | 4.49 ± 1.42 (4.91) |
| Distance [m] | 1.68 ± 0.75 (1.71) |
| Path length [m] | 1.68 ± 0.75 (1.72) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 48/50 | 0 | 42 | 1.69 ± 1.98 (1.35) | 7.64 ± 9.29 (3.78) | 1.99 ± 0.59 (2.06) | 4.48 ± 1.46 (4.19) | 1.68 ± 0.83 (1.65) |
| left | p | 0.797 | 49/50 | 0 | 41 | 1.87 ± 1.53 (1.72) | 19.45 ± 35.65 (5.79) | 1.93 ± 0.63 (2.08) | 4.46 ± 1.61 (5.03) | 1.67 ± 0.81 (1.79) |
| back | p | 0.742 | 47/50 | 0 | 42 | 2.42 ± 0.58 (2.46) | 21.02 ± 46.92 (5.24) | 2.01 ± 0.47 (2.18) | 4.57 ± 1.23 (5.08) | 1.70 ± 0.65 (1.75) |
| right | p | 0.790 | 48/50 | 0 | 41 | 1.68 ± 0.46 (1.72) | 16.15 ± 32.77 (3.72) | 1.96 ± 0.52 (2.08) | 4.47 ± 1.36 (4.89) | 1.65 ± 0.69 (1.70) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 99/100 | 0 | 86 | 1.84 ± 1.09 (1.70) | 15.95 ± 35.13 (3.85) | 2.01 ± 0.54 (2.10) | 4.56 ± 1.38 (5.03) | 1.71 ± 0.73 (1.75) |
| right | p | 0.748 | 93/100 | 0 | 80 | 1.99 ± 1.56 (1.72) | 16.17 ± 33.50 (5.25) | 1.94 ± 0.57 (2.10) | 4.42 ± 1.47 (4.85) | 1.64 ± 0.76 (1.71) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 23 | 1.66 ± 1.87 (1.32) | 5.77 ± 8.33 (3.02) | 2.12 ± 0.49 (2.20) | 4.75 ± 1.27 (5.04) | 1.82 ± 0.73 (1.88) |
| forward/right | p | 0.737 | 23/25 | 0 | 19 | 1.73 ± 2.10 (1.36) | 9.67 ± 9.84 (7.34) | 1.86 ± 0.65 (1.84) | 4.18 ± 1.59 (3.89) | 1.54 ± 0.90 (1.43) |
| left/left | p | 0.834 | 25/25 | 0 | 21 | 1.58 ± 0.40 (1.66) | 14.16 ± 23.55 (5.66) | 1.95 ± 0.62 (2.05) | 4.49 ± 1.55 (5.03) | 1.71 ± 0.79 (1.71) |
| left/right | p | 0.760 | 24/25 | 0 | 20 | 2.17 ± 2.10 (1.93) | 24.96 ± 44.25 (6.13) | 1.91 ± 0.63 (2.10) | 4.43 ± 1.67 (4.99) | 1.64 ± 0.82 (1.82) |
| back/left | p | 0.758 | 24/25 | 0 | 21 | 2.37 ± 0.68 (2.46) | 23.76 ± 51.11 (5.10) | 2.05 ± 0.41 (2.19) | 4.68 ± 1.13 (5.14) | 1.75 ± 0.63 (1.93) |
| back/right | p | 0.726 | 23/25 | 0 | 21 | 2.48 ± 0.44 (2.52) | 18.17 ± 41.91 (5.25) | 1.96 ± 0.52 (2.15) | 4.45 ± 1.31 (4.96) | 1.65 ± 0.65 (1.70) |
| right/left | p | 0.811 | 25/25 | 0 | 21 | 1.78 ± 0.47 (1.74) | 20.42 ± 39.63 (4.37) | 1.90 ± 0.58 (2.09) | 4.32 ± 1.47 (4.86) | 1.58 ± 0.74 (1.69) |
| right/right | p | 0.769 | 23/25 | 0 | 20 | 1.58 ± 0.42 (1.60) | 11.49 ± 22.17 (2.75) | 2.02 ± 0.44 (2.07) | 4.64 ± 1.21 (4.92) | 1.72 ± 0.63 (1.72) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.795 | 13.3 | 5.23 | 2.04 |
| p | normal | 0.763 | 18.7 | 3.78 | 1.32 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.720 | 0.20 | 2.18 ± 0.88 (2.11) | 3.45 | 1.14 |
| p | medium | 16 | 0.861 | 0.78 | 1.18 ± 0.21 (1.18) | 3.82 | 1.35 |
| p | strong | 126 | 0.796 | 0.68 | - | 5.07 | 1.97 |

## Notes

- p: score 0.779, 192/200 kicked, 0 fell; worst sector back (0.742).
