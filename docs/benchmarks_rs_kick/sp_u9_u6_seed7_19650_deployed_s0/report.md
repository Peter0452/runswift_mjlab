# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u9_u6_seed7/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.773** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 2.19 ± 2.02 (1.76) |
| Direction error [°] | 18.76 ± 36.72 (5.84) |
| Avg ball speed [m/s] | 2.03 ± 0.66 (2.18) |
| Peak ball speed [m/s] | 4.40 ± 1.55 (4.90) |
| Distance [m] | 1.80 ± 0.83 (1.87) |
| Path length [m] | 1.81 ± 0.83 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.798 | 50/50 | 0 | 45 | 2.04 ± 2.63 (1.33) | 7.61 ± 10.75 (4.08) | 2.03 ± 0.54 (2.11) | 4.41 ± 1.35 (4.31) | 1.73 ± 0.74 (1.74) |
| left | p | 0.801 | 50/50 | 0 | 41 | 1.99 ± 1.86 (1.75) | 19.21 ± 33.21 (5.61) | 1.97 ± 0.71 (2.22) | 4.34 ± 1.66 (5.12) | 1.76 ± 0.84 (1.98) |
| back | p | 0.725 | 49/50 | 0 | 40 | 2.63 ± 1.32 (2.58) | 30.03 ± 53.16 (7.80) | 2.09 ± 0.74 (2.31) | 4.48 ± 1.67 (5.32) | 1.93 ± 0.92 (2.21) |
| right | p | 0.769 | 49/50 | 0 | 40 | 2.08 ± 1.95 (1.76) | 18.40 ± 33.55 (5.25) | 2.02 ± 0.63 (2.16) | 4.38 ± 1.48 (4.76) | 1.77 ± 0.78 (1.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 98/100 | 0 | 86 | 1.84 ± 1.09 (1.72) | 16.58 ± 35.25 (5.19) | 2.11 ± 0.54 (2.24) | 4.56 ± 1.30 (4.97) | 1.86 ± 0.73 (1.88) |
| right | p | 0.751 | 100/100 | 0 | 80 | 2.52 ± 2.58 (1.76) | 20.89 ± 37.99 (6.14) | 1.95 ± 0.75 (2.15) | 4.24 ± 1.74 (4.66) | 1.73 ± 0.90 (1.84) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 23 | 1.65 ± 1.84 (1.30) | 6.34 ± 10.60 (2.76) | 2.15 ± 0.45 (2.13) | 4.64 ± 1.13 (4.54) | 1.88 ± 0.66 (1.83) |
| forward/right | p | 0.764 | 25/25 | 0 | 22 | 2.44 ± 3.19 (1.34) | 8.88 ± 10.75 (5.64) | 1.92 ± 0.60 (2.01) | 4.18 ± 1.50 (4.06) | 1.59 ± 0.79 (1.56) |
| left/left | p | 0.841 | 25/25 | 0 | 22 | 1.56 ± 0.43 (1.66) | 14.23 ± 22.94 (6.46) | 2.07 ± 0.57 (2.20) | 4.58 ± 1.37 (5.17) | 1.86 ± 0.74 (1.97) |
| left/right | p | 0.761 | 25/25 | 0 | 19 | 2.42 ± 2.52 (1.90) | 24.18 ± 40.38 (5.00) | 1.87 ± 0.81 (2.24) | 4.10 ± 1.88 (5.06) | 1.65 ± 0.91 (1.98) |
| back/left | p | 0.740 | 24/25 | 0 | 21 | 2.38 ± 0.70 (2.49) | 25.76 ± 51.31 (7.51) | 2.21 ± 0.50 (2.33) | 4.73 ± 1.20 (5.37) | 2.02 ± 0.77 (2.20) |
| back/right | p | 0.709 | 25/25 | 0 | 19 | 2.88 ± 1.68 (2.60) | 34.13 ± 54.57 (8.09) | 1.98 ± 0.90 (2.31) | 4.25 ± 1.99 (5.31) | 1.85 ± 1.04 (2.21) |
| right/left | p | 0.769 | 24/25 | 0 | 20 | 1.80 ± 0.51 (1.78) | 20.50 ± 39.50 (4.03) | 1.99 ± 0.60 (2.15) | 4.31 ± 1.44 (4.57) | 1.70 ± 0.73 (1.83) |
| right/right | p | 0.769 | 25/25 | 0 | 20 | 2.35 ± 2.66 (1.72) | 16.39 ± 26.45 (5.98) | 2.05 ± 0.65 (2.16) | 4.45 ± 1.52 (4.87) | 1.84 ± 0.81 (1.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.797 | 17.2 | 5.03 | 2.15 |
| p | normal | 0.749 | 20.2 | 3.79 | 1.46 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.18 | 2.23 ± 0.98 (2.16) | 3.49 | 1.29 |
| p | medium | 16 | 0.811 | 0.68 | 1.19 ± 0.34 (1.25) | 3.84 | 1.51 |
| p | strong | 126 | 0.797 | 0.65 | - | 4.90 | 2.07 |

## Notes

- p: score 0.773, 198/200 kicked, 0 fell; worst sector back (0.725).
