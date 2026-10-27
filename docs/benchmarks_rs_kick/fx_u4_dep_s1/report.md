# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.89 ± 0.59 (1.80) |
| Direction error [°] | 6.67 ± 12.12 (5.49) |
| Avg ball speed [m/s] | 2.46 ± 0.55 (2.63) |
| Peak ball speed [m/s] | 5.30 ± 1.34 (6.00) |
| Distance [m] | 2.55 ± 0.98 (2.98) |
| Path length [m] | 2.56 ± 0.98 (3.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.889 | 50/50 | 0 | 50 | 1.29 ± 0.27 (1.29) | 4.04 ± 3.02 (3.23) | 2.39 ± 0.49 (2.66) | 5.22 ± 1.28 (6.01) | 2.43 ± 0.89 (2.89) |
| left | p | 0.860 | 50/50 | 0 | 48 | 1.84 ± 0.38 (1.70) | 6.71 ± 4.01 (6.65) | 2.46 ± 0.48 (2.58) | 5.26 ± 1.25 (5.80) | 2.51 ± 0.94 (2.82) |
| back | p | 0.806 | 50/50 | 0 | 48 | 2.60 ± 0.41 (2.60) | 10.61 ± 22.97 (6.69) | 2.61 ± 0.63 (2.86) | 5.60 ± 1.47 (6.39) | 2.85 ± 1.05 (3.37) |
| right | p | 0.859 | 50/50 | 0 | 49 | 1.84 ± 0.40 (1.84) | 5.34 ± 3.25 (5.40) | 2.38 ± 0.53 (2.58) | 5.11 ± 1.32 (5.84) | 2.41 ± 0.98 (2.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 99 | 1.89 ± 0.59 (1.71) | 5.76 ± 3.76 (5.58) | 2.48 ± 0.51 (2.62) | 5.36 ± 1.27 (6.00) | 2.58 ± 0.95 (2.95) |
| right | p | 0.856 | 100/100 | 0 | 96 | 1.89 ± 0.60 (1.87) | 7.59 ± 16.67 (5.40) | 2.44 ± 0.58 (2.65) | 5.24 ± 1.41 (6.00) | 2.52 ± 1.01 (3.01) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.884 | 25/25 | 0 | 25 | 1.26 ± 0.26 (1.28) | 3.96 ± 3.28 (2.39) | 2.34 ± 0.47 (2.61) | 5.14 ± 1.24 (6.02) | 2.37 ± 0.85 (2.79) |
| forward/right | p | 0.893 | 25/25 | 0 | 25 | 1.31 ± 0.27 (1.32) | 4.12 ± 2.75 (3.63) | 2.45 ± 0.50 (2.68) | 5.31 ± 1.32 (6.01) | 2.49 ± 0.92 (3.00) |
| left/left | p | 0.860 | 25/25 | 0 | 24 | 1.71 ± 0.34 (1.66) | 7.11 ± 4.09 (8.00) | 2.47 ± 0.46 (2.53) | 5.30 ± 1.18 (5.73) | 2.54 ± 0.89 (2.80) |
| left/right | p | 0.861 | 25/25 | 0 | 24 | 1.96 ± 0.38 (2.00) | 6.31 ± 3.89 (6.09) | 2.45 ± 0.51 (2.61) | 5.23 ± 1.31 (5.88) | 2.49 ± 0.99 (2.99) |
| back/left | p | 0.805 | 25/25 | 0 | 25 | 2.63 ± 0.30 (2.60) | 7.42 ± 3.48 (6.48) | 2.71 ± 0.53 (2.94) | 5.78 ± 1.27 (6.58) | 2.96 ± 0.98 (3.49) |
| back/right | p | 0.806 | 25/25 | 0 | 23 | 2.57 ± 0.50 (2.60) | 13.81 ± 31.97 (7.08) | 2.51 ± 0.71 (2.77) | 5.42 ± 1.62 (6.35) | 2.73 ± 1.11 (3.29) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.96 ± 0.39 (1.98) | 4.55 ± 2.79 (3.92) | 2.42 ± 0.52 (2.60) | 5.21 ± 1.30 (5.94) | 2.46 ± 0.95 (2.97) |
| right/right | p | 0.865 | 25/25 | 0 | 24 | 1.72 ± 0.36 (1.66) | 6.12 ± 3.48 (5.51) | 2.35 ± 0.55 (2.48) | 5.01 ± 1.33 (5.51) | 2.36 ± 1.00 (2.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.888 | 6.2 | 6.28 | 3.25 |
| p | normal | 0.819 | 7.2 | 4.32 | 1.85 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.760 | 0.15 | 2.33 ± 0.79 (2.22) | 3.61 | 1.33 |
| p | medium | 20 | 0.898 | 0.84 | 1.15 ± 0.14 (1.18) | 3.68 | 1.39 |
| p | strong | 126 | 0.886 | 0.84 | - | 6.28 | 3.26 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector back (0.806).
