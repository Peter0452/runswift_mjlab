# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 2.22 ± 2.00 (1.74) |
| Direction error [°] | 16.96 ± 35.88 (4.72) |
| Avg ball speed [m/s] | 1.95 ± 0.63 (2.07) |
| Peak ball speed [m/s] | 4.71 ± 1.59 (5.19) |
| Distance [m] | 2.05 ± 0.90 (2.08) |
| Path length [m] | 2.06 ± 0.90 (2.08) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.809 | 50/50 | 0 | 45 | 1.68 ± 1.91 (1.29) | 8.98 ± 14.29 (4.23) | 1.96 ± 0.62 (2.09) | 4.73 ± 1.61 (4.73) | 2.06 ± 0.91 (2.06) |
| left | p | 0.809 | 49/50 | 0 | 43 | 1.66 ± 0.45 (1.70) | 14.05 ± 28.46 (4.67) | 1.94 ± 0.56 (2.02) | 4.84 ± 1.43 (5.34) | 2.10 ± 0.85 (2.09) |
| back | p | 0.751 | 50/50 | 0 | 42 | 2.85 ± 1.94 (2.53) | 25.79 ± 49.27 (4.93) | 1.99 ± 0.70 (2.17) | 4.70 ± 1.70 (5.23) | 2.09 ± 0.97 (2.26) |
| right | p | 0.756 | 50/50 | 0 | 42 | 2.67 ± 2.65 (1.86) | 18.97 ± 39.29 (4.78) | 1.90 ± 0.64 (2.01) | 4.58 ± 1.61 (4.51) | 1.96 ± 0.87 (1.98) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 100/100 | 0 | 88 | 1.85 ± 0.92 (1.73) | 14.82 ± 33.16 (4.40) | 1.98 ± 0.60 (2.11) | 4.78 ± 1.52 (5.31) | 2.09 ± 0.88 (2.08) |
| right | p | 0.750 | 99/100 | 0 | 84 | 2.59 ± 2.62 (1.82) | 19.13 ± 38.31 (5.26) | 1.92 ± 0.67 (2.06) | 4.65 ± 1.66 (4.87) | 2.01 ± 0.92 (2.07) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 22 | 1.38 ± 0.72 (1.28) | 8.76 ± 14.42 (4.04) | 1.91 ± 0.65 (1.98) | 4.59 ± 1.66 (4.52) | 1.99 ± 0.95 (1.90) |
| forward/right | p | 0.796 | 25/25 | 0 | 23 | 1.98 ± 2.57 (1.30) | 9.20 ± 14.15 (5.36) | 2.00 ± 0.60 (2.20) | 4.87 ± 1.54 (5.42) | 2.14 ± 0.85 (2.24) |
| left/left | p | 0.809 | 25/25 | 0 | 21 | 1.56 ± 0.42 (1.58) | 13.63 ± 22.42 (5.22) | 1.87 ± 0.58 (2.01) | 4.68 ± 1.54 (5.26) | 2.01 ± 0.87 (2.09) |
| left/right | p | 0.809 | 24/25 | 0 | 22 | 1.76 ± 0.45 (1.78) | 14.49 ± 33.61 (4.02) | 2.01 ± 0.53 (2.09) | 5.02 ± 1.29 (5.36) | 2.19 ± 0.82 (2.12) |
| back/left | p | 0.806 | 25/25 | 0 | 23 | 2.48 ± 0.64 (2.44) | 16.32 ± 38.71 (4.53) | 2.12 ± 0.54 (2.26) | 5.03 ± 1.34 (5.60) | 2.27 ± 0.82 (2.52) |
| back/right | p | 0.696 | 25/25 | 0 | 19 | 3.22 ± 2.61 (2.58) | 35.27 ± 56.36 (5.26) | 1.86 ± 0.81 (2.11) | 4.37 ± 1.94 (4.61) | 1.91 ± 1.07 (1.94) |
| right/left | p | 0.812 | 25/25 | 0 | 22 | 1.97 ± 1.26 (1.86) | 20.58 ± 45.99 (3.92) | 2.00 ± 0.59 (2.12) | 4.81 ± 1.49 (5.38) | 2.11 ± 0.85 (1.95) |
| right/right | p | 0.700 | 25/25 | 0 | 20 | 3.37 ± 3.39 (1.86) | 17.37 ± 31.09 (6.71) | 1.79 ± 0.67 (1.99) | 4.35 ± 1.69 (4.50) | 1.82 ± 0.86 (2.02) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.828 | 12.8 | 5.24 | 2.36 |
| p | normal | 0.735 | 21.1 | 4.18 | 1.74 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.699 | 0.09 | 2.47 ± 0.92 (2.35) | 3.99 | 1.63 |
| p | medium | 18 | 0.809 | 0.60 | 1.20 ± 0.40 (1.37) | 3.87 | 1.55 |
| p | strong | 124 | 0.816 | 0.69 | - | 5.17 | 2.32 |

## Notes

- p: score 0.781, 199/200 kicked, 0 fell; worst sector back (0.751).
