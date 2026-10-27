# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.87 ± 0.55 (1.80) |
| Direction error [°] | 4.76 ± 3.65 (3.86) |
| Avg ball speed [m/s] | 2.26 ± 0.39 (2.39) |
| Peak ball speed [m/s] | 5.02 ± 1.06 (5.57) |
| Distance [m] | 2.10 ± 0.66 (2.29) |
| Path length [m] | 2.11 ± 0.66 (2.31) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.867 | 50/50 | 0 | 50 | 1.30 ± 0.26 (1.32) | 4.04 ± 3.16 (2.53) | 2.15 ± 0.47 (2.16) | 4.75 ± 1.23 (4.96) | 1.93 ± 0.76 (1.88) |
| left | p | 0.883 | 50/50 | 0 | 49 | 1.81 ± 0.36 (1.81) | 4.90 ± 3.88 (4.11) | 2.38 ± 0.34 (2.43) | 5.30 ± 0.95 (5.74) | 2.28 ± 0.60 (2.47) |
| back | p | 0.814 | 50/50 | 0 | 49 | 2.57 ± 0.32 (2.51) | 5.73 ± 3.69 (5.44) | 2.31 ± 0.32 (2.41) | 5.12 ± 0.95 (5.67) | 2.19 ± 0.60 (2.42) |
| right | p | 0.861 | 50/50 | 0 | 49 | 1.82 ± 0.33 (1.79) | 4.38 ± 3.59 (3.21) | 2.20 ± 0.35 (2.27) | 4.89 ± 1.01 (5.43) | 1.99 ± 0.60 (2.19) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 98 | 1.88 ± 0.57 (1.82) | 5.17 ± 4.02 (4.09) | 2.25 ± 0.36 (2.39) | 4.99 ± 1.03 (5.52) | 2.08 ± 0.64 (2.31) |
| right | p | 0.860 | 100/100 | 0 | 99 | 1.86 ± 0.54 (1.75) | 4.35 ± 3.19 (3.71) | 2.27 ± 0.41 (2.39) | 5.04 ± 1.10 (5.67) | 2.11 ± 0.68 (2.27) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.864 | 25/25 | 0 | 25 | 1.31 ± 0.26 (1.34) | 4.68 ± 3.68 (2.91) | 2.15 ± 0.45 (2.15) | 4.73 ± 1.20 (5.15) | 1.91 ± 0.75 (1.90) |
| forward/right | p | 0.870 | 25/25 | 0 | 25 | 1.29 ± 0.26 (1.32) | 3.40 ± 2.37 (2.31) | 2.16 ± 0.49 (2.17) | 4.77 ± 1.26 (4.77) | 1.95 ± 0.78 (1.87) |
| left/left | p | 0.873 | 25/25 | 0 | 24 | 1.68 ± 0.36 (1.78) | 5.59 ± 4.75 (4.19) | 2.31 ± 0.32 (2.40) | 5.11 ± 0.93 (5.49) | 2.17 ± 0.57 (2.40) |
| left/right | p | 0.893 | 25/25 | 0 | 25 | 1.93 ± 0.31 (1.96) | 4.20 ± 2.58 (3.85) | 2.44 ± 0.35 (2.48) | 5.49 ± 0.94 (5.90) | 2.39 ± 0.62 (2.63) |
| back/left | p | 0.811 | 25/25 | 0 | 25 | 2.60 ± 0.35 (2.52) | 5.57 ± 3.42 (4.92) | 2.33 ± 0.26 (2.37) | 5.17 ± 0.87 (5.56) | 2.23 ± 0.57 (2.49) |
| back/right | p | 0.816 | 25/25 | 0 | 24 | 2.53 ± 0.29 (2.50) | 5.89 ± 3.94 (5.64) | 2.29 ± 0.36 (2.44) | 5.07 ± 1.01 (5.69) | 2.15 ± 0.62 (2.40) |
| right/left | p | 0.861 | 25/25 | 0 | 24 | 1.94 ± 0.29 (1.92) | 4.83 ± 4.00 (3.59) | 2.22 ± 0.36 (2.43) | 4.94 ± 1.02 (5.47) | 2.03 ± 0.60 (2.26) |
| right/right | p | 0.861 | 25/25 | 0 | 25 | 1.70 ± 0.33 (1.72) | 3.92 ± 3.07 (2.40) | 2.19 ± 0.34 (2.25) | 4.84 ± 1.00 (5.34) | 1.96 ± 0.60 (2.05) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.897 | 4.5 | 5.79 | 2.55 |
| p | normal | 0.815 | 5.0 | 4.24 | 1.64 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.763 | 0.13 | 2.29 ± 0.68 (2.13) | 3.65 | 1.29 |
| p | medium | 16 | 0.891 | 0.79 | 1.19 ± 0.15 (1.19) | 3.86 | 1.44 |
| p | strong | 126 | 0.895 | 0.77 | - | 5.79 | 2.55 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.814).
