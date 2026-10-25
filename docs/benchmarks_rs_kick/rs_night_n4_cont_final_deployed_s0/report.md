# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n4_cont/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.10 ± 1.66 (1.79) |
| Direction error [°] | 18.26 ± 38.09 (4.80) |
| Avg ball speed [m/s] | 1.99 ± 0.65 (2.20) |
| Peak ball speed [m/s] | 4.39 ± 1.55 (4.77) |
| Distance [m] | 1.70 ± 0.80 (1.77) |
| Path length [m] | 1.70 ± 0.81 (1.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.890 | 50/50 | 0 | 42 | 1.78 ± 1.88 (1.39) | 8.18 ± 9.70 (5.00) | 1.95 ± 0.70 (2.07) | 4.28 ± 1.66 (4.23) | 1.65 ± 0.86 (1.66) |
| left | p | 0.875 | 49/50 | 0 | 42 | 1.91 ± 1.46 (1.86) | 17.64 ± 34.19 (4.91) | 2.05 ± 0.61 (2.24) | 4.55 ± 1.49 (5.10) | 1.76 ± 0.75 (1.85) |
| back | p | 0.798 | 48/50 | 0 | 41 | 2.83 ± 1.66 (2.67) | 26.95 ± 55.03 (4.53) | 2.05 ± 0.60 (2.26) | 4.50 ± 1.44 (5.15) | 1.75 ± 0.78 (1.84) |
| right | p | 0.860 | 49/50 | 0 | 40 | 1.92 ± 1.37 (1.78) | 20.67 ± 37.25 (4.55) | 1.93 ± 0.67 (2.08) | 4.22 ± 1.56 (4.52) | 1.62 ± 0.81 (1.68) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.873 | 98/100 | 0 | 84 | 1.82 ± 0.68 (1.78) | 17.41 ± 37.40 (4.45) | 2.05 ± 0.60 (2.20) | 4.50 ± 1.43 (4.93) | 1.75 ± 0.76 (1.81) |
| right | p | 0.838 | 98/100 | 0 | 81 | 2.39 ± 2.21 (1.82) | 19.11 ± 38.75 (5.03) | 1.94 ± 0.69 (2.17) | 4.27 ± 1.65 (4.64) | 1.64 ± 0.85 (1.71) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.923 | 25/25 | 0 | 22 | 1.33 ± 0.32 (1.34) | 7.55 ± 9.44 (4.66) | 2.07 ± 0.65 (2.10) | 4.56 ± 1.54 (4.26) | 1.80 ± 0.85 (1.69) |
| forward/right | p | 0.857 | 25/25 | 0 | 20 | 2.22 ± 2.56 (1.40) | 8.80 ± 9.91 (5.00) | 1.83 ± 0.72 (1.98) | 4.00 ± 1.73 (4.07) | 1.51 ± 0.85 (1.64) |
| left/left | p | 0.913 | 25/25 | 0 | 22 | 1.65 ± 0.44 (1.72) | 12.65 ± 22.13 (7.03) | 2.10 ± 0.48 (2.21) | 4.69 ± 1.18 (5.09) | 1.82 ± 0.59 (1.85) |
| left/right | p | 0.837 | 24/25 | 0 | 20 | 2.19 ± 2.00 (1.95) | 22.83 ± 42.70 (3.81) | 1.99 ± 0.72 (2.31) | 4.41 ± 1.75 (5.24) | 1.71 ± 0.89 (1.90) |
| back/left | p | 0.786 | 23/25 | 0 | 20 | 2.50 ± 0.76 (2.64) | 24.41 ± 52.89 (4.21) | 2.12 ± 0.47 (2.26) | 4.64 ± 1.13 (5.13) | 1.79 ± 0.66 (1.81) |
| back/right | p | 0.809 | 25/25 | 0 | 21 | 3.14 ± 2.14 (2.68) | 29.29 ± 56.84 (5.85) | 1.99 ± 0.69 (2.26) | 4.37 ± 1.66 (5.27) | 1.71 ± 0.88 (1.88) |
| right/left | p | 0.872 | 25/25 | 0 | 20 | 1.84 ± 0.52 (1.88) | 25.59 ± 45.81 (4.12) | 1.90 ± 0.73 (2.14) | 4.12 ± 1.70 (4.51) | 1.60 ± 0.86 (1.76) |
| right/right | p | 0.848 | 24/25 | 0 | 20 | 2.00 ± 1.88 (1.74) | 15.54 ± 24.38 (5.58) | 1.96 ± 0.59 (2.06) | 4.32 ± 1.39 (4.59) | 1.65 ± 0.74 (1.61) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.844 | 17.0 | 5.02 | 2.01 |
| p | normal | 0.867 | 19.5 | 3.79 | 1.39 |

## Notes

- p: score 0.856, 196/200 kicked, 0 fell; worst sector back (0.798).
