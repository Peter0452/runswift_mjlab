# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.870** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.64 ± 0.54 (1.57) |
| Direction error [°] | 5.08 ± 3.19 (4.73) |
| Avg ball speed [m/s] | 1.90 ± 0.55 (2.15) |
| Peak ball speed [m/s] | 4.10 ± 1.26 (4.74) |
| Distance [m] | 1.59 ± 0.75 (1.81) |
| Path length [m] | 1.59 ± 0.76 (1.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.865 | 50/50 | 0 | 49 | 1.07 ± 0.24 (1.10) | 5.00 ± 3.56 (4.13) | 1.64 ± 0.56 (1.66) | 3.55 ± 1.23 (3.67) | 1.22 ± 0.70 (1.15) |
| left | p | 0.891 | 50/50 | 0 | 50 | 1.60 ± 0.36 (1.57) | 4.61 ± 3.19 (3.52) | 2.03 ± 0.50 (2.25) | 4.40 ± 1.19 (4.94) | 1.77 ± 0.70 (1.99) |
| back | p | 0.857 | 50/50 | 0 | 50 | 2.30 ± 0.26 (2.29) | 5.30 ± 2.52 (5.40) | 2.08 ± 0.49 (2.32) | 4.50 ± 1.16 (5.16) | 1.84 ± 0.74 (2.11) |
| right | p | 0.868 | 50/50 | 0 | 50 | 1.58 ± 0.36 (1.53) | 5.41 ± 3.34 (4.69) | 1.85 ± 0.54 (2.08) | 3.97 ± 1.23 (4.51) | 1.51 ± 0.71 (1.76) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.869 | 100/100 | 0 | 99 | 1.64 ± 0.55 (1.60) | 5.03 ± 3.26 (4.56) | 1.93 ± 0.54 (2.17) | 4.17 ± 1.25 (4.77) | 1.63 ± 0.75 (1.86) |
| right | p | 0.871 | 100/100 | 0 | 100 | 1.63 ± 0.53 (1.54) | 5.13 ± 3.12 (4.82) | 1.87 ± 0.56 (2.11) | 4.04 ± 1.27 (4.67) | 1.54 ± 0.75 (1.76) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.865 | 25/25 | 0 | 24 | 1.07 ± 0.24 (1.08) | 5.04 ± 3.75 (3.41) | 1.70 ± 0.53 (1.87) | 3.65 ± 1.19 (4.00) | 1.29 ± 0.69 (1.38) |
| forward/right | p | 0.864 | 25/25 | 0 | 25 | 1.07 ± 0.24 (1.12) | 4.96 ± 3.37 (4.25) | 1.58 ± 0.59 (1.54) | 3.46 ± 1.26 (3.23) | 1.16 ± 0.70 (1.09) |
| left/left | p | 0.888 | 25/25 | 0 | 25 | 1.48 ± 0.34 (1.52) | 4.83 ± 3.47 (3.71) | 1.97 ± 0.53 (2.22) | 4.27 ± 1.25 (4.90) | 1.69 ± 0.74 (1.92) |
| left/right | p | 0.894 | 25/25 | 0 | 25 | 1.71 ± 0.34 (1.74) | 4.39 ± 2.86 (3.44) | 2.09 ± 0.47 (2.29) | 4.53 ± 1.11 (5.00) | 1.84 ± 0.66 (2.00) |
| back/left | p | 0.850 | 25/25 | 0 | 25 | 2.33 ± 0.26 (2.30) | 5.25 ± 2.78 (5.37) | 2.14 ± 0.44 (2.32) | 4.60 ± 1.08 (5.23) | 1.92 ± 0.71 (2.15) |
| back/right | p | 0.864 | 25/25 | 0 | 25 | 2.28 ± 0.25 (2.28) | 5.34 ± 2.23 (5.43) | 2.03 ± 0.52 (2.31) | 4.39 ± 1.23 (4.99) | 1.77 ± 0.75 (2.04) |
| right/left | p | 0.872 | 25/25 | 0 | 25 | 1.70 ± 0.34 (1.62) | 4.99 ± 2.94 (4.23) | 1.91 ± 0.55 (2.18) | 4.15 ± 1.27 (4.82) | 1.61 ± 0.72 (1.86) |
| right/right | p | 0.863 | 25/25 | 0 | 25 | 1.47 ± 0.34 (1.50) | 5.84 ± 3.65 (5.09) | 1.79 ± 0.52 (2.04) | 3.79 ± 1.16 (4.34) | 1.41 ± 0.68 (1.69) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.880 | 4.7 | 4.98 | 2.08 |
| p | normal | 0.860 | 5.5 | 3.23 | 1.09 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.837 | 0.49 | 1.58 ± 0.55 (1.41) | 2.52 | 0.67 |
| p | medium | 16 | 0.899 | 0.84 | 0.84 ± 0.14 (0.88) | 2.74 | 0.78 |
| p | strong | 126 | 0.881 | 0.67 | - | 5.01 | 2.11 |

## Notes

- p: score 0.870, 200/200 kicked, 0 fell; worst sector back (0.857).
