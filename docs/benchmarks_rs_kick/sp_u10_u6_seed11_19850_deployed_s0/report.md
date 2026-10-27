# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u10_u6_seed11/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.99 ± 1.61 (1.72) |
| Direction error [°] | 18.32 ± 37.09 (5.23) |
| Avg ball speed [m/s] | 2.09 ± 0.63 (2.27) |
| Peak ball speed [m/s] | 4.50 ± 1.48 (5.14) |
| Distance [m] | 1.87 ± 0.83 (2.03) |
| Path length [m] | 1.88 ± 0.83 (2.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.786 | 49/50 | 0 | 40 | 1.67 ± 1.97 (1.32) | 8.71 ± 11.65 (4.54) | 2.03 ± 0.60 (2.15) | 4.35 ± 1.44 (4.33) | 1.75 ± 0.80 (1.69) |
| left | p | 0.802 | 49/50 | 0 | 42 | 1.85 ± 1.52 (1.72) | 18.67 ± 34.35 (5.01) | 2.14 ± 0.60 (2.33) | 4.60 ± 1.43 (5.35) | 1.91 ± 0.80 (2.18) |
| back | p | 0.738 | 49/50 | 0 | 39 | 2.57 ± 1.25 (2.58) | 28.85 ± 54.16 (5.82) | 2.15 ± 0.69 (2.32) | 4.61 ± 1.60 (5.15) | 1.99 ± 0.90 (2.11) |
| right | p | 0.791 | 49/50 | 0 | 41 | 1.87 ± 1.46 (1.72) | 17.06 ± 32.38 (5.50) | 2.05 ± 0.62 (2.27) | 4.42 ± 1.45 (5.19) | 1.81 ± 0.79 (2.12) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 100/100 | 0 | 86 | 1.92 ± 1.35 (1.68) | 17.71 ± 37.86 (5.10) | 2.15 ± 0.56 (2.27) | 4.63 ± 1.32 (5.15) | 1.93 ± 0.79 (2.08) |
| right | p | 0.750 | 96/100 | 0 | 76 | 2.07 ± 1.83 (1.72) | 18.96 ± 36.26 (5.47) | 2.04 ± 0.70 (2.24) | 4.36 ± 1.62 (4.56) | 1.80 ± 0.87 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 22 | 1.62 ± 1.83 (1.28) | 7.09 ± 11.33 (3.47) | 2.18 ± 0.51 (2.22) | 4.68 ± 1.22 (5.06) | 1.93 ± 0.75 (1.91) |
| forward/right | p | 0.743 | 24/25 | 0 | 18 | 1.72 ± 2.09 (1.33) | 10.39 ± 11.73 (5.67) | 1.87 ± 0.65 (2.02) | 4.02 ± 1.56 (4.04) | 1.56 ± 0.81 (1.63) |
| left/left | p | 0.844 | 25/25 | 0 | 23 | 1.58 ± 0.41 (1.62) | 12.47 ± 21.60 (6.36) | 2.22 ± 0.52 (2.33) | 4.80 ± 1.26 (5.43) | 2.04 ± 0.73 (2.22) |
| left/right | p | 0.760 | 24/25 | 0 | 19 | 2.14 ± 2.09 (1.90) | 25.13 ± 42.92 (4.79) | 2.06 ± 0.66 (2.35) | 4.38 ± 1.55 (5.33) | 1.78 ± 0.85 (2.10) |
| back/left | p | 0.753 | 25/25 | 0 | 20 | 2.71 ± 1.63 (2.58) | 29.83 ± 56.73 (5.82) | 2.19 ± 0.56 (2.27) | 4.70 ± 1.32 (5.15) | 1.99 ± 0.85 (2.05) |
| back/right | p | 0.724 | 24/25 | 0 | 19 | 2.42 ± 0.61 (2.56) | 27.83 ± 51.34 (5.80) | 2.11 ± 0.81 (2.40) | 4.52 ± 1.84 (5.49) | 1.99 ± 0.94 (2.28) |
| right/left | p | 0.807 | 25/25 | 0 | 21 | 1.76 ± 0.49 (1.76) | 21.46 ± 40.25 (5.50) | 2.01 ± 0.62 (2.25) | 4.33 ± 1.44 (5.12) | 1.75 ± 0.78 (2.12) |
| right/right | p | 0.774 | 24/25 | 0 | 20 | 1.99 ± 2.02 (1.70) | 12.47 ± 20.31 (5.03) | 2.10 ± 0.62 (2.35) | 4.52 ± 1.45 (5.26) | 1.88 ± 0.79 (2.19) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.793 | 18.0 | 5.15 | 2.23 |
| p | normal | 0.765 | 18.7 | 3.87 | 1.51 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.728 | 0.17 | 2.20 ± 0.98 (2.08) | 3.48 | 1.29 |
| p | medium | 16 | 0.854 | 0.72 | 1.23 ± 0.22 (1.23) | 3.98 | 1.55 |
| p | strong | 126 | 0.794 | 0.67 | - | 5.05 | 2.18 |

## Notes

- p: score 0.779, 196/200 kicked, 0 fell; worst sector back (0.738).
