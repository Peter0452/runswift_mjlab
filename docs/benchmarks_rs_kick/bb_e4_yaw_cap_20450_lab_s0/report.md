# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-47-18_e4_yaw_cap/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.60 ± 0.55 (1.54) |
| Direction error [°] | 6.88 ± 16.97 (4.40) |
| Avg ball speed [m/s] | 1.75 ± 0.37 (1.81) |
| Peak ball speed [m/s] | 4.11 ± 0.87 (4.15) |
| Distance [m] | 1.48 ± 0.49 (1.50) |
| Path length [m] | 1.49 ± 0.49 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.829 | 50/50 | 0 | 48 | 1.14 ± 0.52 (1.08) | 9.06 ± 23.75 (3.38) | 1.48 ± 0.36 (1.47) | 3.48 ± 0.81 (3.29) | 1.11 ± 0.43 (0.95) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.53 ± 0.35 (1.55) | 5.17 ± 3.89 (3.80) | 1.85 ± 0.29 (1.90) | 4.34 ± 0.72 (4.55) | 1.60 ± 0.42 (1.67) |
| back | p | 0.842 | 50/50 | 0 | 49 | 2.24 ± 0.26 (2.21) | 7.88 ± 23.45 (4.73) | 1.89 ± 0.35 (1.98) | 4.47 ± 0.85 (4.77) | 1.73 ± 0.48 (1.81) |
| right | p | 0.838 | 50/50 | 0 | 49 | 1.50 ± 0.34 (1.47) | 5.41 ± 3.40 (4.94) | 1.76 ± 0.30 (1.79) | 4.13 ± 0.73 (4.18) | 1.47 ± 0.40 (1.42) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.835 | 100/100 | 0 | 97 | 1.63 ± 0.57 (1.55) | 9.10 ± 23.55 (4.68) | 1.75 ± 0.35 (1.81) | 4.11 ± 0.84 (4.14) | 1.48 ± 0.47 (1.47) |
| right | p | 0.852 | 100/100 | 0 | 99 | 1.58 ± 0.53 (1.48) | 4.66 ± 3.36 (3.84) | 1.75 ± 0.38 (1.81) | 4.10 ± 0.90 (4.23) | 1.48 ± 0.51 (1.53) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.803 | 25/25 | 0 | 23 | 1.26 ± 0.69 (1.12) | 13.99 ± 32.67 (3.94) | 1.50 ± 0.31 (1.52) | 3.53 ± 0.61 (3.52) | 1.12 ± 0.37 (1.02) |
| forward/right | p | 0.855 | 25/25 | 0 | 25 | 1.02 ± 0.22 (1.04) | 4.12 ± 3.50 (3.29) | 1.46 ± 0.41 (1.39) | 3.44 ± 0.97 (3.05) | 1.09 ± 0.49 (0.88) |
| left/left | p | 0.849 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.50) | 6.25 ± 4.41 (4.47) | 1.77 ± 0.24 (1.77) | 4.12 ± 0.66 (4.13) | 1.48 ± 0.34 (1.46) |
| left/right | p | 0.881 | 25/25 | 0 | 25 | 1.64 ± 0.32 (1.60) | 4.09 ± 2.92 (3.43) | 1.94 ± 0.31 (1.98) | 4.56 ± 0.70 (4.80) | 1.73 ± 0.45 (1.83) |
| back/left | p | 0.836 | 25/25 | 0 | 24 | 2.23 ± 0.25 (2.18) | 11.16 ± 32.74 (4.71) | 1.87 ± 0.40 (1.92) | 4.41 ± 1.00 (4.78) | 1.73 ± 0.54 (1.84) |
| back/right | p | 0.848 | 25/25 | 0 | 25 | 2.25 ± 0.26 (2.22) | 4.60 ± 2.54 (4.91) | 1.91 ± 0.28 (2.00) | 4.53 ± 0.67 (4.77) | 1.73 ± 0.41 (1.78) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.58) | 4.99 ± 2.63 (4.79) | 1.84 ± 0.29 (1.90) | 4.36 ± 0.71 (4.65) | 1.60 ± 0.39 (1.72) |
| right/right | p | 0.824 | 25/25 | 0 | 24 | 1.40 ± 0.32 (1.40) | 5.82 ± 3.98 (5.10) | 1.67 ± 0.29 (1.64) | 3.89 ± 0.68 (3.76) | 1.35 ± 0.36 (1.33) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.867 | 4.8 | 4.50 | 1.67 |
| p | normal | 0.820 | 9.0 | 3.72 | 1.29 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.773 | 0.20 | 2.11 ± 0.75 (1.99) | 3.33 | 1.06 |
| p | medium | 16 | 0.899 | 0.85 | 1.04 ± 0.19 (1.00) | 3.37 | 1.09 |
| p | strong | 126 | 0.869 | 0.61 | - | 4.56 | 1.72 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector forward (0.829).
