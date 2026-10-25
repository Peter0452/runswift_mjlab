# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.940** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.62 ± 0.56 (1.55) |
| Direction error [°] | 5.05 ± 3.29 (4.41) |
| Avg ball speed [m/s] | 1.76 ± 0.32 (1.76) |
| Peak ball speed [m/s] | 3.82 ± 0.76 (3.77) |
| Distance [m] | 1.38 ± 0.45 (1.33) |
| Path length [m] | 1.38 ± 0.45 (1.34) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.950 | 50/50 | 0 | 50 | 1.05 ± 0.27 (1.12) | 4.18 ± 2.49 (3.32) | 1.56 ± 0.33 (1.53) | 3.40 ± 0.78 (3.23) | 1.12 ± 0.44 (0.98) |
| left | h022 | 0.937 | 50/50 | 0 | 50 | 1.56 ± 0.36 (1.51) | 5.98 ± 3.82 (4.90) | 1.73 ± 0.28 (1.71) | 3.75 ± 0.69 (3.66) | 1.34 ± 0.40 (1.23) |
| back | h022 | 0.927 | 50/50 | 0 | 50 | 2.34 ± 0.29 (2.33) | 4.67 ± 2.40 (4.57) | 1.97 ± 0.26 (2.01) | 4.25 ± 0.65 (4.47) | 1.65 ± 0.40 (1.72) |
| right | h022 | 0.946 | 50/50 | 0 | 50 | 1.53 ± 0.36 (1.56) | 5.35 ± 3.86 (4.63) | 1.79 ± 0.24 (1.78) | 3.88 ± 0.65 (3.82) | 1.41 ± 0.37 (1.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.939 | 100/100 | 0 | 100 | 1.62 ± 0.55 (1.53) | 5.07 ± 3.39 (4.41) | 1.76 ± 0.33 (1.77) | 3.83 ± 0.80 (3.79) | 1.38 ± 0.46 (1.35) |
| right | h022 | 0.941 | 100/100 | 0 | 100 | 1.63 ± 0.57 (1.56) | 5.02 ± 3.19 (4.33) | 1.76 ± 0.30 (1.74) | 3.81 ± 0.71 (3.69) | 1.37 ± 0.43 (1.32) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.951 | 25/25 | 0 | 25 | 1.05 ± 0.27 (1.04) | 3.78 ± 2.52 (2.78) | 1.55 ± 0.34 (1.51) | 3.37 ± 0.80 (3.15) | 1.10 ± 0.42 (0.98) |
| forward/right | h022 | 0.948 | 25/25 | 0 | 25 | 1.06 ± 0.26 (1.12) | 4.59 ± 2.40 (3.63) | 1.57 ± 0.32 (1.55) | 3.44 ± 0.76 (3.32) | 1.13 ± 0.45 (0.98) |
| left/left | h022 | 0.929 | 25/25 | 0 | 25 | 1.47 ± 0.35 (1.44) | 6.48 ± 3.75 (5.25) | 1.68 ± 0.31 (1.69) | 3.67 ± 0.76 (3.43) | 1.31 ± 0.43 (1.20) |
| left/right | h022 | 0.945 | 25/25 | 0 | 25 | 1.64 ± 0.35 (1.62) | 5.49 ± 3.82 (3.84) | 1.77 ± 0.23 (1.71) | 3.82 ± 0.59 (3.75) | 1.37 ± 0.35 (1.28) |
| back/left | h022 | 0.931 | 25/25 | 0 | 25 | 2.34 ± 0.24 (2.32) | 4.58 ± 2.30 (4.62) | 1.97 ± 0.27 (2.02) | 4.28 ± 0.67 (4.48) | 1.66 ± 0.41 (1.72) |
| back/right | h022 | 0.923 | 25/25 | 0 | 25 | 2.35 ± 0.34 (2.34) | 4.77 ± 2.49 (4.51) | 1.96 ± 0.24 (2.01) | 4.22 ± 0.63 (4.46) | 1.64 ± 0.39 (1.71) |
| right/left | h022 | 0.945 | 25/25 | 0 | 25 | 1.61 ± 0.34 (1.56) | 5.46 ± 4.03 (3.74) | 1.83 ± 0.23 (1.93) | 3.99 ± 0.65 (4.21) | 1.47 ± 0.36 (1.54) |
| right/right | h022 | 0.947 | 25/25 | 0 | 25 | 1.45 ± 0.35 (1.52) | 5.24 ± 3.68 (5.69) | 1.75 ± 0.25 (1.71) | 3.77 ± 0.63 (3.62) | 1.35 ± 0.36 (1.31) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.933 | 5.3 | 4.16 | 1.57 |
| h022 | normal | 0.947 | 4.8 | 3.48 | 1.19 |

## Notes

- h022: score 0.940, 200/200 kicked, 0 fell; worst sector back (0.927).
