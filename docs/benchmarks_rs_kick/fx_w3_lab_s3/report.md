# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.858** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.61 ± 0.53 (1.57) |
| Direction error [°] | 5.84 ± 11.99 (4.54) |
| Avg ball speed [m/s] | 1.93 ± 0.49 (2.06) |
| Peak ball speed [m/s] | 4.16 ± 1.12 (4.52) |
| Distance [m] | 1.62 ± 0.68 (1.80) |
| Path length [m] | 1.62 ± 0.69 (1.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.870 | 50/50 | 0 | 48 | 1.05 ± 0.22 (1.05) | 5.11 ± 3.94 (3.76) | 1.70 ± 0.49 (1.86) | 3.70 ± 1.08 (4.03) | 1.30 ± 0.64 (1.40) |
| left | p | 0.867 | 50/50 | 0 | 50 | 1.56 ± 0.33 (1.56) | 4.84 ± 3.04 (4.89) | 2.04 ± 0.42 (2.17) | 4.41 ± 0.99 (4.81) | 1.76 ± 0.61 (1.96) |
| back | p | 0.842 | 50/50 | 0 | 49 | 2.28 ± 0.32 (2.27) | 8.32 ± 23.09 (4.65) | 2.04 ± 0.48 (2.30) | 4.33 ± 1.15 (4.99) | 1.76 ± 0.72 (2.01) |
| right | p | 0.854 | 50/50 | 0 | 50 | 1.56 ± 0.32 (1.59) | 5.07 ± 3.00 (4.71) | 1.96 ± 0.47 (2.14) | 4.21 ± 1.10 (4.82) | 1.64 ± 0.66 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.862 | 100/100 | 0 | 99 | 1.60 ± 0.51 (1.57) | 6.31 ± 16.59 (4.31) | 1.94 ± 0.50 (2.10) | 4.17 ± 1.14 (4.60) | 1.62 ± 0.70 (1.84) |
| right | p | 0.855 | 100/100 | 0 | 98 | 1.62 ± 0.55 (1.58) | 5.36 ± 3.45 (5.05) | 1.93 ± 0.48 (2.05) | 4.16 ± 1.09 (4.45) | 1.61 ± 0.67 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.880 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.04) | 4.06 ± 2.90 (3.41) | 1.69 ± 0.49 (1.75) | 3.70 ± 1.10 (3.67) | 1.31 ± 0.66 (1.31) |
| forward/right | p | 0.860 | 25/25 | 0 | 23 | 1.04 ± 0.22 (1.10) | 6.16 ± 4.52 (4.59) | 1.70 ± 0.49 (1.94) | 3.71 ± 1.07 (4.19) | 1.30 ± 0.62 (1.47) |
| left/left | p | 0.864 | 25/25 | 0 | 25 | 1.44 ± 0.29 (1.50) | 5.08 ± 3.20 (4.71) | 2.04 ± 0.41 (2.17) | 4.40 ± 0.96 (4.64) | 1.74 ± 0.57 (1.99) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.68 ± 0.32 (1.64) | 4.61 ± 2.84 (5.26) | 2.03 ± 0.43 (2.17) | 4.42 ± 1.02 (4.94) | 1.77 ± 0.65 (1.93) |
| back/left | p | 0.849 | 25/25 | 0 | 24 | 2.25 ± 0.28 (2.24) | 11.37 ± 32.25 (4.40) | 2.02 ± 0.53 (2.32) | 4.30 ± 1.25 (5.00) | 1.75 ± 0.76 (2.02) |
| back/right | p | 0.836 | 25/25 | 0 | 25 | 2.31 ± 0.35 (2.30) | 5.27 ± 2.76 (5.12) | 2.06 ± 0.43 (2.30) | 4.35 ± 1.03 (4.95) | 1.77 ± 0.67 (2.00) |
| right/left | p | 0.856 | 25/25 | 0 | 25 | 1.67 ± 0.28 (1.70) | 4.74 ± 2.73 (4.46) | 1.99 ± 0.46 (2.27) | 4.28 ± 1.11 (4.96) | 1.70 ± 0.68 (2.03) |
| right/right | p | 0.852 | 25/25 | 0 | 25 | 1.46 ± 0.32 (1.38) | 5.40 ± 3.22 (4.95) | 1.94 ± 0.48 (2.07) | 4.15 ± 1.10 (4.56) | 1.59 ± 0.64 (1.79) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.877 | 6.4 | 4.89 | 2.05 |
| p | normal | 0.840 | 5.3 | 3.44 | 1.18 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.803 | 0.33 | 1.84 ± 0.59 (1.78) | 2.91 | 0.86 |
| p | medium | 18 | 0.905 | 0.85 | 0.93 ± 0.18 (0.94) | 2.97 | 0.89 |
| p | strong | 124 | 0.878 | 0.66 | - | 4.93 | 2.08 |

## Notes

- p: score 0.858, 200/200 kicked, 0 fell; worst sector back (0.842).
