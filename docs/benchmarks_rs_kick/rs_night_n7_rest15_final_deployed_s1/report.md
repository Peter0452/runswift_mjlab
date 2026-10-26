# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.879** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 20 |
| Time to kick [s] | 1.89 ± 1.12 (1.67) |
| Direction error [°] | 15.36 ± 33.30 (4.58) |
| Avg ball speed [m/s] | 2.14 ± 0.72 (2.28) |
| Peak ball speed [m/s] | 4.64 ± 1.66 (5.19) |
| Distance [m] | 2.03 ± 0.92 (2.08) |
| Path length [m] | 2.03 ± 0.93 (2.09) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.881 | 49/50 | 0 | 42 | 1.42 ± 1.22 (1.30) | 9.93 ± 16.78 (4.65) | 2.10 ± 0.77 (2.17) | 4.56 ± 1.79 (5.00) | 1.98 ± 0.96 (2.09) |
| left | p | 0.899 | 50/50 | 0 | 43 | 1.91 ± 1.44 (1.74) | 12.40 ± 24.58 (3.85) | 2.16 ± 0.68 (2.28) | 4.68 ± 1.61 (5.23) | 2.07 ± 0.92 (2.14) |
| back | p | 0.824 | 49/50 | 0 | 41 | 2.41 ± 0.70 (2.56) | 27.54 ± 51.84 (6.09) | 2.17 ± 0.76 (2.37) | 4.71 ± 1.73 (5.49) | 2.08 ± 0.98 (2.35) |
| right | p | 0.914 | 50/50 | 0 | 45 | 1.82 ± 0.70 (1.79) | 11.72 ± 26.09 (3.48) | 2.16 ± 0.64 (2.25) | 4.62 ± 1.48 (4.77) | 1.98 ± 0.83 (1.95) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.883 | 100/100 | 0 | 84 | 1.88 ± 1.21 (1.66) | 18.13 ± 36.64 (4.19) | 2.09 ± 0.75 (2.28) | 4.57 ± 1.75 (5.20) | 1.98 ± 0.96 (2.08) |
| right | p | 0.876 | 98/100 | 0 | 87 | 1.91 ± 1.02 (1.79) | 12.54 ± 29.23 (4.70) | 2.20 ± 0.67 (2.28) | 4.72 ± 1.56 (5.19) | 2.07 ± 0.88 (2.08) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.915 | 25/25 | 0 | 22 | 1.23 ± 0.28 (1.26) | 11.14 ± 21.20 (3.43) | 2.11 ± 0.75 (2.47) | 4.66 ± 1.77 (5.64) | 2.04 ± 1.01 (2.46) |
| forward/right | p | 0.846 | 24/25 | 0 | 20 | 1.63 ± 1.70 (1.37) | 8.67 ± 10.17 (4.93) | 2.08 ± 0.79 (2.16) | 4.46 ± 1.81 (4.67) | 1.92 ± 0.92 (1.98) |
| left/left | p | 0.903 | 25/25 | 0 | 22 | 2.06 ± 1.96 (1.66) | 7.52 ± 8.19 (5.71) | 2.24 ± 0.62 (2.33) | 4.89 ± 1.51 (5.49) | 2.18 ± 0.83 (2.39) |
| left/right | p | 0.895 | 25/25 | 0 | 21 | 1.77 ± 0.52 (1.90) | 17.27 ± 33.07 (2.66) | 2.09 ± 0.72 (2.12) | 4.47 ± 1.69 (4.27) | 1.95 ± 0.98 (1.75) |
| back/left | p | 0.825 | 25/25 | 0 | 19 | 2.22 ± 0.77 (2.54) | 36.17 ± 55.80 (6.44) | 2.00 ± 0.85 (2.24) | 4.37 ± 1.90 (4.91) | 1.88 ± 1.06 (1.91) |
| back/right | p | 0.824 | 24/25 | 0 | 22 | 2.60 ± 0.56 (2.59) | 18.56 ± 45.68 (5.09) | 2.33 ± 0.61 (2.43) | 5.07 ± 1.43 (5.65) | 2.28 ± 0.82 (2.44) |
| right/left | p | 0.889 | 25/25 | 0 | 21 | 1.99 ± 0.90 (2.02) | 17.68 ± 35.41 (2.70) | 2.01 ± 0.75 (2.17) | 4.35 ± 1.73 (4.49) | 1.82 ± 0.88 (1.93) |
| right/right | p | 0.938 | 25/25 | 0 | 24 | 1.66 ± 0.33 (1.64) | 5.76 ± 6.04 (4.79) | 2.30 ± 0.46 (2.27) | 4.89 ± 1.12 (5.22) | 2.14 ± 0.74 (1.96) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.869 | 15.2 | 5.18 | 2.36 |
| p | normal | 0.890 | 15.5 | 4.11 | 1.70 |

## Notes

- p: score 0.879, 198/200 kicked, 0 fell; worst sector back (0.824).
