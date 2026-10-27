# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u10_u6_seed11/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.53 (1.46) |
| Direction error [°] | 5.49 ± 3.52 (4.92) |
| Avg ball speed [m/s] | 1.82 ± 0.37 (1.96) |
| Peak ball speed [m/s] | 3.95 ± 0.88 (4.25) |
| Distance [m] | 1.38 ± 0.49 (1.44) |
| Path length [m] | 1.38 ± 0.49 (1.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 50 | 1.03 ± 0.22 (1.06) | 4.78 ± 3.64 (2.96) | 1.55 ± 0.40 (1.46) | 3.31 ± 0.84 (3.14) | 1.00 ± 0.46 (0.92) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.51) | 5.66 ± 3.68 (4.53) | 1.91 ± 0.31 (2.03) | 4.18 ± 0.77 (4.52) | 1.50 ± 0.44 (1.57) |
| back | p | 0.836 | 50/50 | 0 | 50 | 2.26 ± 0.27 (2.20) | 5.70 ± 2.85 (5.72) | 2.03 ± 0.22 (2.11) | 4.40 ± 0.66 (4.68) | 1.66 ± 0.38 (1.78) |
| right | p | 0.842 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.45) | 5.85 ± 3.74 (4.94) | 1.80 ± 0.32 (1.92) | 3.91 ± 0.81 (4.27) | 1.34 ± 0.41 (1.39) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 100 | 1.58 ± 0.53 (1.48) | 5.70 ± 3.44 (4.92) | 1.84 ± 0.35 (1.97) | 3.98 ± 0.86 (4.23) | 1.40 ± 0.48 (1.48) |
| right | p | 0.850 | 100/100 | 0 | 100 | 1.57 ± 0.53 (1.46) | 5.28 ± 3.59 (4.77) | 1.81 ± 0.39 (1.93) | 3.92 ± 0.89 (4.25) | 1.35 ± 0.49 (1.43) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.844 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 5.10 ± 3.45 (3.81) | 1.60 ± 0.36 (1.58) | 3.36 ± 0.75 (3.22) | 1.05 ± 0.43 (1.01) |
| forward/right | p | 0.857 | 25/25 | 0 | 25 | 1.02 ± 0.23 (1.04) | 4.46 ± 3.79 (2.49) | 1.50 ± 0.43 (1.39) | 3.25 ± 0.92 (2.89) | 0.95 ± 0.48 (0.83) |
| left/left | p | 0.851 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.46) | 6.27 ± 3.91 (5.02) | 1.84 ± 0.32 (1.98) | 3.99 ± 0.81 (4.44) | 1.41 ± 0.46 (1.51) |
| left/right | p | 0.872 | 25/25 | 0 | 25 | 1.60 ± 0.30 (1.60) | 5.04 ± 3.33 (4.44) | 1.98 ± 0.28 (2.05) | 4.36 ± 0.69 (4.61) | 1.60 ± 0.40 (1.62) |
| back/left | p | 0.834 | 25/25 | 0 | 25 | 2.27 ± 0.27 (2.18) | 6.05 ± 2.89 (6.80) | 2.05 ± 0.19 (2.14) | 4.49 ± 0.65 (4.83) | 1.71 ± 0.39 (1.84) |
| back/right | p | 0.838 | 25/25 | 0 | 25 | 2.25 ± 0.27 (2.28) | 5.34 ± 2.76 (5.52) | 2.01 ± 0.24 (2.10) | 4.32 ± 0.65 (4.66) | 1.60 ± 0.35 (1.62) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.58) | 5.39 ± 3.30 (4.81) | 1.86 ± 0.32 (2.00) | 4.07 ± 0.81 (4.51) | 1.42 ± 0.40 (1.49) |
| right/right | p | 0.833 | 25/25 | 0 | 25 | 1.41 ± 0.35 (1.42) | 6.30 ± 4.09 (7.74) | 1.75 ± 0.32 (1.75) | 3.74 ± 0.77 (3.68) | 1.26 ± 0.40 (1.24) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.860 | 5.4 | 4.44 | 1.63 |
| p | normal | 0.836 | 5.6 | 3.46 | 1.12 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.806 | 0.32 | 1.89 ± 0.62 (1.70) | 3.02 | 0.90 |
| p | medium | 16 | 0.891 | 0.82 | 0.96 ± 0.20 (1.00) | 3.12 | 0.95 |
| p | strong | 126 | 0.861 | 0.60 | - | 4.48 | 1.65 |

## Notes

- p: score 0.848, 200/200 kicked, 0 fell; worst sector back (0.836).
