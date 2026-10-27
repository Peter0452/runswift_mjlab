# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.859** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.60 ± 0.54 (1.55) |
| Direction error [°] | 4.85 ± 3.14 (4.24) |
| Avg ball speed [m/s] | 1.94 ± 0.43 (2.07) |
| Peak ball speed [m/s] | 4.23 ± 1.02 (4.58) |
| Distance [m] | 1.62 ± 0.64 (1.76) |
| Path length [m] | 1.63 ± 0.64 (1.77) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.868 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.05) | 4.72 ± 3.61 (3.86) | 1.72 ± 0.42 (1.78) | 3.78 ± 0.96 (3.97) | 1.33 ± 0.58 (1.39) |
| left | p | 0.869 | 50/50 | 0 | 49 | 1.54 ± 0.33 (1.53) | 5.08 ± 3.21 (4.09) | 2.01 ± 0.41 (2.16) | 4.41 ± 1.01 (4.86) | 1.73 ± 0.62 (1.94) |
| back | p | 0.843 | 50/50 | 0 | 50 | 2.28 ± 0.33 (2.25) | 5.24 ± 2.86 (5.44) | 2.06 ± 0.39 (2.28) | 4.47 ± 0.97 (5.06) | 1.80 ± 0.63 (1.97) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.54 ± 0.32 (1.57) | 4.36 ± 2.75 (4.05) | 1.95 ± 0.41 (2.12) | 4.25 ± 0.98 (4.79) | 1.64 ± 0.61 (1.80) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.861 | 100/100 | 0 | 99 | 1.60 ± 0.53 (1.57) | 4.75 ± 3.10 (4.33) | 1.95 ± 0.42 (2.08) | 4.25 ± 0.99 (4.65) | 1.63 ± 0.63 (1.80) |
| right | p | 0.858 | 100/100 | 0 | 100 | 1.60 ± 0.54 (1.53) | 4.96 ± 3.18 (4.06) | 1.93 ± 0.44 (2.04) | 4.21 ± 1.04 (4.56) | 1.61 ± 0.64 (1.63) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.876 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.04) | 4.03 ± 2.99 (2.48) | 1.74 ± 0.43 (1.76) | 3.83 ± 0.96 (4.03) | 1.35 ± 0.60 (1.39) |
| forward/right | p | 0.860 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.10) | 5.41 ± 4.02 (4.12) | 1.70 ± 0.41 (1.79) | 3.74 ± 0.95 (3.92) | 1.30 ± 0.55 (1.39) |
| left/left | p | 0.864 | 25/25 | 0 | 24 | 1.45 ± 0.30 (1.48) | 5.20 ± 3.89 (4.01) | 2.03 ± 0.38 (2.16) | 4.46 ± 0.93 (4.87) | 1.75 ± 0.57 (1.94) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.64 ± 0.33 (1.60) | 4.97 ± 2.33 (5.65) | 1.98 ± 0.44 (2.16) | 4.36 ± 1.08 (4.74) | 1.71 ± 0.67 (1.94) |
| back/left | p | 0.845 | 25/25 | 0 | 25 | 2.28 ± 0.34 (2.22) | 5.62 ± 2.95 (6.07) | 2.07 ± 0.39 (2.24) | 4.48 ± 0.96 (4.86) | 1.81 ± 0.64 (1.97) |
| back/right | p | 0.840 | 25/25 | 0 | 25 | 2.28 ± 0.32 (2.32) | 4.86 ± 2.71 (5.26) | 2.06 ± 0.39 (2.28) | 4.47 ± 0.98 (5.12) | 1.79 ± 0.63 (2.00) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.64 ± 0.28 (1.68) | 4.13 ± 1.96 (4.31) | 1.94 ± 0.40 (2.13) | 4.24 ± 0.98 (4.79) | 1.62 ± 0.61 (1.79) |
| right/right | p | 0.858 | 25/25 | 0 | 25 | 1.45 ± 0.32 (1.38) | 4.59 ± 3.34 (3.43) | 1.97 ± 0.42 (2.12) | 4.26 ± 0.98 (4.80) | 1.65 ± 0.61 (1.84) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.879 | 4.8 | 4.94 | 2.04 |
| p | normal | 0.840 | 4.9 | 3.52 | 1.21 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.797 | 0.28 | 1.94 ± 0.58 (1.88) | 3.06 | 0.93 |
| p | medium | 18 | 0.918 | 0.87 | 0.96 ± 0.16 (1.01) | 3.07 | 0.93 |
| p | strong | 124 | 0.880 | 0.66 | - | 4.94 | 2.05 |

## Notes

- p: score 0.859, 200/200 kicked, 0 fell; worst sector back (0.843).
