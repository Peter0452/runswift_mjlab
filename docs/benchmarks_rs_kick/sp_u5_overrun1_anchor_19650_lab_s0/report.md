# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.56 ± 0.52 (1.48) |
| Direction error [°] | 6.54 ± 12.65 (4.80) |
| Avg ball speed [m/s] | 2.13 ± 0.44 (2.20) |
| Peak ball speed [m/s] | 4.49 ± 0.98 (4.73) |
| Distance [m] | 1.97 ± 0.63 (2.07) |
| Path length [m] | 1.98 ± 0.63 (2.08) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.838 | 50/50 | 0 | 49 | 1.02 ± 0.23 (1.05) | 5.43 ± 3.92 (4.43) | 1.92 ± 0.35 (1.89) | 4.03 ± 0.79 (3.94) | 1.63 ± 0.54 (1.53) |
| left | p | 0.863 | 50/50 | 0 | 49 | 1.49 ± 0.34 (1.49) | 6.08 ± 4.18 (5.17) | 2.27 ± 0.34 (2.37) | 4.79 ± 0.81 (5.04) | 2.17 ± 0.57 (2.33) |
| back | p | 0.842 | 50/50 | 0 | 48 | 2.21 ± 0.25 (2.16) | 8.73 ± 24.23 (4.64) | 2.19 ± 0.59 (2.30) | 4.62 ± 1.29 (5.04) | 2.12 ± 0.74 (2.33) |
| right | p | 0.838 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.47) | 5.90 ± 3.69 (5.93) | 2.15 ± 0.33 (2.20) | 4.51 ± 0.77 (4.68) | 1.96 ± 0.51 (2.07) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 97 | 1.56 ± 0.53 (1.49) | 5.96 ± 4.10 (5.07) | 2.13 ± 0.44 (2.20) | 4.49 ± 0.98 (4.72) | 1.98 ± 0.62 (2.05) |
| right | p | 0.847 | 100/100 | 0 | 99 | 1.55 ± 0.51 (1.47) | 7.11 ± 17.40 (4.43) | 2.13 ± 0.44 (2.17) | 4.48 ± 0.98 (4.78) | 1.96 ± 0.64 (2.07) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.841 | 25/25 | 0 | 24 | 1.02 ± 0.22 (1.06) | 5.57 ± 4.06 (4.38) | 1.94 ± 0.28 (1.89) | 4.07 ± 0.67 (4.00) | 1.65 ± 0.47 (1.58) |
| forward/right | p | 0.835 | 25/25 | 0 | 25 | 1.01 ± 0.23 (1.02) | 5.30 ± 3.77 (4.45) | 1.90 ± 0.41 (1.88) | 3.99 ± 0.89 (3.86) | 1.60 ± 0.59 (1.50) |
| left/left | p | 0.852 | 25/25 | 0 | 24 | 1.38 ± 0.33 (1.44) | 6.58 ± 3.81 (6.17) | 2.22 ± 0.32 (2.27) | 4.70 ± 0.79 (4.98) | 2.10 ± 0.54 (2.28) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.62) | 5.57 ± 4.47 (3.86) | 2.32 ± 0.36 (2.45) | 4.88 ± 0.82 (5.08) | 2.24 ± 0.58 (2.38) |
| back/left | p | 0.834 | 25/25 | 0 | 24 | 2.24 ± 0.25 (2.16) | 6.33 ± 4.75 (5.86) | 2.18 ± 0.65 (2.35) | 4.57 ± 1.41 (5.11) | 2.12 ± 0.80 (2.44) |
| back/right | p | 0.850 | 25/25 | 0 | 24 | 2.17 ± 0.24 (2.14) | 11.12 ± 33.76 (4.31) | 2.20 ± 0.52 (2.27) | 4.67 ± 1.16 (5.03) | 2.12 ± 0.67 (2.26) |
| right/left | p | 0.848 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.58) | 5.37 ± 3.53 (4.97) | 2.20 ± 0.33 (2.23) | 4.63 ± 0.75 (4.75) | 2.05 ± 0.50 (2.22) |
| right/right | p | 0.828 | 25/25 | 0 | 25 | 1.42 ± 0.35 (1.44) | 6.43 ± 3.77 (5.99) | 2.09 ± 0.33 (2.09) | 4.39 ± 0.77 (4.15) | 1.88 ± 0.52 (1.77) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.879 | 5.1 | 5.02 | 2.31 |
| p | normal | 0.811 | 8.0 | 3.96 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.754 | 0.13 | 2.20 ± 0.84 (2.10) | 3.47 | 1.31 |
| p | medium | 16 | 0.885 | 0.85 | 1.11 ± 0.15 (1.09) | 3.60 | 1.37 |
| p | strong | 126 | 0.882 | 0.68 | - | 5.07 | 2.35 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector forward (0.838).
