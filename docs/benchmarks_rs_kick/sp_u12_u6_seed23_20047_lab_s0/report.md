# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-01-05_u12_u6_seed23/model_20047.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.834** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.54 ± 0.52 (1.46) |
| Direction error [°] | 7.38 ± 11.60 (6.17) |
| Avg ball speed [m/s] | 2.09 ± 0.38 (2.08) |
| Peak ball speed [m/s] | 4.43 ± 0.86 (4.51) |
| Distance [m] | 1.92 ± 0.58 (1.93) |
| Path length [m] | 1.93 ± 0.58 (1.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.825 | 50/50 | 0 | 49 | 1.02 ± 0.22 (1.06) | 6.43 ± 3.68 (6.17) | 1.91 ± 0.31 (1.85) | 4.01 ± 0.70 (3.82) | 1.61 ± 0.48 (1.47) |
| left | p | 0.854 | 50/50 | 0 | 50 | 1.47 ± 0.32 (1.49) | 6.46 ± 3.49 (6.35) | 2.18 ± 0.28 (2.20) | 4.61 ± 0.66 (4.77) | 2.04 ± 0.47 (2.13) |
| back | p | 0.835 | 50/50 | 0 | 48 | 2.16 ± 0.24 (2.13) | 9.51 ± 22.11 (5.72) | 2.17 ± 0.51 (2.32) | 4.60 ± 1.13 (4.96) | 2.09 ± 0.68 (2.32) |
| right | p | 0.822 | 50/50 | 0 | 50 | 1.52 ± 0.48 (1.43) | 7.10 ± 4.10 (6.63) | 2.12 ± 0.30 (2.07) | 4.50 ± 0.74 (4.49) | 1.96 ± 0.52 (1.89) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.835 | 100/100 | 0 | 98 | 1.56 ± 0.56 (1.48) | 6.65 ± 3.98 (5.88) | 2.09 ± 0.36 (2.14) | 4.43 ± 0.85 (4.66) | 1.92 ± 0.58 (1.91) |
| right | p | 0.833 | 100/100 | 0 | 99 | 1.52 ± 0.48 (1.46) | 8.10 ± 15.88 (6.35) | 2.10 ± 0.39 (2.07) | 4.43 ± 0.87 (4.50) | 1.92 ± 0.57 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.817 | 25/25 | 0 | 24 | 1.03 ± 0.22 (1.06) | 7.59 ± 3.70 (7.48) | 1.92 ± 0.27 (1.86) | 4.00 ± 0.62 (3.78) | 1.61 ± 0.46 (1.46) |
| forward/right | p | 0.832 | 25/25 | 0 | 25 | 1.01 ± 0.22 (1.04) | 5.26 ± 3.27 (4.24) | 1.90 ± 0.34 (1.84) | 4.02 ± 0.76 (3.83) | 1.61 ± 0.49 (1.49) |
| left/left | p | 0.853 | 25/25 | 0 | 25 | 1.39 ± 0.32 (1.46) | 6.46 ± 3.55 (5.84) | 2.16 ± 0.26 (2.25) | 4.58 ± 0.66 (4.91) | 2.01 ± 0.47 (2.21) |
| left/right | p | 0.855 | 25/25 | 0 | 25 | 1.56 ± 0.28 (1.56) | 6.46 ± 3.43 (6.96) | 2.20 ± 0.30 (2.20) | 4.64 ± 0.65 (4.69) | 2.06 ± 0.47 (2.07) |
| back/left | p | 0.837 | 25/25 | 0 | 24 | 2.19 ± 0.25 (2.14) | 6.22 ± 4.60 (5.16) | 2.18 ± 0.50 (2.37) | 4.63 ± 1.13 (5.15) | 2.11 ± 0.69 (2.39) |
| back/right | p | 0.832 | 25/25 | 0 | 24 | 2.14 ± 0.22 (2.12) | 12.81 ± 30.58 (6.55) | 2.16 ± 0.51 (2.31) | 4.57 ± 1.13 (4.91) | 2.07 ± 0.67 (2.22) |
| right/left | p | 0.832 | 25/25 | 0 | 25 | 1.65 ± 0.57 (1.52) | 6.33 ± 3.82 (5.28) | 2.09 ± 0.29 (2.12) | 4.51 ± 0.75 (4.70) | 1.96 ± 0.53 (1.90) |
| right/right | p | 0.813 | 25/25 | 0 | 25 | 1.39 ± 0.32 (1.40) | 7.87 ± 4.22 (7.46) | 2.14 ± 0.31 (2.07) | 4.50 ± 0.74 (4.47) | 1.96 ± 0.52 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.867 | 5.9 | 4.91 | 2.24 |
| p | normal | 0.801 | 8.8 | 3.95 | 1.61 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.747 | 0.13 | 2.24 ± 0.81 (2.14) | 3.52 | 1.32 |
| p | medium | 16 | 0.885 | 0.85 | 1.14 ± 0.12 (1.12) | 3.70 | 1.42 |
| p | strong | 126 | 0.868 | 0.66 | - | 4.94 | 2.26 |

## Notes

- p: score 0.834, 200/200 kicked, 0 fell; worst sector right (0.822).
