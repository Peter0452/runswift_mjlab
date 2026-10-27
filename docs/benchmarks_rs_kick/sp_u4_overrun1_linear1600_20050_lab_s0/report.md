# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.858** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.64 ± 0.54 (1.54) |
| Direction error [°] | 5.26 ± 3.20 (4.98) |
| Avg ball speed [m/s] | 1.73 ± 0.47 (1.89) |
| Peak ball speed [m/s] | 3.80 ± 1.07 (4.13) |
| Distance [m] | 1.31 ± 0.60 (1.41) |
| Path length [m] | 1.32 ± 0.60 (1.42) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.860 | 50/50 | 0 | 50 | 1.09 ± 0.24 (1.13) | 4.50 ± 3.41 (3.79) | 1.45 ± 0.45 (1.51) | 3.17 ± 0.92 (3.21) | 0.93 ± 0.48 (0.89) |
| left | p | 0.871 | 50/50 | 0 | 50 | 1.56 ± 0.34 (1.54) | 5.50 ± 3.45 (5.60) | 1.85 ± 0.45 (2.06) | 4.08 ± 1.02 (4.59) | 1.46 ± 0.57 (1.64) |
| back | p | 0.846 | 50/50 | 0 | 50 | 2.32 ± 0.27 (2.30) | 5.57 ± 2.47 (5.59) | 1.93 ± 0.43 (2.16) | 4.25 ± 1.05 (4.87) | 1.58 ± 0.60 (1.88) |
| right | p | 0.854 | 50/50 | 0 | 50 | 1.57 ± 0.35 (1.53) | 5.46 ± 3.23 (5.01) | 1.71 ± 0.42 (1.87) | 3.71 ± 0.97 (4.13) | 1.26 ± 0.53 (1.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 100 | 1.63 ± 0.54 (1.55) | 5.41 ± 3.18 (5.03) | 1.73 ± 0.47 (1.93) | 3.79 ± 1.07 (4.22) | 1.31 ± 0.60 (1.48) |
| right | p | 0.863 | 100/100 | 0 | 100 | 1.64 ± 0.53 (1.54) | 5.10 ± 3.20 (4.94) | 1.74 ± 0.48 (1.85) | 3.82 ± 1.08 (4.07) | 1.31 ± 0.60 (1.34) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.858 | 25/25 | 0 | 25 | 1.08 ± 0.24 (1.12) | 4.58 ± 3.29 (3.77) | 1.46 ± 0.45 (1.36) | 3.15 ± 0.94 (2.84) | 0.95 ± 0.50 (0.76) |
| forward/right | p | 0.863 | 25/25 | 0 | 25 | 1.10 ± 0.24 (1.14) | 4.42 ± 3.52 (4.00) | 1.44 ± 0.44 (1.54) | 3.18 ± 0.90 (3.23) | 0.91 ± 0.47 (0.99) |
| left/left | p | 0.855 | 25/25 | 0 | 25 | 1.46 ± 0.33 (1.52) | 6.23 ± 3.97 (5.89) | 1.73 ± 0.46 (1.94) | 3.80 ± 1.02 (4.28) | 1.29 ± 0.55 (1.50) |
| left/right | p | 0.886 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.66) | 4.76 ± 2.66 (4.36) | 1.97 ± 0.40 (2.17) | 4.36 ± 0.94 (4.77) | 1.63 ± 0.54 (1.79) |
| back/left | p | 0.839 | 25/25 | 0 | 25 | 2.34 ± 0.25 (2.26) | 5.70 ± 2.42 (5.76) | 1.96 ± 0.36 (2.15) | 4.32 ± 0.93 (4.87) | 1.63 ± 0.56 (1.90) |
| back/right | p | 0.853 | 25/25 | 0 | 25 | 2.31 ± 0.28 (2.34) | 5.44 ± 2.51 (5.43) | 1.89 ± 0.48 (2.22) | 4.18 ± 1.15 (4.92) | 1.53 ± 0.63 (1.81) |
| right/left | p | 0.857 | 25/25 | 0 | 25 | 1.66 ± 0.34 (1.64) | 5.13 ± 2.56 (5.03) | 1.77 ± 0.45 (1.96) | 3.87 ± 1.04 (4.38) | 1.36 ± 0.57 (1.50) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.47 ± 0.32 (1.46) | 5.79 ± 3.76 (4.96) | 1.64 ± 0.38 (1.82) | 3.55 ± 0.87 (3.91) | 1.17 ± 0.48 (1.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.862 | 5.1 | 4.48 | 1.67 |
| p | normal | 0.854 | 5.4 | 3.12 | 0.95 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.838 | 0.47 | 1.61 ± 0.57 (1.52) | 2.55 | 0.63 |
| p | medium | 16 | 0.889 | 0.82 | 0.84 ± 0.17 (0.88) | 2.71 | 0.72 |
| p | strong | 126 | 0.863 | 0.60 | - | 4.52 | 1.69 |

## Notes

- p: score 0.858, 200/200 kicked, 0 fell; worst sector back (0.846).
