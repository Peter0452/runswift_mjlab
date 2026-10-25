# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n3_aim025/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.939** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.55 ± 0.51 (1.48) |
| Direction error [°] | 6.04 ± 10.13 (5.08) |
| Avg ball speed [m/s] | 1.83 ± 0.31 (1.93) |
| Peak ball speed [m/s] | 3.92 ± 0.71 (4.06) |
| Distance [m] | 1.38 ± 0.40 (1.39) |
| Path length [m] | 1.38 ± 0.40 (1.39) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.951 | 50/50 | 0 | 50 | 1.05 ± 0.25 (1.07) | 4.37 ± 3.34 (3.26) | 1.61 ± 0.30 (1.59) | 3.43 ± 0.65 (3.26) | 1.07 ± 0.38 (1.07) |
| left | p | 0.945 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.52) | 5.47 ± 3.14 (5.21) | 1.91 ± 0.25 (1.95) | 4.12 ± 0.60 (4.31) | 1.48 ± 0.34 (1.46) |
| back | p | 0.919 | 50/50 | 0 | 49 | 2.19 ± 0.26 (2.15) | 8.63 ± 19.19 (6.00) | 1.94 ± 0.33 (2.01) | 4.15 ± 0.77 (4.37) | 1.54 ± 0.38 (1.57) |
| right | p | 0.942 | 50/50 | 0 | 50 | 1.46 ± 0.32 (1.45) | 5.69 ± 3.42 (5.90) | 1.88 ± 0.22 (1.95) | 3.99 ± 0.57 (4.18) | 1.41 ± 0.31 (1.39) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.934 | 100/100 | 0 | 99 | 1.54 ± 0.50 (1.48) | 7.03 ± 13.94 (5.46) | 1.84 ± 0.33 (1.93) | 3.93 ± 0.75 (4.11) | 1.39 ± 0.41 (1.40) |
| right | p | 0.944 | 100/100 | 0 | 100 | 1.55 ± 0.51 (1.48) | 5.05 ± 3.02 (4.57) | 1.83 ± 0.29 (1.91) | 3.91 ± 0.67 (3.98) | 1.36 ± 0.39 (1.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.947 | 25/25 | 0 | 25 | 1.04 ± 0.24 (1.08) | 4.82 ± 4.05 (2.78) | 1.65 ± 0.27 (1.57) | 3.47 ± 0.58 (3.27) | 1.11 ± 0.36 (1.06) |
| forward/right | p | 0.955 | 25/25 | 0 | 25 | 1.06 ± 0.26 (1.06) | 3.92 ± 2.34 (3.80) | 1.57 ± 0.33 (1.60) | 3.38 ± 0.72 (3.23) | 1.03 ± 0.39 (1.08) |
| left/left | p | 0.940 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.46) | 5.98 ± 3.31 (5.75) | 1.87 ± 0.28 (1.93) | 4.01 ± 0.65 (4.13) | 1.43 ± 0.38 (1.45) |
| left/right | p | 0.950 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.62) | 4.96 ± 2.87 (4.94) | 1.95 ± 0.20 (1.96) | 4.22 ± 0.51 (4.33) | 1.52 ± 0.30 (1.47) |
| back/left | p | 0.909 | 25/25 | 0 | 24 | 2.19 ± 0.26 (2.16) | 11.63 ± 26.67 (6.54) | 1.94 ± 0.42 (2.03) | 4.16 ± 0.95 (4.48) | 1.57 ± 0.45 (1.62) |
| back/right | p | 0.929 | 25/25 | 0 | 25 | 2.20 ± 0.27 (2.14) | 5.64 ± 2.63 (5.82) | 1.95 ± 0.19 (1.94) | 4.13 ± 0.52 (4.24) | 1.51 ± 0.30 (1.50) |
| right/left | p | 0.942 | 25/25 | 0 | 25 | 1.55 ± 0.30 (1.54) | 5.69 ± 3.08 (6.00) | 1.91 ± 0.21 (1.98) | 4.07 ± 0.56 (4.40) | 1.45 ± 0.29 (1.49) |
| right/right | p | 0.942 | 25/25 | 0 | 25 | 1.36 ± 0.32 (1.40) | 5.69 ± 3.73 (5.88) | 1.85 ± 0.22 (1.94) | 3.90 ± 0.57 (3.83) | 1.37 ± 0.32 (1.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.941 | 5.2 | 4.24 | 1.53 |
| p | normal | 0.937 | 6.9 | 3.60 | 1.22 |

## Notes

- p: score 0.939, 200/200 kicked, 0 fell; worst sector back (0.919).
