# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball ours, kick rule ours, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **pow_b** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_21-02-12_pow_b/model_19249.pt`.

## Overall

| Metric | pow_b |
|---|---|
| **Score** | **0.879** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 2.11 ± 1.23 (1.90) |
| Direction error [°] | 9.91 ± 19.09 (6.06) |
| Avg ball speed [m/s] | 2.00 ± 0.40 (2.11) |
| Peak ball speed [m/s] | 7.40 ± 1.63 (7.98) |
| Distance [m] | 6.31 ± 1.76 (6.89) |
| Path length [m] | 6.31 ± 1.76 (6.89) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | pow_b | 0.850 | 50/50 | 0 | 36 | 2.02 ± 2.20 (1.40) | 14.80 ± 25.63 (9.26) | 1.82 ± 0.45 (1.77) | 6.70 ± 1.80 (6.43) | 5.57 ± 1.91 (5.29) |
| left | pow_b | 0.905 | 49/50 | 0 | 43 | 1.86 ± 0.42 (1.90) | 7.13 ± 6.42 (5.23) | 2.09 ± 0.29 (2.14) | 7.74 ± 1.23 (8.11) | 6.66 ± 1.43 (7.03) |
| back | pow_b | 0.850 | 49/50 | 0 | 47 | 2.73 ± 0.47 (2.72) | 8.20 ± 22.79 (4.26) | 2.09 ± 0.38 (2.23) | 7.72 ± 1.53 (8.26) | 6.66 ± 1.66 (7.21) |
| right | pow_b | 0.912 | 50/50 | 0 | 43 | 1.86 ± 0.54 (1.78) | 9.41 ± 14.22 (6.54) | 2.01 ± 0.40 (2.18) | 7.44 ± 1.65 (8.09) | 6.35 ± 1.77 (7.18) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | pow_b | 0.892 | 100/100 | 0 | 88 | 2.15 ± 1.36 (1.93) | 10.95 ± 25.37 (5.60) | 1.99 ± 0.41 (2.10) | 7.36 ± 1.65 (7.91) | 6.26 ± 1.81 (6.90) |
| right | pow_b | 0.867 | 98/100 | 0 | 81 | 2.08 ± 1.09 (1.90) | 8.85 ± 8.81 (6.64) | 2.01 ± 0.39 (2.13) | 7.43 ± 1.60 (8.07) | 6.36 ± 1.70 (6.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | pow_b | 0.868 | 25/25 | 0 | 21 | 2.14 ± 2.44 (1.40) | 15.23 ± 34.02 (6.84) | 1.82 ± 0.47 (1.83) | 6.73 ± 1.83 (6.69) | 5.60 ± 1.98 (5.55) |
| forward/right | pow_b | 0.832 | 25/25 | 0 | 15 | 1.90 ± 1.92 (1.34) | 14.37 ± 12.51 (11.81) | 1.82 ± 0.44 (1.69) | 6.66 ± 1.77 (6.07) | 5.55 ± 1.84 (4.79) |
| left/left | pow_b | 0.931 | 25/25 | 0 | 22 | 1.70 ± 0.41 (1.76) | 6.79 ± 6.03 (4.77) | 2.03 ± 0.30 (2.11) | 7.52 ± 1.26 (7.99) | 6.38 ± 1.51 (7.00) |
| left/right | pow_b | 0.878 | 24/25 | 0 | 21 | 2.03 ± 0.37 (1.99) | 7.49 ± 6.79 (5.49) | 2.14 ± 0.28 (2.18) | 7.98 ± 1.15 (8.23) | 6.96 ± 1.27 (7.17) |
| back/left | pow_b | 0.859 | 25/25 | 0 | 23 | 2.72 ± 0.56 (2.70) | 11.34 ± 31.37 (4.43) | 2.05 ± 0.41 (2.23) | 7.56 ± 1.65 (8.26) | 6.51 ± 1.76 (7.21) |
| back/right | pow_b | 0.841 | 24/25 | 0 | 24 | 2.73 ± 0.34 (2.73) | 4.93 ± 3.83 (3.89) | 2.13 ± 0.33 (2.22) | 7.88 ± 1.39 (8.32) | 6.82 ± 1.52 (7.22) |
| right/left | pow_b | 0.908 | 25/25 | 0 | 22 | 2.04 ± 0.62 (1.96) | 10.42 ± 18.97 (6.00) | 2.05 ± 0.41 (2.22) | 7.62 ± 1.66 (8.47) | 6.56 ± 1.80 (7.35) |
| right/right | pow_b | 0.915 | 25/25 | 0 | 21 | 1.69 ± 0.36 (1.72) | 8.41 ± 6.49 (7.70) | 1.96 ± 0.39 (2.04) | 7.25 ± 1.63 (7.88) | 6.14 ± 1.72 (6.53) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| pow_b | strong | 0.890 | 7.5 | 8.32 | 7.32 |
| pow_b | normal | 0.869 | 12.3 | 6.47 | 5.30 |

## Notes

- pow_b: score 0.879, 198/200 kicked, 0 fell; worst sector back (0.850).
