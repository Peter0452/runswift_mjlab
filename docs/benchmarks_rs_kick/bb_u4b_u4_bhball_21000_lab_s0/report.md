# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_21000.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.820** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 186 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.60 ± 0.54 (1.52) |
| Direction error [°] | 9.25 ± 11.32 (8.29) |
| Avg ball speed [m/s] | 2.04 ± 0.46 (2.11) |
| Peak ball speed [m/s] | 4.28 ± 1.05 (4.59) |
| Distance [m] | 1.83 ± 0.66 (1.97) |
| Path length [m] | 1.83 ± 0.66 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.834 | 50/50 | 0 | 49 | 1.06 ± 0.24 (1.11) | 6.25 ± 3.68 (6.00) | 1.82 ± 0.35 (1.82) | 3.82 ± 0.81 (3.67) | 1.47 ± 0.51 (1.34) |
| left | p | 0.839 | 50/50 | 0 | 44 | 1.52 ± 0.36 (1.52) | 8.52 ± 4.82 (8.49) | 2.15 ± 0.36 (2.27) | 4.53 ± 0.85 (4.83) | 1.99 ± 0.58 (2.16) |
| back | p | 0.785 | 50/50 | 0 | 45 | 2.28 ± 0.30 (2.24) | 13.95 ± 20.63 (9.92) | 2.12 ± 0.61 (2.33) | 4.46 ± 1.34 (4.99) | 2.02 ± 0.75 (2.29) |
| right | p | 0.821 | 50/50 | 0 | 48 | 1.55 ± 0.35 (1.52) | 8.28 ± 4.19 (8.71) | 2.06 ± 0.42 (2.11) | 4.29 ± 0.96 (4.52) | 1.82 ± 0.63 (1.94) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.822 | 100/100 | 0 | 93 | 1.60 ± 0.54 (1.55) | 9.82 ± 15.38 (7.89) | 2.04 ± 0.52 (2.13) | 4.31 ± 1.16 (4.63) | 1.86 ± 0.70 (2.01) |
| right | p | 0.817 | 100/100 | 0 | 93 | 1.60 ± 0.54 (1.50) | 8.68 ± 4.37 (8.97) | 2.03 ± 0.40 (2.11) | 4.25 ± 0.91 (4.51) | 1.79 ± 0.62 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.14) | 5.51 ± 3.27 (3.96) | 1.85 ± 0.32 (1.96) | 3.90 ± 0.78 (4.29) | 1.52 ± 0.50 (1.62) |
| forward/right | p | 0.823 | 25/25 | 0 | 24 | 1.06 ± 0.24 (1.10) | 7.00 ± 3.91 (6.03) | 1.80 ± 0.38 (1.73) | 3.75 ± 0.83 (3.56) | 1.43 ± 0.51 (1.30) |
| left/left | p | 0.837 | 25/25 | 0 | 22 | 1.41 ± 0.34 (1.42) | 8.57 ± 4.59 (8.03) | 2.13 ± 0.39 (2.27) | 4.47 ± 0.90 (4.87) | 1.95 ± 0.61 (2.17) |
| left/right | p | 0.841 | 25/25 | 0 | 22 | 1.63 ± 0.34 (1.58) | 8.46 ± 5.04 (9.79) | 2.17 ± 0.34 (2.24) | 4.59 ± 0.79 (4.82) | 2.03 ± 0.55 (2.15) |
| back/left | p | 0.773 | 25/25 | 0 | 21 | 2.27 ± 0.29 (2.22) | 17.90 ± 28.39 (9.89) | 2.04 ± 0.77 (2.36) | 4.33 ± 1.68 (5.12) | 2.00 ± 0.89 (2.39) |
| back/right | p | 0.797 | 25/25 | 0 | 24 | 2.29 ± 0.30 (2.26) | 10.01 ± 3.73 (11.19) | 2.19 ± 0.35 (2.31) | 4.59 ± 0.85 (4.97) | 2.04 ± 0.59 (2.17) |
| right/left | p | 0.834 | 25/25 | 0 | 25 | 1.66 ± 0.33 (1.64) | 7.31 ± 4.07 (7.97) | 2.15 ± 0.43 (2.20) | 4.52 ± 0.97 (4.85) | 1.98 ± 0.64 (2.20) |
| right/right | p | 0.809 | 25/25 | 0 | 23 | 1.43 ± 0.34 (1.44) | 9.24 ± 4.08 (8.93) | 1.96 ± 0.38 (1.99) | 4.06 ± 0.89 (4.21) | 1.67 ± 0.58 (1.66) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.847 | 7.9 | 4.95 | 2.25 |
| p | normal | 0.793 | 10.6 | 3.61 | 1.41 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.751 | 0.23 | 1.95 ± 0.77 (1.79) | 3.08 | 1.07 |
| p | medium | 16 | 0.866 | 0.86 | 1.03 ± 0.15 (1.02) | 3.33 | 1.20 |
| p | strong | 126 | 0.846 | 0.66 | - | 4.95 | 2.25 |

## Notes

- p: score 0.820, 200/200 kicked, 0 fell; worst sector back (0.785).
