# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.89 ± 0.58 (1.81) |
| Direction error [°] | 5.25 ± 3.21 (4.80) |
| Avg ball speed [m/s] | 2.23 ± 0.40 (2.36) |
| Peak ball speed [m/s] | 4.91 ± 1.09 (5.48) |
| Distance [m] | 2.02 ± 0.67 (2.17) |
| Path length [m] | 2.03 ± 0.67 (2.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.879 | 50/50 | 0 | 49 | 1.30 ± 0.26 (1.33) | 4.42 ± 2.96 (3.97) | 2.22 ± 0.42 (2.33) | 4.92 ± 1.14 (5.43) | 2.02 ± 0.70 (2.17) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.83 ± 0.38 (1.78) | 6.04 ± 3.29 (5.48) | 2.22 ± 0.37 (2.35) | 4.87 ± 1.02 (5.41) | 1.99 ± 0.63 (2.15) |
| back | p | 0.817 | 50/50 | 0 | 49 | 2.61 ± 0.35 (2.55) | 5.67 ± 3.36 (5.17) | 2.29 ± 0.38 (2.43) | 5.10 ± 1.04 (5.62) | 2.13 ± 0.63 (2.34) |
| right | p | 0.859 | 50/50 | 0 | 50 | 1.82 ± 0.37 (1.81) | 4.87 ± 2.97 (4.42) | 2.17 ± 0.42 (2.30) | 4.77 ± 1.11 (5.37) | 1.94 ± 0.68 (2.06) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 98 | 1.88 ± 0.58 (1.80) | 5.52 ± 3.70 (4.80) | 2.25 ± 0.40 (2.34) | 4.97 ± 1.06 (5.46) | 2.07 ± 0.67 (2.17) |
| right | p | 0.862 | 100/100 | 0 | 100 | 1.89 ± 0.59 (1.83) | 4.98 ± 2.62 (4.79) | 2.20 ± 0.40 (2.36) | 4.86 ± 1.11 (5.49) | 1.97 ± 0.66 (2.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.869 | 25/25 | 0 | 24 | 1.29 ± 0.27 (1.32) | 5.04 ± 3.65 (4.03) | 2.23 ± 0.44 (2.29) | 4.93 ± 1.15 (5.33) | 2.05 ± 0.74 (2.01) |
| forward/right | p | 0.888 | 25/25 | 0 | 25 | 1.31 ± 0.25 (1.34) | 3.81 ± 1.84 (3.96) | 2.21 ± 0.41 (2.43) | 4.92 ± 1.12 (5.51) | 1.99 ± 0.66 (2.23) |
| left/left | p | 0.854 | 25/25 | 0 | 25 | 1.71 ± 0.34 (1.66) | 6.68 ± 3.80 (7.48) | 2.25 ± 0.34 (2.34) | 4.94 ± 0.94 (5.30) | 2.05 ± 0.59 (2.26) |
| left/right | p | 0.865 | 25/25 | 0 | 25 | 1.94 ± 0.38 (1.96) | 5.40 ± 2.53 (5.37) | 2.18 ± 0.40 (2.36) | 4.80 ± 1.09 (5.48) | 1.94 ± 0.66 (2.01) |
| back/left | p | 0.808 | 25/25 | 0 | 24 | 2.60 ± 0.30 (2.62) | 5.91 ± 3.98 (5.50) | 2.35 ± 0.36 (2.45) | 5.20 ± 0.99 (5.69) | 2.22 ± 0.61 (2.43) |
| back/right | p | 0.827 | 25/25 | 0 | 25 | 2.61 ± 0.40 (2.52) | 5.43 ± 2.58 (5.10) | 2.23 ± 0.39 (2.42) | 4.99 ± 1.08 (5.59) | 2.05 ± 0.64 (2.31) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.93 ± 0.37 (1.82) | 4.46 ± 2.86 (3.76) | 2.17 ± 0.42 (2.33) | 4.82 ± 1.12 (5.39) | 1.95 ± 0.71 (2.09) |
| right/right | p | 0.869 | 25/25 | 0 | 25 | 1.70 ± 0.34 (1.70) | 5.28 ± 3.03 (4.88) | 2.17 ± 0.41 (2.26) | 4.73 ± 1.10 (5.29) | 1.92 ± 0.66 (2.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.887 | 5.0 | 5.73 | 2.48 |
| p | normal | 0.820 | 5.5 | 4.10 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.762 | 0.18 | 2.27 ± 0.72 (2.21) | 3.53 | 1.21 |
| p | medium | 20 | 0.900 | 0.85 | 1.14 ± 0.14 (1.11) | 3.64 | 1.29 |
| p | strong | 126 | 0.886 | 0.76 | - | 5.71 | 2.48 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.817).
