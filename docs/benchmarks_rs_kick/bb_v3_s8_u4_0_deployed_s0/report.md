# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v3_s8_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.87 ± 0.57 (1.80) |
| Direction error [°] | 5.09 ± 4.05 (4.51) |
| Avg ball speed [m/s] | 2.23 ± 0.40 (2.30) |
| Peak ball speed [m/s] | 4.98 ± 1.09 (5.43) |
| Distance [m] | 2.06 ± 0.66 (2.16) |
| Path length [m] | 2.07 ± 0.66 (2.16) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.868 | 50/50 | 0 | 49 | 1.30 ± 0.26 (1.30) | 3.81 ± 3.16 (2.51) | 2.20 ± 0.45 (2.24) | 4.86 ± 1.17 (5.16) | 2.00 ± 0.75 (1.95) |
| left | p | 0.865 | 50/50 | 0 | 46 | 1.80 ± 0.36 (1.83) | 6.01 ± 5.60 (4.47) | 2.21 ± 0.43 (2.26) | 5.03 ± 1.14 (5.34) | 2.08 ± 0.63 (2.22) |
| back | p | 0.795 | 49/50 | 0 | 48 | 2.58 ± 0.34 (2.52) | 5.64 ± 3.13 (5.58) | 2.26 ± 0.31 (2.33) | 5.05 ± 0.94 (5.57) | 2.09 ± 0.58 (2.22) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.82 ± 0.36 (1.79) | 4.90 ± 3.38 (4.65) | 2.24 ± 0.41 (2.26) | 4.97 ± 1.08 (5.45) | 2.05 ± 0.67 (2.15) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 99/100 | 0 | 96 | 1.87 ± 0.58 (1.82) | 5.08 ± 3.82 (4.32) | 2.24 ± 0.36 (2.26) | 4.99 ± 1.01 (5.37) | 2.07 ± 0.63 (2.15) |
| right | p | 0.850 | 100/100 | 0 | 97 | 1.87 ± 0.55 (1.80) | 5.10 ± 4.26 (4.74) | 2.21 ± 0.44 (2.31) | 4.96 ± 1.17 (5.49) | 2.04 ± 0.69 (2.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.877 | 25/25 | 0 | 25 | 1.30 ± 0.25 (1.30) | 3.31 ± 2.86 (2.36) | 2.23 ± 0.40 (2.15) | 4.88 ± 1.11 (5.09) | 2.02 ± 0.71 (1.89) |
| forward/right | p | 0.859 | 25/25 | 0 | 24 | 1.30 ± 0.27 (1.30) | 4.32 ± 3.36 (2.96) | 2.18 ± 0.49 (2.40) | 4.84 ± 1.23 (5.56) | 1.99 ± 0.78 (2.12) |
| left/left | p | 0.864 | 25/25 | 0 | 23 | 1.68 ± 0.37 (1.76) | 6.17 ± 4.55 (4.62) | 2.20 ± 0.29 (2.18) | 4.96 ± 0.87 (5.37) | 2.03 ± 0.53 (2.12) |
| left/right | p | 0.866 | 25/25 | 0 | 23 | 1.91 ± 0.32 (1.98) | 5.85 ± 6.47 (3.87) | 2.22 ± 0.54 (2.31) | 5.10 ± 1.34 (5.31) | 2.13 ± 0.72 (2.22) |
| back/left | p | 0.771 | 24/25 | 0 | 23 | 2.62 ± 0.35 (2.56) | 6.16 ± 3.57 (5.94) | 2.25 ± 0.33 (2.30) | 5.02 ± 0.99 (5.33) | 2.09 ± 0.64 (2.18) |
| back/right | p | 0.819 | 25/25 | 0 | 25 | 2.54 ± 0.33 (2.48) | 5.14 ± 2.55 (5.50) | 2.27 ± 0.28 (2.33) | 5.08 ± 0.90 (5.58) | 2.09 ± 0.51 (2.23) |
| right/left | p | 0.861 | 25/25 | 0 | 25 | 1.93 ± 0.34 (1.82) | 4.71 ± 3.33 (4.06) | 2.30 ± 0.40 (2.33) | 5.12 ± 1.03 (5.59) | 2.13 ± 0.64 (2.29) |
| right/right | p | 0.855 | 25/25 | 0 | 25 | 1.70 ± 0.34 (1.74) | 5.09 ± 3.42 (4.97) | 2.18 ± 0.41 (2.18) | 4.81 ± 1.11 (5.12) | 1.97 ± 0.69 (2.00) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.879 | 5.3 | 5.77 | 2.51 |
| p | normal | 0.814 | 4.9 | 4.19 | 1.61 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.770 | 0.12 | 2.33 ± 0.68 (2.12) | 3.71 | 1.32 |
| p | medium | 16 | 0.868 | 0.77 | 1.11 ± 0.30 (1.14) | 3.58 | 1.32 |
| p | strong | 126 | 0.879 | 0.77 | - | 5.74 | 2.49 |

## Notes

- p: score 0.846, 199/200 kicked, 0 fell; worst sector back (0.795).
