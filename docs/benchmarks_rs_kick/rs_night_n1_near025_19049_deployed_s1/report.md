# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.879** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 175 |
| Weak kicks (< 0.3 m) | 20 |
| Time to kick [s] | 1.86 ± 1.06 (1.66) |
| Direction error [°] | 12.65 ± 26.66 (5.04) |
| Avg ball speed [m/s] | 2.27 ± 0.75 (2.47) |
| Peak ball speed [m/s] | 4.83 ± 1.69 (5.56) |
| Distance [m] | 2.27 ± 1.01 (2.59) |
| Path length [m] | 2.28 ± 1.01 (2.62) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.901 | 49/50 | 0 | 45 | 1.38 ± 1.07 (1.30) | 7.99 ± 14.84 (3.42) | 2.23 ± 0.66 (2.33) | 4.81 ± 1.51 (5.45) | 2.18 ± 0.87 (2.23) |
| left | p | 0.903 | 50/50 | 0 | 44 | 1.89 ± 1.50 (1.62) | 11.74 ± 23.53 (4.85) | 2.28 ± 0.75 (2.45) | 4.83 ± 1.66 (5.53) | 2.27 ± 1.05 (2.63) |
| back | p | 0.800 | 49/50 | 0 | 39 | 2.43 ± 0.61 (2.44) | 24.39 ± 42.26 (8.05) | 2.22 ± 0.95 (2.60) | 4.76 ± 2.10 (5.72) | 2.33 ± 1.22 (2.84) |
| right | p | 0.912 | 49/50 | 0 | 47 | 1.73 ± 0.38 (1.78) | 6.50 ± 9.39 (3.74) | 2.34 ± 0.59 (2.47) | 4.95 ± 1.38 (5.60) | 2.31 ± 0.85 (2.55) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.894 | 99/100 | 0 | 89 | 1.86 ± 1.18 (1.62) | 11.76 ± 26.43 (4.92) | 2.30 ± 0.72 (2.49) | 4.92 ± 1.64 (5.64) | 2.33 ± 1.00 (2.61) |
| right | p | 0.864 | 98/100 | 0 | 86 | 1.86 ± 0.92 (1.68) | 13.55 ± 26.87 (5.73) | 2.24 ± 0.78 (2.42) | 4.74 ± 1.73 (5.47) | 2.22 ± 1.01 (2.52) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.925 | 25/25 | 0 | 22 | 1.23 ± 0.32 (1.28) | 8.29 ± 14.63 (3.66) | 2.24 ± 0.64 (2.32) | 4.87 ± 1.49 (5.45) | 2.23 ± 0.88 (2.44) |
| forward/right | p | 0.877 | 24/25 | 0 | 23 | 1.54 ± 1.47 (1.30) | 7.68 ± 15.05 (3.14) | 2.21 ± 0.68 (2.33) | 4.74 ± 1.54 (5.28) | 2.13 ± 0.86 (2.13) |
| left/left | p | 0.917 | 25/25 | 0 | 23 | 2.04 ± 2.04 (1.58) | 6.24 ± 7.39 (3.70) | 2.36 ± 0.68 (2.66) | 5.01 ± 1.56 (5.86) | 2.41 ± 0.99 (2.93) |
| left/right | p | 0.890 | 25/25 | 0 | 21 | 1.75 ± 0.52 (1.80) | 17.24 ± 31.50 (4.91) | 2.20 ± 0.80 (2.31) | 4.64 ± 1.74 (4.50) | 2.14 ± 1.09 (1.89) |
| back/left | p | 0.840 | 25/25 | 0 | 21 | 2.31 ± 0.68 (2.40) | 25.97 ± 45.74 (6.86) | 2.30 ± 0.85 (2.65) | 4.90 ± 1.89 (5.77) | 2.39 ± 1.17 (2.80) |
| back/right | p | 0.760 | 24/25 | 0 | 18 | 2.55 ± 0.50 (2.55) | 22.74 ± 38.24 (8.72) | 2.14 ± 1.05 (2.56) | 4.61 ± 2.29 (5.71) | 2.27 ± 1.26 (2.85) |
| right/left | p | 0.895 | 24/25 | 0 | 23 | 1.85 ± 0.37 (1.87) | 6.31 ± 11.72 (2.68) | 2.29 ± 0.69 (2.39) | 4.91 ± 1.60 (5.64) | 2.30 ± 0.93 (2.51) |
| right/right | p | 0.930 | 25/25 | 0 | 24 | 1.62 ± 0.35 (1.56) | 6.68 ± 6.38 (5.42) | 2.39 ± 0.48 (2.52) | 4.98 ± 1.13 (5.46) | 2.32 ± 0.77 (2.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.878 | 12.9 | 5.41 | 2.70 |
| p | normal | 0.880 | 12.4 | 4.24 | 1.84 |

## Notes

- p: score 0.879, 197/200 kicked, 0 fell; worst sector back (0.800).
