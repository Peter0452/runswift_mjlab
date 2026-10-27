# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.842** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.57 ± 0.51 (1.50) |
| Direction error [°] | 6.79 ± 12.00 (5.39) |
| Avg ball speed [m/s] | 1.79 ± 0.40 (1.92) |
| Peak ball speed [m/s] | 3.87 ± 0.93 (4.16) |
| Distance [m] | 1.34 ± 0.50 (1.42) |
| Path length [m] | 1.35 ± 0.50 (1.42) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.850 | 50/50 | 0 | 49 | 1.05 ± 0.22 (1.06) | 4.80 ± 3.49 (3.48) | 1.53 ± 0.41 (1.47) | 3.31 ± 0.89 (3.13) | 1.00 ± 0.46 (0.86) |
| left | p | 0.860 | 50/50 | 0 | 48 | 1.52 ± 0.33 (1.54) | 5.86 ± 4.36 (4.55) | 1.88 ± 0.36 (1.99) | 4.11 ± 0.87 (4.46) | 1.48 ± 0.50 (1.57) |
| back | p | 0.815 | 50/50 | 0 | 49 | 2.23 ± 0.26 (2.19) | 10.48 ± 22.67 (7.85) | 1.94 ± 0.36 (2.06) | 4.21 ± 0.87 (4.51) | 1.56 ± 0.44 (1.68) |
| right | p | 0.842 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.48) | 6.03 ± 3.41 (5.00) | 1.79 ± 0.33 (1.87) | 3.87 ± 0.80 (4.09) | 1.32 ± 0.40 (1.35) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.834 | 100/100 | 0 | 97 | 1.57 ± 0.51 (1.52) | 7.96 ± 16.52 (5.68) | 1.78 ± 0.39 (1.93) | 3.86 ± 0.92 (4.19) | 1.33 ± 0.49 (1.42) |
| right | p | 0.849 | 100/100 | 0 | 99 | 1.58 ± 0.52 (1.50) | 5.63 ± 3.50 (4.95) | 1.80 ± 0.41 (1.87) | 3.89 ± 0.94 (4.09) | 1.35 ± 0.52 (1.43) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 25 | 1.05 ± 0.21 (1.08) | 5.12 ± 3.56 (3.91) | 1.56 ± 0.37 (1.42) | 3.34 ± 0.79 (2.94) | 1.03 ± 0.43 (0.81) |
| forward/right | p | 0.855 | 25/25 | 0 | 24 | 1.05 ± 0.23 (1.04) | 4.48 ± 3.39 (3.16) | 1.50 ± 0.45 (1.48) | 3.28 ± 0.98 (3.25) | 0.97 ± 0.49 (0.91) |
| left/left | p | 0.838 | 25/25 | 0 | 23 | 1.42 ± 0.34 (1.50) | 7.12 ± 5.18 (6.00) | 1.81 ± 0.35 (1.93) | 3.94 ± 0.86 (4.23) | 1.39 ± 0.47 (1.47) |
| left/right | p | 0.881 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.60) | 4.61 ± 2.85 (4.35) | 1.96 ± 0.36 (2.11) | 4.28 ± 0.84 (4.69) | 1.58 ± 0.51 (1.75) |
| back/left | p | 0.803 | 25/25 | 0 | 24 | 2.23 ± 0.25 (2.18) | 13.97 ± 31.50 (8.24) | 1.92 ± 0.39 (2.07) | 4.17 ± 0.94 (4.54) | 1.55 ± 0.47 (1.68) |
| back/right | p | 0.827 | 25/25 | 0 | 25 | 2.23 ± 0.27 (2.22) | 6.99 ± 3.36 (7.72) | 1.96 ± 0.31 (2.06) | 4.24 ± 0.79 (4.49) | 1.57 ± 0.42 (1.69) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.58) | 5.62 ± 3.11 (4.90) | 1.82 ± 0.33 (1.95) | 3.99 ± 0.85 (4.36) | 1.37 ± 0.42 (1.44) |
| right/right | p | 0.833 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.48) | 6.43 ± 3.63 (6.06) | 1.77 ± 0.33 (1.82) | 3.75 ± 0.73 (3.84) | 1.27 ± 0.37 (1.26) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.853 | 6.0 | 4.38 | 1.59 |
| p | normal | 0.830 | 7.6 | 3.37 | 1.09 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.799 | 0.32 | 1.85 ± 0.64 (1.69) | 2.93 | 0.86 |
| p | medium | 16 | 0.893 | 0.83 | 0.89 ± 0.19 (0.94) | 2.90 | 0.83 |
| p | strong | 126 | 0.855 | 0.59 | - | 4.43 | 1.63 |

## Notes

- p: score 0.842, 200/200 kicked, 0 fell; worst sector back (0.815).
