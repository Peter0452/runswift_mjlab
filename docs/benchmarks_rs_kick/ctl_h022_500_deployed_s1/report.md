# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_21-10-41_control_h022_500/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.00 ± 1.47 (1.64) |
| Direction error [°] | 12.77 ± 23.47 (6.02) |
| Avg ball speed [m/s] | 2.10 ± 0.52 (2.24) |
| Peak ball speed [m/s] | 4.65 ± 1.28 (4.99) |
| Distance [m] | 1.87 ± 0.67 (1.93) |
| Path length [m] | 1.87 ± 0.67 (1.93) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.791 | 49/50 | 0 | 43 | 1.62 ± 1.71 (1.28) | 10.30 ± 14.28 (5.14) | 2.07 ± 0.53 (2.20) | 4.63 ± 1.29 (4.98) | 1.83 ± 0.64 (1.84) |
| left | p | 0.809 | 50/50 | 0 | 44 | 1.83 ± 1.19 (1.60) | 12.68 ± 21.71 (5.21) | 2.06 ± 0.58 (2.22) | 4.57 ± 1.40 (4.78) | 1.82 ± 0.72 (1.85) |
| back | p | 0.733 | 49/50 | 0 | 44 | 2.93 ± 1.75 (2.56) | 15.78 ± 33.01 (7.79) | 2.25 ± 0.41 (2.36) | 4.96 ± 1.05 (5.39) | 2.07 ± 0.59 (2.20) |
| right | p | 0.787 | 49/50 | 0 | 40 | 1.64 ± 0.34 (1.64) | 12.34 ± 20.60 (4.68) | 2.01 ± 0.51 (2.14) | 4.44 ± 1.28 (4.44) | 1.75 ± 0.66 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.774 | 98/100 | 0 | 87 | 1.99 ± 1.35 (1.63) | 13.15 ± 23.55 (7.12) | 2.11 ± 0.53 (2.24) | 4.69 ± 1.29 (4.99) | 1.89 ± 0.68 (1.93) |
| right | p | 0.787 | 99/100 | 0 | 84 | 2.01 ± 1.59 (1.64) | 12.40 ± 23.38 (5.45) | 2.08 ± 0.51 (2.24) | 4.61 ± 1.26 (4.96) | 1.85 ± 0.65 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.793 | 24/25 | 0 | 21 | 1.27 ± 0.28 (1.28) | 10.82 ± 15.54 (4.79) | 2.08 ± 0.48 (2.17) | 4.65 ± 1.19 (4.94) | 1.86 ± 0.64 (1.85) |
| forward/right | p | 0.790 | 25/25 | 0 | 22 | 1.95 ± 2.32 (1.30) | 9.79 ± 12.93 (5.88) | 2.05 ± 0.58 (2.23) | 4.61 ± 1.39 (5.05) | 1.81 ± 0.65 (1.83) |
| left/left | p | 0.827 | 25/25 | 0 | 24 | 1.96 ± 1.57 (1.58) | 6.82 ± 4.28 (7.21) | 2.20 ± 0.46 (2.26) | 4.90 ± 1.10 (4.99) | 1.98 ± 0.58 (1.93) |
| left/right | p | 0.792 | 25/25 | 0 | 20 | 1.70 ± 0.57 (1.74) | 18.54 ± 29.26 (4.55) | 1.91 ± 0.64 (2.08) | 4.23 ± 1.57 (4.35) | 1.65 ± 0.81 (1.71) |
| back/left | p | 0.728 | 25/25 | 0 | 22 | 3.01 ± 1.68 (2.50) | 17.25 ± 33.37 (7.82) | 2.19 ± 0.50 (2.36) | 4.86 ± 1.25 (5.39) | 2.01 ± 0.67 (2.20) |
| back/right | p | 0.737 | 24/25 | 0 | 22 | 2.86 ± 1.82 (2.56) | 14.26 ± 32.57 (7.46) | 2.30 ± 0.28 (2.35) | 5.08 ± 0.77 (5.38) | 2.12 ± 0.48 (2.21) |
| right/left | p | 0.746 | 24/25 | 0 | 20 | 1.70 ± 0.36 (1.77) | 17.82 ± 27.53 (6.14) | 1.96 ± 0.62 (2.16) | 4.34 ± 1.51 (4.41) | 1.69 ± 0.78 (1.82) |
| right/right | p | 0.828 | 25/25 | 0 | 20 | 1.58 ± 0.31 (1.56) | 7.07 ± 6.89 (4.02) | 2.07 ± 0.38 (2.14) | 4.53 ± 1.01 (4.51) | 1.81 ± 0.52 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.803 | 15.0 | 4.95 | 2.02 |
| p | normal | 0.757 | 10.5 | 4.35 | 1.71 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.702 | 0.08 | 2.59 ± 0.89 (2.47) | 4.00 | 1.52 |
| p | medium | 20 | 0.850 | 0.65 | 1.33 ± 0.19 (1.35) | 4.27 | 1.71 |
| p | strong | 126 | 0.802 | 0.66 | - | 4.98 | 2.03 |

## Notes

- p: score 0.780, 197/200 kicked, 0 fell; worst sector back (0.733).
