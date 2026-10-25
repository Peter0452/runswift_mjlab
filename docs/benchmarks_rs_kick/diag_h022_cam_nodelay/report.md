# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.834** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 158 |
| Weak kicks (< 0.3 m) | 30 |
| Time to kick [s] | 1.94 ± 1.80 (1.53) |
| Direction error [°] | 20.64 ± 38.09 (6.36) |
| Avg ball speed [m/s] | 1.52 ± 0.55 (1.65) |
| Peak ball speed [m/s] | 3.25 ± 1.24 (3.46) |
| Distance [m] | 1.10 ± 0.59 (1.14) |
| Path length [m] | 1.10 ± 0.59 (1.14) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.858 | 49/50 | 0 | 40 | 1.73 ± 2.34 (1.16) | 10.45 ± 15.43 (4.95) | 1.39 ± 0.51 (1.47) | 2.95 ± 1.14 (3.11) | 0.91 ± 0.52 (0.97) |
| left | h022 | 0.826 | 48/50 | 0 | 40 | 1.88 ± 1.82 (1.60) | 19.48 ± 33.05 (6.84) | 1.53 ± 0.53 (1.63) | 3.31 ± 1.23 (3.51) | 1.12 ± 0.58 (1.11) |
| back | h022 | 0.798 | 48/50 | 0 | 39 | 2.45 ± 1.38 (2.41) | 32.73 ± 56.73 (7.24) | 1.60 ± 0.59 (1.75) | 3.44 ± 1.34 (3.71) | 1.23 ± 0.62 (1.31) |
| right | h022 | 0.853 | 49/50 | 0 | 39 | 1.70 ± 1.34 (1.52) | 20.11 ± 32.16 (6.90) | 1.55 ± 0.53 (1.67) | 3.32 ± 1.20 (3.50) | 1.13 ± 0.58 (1.18) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.871 | 100/100 | 0 | 84 | 1.80 ± 1.37 (1.53) | 20.60 ± 39.15 (6.14) | 1.55 ± 0.54 (1.67) | 3.32 ± 1.22 (3.47) | 1.13 ± 0.59 (1.13) |
| right | h022 | 0.796 | 94/100 | 0 | 74 | 2.08 ± 2.15 (1.53) | 20.68 ± 36.93 (6.46) | 1.48 ± 0.55 (1.64) | 3.19 ± 1.26 (3.46) | 1.07 ± 0.58 (1.17) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.898 | 25/25 | 0 | 23 | 1.50 ± 1.70 (1.20) | 8.70 ± 15.28 (4.56) | 1.39 ± 0.50 (1.44) | 2.95 ± 1.06 (2.96) | 0.90 ± 0.49 (0.86) |
| forward/right | h022 | 0.818 | 24/25 | 0 | 17 | 1.96 ± 2.84 (1.14) | 12.27 ± 15.38 (5.08) | 1.38 ± 0.52 (1.54) | 2.96 ± 1.21 (3.22) | 0.93 ± 0.54 (1.06) |
| left/left | h022 | 0.896 | 25/25 | 0 | 22 | 1.42 ± 0.43 (1.54) | 15.02 ± 23.20 (6.85) | 1.60 ± 0.49 (1.62) | 3.47 ± 1.14 (3.54) | 1.19 ± 0.55 (1.12) |
| left/right | h022 | 0.756 | 23/25 | 0 | 18 | 2.37 ± 2.50 (1.72) | 24.34 ± 40.62 (6.53) | 1.45 ± 0.57 (1.63) | 3.14 ± 1.29 (3.49) | 1.05 ± 0.60 (1.10) |
| back/left | h022 | 0.821 | 25/25 | 0 | 20 | 2.68 ± 1.78 (2.44) | 34.86 ± 59.53 (7.11) | 1.62 ± 0.61 (1.77) | 3.46 ± 1.36 (3.79) | 1.25 ± 0.65 (1.34) |
| back/right | h022 | 0.774 | 23/25 | 0 | 19 | 2.21 ± 0.65 (2.38) | 30.42 ± 53.41 (7.38) | 1.59 ± 0.58 (1.69) | 3.41 ± 1.31 (3.64) | 1.22 ± 0.59 (1.24) |
| right/left | h022 | 0.870 | 25/25 | 0 | 19 | 1.58 ± 0.46 (1.54) | 23.81 ± 37.78 (6.79) | 1.58 ± 0.54 (1.74) | 3.38 ± 1.23 (3.57) | 1.18 ± 0.60 (1.24) |
| right/right | h022 | 0.837 | 24/25 | 0 | 20 | 1.82 ± 1.85 (1.51) | 16.25 ± 24.40 (6.98) | 1.51 ± 0.51 (1.64) | 3.26 ± 1.16 (3.37) | 1.08 ± 0.55 (1.12) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.827 | 19.8 | 3.63 | 1.28 |
| h022 | normal | 0.841 | 21.4 | 2.88 | 0.92 |

## Notes

- h022: score 0.834, 194/200 kicked, 0 fell; worst sector back (0.798).
