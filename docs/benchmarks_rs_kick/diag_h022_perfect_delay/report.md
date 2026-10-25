# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.935** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.87 ± 0.58 (1.82) |
| Direction error [°] | 5.95 ± 15.44 (3.70) |
| Avg ball speed [m/s] | 2.12 ± 0.34 (2.16) |
| Peak ball speed [m/s] | 4.62 ± 0.91 (4.93) |
| Distance [m] | 1.85 ± 0.49 (1.88) |
| Path length [m] | 1.86 ± 0.49 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.968 | 50/50 | 0 | 50 | 1.27 ± 0.24 (1.31) | 3.21 ± 2.39 (2.58) | 2.11 ± 0.26 (2.12) | 4.58 ± 0.80 (4.72) | 1.80 ± 0.46 (1.70) |
| left | h022 | 0.946 | 50/50 | 0 | 49 | 1.81 ± 0.37 (1.83) | 5.02 ± 4.95 (3.68) | 2.12 ± 0.36 (2.22) | 4.68 ± 0.91 (4.97) | 1.88 ± 0.49 (1.94) |
| back | h022 | 0.874 | 50/50 | 0 | 48 | 2.60 ± 0.33 (2.59) | 11.26 ± 29.57 (5.09) | 2.11 ± 0.46 (2.15) | 4.58 ± 1.14 (5.00) | 1.88 ± 0.58 (1.98) |
| right | h022 | 0.953 | 50/50 | 0 | 49 | 1.81 ± 0.36 (1.82) | 4.32 ± 3.15 (3.43) | 2.14 ± 0.24 (2.15) | 4.66 ± 0.73 (4.84) | 1.84 ± 0.43 (1.79) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.929 | 100/100 | 0 | 97 | 1.87 ± 0.57 (1.84) | 7.56 ± 21.52 (3.55) | 2.08 ± 0.42 (2.15) | 4.55 ± 1.05 (4.95) | 1.82 ± 0.54 (1.91) |
| right | h022 | 0.941 | 100/100 | 0 | 99 | 1.87 ± 0.58 (1.81) | 4.35 ± 2.96 (3.74) | 2.15 ± 0.24 (2.16) | 4.70 ± 0.73 (4.93) | 1.88 ± 0.44 (1.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.971 | 25/25 | 0 | 25 | 1.28 ± 0.24 (1.34) | 2.86 ± 1.46 (2.76) | 2.09 ± 0.25 (2.14) | 4.56 ± 0.77 (4.85) | 1.78 ± 0.45 (1.74) |
| forward/right | h022 | 0.964 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.28) | 3.55 ± 3.00 (2.41) | 2.13 ± 0.26 (2.11) | 4.60 ± 0.83 (4.41) | 1.82 ± 0.46 (1.67) |
| left/left | h022 | 0.939 | 25/25 | 0 | 24 | 1.71 ± 0.37 (1.80) | 5.63 ± 6.60 (3.53) | 2.09 ± 0.46 (2.22) | 4.60 ± 1.11 (5.02) | 1.85 ± 0.55 (1.96) |
| left/right | h022 | 0.953 | 25/25 | 0 | 25 | 1.90 ± 0.34 (1.88) | 4.42 ± 2.19 (3.95) | 2.14 ± 0.22 (2.22) | 4.77 ± 0.65 (4.92) | 1.90 ± 0.41 (1.92) |
| back/left | h022 | 0.853 | 25/25 | 0 | 23 | 2.59 ± 0.30 (2.60) | 17.64 ± 40.73 (7.14) | 2.02 ± 0.60 (2.15) | 4.41 ± 1.42 (5.00) | 1.82 ± 0.68 (2.06) |
| back/right | h022 | 0.896 | 25/25 | 0 | 25 | 2.61 ± 0.36 (2.58) | 4.89 ± 2.90 (4.36) | 2.19 ± 0.23 (2.21) | 4.75 ± 0.71 (5.01) | 1.94 ± 0.44 (1.98) |
| right/left | h022 | 0.953 | 25/25 | 0 | 25 | 1.92 ± 0.32 (1.86) | 4.11 ± 2.82 (3.18) | 2.12 ± 0.25 (2.16) | 4.65 ± 0.74 (4.84) | 1.82 ± 0.43 (1.82) |
| right/right | h022 | 0.953 | 25/25 | 0 | 24 | 1.70 ± 0.35 (1.80) | 4.54 ± 3.44 (3.52) | 2.15 ± 0.22 (2.10) | 4.66 ± 0.72 (5.00) | 1.86 ± 0.43 (1.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.936 | 6.0 | 5.16 | 2.13 |
| h022 | normal | 0.935 | 5.9 | 4.09 | 1.57 |

## Notes

- h022: score 0.935, 200/200 kicked, 0 fell; worst sector back (0.874).
