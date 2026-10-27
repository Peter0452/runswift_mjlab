# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w4_u4_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.858** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.89 ± 0.58 (1.80) |
| Direction error [°] | 5.15 ± 3.53 (4.34) |
| Avg ball speed [m/s] | 2.20 ± 0.49 (2.34) |
| Peak ball speed [m/s] | 4.96 ± 1.28 (5.44) |
| Distance [m] | 1.98 ± 0.78 (2.17) |
| Path length [m] | 1.98 ± 0.78 (2.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.871 | 50/50 | 0 | 50 | 1.30 ± 0.26 (1.30) | 4.77 ± 2.86 (4.16) | 2.12 ± 0.59 (2.25) | 4.74 ± 1.44 (5.27) | 1.86 ± 0.87 (2.02) |
| left | p | 0.886 | 50/50 | 0 | 49 | 1.82 ± 0.37 (1.82) | 4.98 ± 3.80 (3.76) | 2.31 ± 0.43 (2.44) | 5.24 ± 1.16 (5.66) | 2.13 ± 0.70 (2.31) |
| back | p | 0.810 | 50/50 | 0 | 48 | 2.62 ± 0.35 (2.53) | 6.23 ± 3.72 (5.52) | 2.20 ± 0.41 (2.36) | 5.00 ± 1.14 (5.46) | 1.99 ± 0.69 (2.21) |
| right | p | 0.865 | 50/50 | 0 | 50 | 1.84 ± 0.36 (1.78) | 4.61 ± 3.42 (3.48) | 2.17 ± 0.50 (2.22) | 4.84 ± 1.28 (5.27) | 1.92 ± 0.80 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 98 | 1.91 ± 0.60 (1.82) | 5.41 ± 3.63 (4.74) | 2.19 ± 0.49 (2.33) | 4.94 ± 1.27 (5.36) | 1.98 ± 0.78 (2.11) |
| right | p | 0.860 | 100/100 | 0 | 99 | 1.88 ± 0.56 (1.78) | 4.89 ± 3.41 (3.94) | 2.21 ± 0.50 (2.38) | 4.97 ± 1.28 (5.46) | 1.97 ± 0.77 (2.18) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.879 | 25/25 | 0 | 25 | 1.31 ± 0.26 (1.30) | 4.57 ± 2.71 (4.56) | 2.15 ± 0.60 (2.25) | 4.78 ± 1.44 (5.28) | 1.91 ± 0.88 (2.11) |
| forward/right | p | 0.863 | 25/25 | 0 | 25 | 1.29 ± 0.26 (1.30) | 4.97 ± 3.00 (4.15) | 2.08 ± 0.59 (2.25) | 4.70 ± 1.45 (5.27) | 1.82 ± 0.86 (1.96) |
| left/left | p | 0.877 | 25/25 | 0 | 24 | 1.71 ± 0.38 (1.80) | 5.39 ± 4.24 (4.24) | 2.23 ± 0.40 (2.36) | 5.02 ± 1.12 (5.46) | 2.01 ± 0.68 (2.20) |
| left/right | p | 0.895 | 25/25 | 0 | 25 | 1.94 ± 0.32 (2.00) | 4.58 ± 3.26 (3.40) | 2.39 ± 0.44 (2.47) | 5.46 ± 1.15 (5.83) | 2.26 ± 0.70 (2.40) |
| back/left | p | 0.799 | 25/25 | 0 | 24 | 2.66 ± 0.37 (2.56) | 6.84 ± 3.64 (5.57) | 2.17 ± 0.41 (2.34) | 4.94 ± 1.15 (5.29) | 1.95 ± 0.69 (2.23) |
| back/right | p | 0.821 | 25/25 | 0 | 24 | 2.58 ± 0.33 (2.50) | 5.62 ± 3.70 (5.44) | 2.24 ± 0.41 (2.38) | 5.06 ± 1.13 (5.64) | 2.02 ± 0.68 (2.20) |
| right/left | p | 0.867 | 25/25 | 0 | 25 | 1.97 ± 0.34 (1.90) | 4.83 ± 3.32 (3.77) | 2.23 ± 0.52 (2.32) | 5.02 ± 1.33 (5.36) | 2.03 ± 0.85 (2.04) |
| right/right | p | 0.863 | 25/25 | 0 | 25 | 1.70 ± 0.34 (1.74) | 4.39 ± 3.50 (2.86) | 2.11 ± 0.47 (2.08) | 4.67 ± 1.20 (4.90) | 1.80 ± 0.73 (1.76) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.887 | 5.5 | 5.89 | 2.50 |
| p | normal | 0.828 | 4.8 | 4.03 | 1.45 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.787 | 0.22 | 2.11 ± 0.66 (1.97) | 3.34 | 1.05 |
| p | medium | 16 | 0.906 | 0.87 | 1.09 ± 0.13 (1.09) | 3.56 | 1.19 |
| p | strong | 126 | 0.884 | 0.78 | - | 5.88 | 2.50 |

## Notes

- p: score 0.858, 200/200 kicked, 0 fell; worst sector back (0.810).
