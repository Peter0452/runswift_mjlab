# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 8 |
| Time to kick [s] | 2.01 ± 1.55 (1.74) |
| Direction error [°] | 17.68 ± 36.41 (5.36) |
| Avg ball speed [m/s] | 2.15 ± 0.62 (2.28) |
| Peak ball speed [m/s] | 4.61 ± 1.44 (5.15) |
| Distance [m] | 1.94 ± 0.84 (2.02) |
| Path length [m] | 1.95 ± 0.84 (2.03) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.781 | 49/50 | 0 | 43 | 1.82 ± 2.10 (1.36) | 7.81 ± 9.96 (4.40) | 2.10 ± 0.58 (2.17) | 4.48 ± 1.38 (4.23) | 1.82 ± 0.79 (1.74) |
| left | p | 0.800 | 49/50 | 0 | 42 | 1.85 ± 1.40 (1.76) | 19.21 ± 34.35 (5.61) | 2.14 ± 0.61 (2.31) | 4.65 ± 1.46 (5.34) | 1.95 ± 0.82 (2.12) |
| back | p | 0.755 | 49/50 | 0 | 40 | 2.53 ± 1.23 (2.52) | 26.94 ± 53.09 (5.73) | 2.27 ± 0.67 (2.45) | 4.80 ± 1.51 (5.44) | 2.14 ± 0.93 (2.35) |
| right | p | 0.790 | 49/50 | 0 | 42 | 1.82 ± 1.14 (1.72) | 16.77 ± 31.94 (4.75) | 2.08 ± 0.58 (2.20) | 4.52 ± 1.38 (4.79) | 1.85 ± 0.77 (2.01) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 100/100 | 0 | 87 | 1.90 ± 1.26 (1.72) | 17.50 ± 37.78 (5.40) | 2.19 ± 0.60 (2.34) | 4.70 ± 1.41 (5.35) | 1.99 ± 0.84 (2.07) |
| right | p | 0.751 | 96/100 | 0 | 80 | 2.11 ± 1.79 (1.75) | 17.87 ± 34.93 (5.07) | 2.11 ± 0.62 (2.24) | 4.52 ± 1.47 (4.94) | 1.88 ± 0.84 (1.98) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 23 | 1.61 ± 1.58 (1.38) | 6.42 ± 10.08 (2.91) | 2.20 ± 0.63 (2.23) | 4.68 ± 1.45 (4.51) | 1.98 ± 0.84 (1.88) |
| forward/right | p | 0.732 | 24/25 | 0 | 20 | 2.04 ± 2.52 (1.35) | 9.27 ± 9.63 (4.72) | 2.00 ± 0.51 (2.02) | 4.26 ± 1.27 (4.10) | 1.67 ± 0.71 (1.64) |
| left/left | p | 0.850 | 25/25 | 0 | 23 | 1.60 ± 0.42 (1.66) | 12.32 ± 21.94 (6.30) | 2.27 ± 0.53 (2.44) | 4.94 ± 1.27 (5.42) | 2.12 ± 0.74 (2.19) |
| left/right | p | 0.750 | 24/25 | 0 | 19 | 2.11 ± 1.92 (1.93) | 26.39 ± 42.51 (5.56) | 2.00 ± 0.66 (2.20) | 4.35 ± 1.58 (4.94) | 1.77 ± 0.87 (1.94) |
| back/left | p | 0.758 | 25/25 | 0 | 20 | 2.64 ± 1.64 (2.42) | 30.64 ± 56.95 (6.58) | 2.29 ± 0.62 (2.50) | 4.81 ± 1.40 (5.44) | 2.14 ± 0.93 (2.51) |
| back/right | p | 0.751 | 24/25 | 0 | 20 | 2.41 ± 0.53 (2.60) | 23.09 ± 48.44 (5.08) | 2.26 ± 0.72 (2.41) | 4.79 ± 1.63 (5.39) | 2.13 ± 0.94 (2.28) |
| right/left | p | 0.810 | 25/25 | 0 | 21 | 1.75 ± 0.47 (1.76) | 20.64 ± 39.39 (4.45) | 1.99 ± 0.59 (2.12) | 4.36 ± 1.44 (4.78) | 1.73 ± 0.77 (1.82) |
| right/right | p | 0.770 | 24/25 | 0 | 21 | 1.90 ± 1.55 (1.70) | 12.74 ± 20.84 (4.86) | 2.17 ± 0.55 (2.29) | 4.68 ± 1.29 (5.27) | 1.98 ± 0.75 (2.12) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 15.9 | 5.28 | 2.33 |
| p | normal | 0.759 | 19.4 | 3.97 | 1.57 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.720 | 0.15 | 2.32 ± 0.92 (2.29) | 3.64 | 1.36 |
| p | medium | 16 | 0.833 | 0.68 | 1.26 ± 0.24 (1.28) | 4.11 | 1.66 |
| p | strong | 126 | 0.803 | 0.68 | - | 5.14 | 2.25 |

## Notes

- p: score 0.781, 196/200 kicked, 0 fell; worst sector back (0.755).
