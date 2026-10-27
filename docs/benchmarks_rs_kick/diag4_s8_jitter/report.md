# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.58 ± 0.53 (1.51) |
| Direction error [°] | 4.91 ± 3.07 (4.62) |
| Avg ball speed [m/s] | 1.95 ± 0.34 (1.99) |
| Peak ball speed [m/s] | 4.21 ± 0.81 (4.41) |
| Distance [m] | 1.60 ± 0.50 (1.62) |
| Path length [m] | 1.61 ± 0.50 (1.63) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.853 | 50/50 | 0 | 50 | 1.04 ± 0.23 (1.06) | 3.97 ± 2.75 (2.81) | 1.73 ± 0.36 (1.64) | 3.72 ± 0.80 (3.49) | 1.28 ± 0.47 (1.19) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.53) | 5.59 ± 3.26 (5.51) | 2.02 ± 0.28 (2.05) | 4.39 ± 0.72 (4.55) | 1.72 ± 0.45 (1.79) |
| back | p | 0.847 | 50/50 | 0 | 50 | 2.26 ± 0.25 (2.22) | 4.76 ± 2.56 (4.72) | 2.09 ± 0.27 (2.16) | 4.52 ± 0.71 (4.84) | 1.81 ± 0.45 (1.96) |
| right | p | 0.845 | 50/50 | 0 | 50 | 1.51 ± 0.33 (1.48) | 5.35 ± 3.39 (5.03) | 1.95 ± 0.32 (2.02) | 4.21 ± 0.76 (4.48) | 1.60 ± 0.46 (1.61) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 100 | 1.59 ± 0.53 (1.53) | 4.89 ± 3.03 (4.46) | 1.97 ± 0.33 (1.99) | 4.25 ± 0.80 (4.41) | 1.63 ± 0.51 (1.64) |
| right | p | 0.850 | 100/100 | 0 | 100 | 1.58 ± 0.52 (1.49) | 4.94 ± 3.12 (4.71) | 1.93 ± 0.34 (1.99) | 4.17 ± 0.81 (4.42) | 1.57 ± 0.49 (1.55) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.859 | 25/25 | 0 | 25 | 1.05 ± 0.24 (1.10) | 4.27 ± 3.11 (3.09) | 1.74 ± 0.38 (1.72) | 3.77 ± 0.87 (3.54) | 1.31 ± 0.51 (1.26) |
| forward/right | p | 0.846 | 25/25 | 0 | 25 | 1.02 ± 0.22 (1.04) | 3.66 ± 2.29 (2.71) | 1.71 ± 0.34 (1.60) | 3.67 ± 0.73 (3.39) | 1.24 ± 0.42 (1.09) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.51 ± 3.28 (4.97) | 1.94 ± 0.26 (1.94) | 4.21 ± 0.68 (4.27) | 1.59 ± 0.40 (1.65) |
| left/right | p | 0.865 | 25/25 | 0 | 25 | 1.64 ± 0.32 (1.64) | 5.66 ± 3.25 (5.96) | 2.10 ± 0.29 (2.17) | 4.56 ± 0.73 (4.83) | 1.84 ± 0.46 (1.87) |
| back/left | p | 0.850 | 25/25 | 0 | 25 | 2.29 ± 0.26 (2.22) | 4.36 ± 2.19 (3.92) | 2.15 ± 0.23 (2.20) | 4.63 ± 0.65 (4.94) | 1.90 ± 0.45 (1.99) |
| back/right | p | 0.845 | 25/25 | 0 | 25 | 2.23 ± 0.25 (2.22) | 5.15 ± 2.82 (5.30) | 2.03 ± 0.29 (2.12) | 4.40 ± 0.75 (4.70) | 1.72 ± 0.43 (1.82) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.58) | 5.42 ± 3.18 (5.38) | 2.03 ± 0.30 (2.03) | 4.38 ± 0.74 (4.54) | 1.71 ± 0.46 (1.63) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.44) | 5.27 ± 3.58 (4.68) | 1.87 ± 0.31 (1.96) | 4.04 ± 0.75 (4.10) | 1.50 ± 0.43 (1.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.872 | 4.7 | 4.64 | 1.84 |
| p | normal | 0.831 | 5.1 | 3.78 | 1.36 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.789 | 0.22 | 2.10 ± 0.65 (1.97) | 3.34 | 1.10 |
| p | medium | 16 | 0.906 | 0.86 | 1.08 ± 0.13 (1.10) | 3.52 | 1.21 |
| p | strong | 126 | 0.874 | 0.63 | - | 4.70 | 1.88 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector right (0.845).
