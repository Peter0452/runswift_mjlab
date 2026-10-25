# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.866** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.00 ± 1.47 (1.64) |
| Direction error [°] | 16.24 ± 32.89 (5.91) |
| Avg ball speed [m/s] | 2.06 ± 0.59 (2.20) |
| Peak ball speed [m/s] | 4.51 ± 1.41 (5.15) |
| Distance [m] | 1.82 ± 0.76 (1.91) |
| Path length [m] | 1.83 ± 0.76 (1.93) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.883 | 49/50 | 0 | 43 | 1.66 ± 1.96 (1.32) | 9.66 ± 16.65 (4.87) | 2.09 ± 0.57 (2.24) | 4.57 ± 1.36 (5.20) | 1.84 ± 0.72 (1.94) |
| left | p | 0.896 | 50/50 | 0 | 44 | 1.90 ± 1.34 (1.67) | 12.68 ± 22.09 (5.62) | 2.07 ± 0.57 (2.18) | 4.54 ± 1.33 (5.17) | 1.83 ± 0.76 (1.91) |
| back | p | 0.786 | 49/50 | 0 | 38 | 2.69 ± 1.50 (2.50) | 32.75 ± 53.82 (9.12) | 2.01 ± 0.71 (2.23) | 4.40 ± 1.63 (5.26) | 1.79 ± 0.83 (2.02) |
| right | p | 0.898 | 49/50 | 0 | 45 | 1.73 ± 0.40 (1.74) | 9.95 ± 17.59 (4.99) | 2.08 ± 0.51 (2.16) | 4.52 ± 1.28 (4.86) | 1.82 ± 0.71 (1.75) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.868 | 98/100 | 0 | 85 | 1.92 ± 1.21 (1.59) | 15.84 ± 31.53 (5.68) | 2.06 ± 0.59 (2.23) | 4.53 ± 1.42 (5.20) | 1.83 ± 0.77 (1.94) |
| right | p | 0.864 | 99/100 | 0 | 85 | 2.07 ± 1.69 (1.68) | 16.64 ± 34.19 (6.58) | 2.06 ± 0.59 (2.19) | 4.48 ± 1.40 (5.08) | 1.81 ± 0.74 (1.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.883 | 24/25 | 0 | 21 | 1.26 ± 0.26 (1.30) | 10.77 ± 20.60 (5.22) | 2.05 ± 0.57 (2.23) | 4.51 ± 1.40 (5.19) | 1.81 ± 0.75 (2.04) |
| forward/right | p | 0.884 | 25/25 | 0 | 22 | 2.05 ± 2.67 (1.38) | 8.59 ± 11.56 (4.87) | 2.14 ± 0.55 (2.30) | 4.63 ± 1.33 (5.21) | 1.86 ± 0.68 (1.90) |
| left/left | p | 0.915 | 25/25 | 0 | 23 | 2.03 ± 1.81 (1.60) | 6.97 ± 5.70 (4.80) | 2.16 ± 0.42 (2.22) | 4.82 ± 1.01 (5.25) | 1.93 ± 0.64 (2.01) |
| left/right | p | 0.878 | 25/25 | 0 | 21 | 1.78 ± 0.55 (1.90) | 18.39 ± 29.64 (6.58) | 1.98 ± 0.68 (2.12) | 4.26 ± 1.54 (4.04) | 1.72 ± 0.85 (1.49) |
| back/left | p | 0.810 | 25/25 | 0 | 20 | 2.51 ± 1.21 (2.54) | 31.66 ± 50.48 (7.84) | 1.99 ± 0.71 (2.34) | 4.37 ± 1.65 (5.27) | 1.77 ± 0.87 (2.00) |
| back/right | p | 0.762 | 24/25 | 0 | 18 | 2.87 ± 1.72 (2.42) | 33.88 ± 57.07 (9.61) | 2.03 ± 0.70 (2.23) | 4.43 ± 1.60 (5.19) | 1.81 ± 0.79 (2.08) |
| right/left | p | 0.865 | 24/25 | 0 | 21 | 1.84 ± 0.42 (2.01) | 13.66 ± 23.93 (4.60) | 2.04 ± 0.61 (2.18) | 4.44 ± 1.49 (4.62) | 1.80 ± 0.81 (1.76) |
| right/right | p | 0.931 | 25/25 | 0 | 24 | 1.63 ± 0.34 (1.62) | 6.40 ± 5.53 (5.13) | 2.11 ± 0.39 (2.16) | 4.60 ± 1.02 (4.86) | 1.84 ± 0.60 (1.75) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.864 | 14.7 | 4.97 | 2.07 |
| p | normal | 0.868 | 17.8 | 4.04 | 1.56 |

## Notes

- p: score 0.866, 197/200 kicked, 0 fell; worst sector back (0.786).
