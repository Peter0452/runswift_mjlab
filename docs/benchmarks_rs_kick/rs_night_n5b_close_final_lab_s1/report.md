# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n5b_close/model_19849.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.946** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.53 ± 0.52 (1.46) |
| Direction error [°] | 5.06 ± 3.77 (4.15) |
| Avg ball speed [m/s] | 2.14 ± 0.36 (2.20) |
| Peak ball speed [m/s] | 4.62 ± 0.86 (4.92) |
| Distance [m] | 1.93 ± 0.58 (2.04) |
| Path length [m] | 1.94 ± 0.58 (2.05) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.944 | 50/50 | 0 | 48 | 1.01 ± 0.26 (1.03) | 5.55 ± 4.36 (4.24) | 1.95 ± 0.37 (2.05) | 4.29 ± 0.86 (4.39) | 1.68 ± 0.56 (1.62) |
| left | p | 0.942 | 50/50 | 0 | 49 | 1.47 ± 0.35 (1.39) | 5.83 ± 3.73 (5.89) | 2.12 ± 0.34 (2.19) | 4.58 ± 0.80 (4.81) | 1.92 ± 0.54 (2.07) |
| back | p | 0.951 | 50/50 | 0 | 50 | 2.19 ± 0.27 (2.16) | 3.66 ± 2.95 (2.70) | 2.32 ± 0.24 (2.37) | 5.00 ± 0.70 (5.31) | 2.19 ± 0.49 (2.33) |
| right | p | 0.948 | 50/50 | 0 | 50 | 1.47 ± 0.34 (1.51) | 5.20 ± 3.53 (5.04) | 2.15 ± 0.36 (2.27) | 4.62 ± 0.90 (4.98) | 1.95 ± 0.61 (2.12) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.947 | 100/100 | 0 | 99 | 1.53 ± 0.52 (1.40) | 5.08 ± 3.67 (3.88) | 2.15 ± 0.35 (2.21) | 4.66 ± 0.83 (4.94) | 1.96 ± 0.56 (2.08) |
| right | p | 0.946 | 100/100 | 0 | 98 | 1.54 ± 0.52 (1.52) | 5.05 ± 3.87 (4.21) | 2.12 ± 0.36 (2.18) | 4.58 ± 0.88 (4.73) | 1.91 ± 0.60 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.945 | 25/25 | 0 | 24 | 1.00 ± 0.26 (1.00) | 5.51 ± 4.17 (4.46) | 1.96 ± 0.39 (2.10) | 4.33 ± 0.90 (4.63) | 1.70 ± 0.56 (1.84) |
| forward/right | p | 0.944 | 25/25 | 0 | 24 | 1.02 ± 0.26 (1.10) | 5.59 ± 4.55 (4.21) | 1.94 ± 0.36 (1.84) | 4.24 ± 0.83 (4.08) | 1.65 ± 0.55 (1.44) |
| left/left | p | 0.941 | 25/25 | 0 | 25 | 1.39 ± 0.34 (1.34) | 5.91 ± 3.75 (6.69) | 2.14 ± 0.36 (2.21) | 4.65 ± 0.83 (4.93) | 1.96 ± 0.57 (2.16) |
| left/right | p | 0.942 | 25/25 | 0 | 24 | 1.56 ± 0.34 (1.54) | 5.75 ± 3.70 (5.46) | 2.10 ± 0.31 (2.08) | 4.52 ± 0.76 (4.61) | 1.88 ± 0.51 (1.94) |
| back/left | p | 0.954 | 25/25 | 0 | 25 | 2.19 ± 0.22 (2.22) | 3.67 ± 2.90 (2.53) | 2.32 ± 0.24 (2.36) | 4.99 ± 0.65 (5.30) | 2.17 ± 0.45 (2.32) |
| back/right | p | 0.948 | 25/25 | 0 | 25 | 2.19 ± 0.31 (2.16) | 3.65 ± 2.99 (2.85) | 2.33 ± 0.24 (2.43) | 5.01 ± 0.73 (5.32) | 2.21 ± 0.52 (2.40) |
| right/left | p | 0.948 | 25/25 | 0 | 25 | 1.55 ± 0.33 (1.52) | 5.22 ± 3.35 (5.18) | 2.18 ± 0.31 (2.26) | 4.69 ± 0.80 (4.96) | 2.00 ± 0.56 (2.09) |
| right/right | p | 0.948 | 25/25 | 0 | 25 | 1.39 ± 0.32 (1.44) | 5.19 ± 3.70 (4.90) | 2.12 ± 0.40 (2.35) | 4.55 ± 0.98 (5.18) | 1.90 ± 0.65 (2.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.948 | 4.8 | 5.17 | 2.28 |
| p | normal | 0.945 | 5.3 | 4.08 | 1.59 |

## Notes

- p: score 0.946, 200/200 kicked, 0 fell; worst sector left (0.942).
