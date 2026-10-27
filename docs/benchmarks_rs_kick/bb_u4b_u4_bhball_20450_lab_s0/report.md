# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.52 ± 0.52 (1.46) |
| Direction error [°] | 6.20 ± 3.90 (5.66) |
| Avg ball speed [m/s] | 1.75 ± 0.47 (1.87) |
| Peak ball speed [m/s] | 3.90 ± 1.10 (4.25) |
| Distance [m] | 1.34 ± 0.60 (1.39) |
| Path length [m] | 1.35 ± 0.61 (1.40) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.859 | 50/50 | 0 | 50 | 1.00 ± 0.23 (1.04) | 4.95 ± 3.51 (3.97) | 1.50 ± 0.47 (1.49) | 3.30 ± 1.04 (3.37) | 0.99 ± 0.52 (0.90) |
| left | p | 0.857 | 50/50 | 0 | 49 | 1.46 ± 0.35 (1.46) | 6.72 ± 4.58 (6.79) | 1.80 ± 0.45 (1.98) | 4.06 ± 1.04 (4.51) | 1.41 ± 0.56 (1.51) |
| back | p | 0.847 | 50/50 | 0 | 50 | 2.18 ± 0.27 (2.14) | 6.24 ± 2.45 (6.32) | 1.98 ± 0.41 (2.10) | 4.40 ± 0.99 (4.85) | 1.65 ± 0.59 (1.87) |
| right | p | 0.842 | 50/50 | 0 | 48 | 1.46 ± 0.35 (1.45) | 6.88 ± 4.40 (6.04) | 1.73 ± 0.44 (1.83) | 3.84 ± 1.04 (4.22) | 1.30 ± 0.55 (1.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 99 | 1.53 ± 0.53 (1.47) | 6.30 ± 4.15 (5.66) | 1.76 ± 0.47 (1.90) | 3.93 ± 1.10 (4.37) | 1.36 ± 0.61 (1.42) |
| right | p | 0.855 | 100/100 | 0 | 98 | 1.52 ± 0.51 (1.45) | 6.09 ± 3.62 (5.66) | 1.74 ± 0.48 (1.83) | 3.87 ± 1.11 (4.12) | 1.32 ± 0.60 (1.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.850 | 25/25 | 0 | 25 | 1.00 ± 0.23 (1.06) | 5.63 ± 3.79 (4.28) | 1.56 ± 0.47 (1.57) | 3.41 ± 1.04 (3.40) | 1.06 ± 0.55 (0.92) |
| forward/right | p | 0.868 | 25/25 | 0 | 25 | 0.99 ± 0.22 (1.04) | 4.27 ± 3.05 (3.39) | 1.44 ± 0.47 (1.39) | 3.20 ± 1.03 (2.94) | 0.92 ± 0.48 (0.89) |
| left/left | p | 0.844 | 25/25 | 0 | 24 | 1.34 ± 0.33 (1.40) | 7.19 ± 5.46 (5.16) | 1.65 ± 0.47 (1.81) | 3.73 ± 1.07 (4.04) | 1.22 ± 0.56 (1.37) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.58 ± 0.33 (1.64) | 6.25 ± 3.41 (6.94) | 1.95 ± 0.38 (2.05) | 4.38 ± 0.89 (4.72) | 1.61 ± 0.48 (1.71) |
| back/left | p | 0.846 | 25/25 | 0 | 25 | 2.20 ± 0.27 (2.16) | 5.94 ± 2.51 (5.76) | 2.02 ± 0.34 (2.10) | 4.50 ± 0.88 (4.91) | 1.70 ± 0.55 (1.92) |
| back/right | p | 0.848 | 25/25 | 0 | 25 | 2.15 ± 0.28 (2.12) | 6.53 ± 2.35 (6.50) | 1.94 ± 0.47 (2.05) | 4.30 ± 1.08 (4.71) | 1.59 ± 0.62 (1.69) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.56 ± 0.34 (1.52) | 6.44 ± 4.15 (6.15) | 1.83 ± 0.44 (1.95) | 4.10 ± 1.07 (4.49) | 1.45 ± 0.57 (1.57) |
| right/right | p | 0.834 | 25/25 | 0 | 23 | 1.36 ± 0.33 (1.38) | 7.32 ± 4.59 (5.92) | 1.63 ± 0.41 (1.72) | 3.59 ± 0.93 (3.84) | 1.16 ± 0.50 (1.22) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.859 | 6.0 | 4.57 | 1.68 |
| p | normal | 0.843 | 6.4 | 3.23 | 1.00 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.823 | 0.44 | 1.63 ± 0.56 (1.47) | 2.61 | 0.66 |
| p | medium | 16 | 0.882 | 0.79 | 0.88 ± 0.23 (0.93) | 2.86 | 0.81 |
| p | strong | 126 | 0.860 | 0.62 | - | 4.63 | 1.72 |

## Notes

- p: score 0.851, 200/200 kicked, 0 fell; worst sector right (0.842).
