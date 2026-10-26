# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_10-42-42_ovp_o2/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.834** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 156 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.02 ± 1.54 (1.80) |
| Direction error [°] | 19.47 ± 35.59 (7.70) |
| Avg ball speed [m/s] | 2.25 ± 0.79 (2.48) |
| Peak ball speed [m/s] | 4.76 ± 1.76 (5.49) |
| Distance [m] | 2.26 ± 1.13 (2.52) |
| Path length [m] | 2.27 ± 1.14 (2.53) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.871 | 49/50 | 0 | 41 | 1.98 ± 2.50 (1.40) | 8.82 ± 11.49 (4.88) | 2.13 ± 0.74 (2.08) | 4.51 ± 1.66 (4.14) | 2.04 ± 1.06 (1.75) |
| left | p | 0.844 | 48/50 | 0 | 40 | 1.69 ± 0.51 (1.77) | 19.20 ± 32.27 (7.35) | 2.33 ± 0.79 (2.64) | 4.93 ± 1.76 (5.84) | 2.39 ± 1.13 (2.95) |
| back | p | 0.769 | 48/50 | 0 | 36 | 2.41 ± 0.72 (2.58) | 32.46 ± 52.34 (10.37) | 2.28 ± 0.82 (2.66) | 4.82 ± 1.83 (5.79) | 2.35 ± 1.20 (2.88) |
| right | p | 0.854 | 49/50 | 0 | 39 | 1.99 ± 1.47 (1.84) | 17.67 ± 29.95 (7.63) | 2.26 ± 0.81 (2.45) | 4.78 ± 1.77 (5.41) | 2.26 ± 1.11 (2.55) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.869 | 99/100 | 0 | 82 | 1.82 ± 0.66 (1.80) | 17.86 ± 34.87 (7.30) | 2.28 ± 0.73 (2.58) | 4.83 ± 1.65 (5.58) | 2.29 ± 1.08 (2.56) |
| right | p | 0.800 | 95/100 | 0 | 74 | 2.23 ± 2.08 (1.80) | 21.14 ± 36.25 (8.09) | 2.22 ± 0.85 (2.33) | 4.69 ± 1.87 (5.28) | 2.22 ± 1.19 (2.30) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.920 | 25/25 | 0 | 22 | 1.34 ± 0.32 (1.34) | 8.22 ± 12.16 (4.80) | 2.13 ± 0.73 (2.17) | 4.54 ± 1.68 (4.21) | 2.05 ± 1.04 (1.79) |
| forward/right | p | 0.821 | 24/25 | 0 | 19 | 2.65 ± 3.43 (1.46) | 9.44 ± 10.72 (5.22) | 2.14 ± 0.74 (2.01) | 4.49 ± 1.64 (4.09) | 2.03 ± 1.07 (1.70) |
| left/left | p | 0.904 | 25/25 | 0 | 23 | 1.62 ± 0.42 (1.74) | 12.20 ± 18.12 (7.10) | 2.37 ± 0.67 (2.60) | 5.07 ± 1.51 (5.76) | 2.48 ± 0.98 (2.93) |
| left/right | p | 0.784 | 23/25 | 0 | 17 | 1.77 ± 0.58 (1.98) | 26.80 ± 41.29 (9.72) | 2.29 ± 0.90 (2.72) | 4.77 ± 1.99 (5.92) | 2.29 ± 1.26 (3.09) |
| back/left | p | 0.769 | 24/25 | 0 | 17 | 2.42 ± 0.77 (2.60) | 33.23 ± 54.00 (10.35) | 2.29 ± 0.73 (2.63) | 4.86 ± 1.69 (5.82) | 2.35 ± 1.15 (2.88) |
| back/right | p | 0.768 | 24/25 | 0 | 19 | 2.40 ± 0.67 (2.54) | 31.69 ± 50.62 (10.50) | 2.28 ± 0.90 (2.71) | 4.79 ± 1.95 (5.72) | 2.35 ± 1.26 (2.88) |
| right/left | p | 0.882 | 25/25 | 0 | 20 | 1.92 ± 0.52 (1.90) | 18.42 ± 34.44 (6.95) | 2.33 ± 0.77 (2.63) | 4.86 ± 1.68 (5.66) | 2.31 ± 1.10 (2.60) |
| right/right | p | 0.825 | 24/25 | 0 | 19 | 2.07 ± 2.03 (1.76) | 16.88 ± 24.39 (7.66) | 2.20 ± 0.84 (2.39) | 4.70 ± 1.85 (5.28) | 2.22 ± 1.13 (2.42) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.829 | 16.3 | 5.64 | 2.87 |
| p | normal | 0.840 | 22.5 | 3.89 | 1.66 |

## Notes

- p: score 0.834, 194/200 kicked, 0 fell; worst sector back (0.769).
