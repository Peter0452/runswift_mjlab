# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.862** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 6 |
| Time to kick [s] | 1.60 ± 0.52 (1.52) |
| Direction error [°] | 5.04 ± 3.24 (4.42) |
| Avg ball speed [m/s] | 1.86 ± 0.47 (2.05) |
| Peak ball speed [m/s] | 4.04 ± 1.08 (4.53) |
| Distance [m] | 1.45 ± 0.61 (1.63) |
| Path length [m] | 1.46 ± 0.61 (1.64) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.861 | 50/50 | 0 | 50 | 1.06 ± 0.24 (1.08) | 4.66 ± 3.48 (3.44) | 1.59 ± 0.53 (1.58) | 3.45 ± 1.14 (3.30) | 1.10 ± 0.62 (0.99) |
| left | p | 0.871 | 50/50 | 0 | 49 | 1.54 ± 0.35 (1.56) | 5.25 ± 3.47 (4.78) | 1.96 ± 0.38 (2.14) | 4.29 ± 0.92 (4.74) | 1.59 ± 0.53 (1.76) |
| back | p | 0.856 | 50/50 | 0 | 50 | 2.25 ± 0.26 (2.23) | 5.02 ± 2.77 (5.29) | 2.03 ± 0.36 (2.22) | 4.42 ± 0.93 (4.95) | 1.69 ± 0.55 (1.94) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.54 ± 0.35 (1.48) | 5.24 ± 3.14 (4.38) | 1.84 ± 0.44 (2.07) | 4.01 ± 1.04 (4.56) | 1.43 ± 0.57 (1.64) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.860 | 100/100 | 0 | 99 | 1.59 ± 0.52 (1.54) | 5.22 ± 3.35 (4.77) | 1.85 ± 0.45 (2.03) | 4.03 ± 1.06 (4.48) | 1.45 ± 0.61 (1.61) |
| right | p | 0.864 | 100/100 | 0 | 100 | 1.61 ± 0.52 (1.52) | 4.86 ± 3.11 (4.18) | 1.86 ± 0.48 (2.07) | 4.06 ± 1.09 (4.57) | 1.46 ± 0.62 (1.65) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 25 | 1.06 ± 0.23 (1.08) | 4.90 ± 3.34 (3.71) | 1.63 ± 0.49 (1.83) | 3.52 ± 1.07 (4.03) | 1.14 ± 0.59 (1.32) |
| forward/right | p | 0.860 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.08) | 4.43 ± 3.59 (3.07) | 1.56 ± 0.57 (1.52) | 3.39 ± 1.20 (3.26) | 1.06 ± 0.65 (0.89) |
| left/left | p | 0.862 | 25/25 | 0 | 24 | 1.43 ± 0.34 (1.50) | 5.67 ± 4.15 (4.29) | 1.87 ± 0.39 (2.01) | 4.08 ± 0.96 (4.55) | 1.47 ± 0.55 (1.66) |
| left/right | p | 0.880 | 25/25 | 0 | 25 | 1.66 ± 0.33 (1.68) | 4.83 ± 2.56 (5.09) | 2.06 ± 0.34 (2.21) | 4.50 ± 0.83 (4.91) | 1.71 ± 0.48 (1.87) |
| back/left | p | 0.853 | 25/25 | 0 | 25 | 2.25 ± 0.25 (2.20) | 5.25 ± 3.09 (5.29) | 2.02 ± 0.38 (2.20) | 4.40 ± 0.95 (4.91) | 1.67 ± 0.58 (1.98) |
| back/right | p | 0.858 | 25/25 | 0 | 25 | 2.25 ± 0.26 (2.24) | 4.79 ± 2.39 (4.89) | 2.04 ± 0.35 (2.24) | 4.44 ± 0.91 (4.97) | 1.70 ± 0.52 (1.93) |
| right/left | p | 0.860 | 25/25 | 0 | 25 | 1.64 ± 0.35 (1.60) | 5.07 ± 2.55 (5.23) | 1.90 ± 0.44 (2.10) | 4.13 ± 1.07 (4.66) | 1.50 ± 0.57 (1.75) |
| right/right | p | 0.856 | 25/25 | 0 | 25 | 1.45 ± 0.33 (1.48) | 5.40 ± 3.62 (3.69) | 1.79 ± 0.44 (2.04) | 3.90 ± 1.01 (4.51) | 1.36 ± 0.57 (1.50) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.869 | 5.4 | 4.77 | 1.85 |
| p | normal | 0.854 | 4.7 | 3.32 | 1.06 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.829 | 0.40 | 1.75 ± 0.63 (1.67) | 2.77 | 0.76 |
| p | medium | 16 | 0.899 | 0.79 | 0.85 ± 0.21 (0.84) | 2.77 | 0.77 |
| p | strong | 126 | 0.872 | 0.64 | - | 4.79 | 1.86 |

## Notes

- p: score 0.862, 200/200 kicked, 0 fell; worst sector back (0.856).
