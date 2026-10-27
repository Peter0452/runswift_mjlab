# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.83 ± 0.58 (1.73) |
| Direction error [°] | 5.32 ± 3.62 (4.60) |
| Avg ball speed [m/s] | 2.28 ± 0.27 (2.28) |
| Peak ball speed [m/s] | 5.13 ± 0.82 (5.46) |
| Distance [m] | 2.11 ± 0.51 (2.12) |
| Path length [m] | 2.12 ± 0.51 (2.14) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.869 | 50/50 | 0 | 48 | 1.25 ± 0.26 (1.29) | 4.78 ± 3.97 (3.90) | 2.26 ± 0.33 (2.34) | 5.15 ± 0.91 (5.58) | 2.11 ± 0.58 (2.23) |
| left | p | 0.864 | 50/50 | 0 | 50 | 1.75 ± 0.35 (1.71) | 5.20 ± 3.37 (4.41) | 2.25 ± 0.24 (2.26) | 5.07 ± 0.79 (5.25) | 2.07 ± 0.50 (2.08) |
| back | p | 0.805 | 50/50 | 0 | 49 | 2.58 ± 0.38 (2.52) | 6.32 ± 3.73 (5.98) | 2.36 ± 0.21 (2.38) | 5.30 ± 0.72 (5.53) | 2.24 ± 0.44 (2.21) |
| right | p | 0.851 | 50/50 | 0 | 50 | 1.74 ± 0.35 (1.71) | 4.97 ± 3.13 (4.89) | 2.24 ± 0.26 (2.24) | 5.00 ± 0.79 (5.34) | 2.02 ± 0.47 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.82 ± 0.56 (1.70) | 5.41 ± 3.51 (4.90) | 2.29 ± 0.26 (2.31) | 5.18 ± 0.79 (5.48) | 2.14 ± 0.49 (2.17) |
| right | p | 0.851 | 100/100 | 0 | 98 | 1.84 ± 0.60 (1.76) | 5.23 ± 3.72 (4.23) | 2.27 ± 0.27 (2.26) | 5.09 ± 0.84 (5.39) | 2.08 ± 0.52 (2.05) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.864 | 25/25 | 0 | 25 | 1.24 ± 0.26 (1.26) | 4.98 ± 3.39 (4.05) | 2.25 ± 0.34 (2.32) | 5.14 ± 0.93 (5.66) | 2.11 ± 0.58 (2.27) |
| forward/right | p | 0.875 | 25/25 | 0 | 23 | 1.27 ± 0.26 (1.32) | 4.59 ± 4.47 (3.51) | 2.27 ± 0.33 (2.35) | 5.17 ± 0.89 (5.57) | 2.11 ± 0.58 (2.07) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.68 ± 0.34 (1.60) | 5.36 ± 3.71 (4.59) | 2.31 ± 0.17 (2.35) | 5.21 ± 0.66 (5.54) | 2.17 ± 0.40 (2.13) |
| left/right | p | 0.866 | 25/25 | 0 | 25 | 1.81 ± 0.35 (1.82) | 5.03 ± 2.98 (4.24) | 2.19 ± 0.28 (2.19) | 4.93 ± 0.88 (5.18) | 1.98 ± 0.57 (1.86) |
| back/left | p | 0.806 | 25/25 | 0 | 24 | 2.55 ± 0.25 (2.52) | 6.22 ± 3.76 (5.74) | 2.38 ± 0.22 (2.39) | 5.34 ± 0.69 (5.59) | 2.27 ± 0.44 (2.24) |
| back/right | p | 0.803 | 25/25 | 0 | 25 | 2.61 ± 0.47 (2.56) | 6.42 ± 3.71 (6.09) | 2.34 ± 0.21 (2.34) | 5.27 ± 0.75 (5.50) | 2.21 ± 0.44 (2.19) |
| right/left | p | 0.844 | 25/25 | 0 | 25 | 1.81 ± 0.35 (1.76) | 5.06 ± 2.97 (5.24) | 2.22 ± 0.27 (2.24) | 5.03 ± 0.80 (5.37) | 2.02 ± 0.48 (2.00) |
| right/right | p | 0.858 | 25/25 | 0 | 25 | 1.66 ± 0.33 (1.58) | 4.87 ± 3.29 (3.50) | 2.26 ± 0.24 (2.23) | 4.98 ± 0.79 (5.33) | 2.02 ± 0.45 (2.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.886 | 5.2 | 5.72 | 2.42 |
| p | normal | 0.809 | 5.5 | 4.54 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.750 | 0.08 | 2.68 ± 0.86 (2.40) | 4.15 | 1.57 |
| p | medium | 20 | 0.871 | 0.70 | 1.30 ± 0.14 (1.32) | 4.17 | 1.62 |
| p | strong | 126 | 0.885 | 0.76 | - | 5.71 | 2.42 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.805).
