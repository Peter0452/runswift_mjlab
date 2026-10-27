# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_05-06-31_u4c_u4b_lowcap03/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.54 ± 0.49 (1.46) |
| Direction error [°] | 6.46 ± 12.15 (5.37) |
| Avg ball speed [m/s] | 1.95 ± 0.40 (2.02) |
| Peak ball speed [m/s] | 4.12 ± 0.89 (4.35) |
| Distance [m] | 1.52 ± 0.53 (1.53) |
| Path length [m] | 1.53 ± 0.53 (1.54) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.852 | 50/50 | 0 | 49 | 1.07 ± 0.21 (1.07) | 4.47 ± 3.61 (3.14) | 1.73 ± 0.37 (1.80) | 3.73 ± 0.83 (3.76) | 1.24 ± 0.46 (1.17) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.45 ± 0.32 (1.46) | 5.52 ± 3.11 (4.61) | 1.97 ± 0.31 (2.07) | 4.21 ± 0.72 (4.51) | 1.56 ± 0.44 (1.63) |
| back | p | 0.826 | 50/50 | 0 | 48 | 2.19 ± 0.26 (2.14) | 10.34 ± 23.14 (6.75) | 2.17 ± 0.41 (2.29) | 4.49 ± 0.95 (4.88) | 1.82 ± 0.55 (1.97) |
| right | p | 0.847 | 50/50 | 0 | 50 | 1.46 ± 0.32 (1.42) | 5.49 ± 3.32 (5.41) | 1.91 ± 0.39 (1.94) | 4.03 ± 0.88 (4.22) | 1.47 ± 0.50 (1.51) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.55 ± 0.51 (1.46) | 5.49 ± 3.17 (4.87) | 1.97 ± 0.36 (2.04) | 4.16 ± 0.83 (4.42) | 1.54 ± 0.52 (1.53) |
| right | p | 0.846 | 100/100 | 0 | 97 | 1.53 ± 0.48 (1.44) | 7.42 ± 16.83 (5.60) | 1.92 ± 0.44 (1.93) | 4.07 ± 0.95 (4.28) | 1.50 ± 0.55 (1.54) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.850 | 25/25 | 0 | 25 | 1.08 ± 0.22 (1.12) | 4.61 ± 3.35 (3.88) | 1.75 ± 0.31 (1.80) | 3.75 ± 0.76 (3.67) | 1.24 ± 0.41 (1.23) |
| forward/right | p | 0.854 | 25/25 | 0 | 24 | 1.06 ± 0.20 (1.06) | 4.33 ± 3.86 (2.68) | 1.72 ± 0.42 (1.82) | 3.70 ± 0.90 (3.85) | 1.23 ± 0.50 (1.16) |
| left/left | p | 0.857 | 25/25 | 0 | 25 | 1.35 ± 0.31 (1.42) | 5.85 ± 3.19 (4.64) | 1.91 ± 0.33 (2.05) | 4.07 ± 0.76 (4.35) | 1.46 ± 0.45 (1.54) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.55 ± 0.30 (1.54) | 5.19 ± 3.00 (4.58) | 2.04 ± 0.28 (2.12) | 4.35 ± 0.65 (4.60) | 1.65 ± 0.42 (1.64) |
| back/left | p | 0.830 | 25/25 | 0 | 25 | 2.23 ± 0.29 (2.14) | 6.53 ± 2.58 (6.81) | 2.25 ± 0.25 (2.35) | 4.64 ± 0.69 (4.93) | 1.91 ± 0.47 (2.09) |
| back/right | p | 0.822 | 25/25 | 0 | 23 | 2.14 ± 0.23 (2.14) | 14.15 ± 32.18 (6.70) | 2.09 ± 0.51 (2.25) | 4.34 ± 1.13 (4.78) | 1.74 ± 0.61 (1.87) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.56 ± 0.31 (1.56) | 4.99 ± 3.17 (3.62) | 1.97 ± 0.35 (2.11) | 4.17 ± 0.84 (4.57) | 1.56 ± 0.49 (1.64) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.37 ± 0.31 (1.38) | 6.00 ± 3.40 (5.89) | 1.84 ± 0.41 (1.86) | 3.89 ± 0.90 (4.00) | 1.39 ± 0.49 (1.32) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.867 | 5.4 | 4.64 | 1.80 |
| p | normal | 0.827 | 7.5 | 3.59 | 1.25 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.792 | 0.25 | 1.98 ± 0.69 (1.86) | 3.13 | 0.98 |
| p | medium | 16 | 0.888 | 0.87 | 0.99 ± 0.15 (1.03) | 3.22 | 1.03 |
| p | strong | 126 | 0.867 | 0.62 | - | 4.68 | 1.84 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.826).
