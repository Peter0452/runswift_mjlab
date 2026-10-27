# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_12-23-01_u8_timecost1_anchor02/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.56 ± 0.52 (1.49) |
| Direction error [°] | 6.82 ± 12.03 (5.83) |
| Avg ball speed [m/s] | 2.16 ± 0.45 (2.21) |
| Peak ball speed [m/s] | 4.52 ± 1.01 (4.68) |
| Distance [m] | 2.00 ± 0.66 (2.05) |
| Path length [m] | 2.01 ± 0.66 (2.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.835 | 50/50 | 0 | 50 | 1.02 ± 0.23 (1.06) | 5.86 ± 3.56 (5.12) | 1.95 ± 0.32 (1.86) | 4.06 ± 0.73 (3.85) | 1.64 ± 0.49 (1.49) |
| left | p | 0.866 | 50/50 | 0 | 49 | 1.51 ± 0.34 (1.50) | 5.52 ± 3.64 (5.46) | 2.27 ± 0.33 (2.32) | 4.78 ± 0.77 (4.94) | 2.16 ± 0.56 (2.22) |
| back | p | 0.833 | 50/50 | 0 | 47 | 2.22 ± 0.25 (2.19) | 9.66 ± 23.01 (5.62) | 2.24 ± 0.63 (2.45) | 4.71 ± 1.38 (5.26) | 2.20 ± 0.80 (2.49) |
| right | p | 0.838 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.46) | 6.26 ± 3.60 (6.48) | 2.17 ± 0.36 (2.21) | 4.53 ± 0.85 (4.67) | 1.98 ± 0.59 (2.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 97 | 1.57 ± 0.53 (1.50) | 5.94 ± 4.13 (5.49) | 2.15 ± 0.46 (2.24) | 4.52 ± 1.03 (4.71) | 2.00 ± 0.66 (2.06) |
| right | p | 0.840 | 100/100 | 0 | 99 | 1.56 ± 0.51 (1.47) | 7.71 ± 16.46 (6.02) | 2.16 ± 0.44 (2.20) | 4.52 ± 0.98 (4.67) | 1.99 ± 0.66 (2.03) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.842 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 5.50 ± 3.33 (5.90) | 1.98 ± 0.27 (1.96) | 4.12 ± 0.67 (4.04) | 1.68 ± 0.47 (1.61) |
| forward/right | p | 0.828 | 25/25 | 0 | 25 | 1.02 ± 0.24 (1.04) | 6.22 ± 3.75 (5.12) | 1.92 ± 0.36 (1.83) | 3.99 ± 0.78 (3.78) | 1.60 ± 0.51 (1.42) |
| left/left | p | 0.860 | 25/25 | 0 | 24 | 1.40 ± 0.34 (1.46) | 5.57 ± 4.09 (5.15) | 2.21 ± 0.32 (2.29) | 4.64 ± 0.77 (4.88) | 2.05 ± 0.53 (2.22) |
| left/right | p | 0.872 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.62) | 5.47 ± 3.12 (5.76) | 2.33 ± 0.34 (2.35) | 4.92 ± 0.76 (4.94) | 2.26 ± 0.57 (2.22) |
| back/left | p | 0.830 | 25/25 | 0 | 23 | 2.26 ± 0.25 (2.20) | 6.96 ± 5.21 (5.60) | 2.23 ± 0.69 (2.47) | 4.69 ± 1.51 (5.40) | 2.21 ± 0.84 (2.58) |
| back/right | p | 0.836 | 25/25 | 0 | 24 | 2.18 ± 0.25 (2.10) | 12.35 ± 31.89 (5.64) | 2.25 ± 0.56 (2.41) | 4.73 ± 1.23 (5.08) | 2.19 ± 0.75 (2.31) |
| right/left | p | 0.850 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.60) | 5.74 ± 3.42 (5.39) | 2.20 ± 0.37 (2.27) | 4.62 ± 0.86 (4.95) | 2.05 ± 0.60 (2.18) |
| right/right | p | 0.827 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.46) | 6.79 ± 3.69 (6.67) | 2.14 ± 0.35 (2.13) | 4.45 ± 0.82 (4.50) | 1.91 ± 0.57 (1.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.876 | 5.5 | 5.10 | 2.38 |
| p | normal | 0.809 | 8.2 | 3.94 | 1.62 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.756 | 0.15 | 2.20 ± 0.85 (2.06) | 3.44 | 1.29 |
| p | medium | 16 | 0.886 | 0.82 | 1.14 ± 0.17 (1.16) | 3.68 | 1.41 |
| p | strong | 126 | 0.878 | 0.68 | - | 5.13 | 2.40 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector back (0.833).
