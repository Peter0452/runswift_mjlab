# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.837** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 159 |
| Weak kicks (< 0.3 m) | 32 |
| Time to kick [s] | 1.97 ± 1.88 (1.54) |
| Direction error [°] | 20.39 ± 37.85 (6.29) |
| Avg ball speed [m/s] | 1.50 ± 0.57 (1.62) |
| Peak ball speed [m/s] | 3.22 ± 1.27 (3.39) |
| Distance [m] | 1.09 ± 0.60 (1.11) |
| Path length [m] | 1.09 ± 0.60 (1.11) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.860 | 49/50 | 0 | 41 | 1.66 ± 2.11 (1.16) | 8.67 ± 12.16 (3.55) | 1.33 ± 0.52 (1.43) | 2.83 ± 1.16 (3.06) | 0.85 ± 0.51 (0.90) |
| left | h022 | 0.827 | 48/50 | 0 | 39 | 1.89 ± 1.88 (1.58) | 18.08 ± 28.56 (7.20) | 1.56 ± 0.55 (1.71) | 3.37 ± 1.24 (3.79) | 1.16 ± 0.58 (1.28) |
| back | h022 | 0.812 | 49/50 | 0 | 39 | 2.63 ± 1.90 (2.42) | 33.24 ± 56.72 (5.67) | 1.59 ± 0.61 (1.82) | 3.42 ± 1.36 (3.82) | 1.22 ± 0.63 (1.40) |
| right | h022 | 0.852 | 49/50 | 0 | 40 | 1.69 ± 1.37 (1.52) | 21.50 ± 35.08 (7.72) | 1.53 ± 0.54 (1.67) | 3.27 ± 1.23 (3.42) | 1.12 ± 0.61 (1.12) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.877 | 100/100 | 0 | 86 | 1.78 ± 1.34 (1.53) | 19.32 ± 37.97 (5.58) | 1.53 ± 0.55 (1.65) | 3.28 ± 1.23 (3.52) | 1.11 ± 0.59 (1.13) |
| right | h022 | 0.798 | 95/100 | 0 | 73 | 2.16 ± 2.30 (1.54) | 21.51 ± 37.70 (7.26) | 1.47 ± 0.58 (1.58) | 3.16 ± 1.32 (3.33) | 1.06 ± 0.61 (1.08) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.911 | 25/25 | 0 | 24 | 1.47 ± 1.59 (1.20) | 5.47 ± 7.51 (2.98) | 1.36 ± 0.50 (1.40) | 2.88 ± 1.05 (2.95) | 0.86 ± 0.46 (0.86) |
| forward/right | h022 | 0.809 | 24/25 | 0 | 17 | 1.86 ± 2.53 (1.14) | 12.01 ± 14.88 (5.94) | 1.30 ± 0.54 (1.47) | 2.77 ± 1.26 (3.15) | 0.84 ± 0.55 (0.95) |
| left/left | h022 | 0.897 | 25/25 | 0 | 22 | 1.41 ± 0.42 (1.56) | 15.26 ± 23.48 (7.28) | 1.63 ± 0.46 (1.77) | 3.52 ± 1.07 (3.81) | 1.23 ± 0.54 (1.35) |
| left/right | h022 | 0.756 | 23/25 | 0 | 17 | 2.40 ± 2.58 (1.74) | 21.16 ± 32.94 (7.13) | 1.48 ± 0.62 (1.63) | 3.20 ± 1.38 (3.62) | 1.09 ± 0.61 (1.10) |
| back/left | h022 | 0.826 | 25/25 | 0 | 20 | 2.67 ± 1.79 (2.36) | 33.01 ± 57.14 (5.67) | 1.60 ± 0.59 (1.85) | 3.45 ± 1.32 (3.82) | 1.23 ± 0.62 (1.47) |
| back/right | h022 | 0.797 | 24/25 | 0 | 19 | 2.58 ± 2.02 (2.45) | 33.47 ± 56.27 (5.72) | 1.59 ± 0.62 (1.69) | 3.40 ± 1.40 (3.53) | 1.21 ± 0.64 (1.22) |
| right/left | h022 | 0.871 | 25/25 | 0 | 20 | 1.58 ± 0.45 (1.54) | 23.54 ± 38.47 (7.13) | 1.52 ± 0.59 (1.72) | 3.26 ± 1.33 (3.59) | 1.13 ± 0.65 (1.17) |
| right/right | h022 | 0.832 | 24/25 | 0 | 20 | 1.80 ± 1.89 (1.50) | 19.38 ± 31.01 (8.47) | 1.53 ± 0.49 (1.60) | 3.28 ± 1.12 (3.30) | 1.11 ± 0.55 (1.10) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.835 | 16.9 | 3.65 | 1.30 |
| h022 | normal | 0.840 | 23.8 | 2.81 | 0.88 |

## Notes

- h022: score 0.837, 195/200 kicked, 0 fell; worst sector back (0.812).
