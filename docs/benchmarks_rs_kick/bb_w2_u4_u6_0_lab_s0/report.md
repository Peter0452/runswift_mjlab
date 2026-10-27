# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w2_u4_u6.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.865** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.62 ± 0.57 (1.52) |
| Direction error [°] | 4.75 ± 9.22 (3.21) |
| Avg ball speed [m/s] | 1.81 ± 0.38 (1.90) |
| Peak ball speed [m/s] | 4.55 ± 0.99 (4.91) |
| Distance [m] | 1.88 ± 0.64 (1.96) |
| Path length [m] | 1.89 ± 0.64 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.844 | 50/50 | 0 | 48 | 1.09 ± 0.39 (1.09) | 7.54 ± 17.51 (4.18) | 1.67 ± 0.37 (1.65) | 4.17 ± 0.95 (4.20) | 1.59 ± 0.57 (1.56) |
| left | p | 0.885 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.53) | 4.22 ± 2.82 (3.36) | 1.91 ± 0.37 (1.99) | 4.75 ± 0.92 (5.05) | 2.03 ± 0.61 (2.16) |
| back | p | 0.876 | 50/50 | 0 | 50 | 2.24 ± 0.25 (2.22) | 2.99 ± 2.18 (2.31) | 1.90 ± 0.33 (1.96) | 4.83 ± 0.88 (5.30) | 2.08 ± 0.60 (2.28) |
| right | p | 0.855 | 50/50 | 0 | 50 | 1.62 ± 0.55 (1.51) | 4.25 ± 3.06 (3.76) | 1.77 ± 0.42 (1.84) | 4.45 ± 1.04 (4.93) | 1.82 ± 0.66 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.861 | 100/100 | 0 | 99 | 1.66 ± 0.62 (1.56) | 5.41 ± 12.68 (3.06) | 1.80 ± 0.38 (1.84) | 4.54 ± 0.98 (4.90) | 1.87 ± 0.64 (1.99) |
| right | p | 0.869 | 100/100 | 0 | 99 | 1.59 ± 0.51 (1.51) | 4.08 ± 2.92 (3.37) | 1.82 ± 0.39 (1.92) | 4.57 ± 1.00 (4.93) | 1.89 ± 0.64 (1.93) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 24 | 1.14 ± 0.50 (1.12) | 10.04 ± 24.21 (5.27) | 1.67 ± 0.31 (1.79) | 4.17 ± 0.88 (4.66) | 1.59 ± 0.52 (1.76) |
| forward/right | p | 0.851 | 25/25 | 0 | 24 | 1.05 ± 0.24 (1.08) | 5.03 ± 3.85 (4.17) | 1.67 ± 0.42 (1.53) | 4.18 ± 1.02 (4.03) | 1.60 ± 0.62 (1.50) |
| left/left | p | 0.878 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.48) | 4.58 ± 2.96 (3.81) | 1.85 ± 0.39 (1.82) | 4.62 ± 0.94 (4.78) | 1.93 ± 0.61 (2.09) |
| left/right | p | 0.892 | 25/25 | 0 | 25 | 1.64 ± 0.31 (1.66) | 3.85 ± 2.63 (2.95) | 1.97 ± 0.33 (2.02) | 4.89 ± 0.89 (5.31) | 2.12 ± 0.60 (2.26) |
| back/left | p | 0.877 | 25/25 | 0 | 25 | 2.25 ± 0.26 (2.20) | 2.67 ± 2.15 (2.07) | 1.91 ± 0.32 (1.98) | 4.85 ± 0.86 (5.29) | 2.09 ± 0.59 (2.35) |
| back/right | p | 0.874 | 25/25 | 0 | 25 | 2.23 ± 0.25 (2.22) | 3.30 ± 2.17 (2.76) | 1.90 ± 0.33 (1.96) | 4.82 ± 0.90 (5.37) | 2.07 ± 0.60 (2.25) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.81 ± 0.65 (1.60) | 4.36 ± 3.56 (2.92) | 1.78 ± 0.45 (1.98) | 4.51 ± 1.10 (5.04) | 1.88 ± 0.70 (2.17) |
| right/right | p | 0.858 | 25/25 | 0 | 25 | 1.44 ± 0.34 (1.46) | 4.14 ± 2.46 (3.89) | 1.75 ± 0.39 (1.77) | 4.39 ± 0.98 (4.45) | 1.77 ± 0.62 (1.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.891 | 4.3 | 5.23 | 2.28 |
| p | normal | 0.839 | 5.2 | 3.88 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.790 | 0.21 | 2.11 ± 0.65 (2.02) | 3.35 | 1.15 |
| p | medium | 16 | 0.925 | 0.85 | 1.08 ± 0.16 (1.11) | 3.51 | 1.26 |
| p | strong | 126 | 0.891 | 0.70 | - | 5.24 | 2.30 |

## Notes

- p: score 0.865, 200/200 kicked, 0 fell; worst sector forward (0.844).
