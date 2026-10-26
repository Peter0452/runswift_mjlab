# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_11-17-40_ovp_o3/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.923** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.61 ± 0.56 (1.52) |
| Direction error [°] | 7.66 ± 16.54 (5.52) |
| Avg ball speed [m/s] | 1.58 ± 0.32 (1.61) |
| Peak ball speed [m/s] | 3.38 ± 0.71 (3.39) |
| Distance [m] | 1.10 ± 0.38 (1.08) |
| Path length [m] | 1.11 ± 0.38 (1.09) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.934 | 50/50 | 0 | 50 | 1.08 ± 0.29 (1.14) | 5.22 ± 3.68 (4.70) | 1.43 ± 0.34 (1.41) | 3.08 ± 0.73 (3.00) | 0.93 ± 0.39 (0.90) |
| left | p | 0.926 | 50/50 | 0 | 48 | 1.53 ± 0.37 (1.44) | 6.92 ± 4.70 (6.32) | 1.65 ± 0.25 (1.64) | 3.48 ± 0.54 (3.46) | 1.16 ± 0.31 (1.11) |
| back | p | 0.896 | 50/50 | 0 | 48 | 2.31 ± 0.32 (2.27) | 12.60 ± 31.76 (5.89) | 1.66 ± 0.37 (1.72) | 3.56 ± 0.83 (3.59) | 1.22 ± 0.38 (1.23) |
| right | p | 0.937 | 50/50 | 0 | 49 | 1.53 ± 0.36 (1.53) | 5.89 ± 4.00 (5.56) | 1.59 ± 0.27 (1.62) | 3.41 ± 0.63 (3.37) | 1.10 ± 0.35 (1.03) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.927 | 100/100 | 0 | 98 | 1.62 ± 0.57 (1.46) | 6.06 ± 4.20 (5.52) | 1.60 ± 0.30 (1.62) | 3.43 ± 0.68 (3.44) | 1.12 ± 0.37 (1.10) |
| right | p | 0.919 | 100/100 | 0 | 97 | 1.60 ± 0.55 (1.55) | 9.25 ± 22.90 (5.56) | 1.57 ± 0.34 (1.60) | 3.34 ± 0.74 (3.34) | 1.09 ± 0.38 (1.07) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.930 | 25/25 | 0 | 25 | 1.09 ± 0.30 (1.10) | 5.74 ± 3.84 (5.15) | 1.43 ± 0.37 (1.44) | 3.09 ± 0.81 (3.08) | 0.94 ± 0.42 (0.94) |
| forward/right | p | 0.937 | 25/25 | 0 | 25 | 1.08 ± 0.29 (1.16) | 4.69 ± 3.44 (3.41) | 1.44 ± 0.31 (1.38) | 3.07 ± 0.64 (2.94) | 0.92 ± 0.35 (0.84) |
| left/left | p | 0.917 | 25/25 | 0 | 23 | 1.45 ± 0.35 (1.34) | 7.61 ± 5.37 (6.18) | 1.60 ± 0.26 (1.63) | 3.39 ± 0.59 (3.53) | 1.11 ± 0.31 (1.14) |
| left/right | p | 0.936 | 25/25 | 0 | 25 | 1.60 ± 0.36 (1.58) | 6.23 ± 3.79 (6.46) | 1.69 ± 0.22 (1.65) | 3.56 ± 0.48 (3.40) | 1.20 ± 0.31 (1.09) |
| back/left | p | 0.917 | 25/25 | 0 | 25 | 2.36 ± 0.28 (2.32) | 5.53 ± 3.30 (5.53) | 1.75 ± 0.23 (1.73) | 3.78 ± 0.56 (3.69) | 1.31 ± 0.32 (1.22) |
| back/right | p | 0.876 | 25/25 | 0 | 23 | 2.27 ± 0.34 (2.22) | 19.67 ± 43.67 (7.25) | 1.56 ± 0.44 (1.69) | 3.35 ± 0.99 (3.49) | 1.14 ± 0.42 (1.25) |
| right/left | p | 0.946 | 25/25 | 0 | 25 | 1.60 ± 0.36 (1.58) | 5.37 ± 3.56 (5.48) | 1.61 ± 0.24 (1.62) | 3.46 ± 0.56 (3.42) | 1.12 ± 0.31 (1.09) |
| right/right | p | 0.929 | 25/25 | 0 | 24 | 1.46 ± 0.34 (1.46) | 6.42 ± 4.34 (5.64) | 1.58 ± 0.30 (1.54) | 3.36 ± 0.68 (3.25) | 1.09 ± 0.39 (1.00) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.924 | 7.0 | 3.59 | 1.21 |
| p | normal | 0.923 | 8.3 | 3.17 | 1.00 |

## Notes

- p: score 0.923, 200/200 kicked, 0 fell; worst sector back (0.896).
