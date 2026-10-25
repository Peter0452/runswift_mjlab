# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n4_cont/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.954** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.62 ± 0.53 (1.54) |
| Direction error [°] | 4.68 ± 11.29 (3.15) |
| Avg ball speed [m/s] | 1.64 ± 0.28 (1.63) |
| Peak ball speed [m/s] | 4.39 ± 0.72 (4.42) |
| Distance [m] | 1.69 ± 0.42 (1.69) |
| Path length [m] | 1.70 ± 0.42 (1.69) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.956 | 50/50 | 0 | 49 | 1.06 ± 0.23 (1.10) | 4.35 ± 3.37 (3.25) | 1.48 ± 0.29 (1.52) | 3.98 ± 0.75 (3.93) | 1.42 ± 0.42 (1.39) |
| left | p | 0.959 | 50/50 | 0 | 50 | 1.57 ± 0.35 (1.55) | 4.11 ± 2.35 (4.26) | 1.73 ± 0.22 (1.76) | 4.60 ± 0.59 (4.87) | 1.84 ± 0.36 (1.88) |
| back | p | 0.942 | 50/50 | 0 | 49 | 2.30 ± 0.28 (2.29) | 6.18 ± 21.98 (2.20) | 1.72 ± 0.30 (1.78) | 4.59 ± 0.80 (4.86) | 1.80 ± 0.45 (1.87) |
| right | p | 0.959 | 50/50 | 0 | 50 | 1.55 ± 0.35 (1.52) | 4.06 ± 2.58 (3.58) | 1.63 ± 0.19 (1.61) | 4.38 ± 0.54 (4.42) | 1.70 ± 0.32 (1.60) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.956 | 100/100 | 0 | 99 | 1.62 ± 0.53 (1.54) | 5.13 ± 15.71 (2.48) | 1.64 ± 0.27 (1.63) | 4.37 ± 0.72 (4.31) | 1.69 ± 0.41 (1.70) |
| right | p | 0.952 | 100/100 | 0 | 99 | 1.62 ± 0.54 (1.52) | 4.22 ± 2.76 (3.57) | 1.64 ± 0.28 (1.63) | 4.41 ± 0.72 (4.53) | 1.70 ± 0.43 (1.68) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.958 | 25/25 | 0 | 25 | 1.06 ± 0.22 (1.10) | 4.13 ± 2.83 (2.85) | 1.49 ± 0.22 (1.49) | 3.96 ± 0.52 (3.89) | 1.41 ± 0.32 (1.35) |
| forward/right | p | 0.954 | 25/25 | 0 | 24 | 1.07 ± 0.23 (1.10) | 4.56 ± 3.82 (3.27) | 1.47 ± 0.35 (1.52) | 4.00 ± 0.92 (3.94) | 1.43 ± 0.50 (1.47) |
| left/left | p | 0.964 | 25/25 | 0 | 25 | 1.47 ± 0.35 (1.54) | 3.58 ± 2.44 (2.55) | 1.71 ± 0.22 (1.71) | 4.49 ± 0.62 (4.40) | 1.78 ± 0.37 (1.84) |
| left/right | p | 0.953 | 25/25 | 0 | 25 | 1.67 ± 0.31 (1.72) | 4.65 ± 2.12 (4.86) | 1.75 ± 0.22 (1.77) | 4.71 ± 0.52 (4.93) | 1.90 ± 0.34 (1.92) |
| back/left | p | 0.947 | 25/25 | 0 | 24 | 2.28 ± 0.27 (2.30) | 8.36 ± 30.84 (1.91) | 1.72 ± 0.35 (1.78) | 4.54 ± 0.92 (4.63) | 1.80 ± 0.48 (1.76) |
| back/right | p | 0.937 | 25/25 | 0 | 25 | 2.31 ± 0.28 (2.28) | 4.01 ± 2.39 (2.97) | 1.73 ± 0.25 (1.67) | 4.63 ± 0.65 (4.89) | 1.80 ± 0.41 (1.87) |
| right/left | p | 0.954 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.60) | 4.46 ± 2.84 (3.99) | 1.65 ± 0.20 (1.64) | 4.49 ± 0.58 (4.70) | 1.75 ± 0.33 (1.80) |
| right/right | p | 0.963 | 25/25 | 0 | 25 | 1.45 ± 0.35 (1.48) | 3.66 ± 2.22 (3.38) | 1.62 ± 0.18 (1.58) | 4.28 ± 0.47 (4.18) | 1.65 ± 0.31 (1.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.952 | 4.1 | 4.76 | 1.88 |
| p | normal | 0.956 | 5.2 | 4.02 | 1.50 |

## Notes

- p: score 0.954, 200/200 kicked, 0 fell; worst sector back (0.942).
