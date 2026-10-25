# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.841** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 159 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.94 ± 1.30 (1.72) |
| Direction error [°] | 19.84 ± 37.93 (5.87) |
| Avg ball speed [m/s] | 1.94 ± 0.60 (2.10) |
| Peak ball speed [m/s] | 4.38 ± 1.49 (4.77) |
| Distance [m] | 1.64 ± 0.75 (1.68) |
| Path length [m] | 1.65 ± 0.75 (1.68) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.881 | 50/50 | 0 | 41 | 1.80 ± 2.03 (1.34) | 12.40 ± 25.14 (5.85) | 1.89 ± 0.61 (2.02) | 4.22 ± 1.52 (4.04) | 1.54 ± 0.76 (1.45) |
| left | p | 0.858 | 48/50 | 0 | 40 | 1.67 ± 0.50 (1.72) | 20.04 ± 36.00 (5.48) | 2.02 ± 0.56 (2.18) | 4.56 ± 1.36 (5.17) | 1.74 ± 0.73 (1.86) |
| back | p | 0.781 | 47/50 | 0 | 39 | 2.58 ± 1.12 (2.50) | 27.69 ± 51.51 (7.09) | 2.00 ± 0.63 (2.18) | 4.53 ± 1.52 (5.18) | 1.76 ± 0.75 (1.98) |
| right | p | 0.846 | 48/50 | 0 | 39 | 1.74 ± 0.72 (1.72) | 19.71 ± 33.38 (5.09) | 1.87 ± 0.60 (1.96) | 4.24 ± 1.51 (4.25) | 1.54 ± 0.71 (1.57) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.881 | 99/100 | 0 | 85 | 1.84 ± 1.13 (1.70) | 18.27 ± 37.07 (5.87) | 2.00 ± 0.52 (2.13) | 4.51 ± 1.30 (4.90) | 1.69 ± 0.68 (1.84) |
| right | p | 0.801 | 94/100 | 0 | 74 | 2.05 ± 1.46 (1.73) | 21.49 ± 38.75 (5.97) | 1.89 ± 0.68 (2.04) | 4.25 ± 1.65 (4.40) | 1.59 ± 0.81 (1.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.922 | 25/25 | 0 | 23 | 1.67 ± 1.94 (1.30) | 6.96 ± 10.35 (3.31) | 2.08 ± 0.45 (2.10) | 4.66 ± 1.17 (4.90) | 1.74 ± 0.63 (1.67) |
| forward/right | p | 0.840 | 25/25 | 0 | 18 | 1.92 ± 2.10 (1.36) | 17.85 ± 33.14 (6.97) | 1.69 ± 0.68 (1.79) | 3.77 ± 1.68 (3.73) | 1.33 ± 0.82 (1.33) |
| left/left | p | 0.917 | 25/25 | 0 | 22 | 1.59 ± 0.42 (1.64) | 12.67 ± 22.64 (5.28) | 2.07 ± 0.42 (2.17) | 4.70 ± 1.07 (5.14) | 1.79 ± 0.59 (1.87) |
| left/right | p | 0.799 | 23/25 | 0 | 18 | 1.75 ± 0.56 (1.86) | 28.04 ± 45.00 (6.33) | 1.96 ± 0.67 (2.20) | 4.41 ± 1.60 (5.20) | 1.69 ± 0.86 (1.77) |
| back/left | p | 0.800 | 24/25 | 0 | 20 | 2.38 ± 0.68 (2.49) | 31.22 ± 54.93 (7.65) | 1.99 ± 0.53 (2.17) | 4.54 ± 1.32 (5.14) | 1.74 ± 0.70 (1.94) |
| back/right | p | 0.761 | 23/25 | 0 | 19 | 2.79 ± 1.42 (2.60) | 24.01 ± 47.39 (5.69) | 2.02 ± 0.71 (2.22) | 4.52 ± 1.71 (5.25) | 1.77 ± 0.80 (1.98) |
| right/left | p | 0.886 | 25/25 | 0 | 20 | 1.74 ± 0.50 (1.74) | 22.76 ± 39.81 (4.76) | 1.84 ± 0.61 (1.96) | 4.16 ± 1.52 (4.17) | 1.50 ± 0.75 (1.59) |
| right/right | p | 0.806 | 23/25 | 0 | 19 | 1.75 ± 0.89 (1.62) | 16.39 ± 24.13 (5.17) | 1.90 ± 0.59 (1.99) | 4.34 ± 1.48 (4.77) | 1.58 ± 0.67 (1.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.836 | 16.8 | 5.06 | 1.98 |
| p | normal | 0.847 | 22.8 | 3.73 | 1.31 |

## Notes

- p: score 0.841, 193/200 kicked, 0 fell; worst sector back (0.781).
