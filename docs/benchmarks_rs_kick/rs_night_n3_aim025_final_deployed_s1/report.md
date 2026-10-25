# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n3_aim025/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.876** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 179 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.05 ± 1.44 (1.76) |
| Direction error [°] | 11.49 ± 23.66 (5.06) |
| Avg ball speed [m/s] | 2.27 ± 0.61 (2.35) |
| Peak ball speed [m/s] | 4.76 ± 1.37 (5.24) |
| Distance [m] | 2.05 ± 0.78 (2.13) |
| Path length [m] | 2.06 ± 0.78 (2.13) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.869 | 48/50 | 0 | 44 | 1.63 ± 1.54 (1.36) | 7.17 ± 9.49 (3.78) | 2.16 ± 0.59 (2.29) | 4.60 ± 1.34 (4.52) | 1.91 ± 0.72 (1.84) |
| left | p | 0.901 | 50/50 | 0 | 44 | 1.89 ± 1.24 (1.67) | 12.15 ± 23.33 (4.89) | 2.23 ± 0.60 (2.32) | 4.73 ± 1.36 (5.20) | 2.02 ± 0.79 (2.10) |
| back | p | 0.826 | 49/50 | 0 | 45 | 2.75 ± 1.32 (2.62) | 15.55 ± 32.88 (5.80) | 2.41 ± 0.62 (2.51) | 5.03 ± 1.35 (5.42) | 2.25 ± 0.80 (2.26) |
| right | p | 0.909 | 50/50 | 0 | 46 | 1.92 ± 1.37 (1.82) | 10.98 ± 21.91 (4.99) | 2.27 ± 0.61 (2.35) | 4.69 ± 1.38 (5.16) | 2.02 ± 0.76 (1.96) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.874 | 99/100 | 0 | 89 | 2.09 ± 1.53 (1.74) | 12.50 ± 25.24 (5.07) | 2.21 ± 0.66 (2.35) | 4.68 ± 1.49 (5.24) | 2.00 ± 0.80 (2.14) |
| right | p | 0.878 | 98/100 | 0 | 90 | 2.01 ± 1.33 (1.77) | 10.46 ± 21.89 (4.94) | 2.33 ± 0.55 (2.36) | 4.84 ± 1.22 (5.17) | 2.10 ± 0.76 (2.11) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.876 | 24/25 | 0 | 22 | 1.41 ± 0.75 (1.32) | 6.89 ± 8.62 (3.83) | 2.16 ± 0.60 (2.29) | 4.64 ± 1.42 (5.04) | 1.94 ± 0.75 (1.97) |
| forward/right | p | 0.862 | 24/25 | 0 | 22 | 1.85 ± 2.02 (1.44) | 7.46 ± 10.29 (3.78) | 2.16 ± 0.57 (2.26) | 4.56 ± 1.27 (4.45) | 1.88 ± 0.70 (1.84) |
| left/left | p | 0.906 | 25/25 | 0 | 23 | 2.01 ± 1.67 (1.64) | 8.00 ± 10.46 (5.04) | 2.26 ± 0.54 (2.34) | 4.84 ± 1.28 (5.40) | 2.07 ± 0.72 (2.16) |
| left/right | p | 0.895 | 25/25 | 0 | 21 | 1.78 ± 0.51 (1.78) | 16.30 ± 30.74 (4.74) | 2.21 ± 0.65 (2.22) | 4.61 ± 1.43 (4.53) | 1.97 ± 0.86 (1.87) |
| back/left | p | 0.824 | 25/25 | 0 | 22 | 2.69 ± 1.29 (2.60) | 19.94 ± 36.49 (7.07) | 2.27 ± 0.74 (2.45) | 4.77 ± 1.62 (5.24) | 2.11 ± 0.88 (2.14) |
| back/right | p | 0.829 | 24/25 | 0 | 23 | 2.82 ± 1.35 (2.63) | 10.96 ± 27.90 (5.12) | 2.56 ± 0.41 (2.58) | 5.30 ± 0.93 (5.70) | 2.41 ± 0.68 (2.54) |
| right/left | p | 0.891 | 25/25 | 0 | 22 | 2.21 ± 1.86 (1.94) | 14.94 ± 29.98 (4.69) | 2.15 ± 0.72 (2.32) | 4.48 ± 1.61 (5.07) | 1.91 ± 0.82 (1.93) |
| right/right | p | 0.926 | 25/25 | 0 | 24 | 1.63 ± 0.34 (1.54) | 7.01 ± 5.49 (6.73) | 2.40 ± 0.44 (2.38) | 4.90 ± 1.06 (5.30) | 2.13 ± 0.67 (2.38) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.868 | 10.4 | 5.20 | 2.32 |
| p | normal | 0.884 | 12.5 | 4.32 | 1.78 |

## Notes

- p: score 0.876, 197/200 kicked, 0 fell; worst sector back (0.826).
