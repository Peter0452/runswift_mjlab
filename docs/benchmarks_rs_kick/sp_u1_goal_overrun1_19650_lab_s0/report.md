# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.63 ± 0.54 (1.56) |
| Direction error [°] | 6.44 ± 12.77 (4.52) |
| Avg ball speed [m/s] | 1.86 ± 0.44 (1.92) |
| Peak ball speed [m/s] | 3.99 ± 0.99 (4.15) |
| Distance [m] | 1.49 ± 0.60 (1.48) |
| Path length [m] | 1.50 ± 0.60 (1.48) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.844 | 50/50 | 0 | 49 | 1.07 ± 0.25 (1.10) | 5.08 ± 3.72 (4.14) | 1.57 ± 0.39 (1.50) | 3.37 ± 0.84 (3.19) | 1.08 ± 0.48 (1.00) |
| left | p | 0.864 | 50/50 | 0 | 50 | 1.58 ± 0.37 (1.58) | 5.55 ± 3.90 (4.12) | 1.95 ± 0.38 (2.07) | 4.20 ± 0.88 (4.52) | 1.61 ± 0.54 (1.67) |
| back | p | 0.837 | 50/50 | 0 | 49 | 2.30 ± 0.27 (2.23) | 8.52 ± 24.49 (5.06) | 2.04 ± 0.42 (2.16) | 4.34 ± 0.99 (4.72) | 1.74 ± 0.58 (1.97) |
| right | p | 0.838 | 50/50 | 0 | 48 | 1.57 ± 0.35 (1.53) | 6.59 ± 4.04 (5.25) | 1.90 ± 0.43 (1.93) | 4.04 ± 0.96 (4.00) | 1.53 ± 0.58 (1.42) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 99 | 1.62 ± 0.54 (1.58) | 7.23 ± 17.59 (4.58) | 1.89 ± 0.44 (1.92) | 4.03 ± 1.00 (4.21) | 1.52 ± 0.60 (1.50) |
| right | p | 0.847 | 100/100 | 0 | 97 | 1.63 ± 0.54 (1.54) | 5.64 ± 3.93 (4.52) | 1.84 ± 0.45 (1.91) | 3.95 ± 0.98 (4.10) | 1.46 ± 0.59 (1.42) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.07 ± 0.25 (1.10) | 5.09 ± 3.20 (4.17) | 1.63 ± 0.36 (1.68) | 3.48 ± 0.80 (3.22) | 1.16 ± 0.48 (1.00) |
| forward/right | p | 0.841 | 25/25 | 0 | 24 | 1.07 ± 0.25 (1.10) | 5.07 ± 4.17 (3.73) | 1.51 ± 0.42 (1.49) | 3.27 ± 0.86 (3.11) | 1.01 ± 0.47 (1.01) |
| left/left | p | 0.850 | 25/25 | 0 | 25 | 1.47 ± 0.37 (1.54) | 6.12 ± 4.45 (3.41) | 1.88 ± 0.37 (1.93) | 4.01 ± 0.88 (4.30) | 1.49 ± 0.52 (1.42) |
| left/right | p | 0.879 | 25/25 | 0 | 25 | 1.68 ± 0.33 (1.68) | 4.99 ± 3.15 (4.52) | 2.03 ± 0.36 (2.12) | 4.39 ± 0.84 (4.59) | 1.72 ± 0.53 (1.78) |
| back/left | p | 0.834 | 25/25 | 0 | 24 | 2.29 ± 0.28 (2.22) | 11.56 ± 34.22 (4.90) | 2.03 ± 0.47 (2.13) | 4.33 ± 1.09 (4.64) | 1.75 ± 0.63 (1.87) |
| back/right | p | 0.839 | 25/25 | 0 | 25 | 2.31 ± 0.26 (2.30) | 5.48 ± 3.25 (5.89) | 2.04 ± 0.37 (2.19) | 4.36 ± 0.88 (4.82) | 1.73 ± 0.53 (1.97) |
| right/left | p | 0.847 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.62) | 6.15 ± 3.32 (5.19) | 2.02 ± 0.42 (2.15) | 4.30 ± 0.97 (4.74) | 1.69 ± 0.59 (1.80) |
| right/right | p | 0.828 | 25/25 | 0 | 23 | 1.46 ± 0.35 (1.52) | 7.03 ± 4.61 (5.63) | 1.78 ± 0.41 (1.74) | 3.78 ± 0.87 (3.65) | 1.36 ± 0.52 (1.26) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.862 | 5.3 | 4.56 | 1.81 |
| p | normal | 0.830 | 7.6 | 3.42 | 1.17 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.801 | 0.31 | 1.89 ± 0.67 (1.71) | 2.98 | 0.91 |
| p | medium | 16 | 0.876 | 0.82 | 0.89 ± 0.19 (0.87) | 2.88 | 0.84 |
| p | strong | 126 | 0.863 | 0.61 | - | 4.60 | 1.84 |

## Notes

- p: score 0.846, 200/200 kicked, 0 fell; worst sector back (0.837).
