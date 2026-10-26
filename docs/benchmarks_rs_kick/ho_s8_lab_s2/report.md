# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.56 ± 0.53 (1.54) |
| Direction error [°] | 5.68 ± 11.26 (4.19) |
| Avg ball speed [m/s] | 2.09 ± 0.38 (2.10) |
| Peak ball speed [m/s] | 4.48 ± 0.88 (4.66) |
| Distance [m] | 1.88 ± 0.57 (1.94) |
| Path length [m] | 1.89 ± 0.57 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.850 | 50/50 | 0 | 49 | 1.02 ± 0.26 (1.01) | 5.05 ± 3.51 (4.12) | 1.93 ± 0.36 (1.85) | 4.16 ± 0.80 (3.97) | 1.65 ± 0.54 (1.45) |
| left | p | 0.853 | 50/50 | 0 | 50 | 1.48 ± 0.36 (1.52) | 5.13 ± 3.23 (4.26) | 2.09 ± 0.32 (2.09) | 4.48 ± 0.78 (4.64) | 1.87 ± 0.51 (1.98) |
| back | p | 0.843 | 50/50 | 0 | 49 | 2.23 ± 0.30 (2.19) | 7.40 ± 21.65 (4.15) | 2.20 ± 0.43 (2.31) | 4.71 ± 1.00 (5.09) | 2.06 ± 0.59 (2.28) |
| right | p | 0.863 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.56) | 5.15 ± 3.40 (4.81) | 2.14 ± 0.33 (2.22) | 4.57 ± 0.81 (4.90) | 1.94 ± 0.54 (2.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.861 | 100/100 | 0 | 99 | 1.56 ± 0.53 (1.56) | 4.70 ± 2.90 (4.17) | 2.11 ± 0.35 (2.21) | 4.54 ± 0.82 (4.82) | 1.92 ± 0.56 (2.01) |
| right | p | 0.844 | 100/100 | 0 | 99 | 1.56 ± 0.54 (1.53) | 6.67 ± 15.60 (4.35) | 2.07 ± 0.40 (2.05) | 4.41 ± 0.92 (4.36) | 1.84 ± 0.58 (1.77) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 24 | 1.02 ± 0.25 (1.02) | 4.94 ± 3.44 (4.22) | 1.91 ± 0.33 (1.84) | 4.12 ± 0.78 (3.91) | 1.63 ± 0.54 (1.44) |
| forward/right | p | 0.854 | 25/25 | 0 | 25 | 1.03 ± 0.26 (0.98) | 5.16 ± 3.57 (3.71) | 1.96 ± 0.38 (1.88) | 4.20 ± 0.82 (4.17) | 1.66 ± 0.55 (1.46) |
| left/left | p | 0.862 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.38) | 4.94 ± 2.92 (3.92) | 2.05 ± 0.31 (2.08) | 4.41 ± 0.75 (4.62) | 1.82 ± 0.48 (1.95) |
| left/right | p | 0.844 | 25/25 | 0 | 25 | 1.57 ± 0.36 (1.54) | 5.32 ± 3.50 (4.60) | 2.13 ± 0.32 (2.10) | 4.55 ± 0.80 (4.68) | 1.93 ± 0.54 (2.02) |
| back/left | p | 0.865 | 25/25 | 0 | 25 | 2.24 ± 0.27 (2.26) | 3.97 ± 2.35 (3.70) | 2.27 ± 0.30 (2.36) | 4.92 ± 0.73 (5.24) | 2.17 ± 0.50 (2.41) |
| back/right | p | 0.821 | 25/25 | 0 | 24 | 2.23 ± 0.32 (2.12) | 10.83 ± 30.15 (4.81) | 2.13 ± 0.52 (2.28) | 4.50 ± 1.17 (4.96) | 1.95 ± 0.66 (2.25) |
| right/left | p | 0.871 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.64) | 4.94 ± 2.64 (5.08) | 2.21 ± 0.32 (2.26) | 4.73 ± 0.77 (5.03) | 2.04 ± 0.54 (2.19) |
| right/right | p | 0.856 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.48) | 5.36 ± 4.01 (4.19) | 2.07 ± 0.33 (2.12) | 4.41 ± 0.81 (4.71) | 1.83 ± 0.51 (1.91) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.876 | 6.5 | 4.93 | 2.17 |
| p | normal | 0.829 | 4.8 | 4.02 | 1.58 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.787 | 0.19 | 2.20 ± 0.68 (2.09) | 3.62 | 1.32 |
| p | medium | 15 | 0.910 | 0.82 | 1.12 ± 0.16 (1.14) | 3.66 | 1.33 |
| p | strong | 125 | 0.877 | 0.67 | - | 4.99 | 2.21 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector back (0.843).
