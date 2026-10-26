# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_10-42-42_ovp_o2/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.927** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.62 ± 0.55 (1.57) |
| Direction error [°] | 6.97 ± 12.74 (5.41) |
| Avg ball speed [m/s] | 1.71 ± 0.32 (1.71) |
| Peak ball speed [m/s] | 3.63 ± 0.73 (3.52) |
| Distance [m] | 1.26 ± 0.42 (1.20) |
| Path length [m] | 1.27 ± 0.42 (1.21) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.931 | 50/50 | 0 | 48 | 1.04 ± 0.24 (1.09) | 5.70 ± 4.41 (4.54) | 1.44 ± 0.29 (1.43) | 3.07 ± 0.63 (2.98) | 0.91 ± 0.32 (0.84) |
| left | p | 0.938 | 50/50 | 0 | 48 | 1.57 ± 0.37 (1.60) | 5.93 ± 4.72 (4.59) | 1.82 ± 0.26 (1.81) | 3.86 ± 0.63 (3.86) | 1.40 ± 0.39 (1.33) |
| back | p | 0.897 | 50/50 | 0 | 49 | 2.32 ± 0.29 (2.24) | 10.49 ± 23.97 (7.73) | 1.85 ± 0.35 (1.82) | 3.92 ± 0.78 (3.92) | 1.47 ± 0.42 (1.40) |
| right | p | 0.940 | 50/50 | 0 | 49 | 1.57 ± 0.36 (1.55) | 5.78 ± 3.99 (4.72) | 1.74 ± 0.22 (1.70) | 3.67 ± 0.53 (3.50) | 1.27 ± 0.29 (1.21) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.924 | 100/100 | 0 | 96 | 1.62 ± 0.56 (1.60) | 7.87 ± 17.46 (5.42) | 1.71 ± 0.34 (1.73) | 3.63 ± 0.75 (3.53) | 1.27 ± 0.43 (1.20) |
| right | p | 0.930 | 100/100 | 0 | 98 | 1.62 ± 0.55 (1.55) | 6.07 ± 4.24 (5.38) | 1.71 ± 0.31 (1.70) | 3.63 ± 0.71 (3.50) | 1.26 ± 0.41 (1.21) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.935 | 25/25 | 0 | 24 | 1.03 ± 0.24 (1.10) | 5.13 ± 3.64 (4.16) | 1.44 ± 0.24 (1.38) | 3.09 ± 0.54 (2.96) | 0.91 ± 0.31 (0.83) |
| forward/right | p | 0.927 | 25/25 | 0 | 24 | 1.04 ± 0.24 (1.08) | 6.26 ± 5.00 (4.89) | 1.44 ± 0.33 (1.46) | 3.05 ± 0.71 (3.00) | 0.91 ± 0.34 (0.88) |
| left/left | p | 0.925 | 25/25 | 0 | 23 | 1.47 ± 0.36 (1.54) | 7.30 ± 5.57 (6.01) | 1.75 ± 0.22 (1.74) | 3.67 ± 0.52 (3.59) | 1.30 ± 0.33 (1.21) |
| left/right | p | 0.952 | 25/25 | 0 | 25 | 1.67 ± 0.34 (1.64) | 4.55 ± 3.13 (2.80) | 1.90 ± 0.27 (1.95) | 4.05 ± 0.68 (4.25) | 1.50 ± 0.42 (1.61) |
| back/left | p | 0.890 | 25/25 | 0 | 24 | 2.32 ± 0.30 (2.22) | 13.74 ± 33.42 (7.79) | 1.86 ± 0.44 (1.92) | 3.94 ± 0.95 (4.17) | 1.50 ± 0.49 (1.63) |
| back/right | p | 0.905 | 25/25 | 0 | 25 | 2.31 ± 0.28 (2.24) | 7.23 ± 3.37 (7.67) | 1.84 ± 0.22 (1.75) | 3.89 ± 0.55 (3.84) | 1.43 ± 0.34 (1.34) |
| right/left | p | 0.945 | 25/25 | 0 | 25 | 1.67 ± 0.33 (1.62) | 5.32 ± 3.10 (4.68) | 1.80 ± 0.24 (1.75) | 3.82 ± 0.60 (3.63) | 1.35 ± 0.34 (1.34) |
| right/right | p | 0.935 | 25/25 | 0 | 24 | 1.47 ± 0.35 (1.52) | 6.24 ± 4.67 (4.77) | 1.68 ± 0.19 (1.66) | 3.51 ± 0.41 (3.48) | 1.19 ± 0.21 (1.17) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.922 | 6.3 | 3.89 | 1.39 |
| p | normal | 0.931 | 7.6 | 3.37 | 1.14 |

## Notes

- p: score 0.927, 200/200 kicked, 0 fell; worst sector back (0.897).
