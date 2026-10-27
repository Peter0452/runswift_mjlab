# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.861** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.88 ± 0.58 (1.80) |
| Direction error [°] | 4.29 ± 3.22 (3.46) |
| Avg ball speed [m/s] | 2.06 ± 0.37 (2.11) |
| Peak ball speed [m/s] | 5.13 ± 1.02 (5.50) |
| Distance [m] | 2.26 ± 0.68 (2.34) |
| Path length [m] | 2.27 ± 0.68 (2.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.883 | 50/50 | 0 | 50 | 1.29 ± 0.25 (1.32) | 3.85 ± 2.69 (2.80) | 2.03 ± 0.37 (2.06) | 5.05 ± 1.05 (5.37) | 2.18 ± 0.69 (2.22) |
| left | p | 0.874 | 50/50 | 0 | 50 | 1.81 ± 0.37 (1.75) | 4.53 ± 3.13 (3.88) | 2.05 ± 0.32 (2.08) | 5.11 ± 0.96 (5.43) | 2.24 ± 0.64 (2.34) |
| back | p | 0.820 | 50/50 | 0 | 48 | 2.61 ± 0.35 (2.55) | 5.45 ± 3.92 (4.72) | 2.20 ± 0.37 (2.25) | 5.42 ± 1.00 (5.82) | 2.50 ± 0.68 (2.71) |
| right | p | 0.870 | 50/50 | 0 | 50 | 1.82 ± 0.38 (1.80) | 3.35 ± 2.57 (2.65) | 1.98 ± 0.38 (1.97) | 4.94 ± 1.00 (5.40) | 2.12 ± 0.65 (2.19) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 99 | 1.87 ± 0.58 (1.79) | 4.61 ± 3.45 (3.77) | 2.07 ± 0.38 (2.13) | 5.15 ± 1.00 (5.52) | 2.28 ± 0.68 (2.31) |
| right | p | 0.868 | 100/100 | 0 | 99 | 1.89 ± 0.59 (1.86) | 3.98 ± 2.93 (3.22) | 2.05 ± 0.36 (2.10) | 5.11 ± 1.03 (5.45) | 2.24 ± 0.68 (2.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.876 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.30) | 4.00 ± 3.03 (2.84) | 2.02 ± 0.39 (2.06) | 5.00 ± 1.03 (5.41) | 2.16 ± 0.68 (2.19) |
| forward/right | p | 0.889 | 25/25 | 0 | 25 | 1.31 ± 0.25 (1.32) | 3.70 ± 2.28 (2.27) | 2.03 ± 0.36 (2.17) | 5.09 ± 1.07 (5.33) | 2.20 ± 0.70 (2.37) |
| left/left | p | 0.867 | 25/25 | 0 | 25 | 1.69 ± 0.33 (1.64) | 5.58 ± 3.36 (4.59) | 2.09 ± 0.32 (2.13) | 5.16 ± 0.95 (5.45) | 2.29 ± 0.64 (2.40) |
| left/right | p | 0.880 | 25/25 | 0 | 25 | 1.93 ± 0.37 (1.98) | 3.48 ± 2.46 (3.19) | 2.00 ± 0.32 (2.01) | 5.06 ± 0.96 (5.32) | 2.19 ± 0.63 (2.21) |
| back/left | p | 0.809 | 25/25 | 0 | 24 | 2.60 ± 0.29 (2.60) | 6.37 ± 4.06 (5.82) | 2.19 ± 0.41 (2.24) | 5.40 ± 0.98 (5.80) | 2.50 ± 0.70 (2.67) |
| back/right | p | 0.830 | 25/25 | 0 | 24 | 2.62 ± 0.39 (2.50) | 4.53 ± 3.53 (3.33) | 2.21 ± 0.33 (2.27) | 5.43 ± 1.01 (5.98) | 2.51 ± 0.67 (2.74) |
| right/left | p | 0.865 | 25/25 | 0 | 25 | 1.93 ± 0.37 (1.88) | 2.49 ± 1.34 (2.26) | 2.00 ± 0.38 (1.94) | 5.04 ± 0.99 (5.43) | 2.18 ± 0.66 (2.25) |
| right/right | p | 0.874 | 25/25 | 0 | 25 | 1.71 ± 0.35 (1.70) | 4.21 ± 3.15 (3.47) | 1.97 ± 0.37 (2.03) | 4.85 ± 0.99 (5.37) | 2.06 ± 0.63 (2.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.894 | 4.6 | 5.85 | 2.69 |
| p | normal | 0.828 | 4.0 | 4.41 | 1.83 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.771 | 0.11 | 2.50 ± 0.79 (2.36) | 3.88 | 1.48 |
| p | medium | 20 | 0.899 | 0.78 | 1.22 ± 0.15 (1.22) | 3.90 | 1.53 |
| p | strong | 126 | 0.894 | 0.78 | - | 5.86 | 2.71 |

## Notes

- p: score 0.861, 200/200 kicked, 0 fell; worst sector back (0.820).
