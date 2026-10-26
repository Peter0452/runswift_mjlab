# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.939** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.56 (1.51) |
| Direction error [°] | 5.46 ± 3.20 (5.17) |
| Avg ball speed [m/s] | 1.98 ± 0.31 (2.06) |
| Peak ball speed [m/s] | 4.30 ± 0.76 (4.39) |
| Distance [m] | 1.63 ± 0.47 (1.66) |
| Path length [m] | 1.64 ± 0.47 (1.67) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.950 | 50/50 | 0 | 50 | 1.04 ± 0.26 (1.07) | 4.91 ± 3.11 (4.20) | 1.82 ± 0.30 (1.83) | 3.96 ± 0.70 (3.85) | 1.39 ± 0.42 (1.33) |
| left | p | 0.937 | 50/50 | 0 | 50 | 1.53 ± 0.36 (1.46) | 6.17 ± 3.62 (6.00) | 1.96 ± 0.31 (2.08) | 4.27 ± 0.78 (4.62) | 1.62 ± 0.45 (1.72) |
| back | p | 0.920 | 50/50 | 0 | 50 | 2.33 ± 0.28 (2.30) | 5.55 ± 2.58 (5.24) | 2.16 ± 0.24 (2.22) | 4.70 ± 0.64 (4.94) | 1.90 ± 0.40 (1.94) |
| right | p | 0.948 | 50/50 | 0 | 50 | 1.53 ± 0.35 (1.52) | 5.21 ± 3.26 (4.92) | 1.97 ± 0.29 (1.92) | 4.27 ± 0.71 (4.15) | 1.62 ± 0.45 (1.62) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.940 | 100/100 | 0 | 100 | 1.61 ± 0.55 (1.48) | 5.43 ± 3.22 (5.17) | 1.98 ± 0.34 (2.07) | 4.31 ± 0.80 (4.63) | 1.64 ± 0.50 (1.67) |
| right | p | 0.938 | 100/100 | 0 | 100 | 1.61 ± 0.57 (1.54) | 5.49 ± 3.18 (5.07) | 1.97 ± 0.29 (2.02) | 4.28 ± 0.71 (4.29) | 1.62 ± 0.43 (1.63) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.952 | 25/25 | 0 | 25 | 1.04 ± 0.26 (1.00) | 4.72 ± 3.01 (4.38) | 1.79 ± 0.30 (1.77) | 3.90 ± 0.69 (3.76) | 1.36 ± 0.41 (1.22) |
| forward/right | p | 0.949 | 25/25 | 0 | 25 | 1.04 ± 0.25 (1.12) | 5.10 ± 3.20 (4.08) | 1.85 ± 0.31 (1.84) | 4.02 ± 0.71 (4.03) | 1.43 ± 0.43 (1.37) |
| left/left | p | 0.934 | 25/25 | 0 | 25 | 1.44 ± 0.34 (1.38) | 6.51 ± 3.84 (5.81) | 1.96 ± 0.38 (2.11) | 4.27 ± 0.89 (4.74) | 1.63 ± 0.54 (1.76) |
| left/right | p | 0.941 | 25/25 | 0 | 25 | 1.61 ± 0.36 (1.56) | 5.83 ± 3.36 (6.07) | 1.96 ± 0.23 (2.02) | 4.27 ± 0.64 (4.31) | 1.61 ± 0.35 (1.68) |
| back/left | p | 0.924 | 25/25 | 0 | 25 | 2.31 ± 0.24 (2.30) | 5.53 ± 2.58 (5.21) | 2.16 ± 0.27 (2.21) | 4.69 ± 0.68 (4.94) | 1.91 ± 0.44 (1.92) |
| back/right | p | 0.917 | 25/25 | 0 | 25 | 2.34 ± 0.31 (2.34) | 5.57 ± 2.57 (5.27) | 2.16 ± 0.21 (2.22) | 4.70 ± 0.60 (4.95) | 1.89 ± 0.37 (1.94) |
| right/left | p | 0.950 | 25/25 | 0 | 25 | 1.63 ± 0.35 (1.52) | 4.96 ± 3.03 (4.31) | 2.01 ± 0.29 (1.93) | 4.39 ± 0.70 (4.30) | 1.68 ± 0.45 (1.65) |
| right/right | p | 0.945 | 25/25 | 0 | 25 | 1.43 ± 0.32 (1.52) | 5.47 ± 3.45 (5.29) | 1.93 ± 0.29 (1.89) | 4.15 ± 0.70 (3.93) | 1.55 ± 0.43 (1.49) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.939 | 5.3 | 4.73 | 1.87 |
| p | normal | 0.939 | 5.7 | 3.87 | 1.39 |

## Notes

- p: score 0.939, 200/200 kicked, 0 fell; worst sector back (0.920).
