# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-45_night_n1_near025/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.11 ± 1.86 (1.72) |
| Direction error [°] | 18.32 ± 37.25 (6.42) |
| Avg ball speed [m/s] | 2.02 ± 0.62 (2.18) |
| Peak ball speed [m/s] | 4.48 ± 1.51 (5.02) |
| Distance [m] | 1.75 ± 0.79 (1.83) |
| Path length [m] | 1.76 ± 0.80 (1.84) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.886 | 50/50 | 0 | 44 | 2.02 ± 2.60 (1.34) | 8.14 ± 10.69 (4.44) | 2.03 ± 0.62 (2.13) | 4.43 ± 1.50 (4.29) | 1.72 ± 0.83 (1.68) |
| left | p | 0.867 | 48/50 | 0 | 42 | 1.69 ± 0.46 (1.73) | 15.82 ± 29.91 (6.43) | 2.09 ± 0.57 (2.29) | 4.68 ± 1.41 (5.27) | 1.85 ± 0.74 (2.12) |
| back | p | 0.773 | 48/50 | 0 | 40 | 3.06 ± 2.30 (2.52) | 31.68 ± 56.77 (7.82) | 1.97 ± 0.67 (2.19) | 4.36 ± 1.57 (5.02) | 1.72 ± 0.77 (1.86) |
| right | p | 0.881 | 49/50 | 0 | 40 | 1.67 ± 0.48 (1.70) | 18.07 ± 32.92 (5.60) | 2.00 ± 0.63 (2.17) | 4.45 ± 1.52 (4.88) | 1.73 ± 0.82 (1.79) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.875 | 99/100 | 0 | 83 | 1.93 ± 1.46 (1.70) | 17.84 ± 37.03 (5.82) | 2.06 ± 0.62 (2.23) | 4.55 ± 1.48 (5.08) | 1.80 ± 0.80 (1.83) |
| right | p | 0.828 | 96/100 | 0 | 83 | 2.29 ± 2.18 (1.77) | 18.81 ± 37.46 (6.60) | 1.99 ± 0.63 (2.17) | 4.41 ± 1.53 (4.96) | 1.71 ± 0.78 (1.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.906 | 25/25 | 0 | 21 | 1.63 ± 1.90 (1.34) | 7.70 ± 10.30 (4.62) | 2.12 ± 0.68 (2.17) | 4.60 ± 1.61 (4.35) | 1.85 ± 0.89 (1.74) |
| forward/right | p | 0.866 | 25/25 | 0 | 23 | 2.41 ± 3.10 (1.34) | 8.59 ± 11.06 (3.91) | 1.95 ± 0.53 (2.00) | 4.27 ± 1.37 (4.11) | 1.60 ± 0.74 (1.57) |
| left/left | p | 0.929 | 25/25 | 0 | 23 | 1.59 ± 0.38 (1.66) | 9.08 ± 15.07 (5.65) | 2.19 ± 0.43 (2.35) | 4.88 ± 1.12 (5.26) | 1.95 ± 0.64 (2.06) |
| left/right | p | 0.805 | 23/25 | 0 | 19 | 1.81 ± 0.50 (1.96) | 23.14 ± 38.95 (6.70) | 1.98 ± 0.67 (2.24) | 4.47 ± 1.65 (5.28) | 1.73 ± 0.82 (2.13) |
| back/left | p | 0.782 | 24/25 | 0 | 20 | 2.77 ± 1.93 (2.55) | 31.96 ± 56.35 (8.42) | 2.06 ± 0.60 (2.26) | 4.52 ± 1.41 (4.89) | 1.81 ± 0.77 (1.90) |
| back/right | p | 0.763 | 24/25 | 0 | 20 | 3.34 ± 2.59 (2.52) | 31.40 ± 57.18 (7.07) | 1.88 ± 0.72 (2.17) | 4.20 ± 1.70 (5.02) | 1.62 ± 0.76 (1.84) |
| right/left | p | 0.883 | 25/25 | 0 | 19 | 1.76 ± 0.50 (1.74) | 23.20 ± 40.60 (4.29) | 1.87 ± 0.69 (2.13) | 4.19 ± 1.66 (4.39) | 1.57 ± 0.83 (1.74) |
| right/right | p | 0.878 | 24/25 | 0 | 21 | 1.57 ± 0.43 (1.55) | 12.73 ± 20.98 (6.60) | 2.14 ± 0.54 (2.19) | 4.72 ± 1.31 (4.89) | 1.90 ± 0.78 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.846 | 17.5 | 5.07 | 2.08 |
| p | normal | 0.857 | 19.2 | 3.89 | 1.42 |

## Notes

- p: score 0.852, 195/200 kicked, 0 fell; worst sector back (0.773).
