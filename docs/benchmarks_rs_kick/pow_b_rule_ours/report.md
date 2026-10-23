# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule ours, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **pow_b** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_21-02-12_pow_b/model_19249.pt`.

## Overall

| Metric | pow_b |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 2.43 ± 2.30 (1.85) |
| Direction error [°] | 13.22 ± 28.36 (6.30) |
| Avg ball speed [m/s] | 2.78 ± 0.73 (3.08) |
| Peak ball speed [m/s] | 5.56 ± 1.51 (6.43) |
| Distance [m] | 2.82 ± 1.11 (3.35) |
| Path length [m] | 2.83 ± 1.11 (3.36) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | pow_b | 0.852 | 48/50 | 0 | 43 | 2.11 ± 2.71 (1.33) | 7.56 ± 7.36 (6.04) | 2.65 ± 0.71 (2.45) | 5.29 ± 1.46 (4.69) | 2.60 ± 1.05 (2.12) |
| left | pow_b | 0.851 | 48/50 | 0 | 41 | 2.00 ± 1.34 (1.85) | 15.14 ± 28.63 (6.99) | 2.81 ± 0.75 (3.10) | 5.64 ± 1.57 (6.48) | 2.90 ± 1.12 (3.37) |
| back | pow_b | 0.801 | 48/50 | 0 | 42 | 2.92 ± 1.96 (2.64) | 19.74 ± 43.84 (6.82) | 2.86 ± 0.73 (3.25) | 5.71 ± 1.52 (6.69) | 2.96 ± 1.15 (3.62) |
| right | pow_b | 0.875 | 50/50 | 0 | 44 | 2.69 ± 2.73 (1.82) | 10.55 ± 18.83 (5.70) | 2.80 ± 0.72 (3.11) | 5.58 ± 1.45 (6.42) | 2.83 ± 1.08 (3.25) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | pow_b | 0.879 | 100/100 | 0 | 90 | 2.35 ± 2.06 (1.86) | 12.35 ± 28.41 (6.05) | 2.86 ± 0.65 (3.21) | 5.72 ± 1.36 (6.48) | 2.94 ± 1.04 (3.42) |
| right | pow_b | 0.810 | 94/100 | 0 | 80 | 2.52 ± 2.52 (1.80) | 14.14 ± 28.29 (6.72) | 2.69 ± 0.80 (2.88) | 5.38 ± 1.63 (6.11) | 2.69 ± 1.16 (3.11) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | pow_b | 0.905 | 25/25 | 0 | 23 | 2.08 ± 2.63 (1.34) | 6.11 ± 5.10 (4.84) | 2.81 ± 0.55 (2.86) | 5.60 ± 1.16 (5.87) | 2.79 ± 0.89 (2.82) |
| forward/right | pow_b | 0.799 | 23/25 | 0 | 20 | 2.15 ± 2.79 (1.32) | 9.13 ± 8.94 (7.10) | 2.48 ± 0.81 (2.30) | 4.96 ± 1.67 (4.55) | 2.39 ± 1.17 (1.96) |
| left/left | pow_b | 0.911 | 25/25 | 0 | 23 | 1.89 ± 0.82 (1.80) | 7.13 ± 4.27 (7.14) | 2.95 ± 0.49 (3.22) | 5.91 ± 1.09 (6.47) | 3.09 ± 0.88 (3.35) |
| left/right | pow_b | 0.791 | 23/25 | 0 | 18 | 2.13 ± 1.73 (1.92) | 23.84 ± 39.32 (6.95) | 2.66 ± 0.94 (3.06) | 5.34 ± 1.91 (6.50) | 2.70 ± 1.30 (3.37) |
| back/left | pow_b | 0.823 | 25/25 | 0 | 22 | 2.84 ± 1.97 (2.64) | 25.33 ± 50.50 (7.12) | 2.78 ± 0.80 (3.25) | 5.59 ± 1.70 (6.70) | 2.91 ± 1.27 (3.57) |
| back/right | pow_b | 0.779 | 23/25 | 0 | 20 | 3.01 ± 1.95 (2.66) | 13.67 ± 34.19 (6.75) | 2.94 ± 0.64 (3.24) | 5.83 ± 1.29 (6.69) | 3.02 ± 1.00 (3.68) |
| right/left | pow_b | 0.876 | 25/25 | 0 | 22 | 2.60 ± 2.22 (1.94) | 10.85 ± 19.93 (6.01) | 2.91 ± 0.68 (3.27) | 5.79 ± 1.40 (6.54) | 2.99 ± 1.06 (3.62) |
| right/right | pow_b | 0.874 | 25/25 | 0 | 22 | 2.77 ± 3.16 (1.72) | 10.24 ± 17.66 (5.05) | 2.69 ± 0.74 (2.80) | 5.38 ± 1.47 (6.08) | 2.67 ± 1.07 (3.09) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| pow_b | strong | 0.832 | 10.7 | 6.51 | 3.54 |
| pow_b | normal | 0.857 | 15.6 | 4.64 | 2.13 |

## Notes

- pow_b: score 0.845, 194/200 kicked, 0 fell; worst sector back (0.801).
