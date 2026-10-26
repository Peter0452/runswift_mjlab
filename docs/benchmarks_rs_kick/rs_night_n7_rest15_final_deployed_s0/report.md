# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.876** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 8 |
| Time to kick [s] | 1.93 ± 1.37 (1.72) |
| Direction error [°] | 18.72 ± 39.35 (4.37) |
| Avg ball speed [m/s] | 1.92 ± 0.60 (2.03) |
| Peak ball speed [m/s] | 4.82 ± 1.55 (5.32) |
| Distance [m] | 2.15 ± 0.92 (2.22) |
| Path length [m] | 2.16 ± 0.92 (2.23) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.905 | 50/50 | 0 | 44 | 1.66 ± 1.93 (1.34) | 8.10 ± 11.32 (4.07) | 1.90 ± 0.55 (1.91) | 4.74 ± 1.40 (4.62) | 2.07 ± 0.84 (2.04) |
| left | p | 0.873 | 48/50 | 0 | 42 | 1.68 ± 0.46 (1.66) | 17.11 ± 32.95 (5.76) | 1.97 ± 0.51 (2.08) | 5.01 ± 1.38 (5.57) | 2.23 ± 0.84 (2.35) |
| back | p | 0.859 | 50/50 | 0 | 42 | 2.54 ± 1.24 (2.49) | 28.68 ± 58.71 (2.89) | 1.93 ± 0.68 (2.05) | 4.87 ± 1.75 (5.50) | 2.24 ± 1.02 (2.44) |
| right | p | 0.867 | 49/50 | 0 | 39 | 1.82 ± 1.20 (1.76) | 20.99 ± 35.93 (5.75) | 1.89 ± 0.64 (2.07) | 4.68 ± 1.62 (4.97) | 2.07 ± 0.95 (2.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.899 | 100/100 | 0 | 86 | 1.82 ± 1.04 (1.67) | 18.58 ± 40.41 (4.24) | 1.95 ± 0.58 (2.06) | 4.86 ± 1.49 (5.35) | 2.18 ± 0.89 (2.31) |
| right | p | 0.853 | 97/100 | 0 | 81 | 2.04 ± 1.64 (1.76) | 18.88 ± 38.23 (4.56) | 1.89 ± 0.62 (1.99) | 4.78 ± 1.61 (5.27) | 2.13 ± 0.95 (2.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.932 | 25/25 | 0 | 22 | 1.29 ± 0.29 (1.30) | 7.38 ± 12.26 (3.87) | 1.97 ± 0.57 (2.02) | 4.86 ± 1.42 (4.81) | 2.15 ± 0.80 (2.11) |
| forward/right | p | 0.878 | 25/25 | 0 | 22 | 2.04 ± 2.66 (1.34) | 8.82 ± 10.24 (6.45) | 1.82 ± 0.51 (1.88) | 4.61 ± 1.37 (4.38) | 2.00 ± 0.86 (1.88) |
| left/left | p | 0.927 | 25/25 | 0 | 23 | 1.55 ± 0.39 (1.62) | 12.17 ± 24.17 (5.43) | 2.00 ± 0.43 (2.09) | 5.07 ± 1.16 (5.49) | 2.27 ± 0.72 (2.39) |
| left/right | p | 0.819 | 23/25 | 0 | 19 | 1.82 ± 0.49 (1.94) | 22.49 ± 39.69 (5.99) | 1.94 ± 0.58 (2.02) | 4.95 ± 1.58 (5.60) | 2.19 ± 0.96 (2.33) |
| back/left | p | 0.853 | 25/25 | 0 | 21 | 2.71 ± 1.64 (2.50) | 29.94 ± 60.87 (3.63) | 1.94 ± 0.63 (2.03) | 4.93 ± 1.59 (5.49) | 2.25 ± 0.96 (2.50) |
| back/right | p | 0.865 | 25/25 | 0 | 21 | 2.38 ± 0.57 (2.48) | 27.42 ± 56.45 (2.82) | 1.91 ± 0.74 (2.07) | 4.81 ± 1.89 (5.74) | 2.23 ± 1.08 (2.34) |
| right/left | p | 0.885 | 25/25 | 0 | 20 | 1.74 ± 0.49 (1.84) | 24.83 ± 41.94 (6.17) | 1.88 ± 0.67 (2.07) | 4.60 ± 1.69 (4.72) | 2.04 ± 1.02 (2.01) |
| right/right | p | 0.850 | 24/25 | 0 | 19 | 1.90 ± 1.63 (1.64) | 16.99 ± 27.78 (5.18) | 1.91 ± 0.60 (2.06) | 4.76 ± 1.53 (5.34) | 2.10 ± 0.87 (2.15) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.868 | 16.6 | 5.44 | 2.52 |
| p | normal | 0.884 | 20.8 | 4.22 | 1.79 |

## Notes

- p: score 0.876, 197/200 kicked, 0 fell; worst sector back (0.859).
