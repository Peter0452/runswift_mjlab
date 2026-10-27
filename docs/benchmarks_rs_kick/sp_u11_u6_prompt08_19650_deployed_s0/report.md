# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_14-36-37_u11_u6_prompt08/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.03 ± 1.68 (1.72) |
| Direction error [°] | 19.51 ± 39.30 (4.66) |
| Avg ball speed [m/s] | 2.05 ± 0.68 (2.24) |
| Peak ball speed [m/s] | 4.51 ± 1.61 (4.84) |
| Distance [m] | 1.84 ± 0.87 (1.90) |
| Path length [m] | 1.85 ± 0.87 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.797 | 50/50 | 0 | 44 | 1.80 ± 2.07 (1.36) | 9.98 ± 16.14 (3.95) | 2.00 ± 0.71 (2.16) | 4.35 ± 1.64 (4.49) | 1.74 ± 0.89 (1.76) |
| left | p | 0.801 | 49/50 | 0 | 42 | 1.85 ± 1.54 (1.74) | 18.83 ± 35.19 (4.66) | 2.05 ± 0.66 (2.24) | 4.57 ± 1.60 (5.31) | 1.86 ± 0.86 (2.02) |
| back | p | 0.753 | 50/50 | 0 | 41 | 2.57 ± 1.48 (2.59) | 30.00 ± 55.09 (5.05) | 2.10 ± 0.73 (2.29) | 4.55 ± 1.65 (5.00) | 1.91 ± 0.89 (1.99) |
| right | p | 0.774 | 48/50 | 0 | 40 | 1.89 ± 1.43 (1.72) | 19.22 ± 37.84 (3.87) | 2.07 ± 0.62 (2.17) | 4.56 ± 1.51 (4.79) | 1.85 ± 0.84 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 100/100 | 0 | 86 | 1.95 ± 1.42 (1.72) | 19.55 ± 40.67 (4.31) | 2.10 ± 0.64 (2.26) | 4.63 ± 1.52 (5.21) | 1.90 ± 0.84 (2.01) |
| right | p | 0.760 | 97/100 | 0 | 81 | 2.11 ± 1.91 (1.72) | 19.48 ± 37.83 (4.87) | 2.00 ± 0.72 (2.20) | 4.39 ± 1.68 (4.58) | 1.78 ± 0.90 (1.85) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.818 | 25/25 | 0 | 23 | 1.62 ± 1.68 (1.36) | 9.99 ± 19.55 (3.21) | 2.15 ± 0.60 (2.24) | 4.69 ± 1.42 (4.80) | 1.92 ± 0.81 (1.79) |
| forward/right | p | 0.777 | 25/25 | 0 | 21 | 1.98 ± 2.38 (1.36) | 9.98 ± 11.79 (5.24) | 1.85 ± 0.77 (2.02) | 4.02 ± 1.78 (4.24) | 1.57 ± 0.93 (1.67) |
| left/left | p | 0.841 | 25/25 | 0 | 22 | 1.57 ± 0.41 (1.72) | 13.32 ± 23.33 (4.13) | 2.11 ± 0.65 (2.31) | 4.69 ± 1.58 (5.44) | 1.94 ± 0.81 (2.23) |
| left/right | p | 0.760 | 24/25 | 0 | 20 | 2.14 ± 2.12 (1.90) | 24.58 ± 43.55 (5.66) | 1.98 ± 0.66 (2.18) | 4.45 ± 1.62 (5.09) | 1.78 ± 0.89 (1.89) |
| back/left | p | 0.749 | 25/25 | 0 | 21 | 2.82 ± 1.95 (2.60) | 29.23 ± 56.51 (5.15) | 2.18 ± 0.58 (2.29) | 4.76 ± 1.36 (5.24) | 1.98 ± 0.80 (2.16) |
| back/right | p | 0.758 | 25/25 | 0 | 20 | 2.31 ± 0.67 (2.54) | 30.77 ± 53.61 (4.69) | 2.02 ± 0.84 (2.29) | 4.35 ± 1.88 (4.60) | 1.85 ± 0.97 (1.85) |
| right/left | p | 0.803 | 25/25 | 0 | 20 | 1.80 ± 0.51 (1.74) | 25.67 ± 47.28 (4.23) | 1.99 ± 0.70 (2.07) | 4.37 ± 1.67 (4.31) | 1.77 ± 0.93 (1.75) |
| right/right | p | 0.746 | 23/25 | 0 | 20 | 1.98 ± 2.00 (1.68) | 12.22 ± 21.53 (3.51) | 2.16 ± 0.50 (2.22) | 4.76 ± 1.28 (5.09) | 1.94 ± 0.71 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.805 | 20.6 | 5.10 | 2.18 |
| p | normal | 0.758 | 18.5 | 3.93 | 1.51 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.727 | 0.18 | 2.27 ± 1.02 (2.23) | 3.59 | 1.33 |
| p | medium | 16 | 0.839 | 0.68 | 1.30 ± 0.18 (1.28) | 4.24 | 1.69 |
| p | strong | 126 | 0.799 | 0.66 | - | 4.98 | 2.11 |

## Notes

- p: score 0.781, 197/200 kicked, 0 fell; worst sector back (0.753).
