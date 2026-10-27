# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.54 (1.49) |
| Direction error [°] | 6.10 ± 8.58 (4.97) |
| Avg ball speed [m/s] | 1.66 ± 0.38 (1.73) |
| Peak ball speed [m/s] | 4.05 ± 0.91 (4.12) |
| Distance [m] | 1.40 ± 0.51 (1.42) |
| Path length [m] | 1.41 ± 0.51 (1.43) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.836 | 50/50 | 0 | 48 | 1.08 ± 0.40 (1.06) | 7.21 ± 15.78 (4.25) | 1.44 ± 0.43 (1.35) | 3.45 ± 0.97 (3.33) | 1.06 ± 0.49 (0.95) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.53) | 5.66 ± 4.00 (4.80) | 1.70 ± 0.33 (1.75) | 4.16 ± 0.80 (4.24) | 1.46 ± 0.44 (1.50) |
| back | p | 0.840 | 50/50 | 0 | 50 | 2.24 ± 0.27 (2.18) | 5.43 ± 2.79 (5.23) | 1.87 ± 0.27 (1.92) | 4.57 ± 0.67 (4.79) | 1.73 ± 0.43 (1.83) |
| right | p | 0.841 | 50/50 | 0 | 47 | 1.49 ± 0.35 (1.43) | 6.13 ± 4.45 (5.40) | 1.65 ± 0.34 (1.68) | 4.03 ± 0.82 (4.04) | 1.37 ± 0.44 (1.33) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 99 | 1.58 ± 0.53 (1.53) | 5.78 ± 3.57 (5.22) | 1.67 ± 0.37 (1.75) | 4.07 ± 0.91 (4.12) | 1.41 ± 0.52 (1.46) |
| right | p | 0.845 | 100/100 | 0 | 96 | 1.58 ± 0.56 (1.46) | 6.43 ± 11.59 (4.71) | 1.66 ± 0.39 (1.71) | 4.03 ± 0.92 (4.13) | 1.39 ± 0.51 (1.41) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 24 | 1.04 ± 0.23 (1.06) | 5.73 ± 3.94 (5.15) | 1.46 ± 0.43 (1.44) | 3.46 ± 0.94 (3.42) | 1.07 ± 0.49 (1.02) |
| forward/right | p | 0.834 | 25/25 | 0 | 24 | 1.12 ± 0.52 (1.04) | 8.70 ± 21.86 (4.04) | 1.42 ± 0.43 (1.31) | 3.44 ± 0.99 (3.07) | 1.04 ± 0.50 (0.87) |
| left/left | p | 0.845 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.50) | 6.39 ± 4.25 (5.21) | 1.63 ± 0.31 (1.71) | 3.99 ± 0.75 (4.01) | 1.35 ± 0.40 (1.41) |
| left/right | p | 0.874 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.62) | 4.93 ± 3.59 (4.20) | 1.77 ± 0.32 (1.81) | 4.33 ± 0.82 (4.48) | 1.57 ± 0.45 (1.72) |
| back/left | p | 0.840 | 25/25 | 0 | 25 | 2.26 ± 0.25 (2.18) | 5.58 ± 2.94 (5.23) | 1.89 ± 0.25 (1.95) | 4.66 ± 0.66 (4.81) | 1.79 ± 0.43 (1.93) |
| back/right | p | 0.840 | 25/25 | 0 | 25 | 2.22 ± 0.29 (2.16) | 5.27 ± 2.62 (5.23) | 1.86 ± 0.30 (1.91) | 4.47 ± 0.67 (4.76) | 1.66 ± 0.42 (1.74) |
| right/left | p | 0.850 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.56) | 5.42 ± 2.87 (5.57) | 1.70 ± 0.33 (1.80) | 4.17 ± 0.82 (4.39) | 1.44 ± 0.46 (1.52) |
| right/right | p | 0.831 | 25/25 | 0 | 22 | 1.38 ± 0.35 (1.38) | 6.83 ± 5.52 (5.22) | 1.59 ± 0.33 (1.56) | 3.89 ± 0.81 (3.60) | 1.30 ± 0.41 (1.27) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.861 | 5.4 | 4.47 | 1.62 |
| p | normal | 0.827 | 6.9 | 3.63 | 1.18 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.784 | 0.27 | 2.03 ± 0.72 (1.83) | 3.23 | 0.96 |
| p | medium | 16 | 0.912 | 0.86 | 1.00 ± 0.17 (0.99) | 3.25 | 0.97 |
| p | strong | 126 | 0.863 | 0.60 | - | 4.53 | 1.66 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector forward (0.836).
