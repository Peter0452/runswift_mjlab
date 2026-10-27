# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.90 ± 0.61 (1.74) |
| Direction error [°] | 5.49 ± 6.60 (4.25) |
| Avg ball speed [m/s] | 2.31 ± 0.49 (2.44) |
| Peak ball speed [m/s] | 4.88 ± 1.15 (5.41) |
| Distance [m] | 2.25 ± 0.76 (2.54) |
| Path length [m] | 2.26 ± 0.76 (2.55) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.869 | 50/50 | 0 | 47 | 1.29 ± 0.26 (1.31) | 5.35 ± 9.62 (3.15) | 2.28 ± 0.49 (2.45) | 4.84 ± 1.15 (5.34) | 2.18 ± 0.71 (2.36) |
| left | h022 | 0.866 | 50/50 | 0 | 49 | 1.82 ± 0.39 (1.76) | 4.76 ± 3.57 (3.43) | 2.30 ± 0.46 (2.43) | 4.85 ± 1.09 (5.31) | 2.22 ± 0.73 (2.40) |
| back | h022 | 0.791 | 50/50 | 0 | 49 | 2.69 ± 0.35 (2.64) | 6.54 ± 3.80 (6.43) | 2.43 ± 0.49 (2.61) | 5.11 ± 1.16 (5.65) | 2.44 ± 0.78 (2.75) |
| right | h022 | 0.853 | 50/50 | 0 | 49 | 1.80 ± 0.37 (1.73) | 5.29 ± 7.25 (4.21) | 2.24 ± 0.50 (2.34) | 4.72 ± 1.15 (5.34) | 2.15 ± 0.77 (2.48) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.843 | 100/100 | 0 | 98 | 1.89 ± 0.61 (1.74) | 5.14 ± 3.81 (4.52) | 2.34 ± 0.43 (2.45) | 4.97 ± 1.02 (5.46) | 2.30 ± 0.71 (2.57) |
| right | h022 | 0.847 | 100/100 | 0 | 96 | 1.91 ± 0.61 (1.79) | 5.84 ± 8.50 (3.87) | 2.29 ± 0.55 (2.43) | 4.79 ± 1.26 (5.33) | 2.20 ± 0.80 (2.40) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.872 | 25/25 | 0 | 24 | 1.26 ± 0.26 (1.30) | 4.19 ± 3.52 (3.06) | 2.32 ± 0.34 (2.45) | 4.92 ± 0.89 (5.46) | 2.23 ± 0.62 (2.43) |
| forward/right | h022 | 0.867 | 25/25 | 0 | 23 | 1.32 ± 0.25 (1.34) | 6.52 ± 13.04 (3.24) | 2.25 ± 0.60 (2.44) | 4.76 ± 1.35 (5.34) | 2.14 ± 0.79 (2.29) |
| left/left | h022 | 0.861 | 25/25 | 0 | 24 | 1.73 ± 0.37 (1.72) | 5.39 ± 3.96 (4.26) | 2.28 ± 0.56 (2.44) | 4.86 ± 1.28 (5.43) | 2.26 ± 0.83 (2.55) |
| left/right | h022 | 0.870 | 25/25 | 0 | 25 | 1.92 ± 0.39 (1.98) | 4.13 ± 2.99 (3.36) | 2.32 ± 0.34 (2.42) | 4.84 ± 0.87 (5.12) | 2.19 ± 0.62 (2.23) |
| back/left | h022 | 0.792 | 25/25 | 0 | 25 | 2.68 ± 0.27 (2.64) | 6.24 ± 3.76 (6.49) | 2.53 ± 0.34 (2.65) | 5.27 ± 0.85 (5.69) | 2.55 ± 0.65 (2.85) |
| back/right | h022 | 0.790 | 25/25 | 0 | 24 | 2.70 ± 0.42 (2.64) | 6.83 ± 3.82 (6.37) | 2.34 ± 0.60 (2.59) | 4.94 ± 1.38 (5.62) | 2.33 ± 0.87 (2.57) |
| right/left | h022 | 0.845 | 25/25 | 0 | 25 | 1.88 ± 0.39 (1.80) | 4.73 ± 3.67 (4.79) | 2.25 ± 0.37 (2.35) | 4.82 ± 0.92 (5.33) | 2.16 ± 0.67 (2.41) |
| right/right | h022 | 0.861 | 25/25 | 0 | 24 | 1.72 ± 0.34 (1.66) | 5.86 ± 9.54 (3.50) | 2.23 ± 0.61 (2.31) | 4.63 ± 1.33 (5.38) | 2.13 ± 0.86 (2.60) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.868 | 6.4 | 5.52 | 2.71 |
| h022 | normal | 0.821 | 4.5 | 4.25 | 1.79 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| h022 | small | 54 | 0.772 | 0.13 | 2.47 ± 0.80 (2.32) | 3.81 | 1.46 |
| h022 | medium | 20 | 0.882 | 0.78 | 1.13 ± 0.27 (1.17) | 3.63 | 1.41 |
| h022 | strong | 126 | 0.870 | 0.74 | - | 5.54 | 2.72 |

## Notes

- h022: score 0.845, 200/200 kicked, 0 fell; worst sector back (0.791).
