# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n4_cont/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.950** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.63 ± 0.56 (1.55) |
| Direction error [°] | 4.97 ± 12.10 (3.18) |
| Avg ball speed [m/s] | 1.74 ± 0.30 (1.75) |
| Peak ball speed [m/s] | 4.42 ± 0.76 (4.42) |
| Distance [m] | 1.73 ± 0.47 (1.69) |
| Path length [m] | 1.74 ± 0.47 (1.69) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.948 | 50/50 | 0 | 49 | 1.11 ± 0.41 (1.15) | 4.89 ± 3.79 (3.12) | 1.57 ± 0.28 (1.59) | 4.05 ± 0.76 (4.00) | 1.48 ± 0.48 (1.45) |
| left | p | 0.959 | 50/50 | 0 | 50 | 1.55 ± 0.36 (1.50) | 4.14 ± 2.72 (4.04) | 1.78 ± 0.27 (1.76) | 4.48 ± 0.69 (4.60) | 1.79 ± 0.44 (1.80) |
| back | p | 0.934 | 50/50 | 0 | 49 | 2.32 ± 0.27 (2.34) | 6.64 ± 23.46 (2.53) | 1.85 ± 0.30 (1.88) | 4.69 ± 0.79 (4.88) | 1.90 ± 0.44 (1.90) |
| right | p | 0.958 | 50/50 | 0 | 50 | 1.54 ± 0.35 (1.56) | 4.21 ± 3.02 (3.16) | 1.76 ± 0.26 (1.74) | 4.46 ± 0.65 (4.39) | 1.75 ± 0.41 (1.67) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.949 | 100/100 | 0 | 99 | 1.65 ± 0.57 (1.53) | 4.29 ± 3.35 (3.22) | 1.74 ± 0.30 (1.79) | 4.44 ± 0.73 (4.50) | 1.74 ± 0.47 (1.72) |
| right | p | 0.950 | 100/100 | 0 | 99 | 1.62 ± 0.55 (1.58) | 5.64 ± 16.75 (2.89) | 1.74 ± 0.29 (1.73) | 4.40 ± 0.78 (4.35) | 1.72 ± 0.47 (1.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.943 | 25/25 | 0 | 24 | 1.16 ± 0.51 (1.12) | 4.98 ± 4.27 (3.38) | 1.54 ± 0.32 (1.50) | 3.99 ± 0.78 (3.94) | 1.45 ± 0.50 (1.37) |
| forward/right | p | 0.952 | 25/25 | 0 | 25 | 1.06 ± 0.26 (1.16) | 4.79 ± 3.25 (2.87) | 1.61 ± 0.24 (1.63) | 4.11 ± 0.73 (4.03) | 1.51 ± 0.46 (1.47) |
| left/left | p | 0.959 | 25/25 | 0 | 25 | 1.47 ± 0.35 (1.42) | 4.14 ± 2.84 (3.89) | 1.76 ± 0.28 (1.80) | 4.47 ± 0.70 (4.75) | 1.78 ± 0.44 (1.82) |
| left/right | p | 0.958 | 25/25 | 0 | 25 | 1.63 ± 0.34 (1.60) | 4.13 ± 2.59 (4.19) | 1.80 ± 0.26 (1.75) | 4.50 ± 0.67 (4.60) | 1.81 ± 0.45 (1.77) |
| back/left | p | 0.942 | 25/25 | 0 | 25 | 2.33 ± 0.27 (2.34) | 3.31 ± 2.51 (2.23) | 1.89 ± 0.23 (1.92) | 4.80 ± 0.57 (4.93) | 1.96 ± 0.37 (1.92) |
| back/right | p | 0.926 | 25/25 | 0 | 24 | 2.31 ± 0.28 (2.34) | 9.97 ± 32.75 (2.77) | 1.81 ± 0.35 (1.84) | 4.57 ± 0.95 (4.86) | 1.84 ± 0.50 (1.84) |
| right/left | p | 0.953 | 25/25 | 0 | 25 | 1.63 ± 0.35 (1.54) | 4.75 ± 3.28 (3.63) | 1.77 ± 0.26 (1.79) | 4.50 ± 0.62 (4.65) | 1.78 ± 0.41 (1.69) |
| right/right | p | 0.963 | 25/25 | 0 | 25 | 1.46 ± 0.32 (1.58) | 3.68 ± 2.64 (2.68) | 1.75 ± 0.26 (1.71) | 4.42 ± 0.67 (4.23) | 1.72 ± 0.41 (1.65) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.943 | 6.1 | 4.79 | 1.91 |
| p | normal | 0.956 | 3.9 | 4.06 | 1.55 |

## Notes

- p: score 0.950, 200/200 kicked, 0 fell; worst sector back (0.934).
