# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v3_s8_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.59 ± 0.52 (1.53) |
| Direction error [°] | 5.74 ± 4.09 (4.92) |
| Avg ball speed [m/s] | 2.15 ± 0.45 (2.29) |
| Peak ball speed [m/s] | 4.58 ± 1.05 (4.97) |
| Distance [m] | 2.01 ± 0.71 (2.23) |
| Path length [m] | 2.02 ± 0.71 (2.24) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.843 | 50/50 | 0 | 48 | 1.04 ± 0.23 (1.07) | 5.78 ± 3.81 (4.98) | 1.95 ± 0.40 (2.02) | 4.14 ± 0.95 (4.35) | 1.68 ± 0.61 (1.68) |
| left | p | 0.874 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.58) | 5.49 ± 3.74 (4.32) | 2.26 ± 0.39 (2.42) | 4.83 ± 0.91 (5.24) | 2.18 ± 0.63 (2.47) |
| back | p | 0.849 | 50/50 | 0 | 49 | 2.24 ± 0.26 (2.20) | 5.72 ± 5.09 (4.47) | 2.23 ± 0.51 (2.47) | 4.74 ± 1.16 (5.28) | 2.16 ± 0.77 (2.40) |
| right | p | 0.850 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.49) | 5.96 ± 3.52 (6.06) | 2.16 ± 0.44 (2.32) | 4.60 ± 1.05 (5.04) | 2.02 ± 0.72 (2.29) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.858 | 100/100 | 0 | 99 | 1.59 ± 0.53 (1.56) | 5.45 ± 3.38 (4.85) | 2.17 ± 0.42 (2.28) | 4.62 ± 1.01 (5.00) | 2.04 ± 0.70 (2.28) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.59 ± 0.52 (1.49) | 6.02 ± 4.67 (5.16) | 2.13 ± 0.49 (2.30) | 4.53 ± 1.10 (4.93) | 1.98 ± 0.72 (2.14) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.848 | 25/25 | 0 | 24 | 1.04 ± 0.23 (1.06) | 5.63 ± 3.74 (4.93) | 1.97 ± 0.36 (2.09) | 4.19 ± 0.90 (4.39) | 1.72 ± 0.60 (1.74) |
| forward/right | p | 0.839 | 25/25 | 0 | 24 | 1.04 ± 0.23 (1.08) | 5.92 ± 3.87 (5.32) | 1.93 ± 0.43 (1.83) | 4.09 ± 0.99 (4.00) | 1.64 ± 0.62 (1.63) |
| left/left | p | 0.868 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.50) | 5.75 ± 3.89 (4.59) | 2.21 ± 0.38 (2.37) | 4.71 ± 0.92 (5.17) | 2.09 ± 0.63 (2.42) |
| left/right | p | 0.880 | 25/25 | 0 | 25 | 1.64 ± 0.31 (1.66) | 5.23 ± 3.56 (4.12) | 2.32 ± 0.38 (2.51) | 4.94 ± 0.87 (5.43) | 2.27 ± 0.61 (2.52) |
| back/left | p | 0.860 | 25/25 | 0 | 25 | 2.25 ± 0.26 (2.18) | 4.56 ± 2.75 (3.83) | 2.29 ± 0.37 (2.45) | 4.86 ± 0.95 (5.34) | 2.22 ± 0.71 (2.47) |
| back/right | p | 0.839 | 25/25 | 0 | 24 | 2.24 ± 0.26 (2.24) | 6.87 ± 6.44 (5.53) | 2.18 ± 0.60 (2.48) | 4.62 ± 1.32 (5.26) | 2.11 ± 0.81 (2.39) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.63 ± 0.33 (1.58) | 5.87 ± 2.83 (5.91) | 2.21 ± 0.47 (2.40) | 4.73 ± 1.10 (5.28) | 2.13 ± 0.75 (2.41) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.46) | 6.05 ± 4.08 (6.21) | 2.10 ± 0.41 (2.17) | 4.47 ± 0.98 (4.89) | 1.92 ± 0.67 (2.08) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.882 | 5.4 | 5.29 | 2.48 |
| p | normal | 0.826 | 6.1 | 3.86 | 1.54 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.773 | 0.21 | 2.07 ± 0.70 (1.96) | 3.28 | 1.15 |
| p | medium | 16 | 0.905 | 0.87 | 1.05 ± 0.13 (1.09) | 3.42 | 1.23 |
| p | strong | 126 | 0.885 | 0.71 | - | 5.32 | 2.51 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector forward (0.843).
