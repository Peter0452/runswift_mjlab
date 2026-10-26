# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s3_ctl7_n7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.839** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.55 (1.52) |
| Direction error [°] | 5.91 ± 4.07 (5.16) |
| Avg ball speed [m/s] | 2.04 ± 0.37 (2.05) |
| Peak ball speed [m/s] | 4.39 ± 0.84 (4.43) |
| Distance [m] | 1.80 ± 0.54 (1.75) |
| Path length [m] | 1.81 ± 0.55 (1.76) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.839 | 50/50 | 0 | 50 | 1.01 ± 0.25 (1.01) | 5.85 ± 3.80 (5.88) | 1.87 ± 0.34 (1.82) | 4.05 ± 0.77 (3.87) | 1.54 ± 0.52 (1.38) |
| left | p | 0.841 | 50/50 | 0 | 49 | 1.48 ± 0.35 (1.47) | 6.19 ± 4.02 (5.31) | 2.09 ± 0.32 (2.06) | 4.46 ± 0.76 (4.47) | 1.86 ± 0.52 (1.80) |
| back | p | 0.821 | 50/50 | 0 | 49 | 2.29 ± 0.30 (2.27) | 6.14 ± 4.84 (5.12) | 2.14 ± 0.40 (2.20) | 4.60 ± 0.92 (4.81) | 1.97 ± 0.52 (2.08) |
| right | p | 0.856 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.54) | 5.48 ± 3.45 (4.51) | 2.07 ± 0.34 (2.18) | 4.43 ± 0.81 (4.71) | 1.82 ± 0.51 (1.87) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 100 | 1.57 ± 0.55 (1.55) | 5.76 ± 3.38 (5.25) | 2.09 ± 0.34 (2.08) | 4.48 ± 0.80 (4.58) | 1.86 ± 0.54 (1.94) |
| right | p | 0.832 | 100/100 | 0 | 98 | 1.57 ± 0.56 (1.51) | 6.07 ± 4.65 (5.04) | 2.00 ± 0.39 (1.99) | 4.29 ± 0.88 (4.24) | 1.74 ± 0.54 (1.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 25 | 1.01 ± 0.24 (1.02) | 6.25 ± 3.88 (6.65) | 1.86 ± 0.34 (1.75) | 4.00 ± 0.78 (3.81) | 1.53 ± 0.53 (1.36) |
| forward/right | p | 0.847 | 25/25 | 0 | 25 | 1.02 ± 0.25 (0.98) | 5.46 ± 3.67 (4.53) | 1.87 ± 0.34 (1.84) | 4.09 ± 0.77 (3.89) | 1.56 ± 0.52 (1.40) |
| left/left | p | 0.842 | 25/25 | 0 | 25 | 1.39 ± 0.34 (1.36) | 6.61 ± 3.59 (6.76) | 2.07 ± 0.32 (2.06) | 4.40 ± 0.73 (4.41) | 1.81 ± 0.48 (1.74) |
| left/right | p | 0.840 | 25/25 | 0 | 24 | 1.56 ± 0.34 (1.50) | 5.77 ± 4.37 (4.51) | 2.10 ± 0.33 (2.08) | 4.52 ± 0.79 (4.60) | 1.90 ± 0.56 (1.86) |
| back/left | p | 0.844 | 25/25 | 0 | 25 | 2.27 ± 0.29 (2.26) | 5.45 ± 2.95 (5.11) | 2.22 ± 0.30 (2.34) | 4.82 ± 0.71 (5.07) | 2.10 ± 0.49 (2.20) |
| back/right | p | 0.799 | 25/25 | 0 | 24 | 2.30 ± 0.30 (2.28) | 6.83 ± 6.09 (5.83) | 2.06 ± 0.47 (2.09) | 4.38 ± 1.05 (4.26) | 1.84 ± 0.52 (1.83) |
| right/left | p | 0.870 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.62) | 4.73 ± 2.64 (3.80) | 2.20 ± 0.29 (2.26) | 4.68 ± 0.71 (4.84) | 1.99 ± 0.48 (2.15) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.46) | 6.22 ± 3.97 (6.91) | 1.95 ± 0.34 (1.95) | 4.18 ± 0.81 (4.21) | 1.66 ± 0.50 (1.70) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.868 | 5.7 | 4.83 | 2.07 |
| p | normal | 0.811 | 6.2 | 3.94 | 1.53 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.777 | 0.19 | 2.22 ± 0.69 (2.12) | 3.65 | 1.32 |
| p | medium | 15 | 0.868 | 0.76 | 1.06 ± 0.32 (1.15) | 3.41 | 1.23 |
| p | strong | 125 | 0.866 | 0.65 | - | 4.86 | 2.10 |

## Notes

- p: score 0.839, 200/200 kicked, 0 fell; worst sector back (0.821).
