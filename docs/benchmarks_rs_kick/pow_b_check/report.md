# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5). Trials, kick rule and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **pow_b** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_21-02-12_pow_b/model_19249.pt`.

## Overall

| Metric | pow_b |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.14 ± 1.95 (1.68) |
| Direction error [°] | 19.36 ± 39.25 (5.22) |
| Avg ball speed [m/s] | 2.18 ± 0.78 (2.30) |
| Peak ball speed [m/s] | 4.89 ± 1.72 (5.10) |
| Distance [m] | 2.17 ± 1.04 (2.19) |
| Path length [m] | 2.18 ± 1.05 (2.20) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | pow_b | 0.872 | 49/50 | 0 | 42 | 1.82 ± 2.24 (1.28) | 8.77 ± 10.73 (5.20) | 2.14 ± 0.65 (2.26) | 4.72 ± 1.43 (4.90) | 1.99 ± 0.88 (2.08) |
| left | pow_b | 0.862 | 48/50 | 0 | 40 | 1.68 ± 0.51 (1.77) | 19.07 ± 35.33 (4.63) | 2.17 ± 0.80 (2.28) | 4.93 ± 1.74 (5.27) | 2.18 ± 1.05 (2.22) |
| back | pow_b | 0.819 | 50/50 | 0 | 41 | 3.00 ± 2.22 (2.59) | 26.81 ± 54.00 (4.64) | 2.28 ± 0.86 (2.49) | 5.10 ± 1.92 (5.74) | 2.37 ± 1.13 (2.29) |
| right | pow_b | 0.837 | 48/50 | 0 | 39 | 2.04 ± 1.96 (1.68) | 22.70 ± 40.88 (5.41) | 2.15 ± 0.78 (2.25) | 4.83 ± 1.74 (5.06) | 2.13 ± 1.05 (2.19) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | pow_b | 0.872 | 99/100 | 0 | 85 | 1.93 ± 1.39 (1.66) | 20.51 ± 42.82 (5.31) | 2.19 ± 0.78 (2.32) | 4.92 ± 1.75 (5.35) | 2.19 ± 1.04 (2.29) |
| right | pow_b | 0.823 | 96/100 | 0 | 77 | 2.36 ± 2.38 (1.73) | 18.18 ± 35.15 (4.92) | 2.17 ± 0.78 (2.28) | 4.87 ± 1.69 (5.01) | 2.15 ± 1.04 (2.13) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | pow_b | 0.922 | 25/25 | 0 | 24 | 1.59 ± 1.69 (1.24) | 7.01 ± 10.20 (4.59) | 2.23 ± 0.48 (2.26) | 5.02 ± 1.12 (4.97) | 2.13 ± 0.74 (2.23) |
| forward/right | pow_b | 0.823 | 24/25 | 0 | 18 | 2.05 ± 2.68 (1.31) | 10.59 ± 10.96 (6.16) | 2.05 ± 0.78 (2.24) | 4.40 ± 1.63 (4.81) | 1.84 ± 0.99 (1.91) |
| left/left | pow_b | 0.921 | 25/25 | 0 | 23 | 1.61 ± 0.44 (1.72) | 11.80 ± 22.18 (5.34) | 2.29 ± 0.78 (2.32) | 5.14 ± 1.69 (5.63) | 2.32 ± 1.03 (2.41) |
| left/right | pow_b | 0.803 | 23/25 | 0 | 17 | 1.76 ± 0.57 (1.86) | 26.98 ± 44.17 (3.51) | 2.04 ± 0.79 (2.23) | 4.69 ± 1.77 (5.10) | 2.02 ± 1.05 (2.10) |
| back/left | pow_b | 0.814 | 25/25 | 0 | 20 | 2.81 ± 1.83 (2.58) | 31.45 ± 59.71 (4.27) | 2.19 ± 0.88 (2.49) | 4.90 ± 2.02 (5.79) | 2.25 ± 1.13 (2.33) |
| back/right | pow_b | 0.825 | 25/25 | 0 | 21 | 3.20 ± 2.54 (2.62) | 22.18 ± 47.15 (5.01) | 2.36 ± 0.83 (2.54) | 5.29 ± 1.79 (5.70) | 2.49 ± 1.11 (2.23) |
| right/left | pow_b | 0.830 | 24/25 | 0 | 18 | 1.71 ± 0.50 (1.66) | 32.25 ± 51.93 (5.47) | 2.06 ± 0.89 (2.21) | 4.60 ± 2.00 (4.90) | 2.03 ± 1.18 (2.19) |
| right/right | pow_b | 0.844 | 24/25 | 0 | 21 | 2.38 ± 2.69 (1.70) | 13.15 ± 21.53 (5.41) | 2.23 ± 0.64 (2.30) | 5.05 ± 1.40 (5.25) | 2.23 ± 0.89 (2.19) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| pow_b | strong | 0.843 | 16.0 | 5.56 | 2.57 |
| pow_b | normal | 0.853 | 22.7 | 4.23 | 1.77 |

## Notes

- pow_b: score 0.848, 195/200 kicked, 0 fell; worst sector back (0.819).
