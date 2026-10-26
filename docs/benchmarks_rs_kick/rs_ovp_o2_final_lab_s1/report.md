# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_10-42-42_ovp_o2/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.927** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.62 ± 0.58 (1.55) |
| Direction error [°] | 6.37 ± 3.96 (5.31) |
| Avg ball speed [m/s] | 1.76 ± 0.30 (1.76) |
| Peak ball speed [m/s] | 3.82 ± 0.70 (3.76) |
| Distance [m] | 1.38 ± 0.41 (1.35) |
| Path length [m] | 1.38 ± 0.41 (1.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.941 | 50/50 | 0 | 49 | 1.03 ± 0.28 (1.08) | 5.38 ± 3.55 (4.46) | 1.58 ± 0.32 (1.60) | 3.46 ± 0.70 (3.41) | 1.14 ± 0.40 (1.14) |
| left | p | 0.924 | 50/50 | 0 | 49 | 1.54 ± 0.37 (1.46) | 7.22 ± 4.12 (7.35) | 1.75 ± 0.29 (1.77) | 3.76 ± 0.68 (3.75) | 1.35 ± 0.40 (1.32) |
| back | p | 0.910 | 50/50 | 0 | 50 | 2.35 ± 0.30 (2.32) | 6.37 ± 3.23 (6.63) | 1.90 ± 0.22 (1.85) | 4.12 ± 0.56 (3.91) | 1.56 ± 0.35 (1.51) |
| right | p | 0.934 | 50/50 | 0 | 47 | 1.56 ± 0.37 (1.56) | 6.50 ± 4.58 (4.78) | 1.82 ± 0.26 (1.74) | 3.93 ± 0.66 (3.68) | 1.45 ± 0.38 (1.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.925 | 100/100 | 0 | 97 | 1.61 ± 0.58 (1.53) | 6.66 ± 3.96 (5.52) | 1.75 ± 0.31 (1.76) | 3.80 ± 0.71 (3.77) | 1.37 ± 0.41 (1.34) |
| right | p | 0.930 | 100/100 | 0 | 98 | 1.62 ± 0.58 (1.57) | 6.07 ± 3.93 (5.02) | 1.77 ± 0.29 (1.76) | 3.83 ± 0.68 (3.74) | 1.38 ± 0.41 (1.37) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.940 | 25/25 | 0 | 25 | 1.03 ± 0.29 (1.04) | 5.61 ± 3.00 (4.81) | 1.56 ± 0.33 (1.58) | 3.41 ± 0.72 (3.40) | 1.11 ± 0.40 (1.11) |
| forward/right | p | 0.943 | 25/25 | 0 | 24 | 1.03 ± 0.27 (1.10) | 5.15 ± 4.01 (3.62) | 1.60 ± 0.31 (1.61) | 3.50 ± 0.67 (3.42) | 1.16 ± 0.41 (1.20) |
| left/left | p | 0.914 | 25/25 | 0 | 24 | 1.42 ± 0.35 (1.36) | 8.10 ± 4.50 (9.02) | 1.76 ± 0.35 (1.80) | 3.76 ± 0.79 (3.76) | 1.36 ± 0.46 (1.30) |
| left/right | p | 0.935 | 25/25 | 0 | 25 | 1.65 ± 0.36 (1.60) | 6.33 ± 3.48 (6.26) | 1.74 ± 0.22 (1.76) | 3.75 ± 0.55 (3.73) | 1.34 ± 0.33 (1.33) |
| back/left | p | 0.911 | 25/25 | 0 | 25 | 2.35 ± 0.26 (2.30) | 6.47 ± 3.05 (6.54) | 1.86 ± 0.20 (1.84) | 4.02 ± 0.52 (3.91) | 1.51 ± 0.31 (1.43) |
| back/right | p | 0.909 | 25/25 | 0 | 25 | 2.35 ± 0.34 (2.38) | 6.27 ± 3.40 (6.72) | 1.95 ± 0.23 (1.93) | 4.21 ± 0.59 (4.16) | 1.62 ± 0.37 (1.65) |
| right/left | p | 0.935 | 25/25 | 0 | 23 | 1.65 ± 0.38 (1.58) | 6.46 ± 4.59 (4.76) | 1.84 ± 0.24 (1.88) | 4.00 ± 0.61 (3.83) | 1.48 ± 0.35 (1.41) |
| right/right | p | 0.934 | 25/25 | 0 | 24 | 1.46 ± 0.35 (1.48) | 6.54 ± 4.57 (5.00) | 1.81 ± 0.28 (1.72) | 3.87 ± 0.70 (3.56) | 1.42 ± 0.40 (1.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.919 | 6.8 | 4.06 | 1.50 |
| p | normal | 0.936 | 5.9 | 3.58 | 1.25 |

## Notes

- p: score 0.927, 200/200 kicked, 0 fell; worst sector back (0.910).
