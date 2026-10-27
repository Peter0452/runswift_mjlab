# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_02-42-52_q4_overrun_linear_noanchor/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.55 ± 0.51 (1.46) |
| Direction error [°] | 6.77 ± 4.08 (6.44) |
| Avg ball speed [m/s] | 2.05 ± 0.43 (2.19) |
| Peak ball speed [m/s] | 4.30 ± 0.98 (4.64) |
| Distance [m] | 1.85 ± 0.67 (2.01) |
| Path length [m] | 1.86 ± 0.67 (2.03) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 49 | 1.03 ± 0.23 (1.08) | 5.07 ± 3.68 (3.91) | 1.87 ± 0.38 (1.73) | 3.90 ± 0.89 (3.56) | 1.55 ± 0.59 (1.28) |
| left | p | 0.864 | 50/50 | 0 | 50 | 1.49 ± 0.34 (1.50) | 6.55 ± 3.78 (6.60) | 2.19 ± 0.43 (2.30) | 4.60 ± 0.96 (4.96) | 2.06 ± 0.64 (2.28) |
| back | p | 0.832 | 50/50 | 0 | 49 | 2.20 ± 0.27 (2.19) | 7.63 ± 3.46 (8.09) | 2.12 ± 0.40 (2.30) | 4.46 ± 0.95 (4.87) | 1.99 ± 0.68 (2.19) |
| right | p | 0.829 | 50/50 | 0 | 47 | 1.46 ± 0.33 (1.42) | 7.84 ± 4.67 (7.22) | 2.03 ± 0.43 (2.11) | 4.22 ± 0.97 (4.48) | 1.79 ± 0.64 (1.85) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.842 | 100/100 | 0 | 98 | 1.54 ± 0.52 (1.46) | 6.84 ± 3.83 (6.80) | 2.05 ± 0.41 (2.20) | 4.31 ± 0.96 (4.61) | 1.86 ± 0.66 (2.01) |
| right | p | 0.844 | 100/100 | 0 | 97 | 1.55 ± 0.50 (1.46) | 6.70 ± 4.31 (5.77) | 2.05 ± 0.44 (2.19) | 4.28 ± 1.00 (4.65) | 1.84 ± 0.67 (2.02) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.849 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.08) | 4.95 ± 2.95 (4.66) | 1.86 ± 0.34 (1.73) | 3.89 ± 0.82 (3.52) | 1.55 ± 0.56 (1.31) |
| forward/right | p | 0.846 | 25/25 | 0 | 24 | 1.04 ± 0.24 (1.04) | 5.18 ± 4.30 (3.67) | 1.88 ± 0.42 (1.71) | 3.90 ± 0.95 (3.59) | 1.56 ± 0.61 (1.26) |
| left/left | p | 0.860 | 25/25 | 0 | 25 | 1.39 ± 0.34 (1.46) | 6.72 ± 3.89 (6.68) | 2.15 ± 0.44 (2.26) | 4.52 ± 1.00 (4.91) | 1.99 ± 0.67 (2.25) |
| left/right | p | 0.868 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.60) | 6.38 ± 3.67 (5.76) | 2.23 ± 0.41 (2.38) | 4.68 ± 0.91 (5.03) | 2.12 ± 0.61 (2.29) |
| back/left | p | 0.826 | 25/25 | 0 | 24 | 2.22 ± 0.26 (2.16) | 7.94 ± 3.15 (7.84) | 2.13 ± 0.37 (2.30) | 4.52 ± 0.91 (4.92) | 2.03 ± 0.66 (2.25) |
| back/right | p | 0.838 | 25/25 | 0 | 25 | 2.18 ± 0.27 (2.22) | 7.32 ± 3.72 (8.46) | 2.11 ± 0.42 (2.29) | 4.41 ± 0.99 (4.87) | 1.95 ± 0.69 (2.19) |
| right/left | p | 0.834 | 25/25 | 0 | 24 | 1.55 ± 0.32 (1.52) | 7.77 ± 4.39 (8.18) | 2.07 ± 0.43 (2.21) | 4.33 ± 0.97 (4.59) | 1.86 ± 0.63 (1.86) |
| right/right | p | 0.825 | 25/25 | 0 | 23 | 1.38 ± 0.33 (1.40) | 7.91 ± 4.94 (6.28) | 1.98 ± 0.42 (1.90) | 4.12 ± 0.96 (3.96) | 1.72 ± 0.63 (1.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.865 | 6.4 | 4.95 | 2.28 |
| p | normal | 0.821 | 7.2 | 3.64 | 1.42 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.781 | 0.27 | 1.97 ± 0.60 (1.83) | 3.13 | 1.07 |
| p | medium | 16 | 0.892 | 0.92 | 0.97 ± 0.09 (0.97) | 3.17 | 1.13 |
| p | strong | 126 | 0.866 | 0.66 | - | 4.98 | 2.30 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector right (0.829).
