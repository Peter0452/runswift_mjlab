# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_11-17-40_ovp_o3/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.935** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.65 ± 0.57 (1.54) |
| Direction error [°] | 6.76 ± 14.89 (4.76) |
| Avg ball speed [m/s] | 1.40 ± 0.27 (1.39) |
| Peak ball speed [m/s] | 3.79 ± 0.69 (3.76) |
| Distance [m] | 1.33 ± 0.39 (1.30) |
| Path length [m] | 1.33 ± 0.39 (1.30) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.922 | 50/50 | 0 | 46 | 1.21 ± 0.53 (1.14) | 8.82 ± 18.04 (4.83) | 1.27 ± 0.28 (1.28) | 3.48 ± 0.69 (3.39) | 1.13 ± 0.39 (1.10) |
| left | p | 0.944 | 50/50 | 0 | 49 | 1.53 ± 0.35 (1.54) | 5.57 ± 3.88 (4.84) | 1.47 ± 0.22 (1.49) | 3.96 ± 0.56 (4.00) | 1.43 ± 0.32 (1.41) |
| back | p | 0.927 | 50/50 | 0 | 48 | 2.32 ± 0.29 (2.31) | 7.58 ± 22.97 (3.75) | 1.48 ± 0.29 (1.47) | 3.99 ± 0.75 (4.00) | 1.48 ± 0.42 (1.48) |
| right | p | 0.946 | 50/50 | 0 | 50 | 1.53 ± 0.36 (1.50) | 5.08 ± 3.15 (5.22) | 1.38 ± 0.26 (1.37) | 3.71 ± 0.60 (3.58) | 1.28 ± 0.33 (1.23) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.932 | 100/100 | 0 | 95 | 1.64 ± 0.56 (1.60) | 7.21 ± 17.11 (4.50) | 1.35 ± 0.25 (1.37) | 3.67 ± 0.66 (3.64) | 1.27 ± 0.38 (1.25) |
| right | p | 0.937 | 100/100 | 0 | 98 | 1.65 ± 0.57 (1.51) | 6.31 ± 12.26 (4.91) | 1.45 ± 0.29 (1.46) | 3.90 ± 0.70 (3.86) | 1.39 ± 0.40 (1.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.921 | 25/25 | 0 | 23 | 1.22 ± 0.54 (1.16) | 7.09 ± 9.74 (4.81) | 1.22 ± 0.20 (1.25) | 3.28 ± 0.48 (3.27) | 1.03 ± 0.28 (1.05) |
| forward/right | p | 0.923 | 25/25 | 0 | 23 | 1.19 ± 0.52 (1.14) | 10.55 ± 23.45 (4.86) | 1.33 ± 0.33 (1.31) | 3.68 ± 0.81 (3.50) | 1.23 ± 0.45 (1.17) |
| left/left | p | 0.942 | 25/25 | 0 | 24 | 1.43 ± 0.35 (1.50) | 5.78 ± 4.13 (5.19) | 1.44 ± 0.19 (1.39) | 3.91 ± 0.47 (3.98) | 1.40 ± 0.27 (1.42) |
| left/right | p | 0.946 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.62) | 5.35 ± 3.60 (4.83) | 1.51 ± 0.24 (1.53) | 4.01 ± 0.64 (4.05) | 1.46 ± 0.36 (1.41) |
| back/left | p | 0.922 | 25/25 | 0 | 23 | 2.30 ± 0.30 (2.30) | 10.85 ± 32.04 (3.29) | 1.46 ± 0.31 (1.44) | 3.91 ± 0.82 (3.99) | 1.45 ± 0.46 (1.46) |
| back/right | p | 0.932 | 25/25 | 0 | 25 | 2.33 ± 0.29 (2.36) | 4.30 ± 2.59 (4.19) | 1.51 ± 0.27 (1.48) | 4.07 ± 0.66 (4.10) | 1.51 ± 0.39 (1.50) |
| right/left | p | 0.944 | 25/25 | 0 | 25 | 1.61 ± 0.33 (1.60) | 5.11 ± 3.57 (4.71) | 1.30 ± 0.23 (1.33) | 3.57 ± 0.57 (3.49) | 1.20 ± 0.31 (1.17) |
| right/right | p | 0.949 | 25/25 | 0 | 25 | 1.45 ± 0.36 (1.46) | 5.04 ± 2.66 (5.26) | 1.45 ± 0.26 (1.45) | 3.85 ± 0.60 (3.80) | 1.36 ± 0.34 (1.29) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.937 | 5.1 | 4.06 | 1.47 |
| p | normal | 0.932 | 8.4 | 3.51 | 1.19 |

## Notes

- p: score 0.935, 200/200 kicked, 0 fell; worst sector forward (0.922).
