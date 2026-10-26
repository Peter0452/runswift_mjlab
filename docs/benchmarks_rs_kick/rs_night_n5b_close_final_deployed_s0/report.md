# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n5b_close/model_19849.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 2.08 ± 1.82 (1.72) |
| Direction error [°] | 18.78 ± 38.00 (5.20) |
| Avg ball speed [m/s] | 2.13 ± 0.66 (2.31) |
| Peak ball speed [m/s] | 4.66 ± 1.59 (5.17) |
| Distance [m] | 1.89 ± 0.86 (1.95) |
| Path length [m] | 1.90 ± 0.86 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.885 | 50/50 | 0 | 41 | 2.04 ± 2.56 (1.38) | 8.70 ± 11.32 (4.35) | 2.13 ± 0.62 (2.23) | 4.65 ± 1.55 (4.56) | 1.87 ± 0.87 (1.83) |
| left | p | 0.867 | 49/50 | 0 | 42 | 1.81 ± 1.37 (1.74) | 18.77 ± 34.11 (5.51) | 2.09 ± 0.68 (2.31) | 4.64 ± 1.63 (5.28) | 1.88 ± 0.87 (1.99) |
| back | p | 0.802 | 47/50 | 0 | 38 | 2.32 ± 0.59 (2.42) | 30.39 ± 56.38 (4.76) | 2.16 ± 0.74 (2.38) | 4.66 ± 1.70 (5.33) | 1.94 ± 0.89 (2.07) |
| right | p | 0.862 | 49/50 | 0 | 42 | 2.17 ± 2.04 (1.74) | 17.94 ± 34.18 (5.43) | 2.13 ± 0.60 (2.30) | 4.67 ± 1.49 (4.87) | 1.87 ± 0.81 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.869 | 97/100 | 0 | 85 | 1.84 ± 1.18 (1.68) | 16.41 ± 35.21 (5.19) | 2.22 ± 0.57 (2.34) | 4.83 ± 1.37 (5.28) | 1.98 ± 0.79 (1.96) |
| right | p | 0.839 | 98/100 | 0 | 78 | 2.33 ± 2.26 (1.76) | 21.13 ± 40.43 (5.20) | 2.04 ± 0.74 (2.31) | 4.48 ± 1.76 (4.80) | 1.79 ± 0.92 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.919 | 25/25 | 0 | 22 | 1.70 ± 2.06 (1.38) | 7.47 ± 11.65 (3.00) | 2.26 ± 0.45 (2.26) | 4.96 ± 1.20 (5.15) | 2.02 ± 0.71 (1.99) |
| forward/right | p | 0.852 | 25/25 | 0 | 19 | 2.38 ± 2.94 (1.38) | 9.92 ± 10.84 (6.03) | 2.00 ± 0.73 (2.01) | 4.33 ± 1.78 (4.36) | 1.72 ± 0.97 (1.60) |
| left/left | p | 0.900 | 25/25 | 0 | 22 | 1.56 ± 0.41 (1.62) | 13.27 ± 20.99 (5.72) | 2.12 ± 0.69 (2.27) | 4.70 ± 1.59 (5.28) | 1.92 ± 0.85 (1.93) |
| left/right | p | 0.833 | 24/25 | 0 | 20 | 2.08 ± 1.88 (1.90) | 24.51 ± 43.04 (5.33) | 2.06 ± 0.68 (2.32) | 4.59 ± 1.66 (5.28) | 1.84 ± 0.90 (2.04) |
| back/left | p | 0.792 | 23/25 | 0 | 20 | 2.35 ± 0.67 (2.56) | 25.70 ± 52.18 (6.61) | 2.30 ± 0.54 (2.41) | 4.95 ± 1.28 (5.48) | 2.07 ± 0.82 (2.07) |
| back/right | p | 0.812 | 24/25 | 0 | 18 | 2.29 ± 0.49 (2.35) | 34.89 ± 59.79 (4.00) | 2.02 ± 0.87 (2.35) | 4.39 ± 1.99 (5.27) | 1.82 ± 0.95 (2.13) |
| right/left | p | 0.866 | 24/25 | 0 | 21 | 1.79 ± 0.47 (1.76) | 20.10 ± 40.13 (5.34) | 2.19 ± 0.55 (2.33) | 4.72 ± 1.37 (5.00) | 1.93 ± 0.77 (1.95) |
| right/right | p | 0.859 | 25/25 | 0 | 21 | 2.54 ± 2.77 (1.64) | 15.87 ± 27.12 (6.21) | 2.08 ± 0.64 (2.29) | 4.63 ± 1.59 (4.87) | 1.81 ± 0.83 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.838 | 16.2 | 5.42 | 2.29 |
| p | normal | 0.870 | 21.2 | 3.93 | 1.51 |

## Notes

- p: score 0.854, 195/200 kicked, 0 fell; worst sector back (0.802).
