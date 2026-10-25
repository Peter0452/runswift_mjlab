# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.945** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.54 ± 0.52 (1.46) |
| Direction error [°] | 6.16 ± 14.69 (3.88) |
| Avg ball speed [m/s] | 1.62 ± 0.34 (1.71) |
| Peak ball speed [m/s] | 3.88 ± 0.82 (4.06) |
| Distance [m] | 1.33 ± 0.45 (1.37) |
| Path length [m] | 1.34 ± 0.46 (1.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.950 | 50/50 | 0 | 48 | 1.08 ± 0.42 (1.04) | 6.48 ± 17.74 (3.15) | 1.42 ± 0.38 (1.48) | 3.38 ± 0.87 (3.51) | 1.04 ± 0.46 (1.14) |
| left | p | 0.943 | 50/50 | 0 | 50 | 1.45 ± 0.32 (1.45) | 5.67 ± 3.59 (5.62) | 1.68 ± 0.26 (1.75) | 4.05 ± 0.67 (4.22) | 1.43 ± 0.40 (1.44) |
| back | p | 0.941 | 50/50 | 0 | 49 | 2.16 ± 0.28 (2.11) | 7.23 ± 22.83 (2.98) | 1.76 ± 0.31 (1.83) | 4.20 ± 0.74 (4.39) | 1.53 ± 0.40 (1.60) |
| right | p | 0.947 | 50/50 | 0 | 50 | 1.45 ± 0.33 (1.42) | 5.27 ± 3.50 (4.94) | 1.63 ± 0.32 (1.65) | 3.88 ± 0.73 (3.97) | 1.32 ± 0.40 (1.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.947 | 100/100 | 0 | 99 | 1.53 ± 0.51 (1.45) | 6.22 ± 16.36 (3.62) | 1.64 ± 0.34 (1.73) | 3.89 ± 0.79 (3.98) | 1.34 ± 0.44 (1.36) |
| right | p | 0.943 | 100/100 | 0 | 98 | 1.55 ± 0.53 (1.46) | 6.10 ± 12.81 (4.20) | 1.60 ± 0.35 (1.70) | 3.86 ± 0.84 (4.10) | 1.32 ± 0.47 (1.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.958 | 25/25 | 0 | 25 | 1.08 ± 0.35 (1.06) | 4.11 ± 2.83 (3.32) | 1.47 ± 0.35 (1.58) | 3.50 ± 0.76 (3.84) | 1.10 ± 0.42 (1.14) |
| forward/right | p | 0.942 | 25/25 | 0 | 23 | 1.09 ± 0.47 (1.02) | 8.85 ± 24.70 (2.40) | 1.37 ± 0.40 (1.29) | 3.25 ± 0.95 (3.28) | 0.98 ± 0.49 (0.87) |
| left/left | p | 0.944 | 25/25 | 0 | 25 | 1.35 ± 0.32 (1.42) | 5.61 ± 3.51 (5.74) | 1.60 ± 0.27 (1.71) | 3.83 ± 0.68 (3.88) | 1.30 ± 0.37 (1.34) |
| left/right | p | 0.943 | 25/25 | 0 | 25 | 1.55 ± 0.29 (1.58) | 5.72 ± 3.66 (5.51) | 1.76 ± 0.23 (1.80) | 4.26 ± 0.60 (4.34) | 1.56 ± 0.39 (1.63) |
| back/left | p | 0.934 | 25/25 | 0 | 24 | 2.16 ± 0.26 (2.12) | 10.51 ± 31.85 (2.71) | 1.77 ± 0.37 (1.85) | 4.20 ± 0.87 (4.43) | 1.56 ± 0.44 (1.64) |
| back/right | p | 0.948 | 25/25 | 0 | 25 | 2.17 ± 0.29 (2.08) | 3.95 ± 2.64 (2.99) | 1.74 ± 0.22 (1.80) | 4.20 ± 0.59 (4.39) | 1.50 ± 0.35 (1.56) |
| right/left | p | 0.953 | 25/25 | 0 | 25 | 1.54 ± 0.31 (1.46) | 4.66 ± 3.16 (3.97) | 1.71 ± 0.28 (1.82) | 4.03 ± 0.66 (4.28) | 1.40 ± 0.38 (1.46) |
| right/right | p | 0.941 | 25/25 | 0 | 25 | 1.36 ± 0.33 (1.40) | 5.89 ± 3.71 (5.65) | 1.54 ± 0.34 (1.60) | 3.73 ± 0.77 (3.85) | 1.24 ± 0.40 (1.26) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.947 | 4.9 | 4.33 | 1.56 |
| p | normal | 0.944 | 7.5 | 3.43 | 1.10 |

## Notes

- p: score 0.945, 200/200 kicked, 0 fell; worst sector back (0.941).
