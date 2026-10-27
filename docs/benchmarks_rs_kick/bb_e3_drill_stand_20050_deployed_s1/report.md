# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-18-00_e3_drill_stand/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.84 ± 0.59 (1.71) |
| Direction error [°] | 5.28 ± 3.91 (4.62) |
| Avg ball speed [m/s] | 2.39 ± 0.33 (2.42) |
| Peak ball speed [m/s] | 5.12 ± 0.86 (5.43) |
| Distance [m] | 2.29 ± 0.61 (2.37) |
| Path length [m] | 2.30 ± 0.61 (2.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.866 | 50/50 | 0 | 48 | 1.26 ± 0.25 (1.27) | 5.25 ± 4.56 (4.15) | 2.38 ± 0.38 (2.44) | 5.12 ± 0.96 (5.51) | 2.27 ± 0.63 (2.42) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.74 ± 0.34 (1.73) | 5.39 ± 3.61 (5.07) | 2.36 ± 0.29 (2.30) | 5.05 ± 0.80 (5.33) | 2.23 ± 0.56 (2.22) |
| back | p | 0.810 | 50/50 | 0 | 50 | 2.61 ± 0.40 (2.58) | 5.67 ± 3.23 (5.68) | 2.51 ± 0.29 (2.49) | 5.36 ± 0.79 (5.50) | 2.49 ± 0.59 (2.51) |
| right | p | 0.852 | 50/50 | 0 | 49 | 1.74 ± 0.35 (1.70) | 4.81 ± 4.08 (3.37) | 2.32 ± 0.31 (2.29) | 4.96 ± 0.83 (5.15) | 2.17 ± 0.59 (2.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 99 | 1.82 ± 0.57 (1.69) | 5.31 ± 3.84 (4.77) | 2.39 ± 0.33 (2.43) | 5.15 ± 0.85 (5.45) | 2.31 ± 0.61 (2.39) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.85 ± 0.61 (1.76) | 5.26 ± 3.99 (4.24) | 2.39 ± 0.33 (2.40) | 5.10 ± 0.87 (5.43) | 2.27 ± 0.60 (2.29) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.865 | 25/25 | 0 | 24 | 1.24 ± 0.26 (1.26) | 4.91 ± 4.53 (3.19) | 2.34 ± 0.36 (2.47) | 5.06 ± 0.98 (5.51) | 2.25 ± 0.65 (2.48) |
| forward/right | p | 0.867 | 25/25 | 0 | 24 | 1.29 ± 0.24 (1.30) | 5.58 ± 4.57 (4.41) | 2.42 ± 0.40 (2.44) | 5.17 ± 0.94 (5.50) | 2.29 ± 0.62 (2.25) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.67 ± 0.33 (1.58) | 5.88 ± 3.74 (5.28) | 2.37 ± 0.25 (2.28) | 5.10 ± 0.74 (5.31) | 2.26 ± 0.51 (2.26) |
| left/right | p | 0.866 | 25/25 | 0 | 25 | 1.81 ± 0.34 (1.86) | 4.91 ± 3.41 (4.07) | 2.35 ± 0.32 (2.31) | 5.01 ± 0.85 (5.35) | 2.19 ± 0.60 (2.07) |
| back/left | p | 0.804 | 25/25 | 0 | 25 | 2.57 ± 0.27 (2.54) | 6.49 ± 3.19 (7.17) | 2.53 ± 0.30 (2.53) | 5.42 ± 0.76 (5.55) | 2.55 ± 0.59 (2.63) |
| back/right | p | 0.816 | 25/25 | 0 | 25 | 2.64 ± 0.50 (2.58) | 4.85 ± 3.05 (4.01) | 2.49 ± 0.28 (2.44) | 5.29 ± 0.81 (5.45) | 2.43 ± 0.58 (2.51) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.82 ± 0.36 (1.70) | 3.94 ± 3.23 (2.76) | 2.33 ± 0.34 (2.31) | 5.01 ± 0.86 (5.16) | 2.18 ± 0.62 (2.01) |
| right/right | p | 0.851 | 25/25 | 0 | 24 | 1.66 ± 0.33 (1.70) | 5.68 ± 4.62 (4.54) | 2.32 ± 0.27 (2.27) | 4.92 ± 0.80 (5.14) | 2.16 ± 0.56 (2.06) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.886 | 5.0 | 5.71 | 2.65 |
| p | normal | 0.809 | 5.6 | 4.54 | 1.93 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.751 | 0.08 | 2.62 ± 0.80 (2.53) | 4.08 | 1.61 |
| p | medium | 20 | 0.871 | 0.72 | 1.28 ± 0.15 (1.31) | 4.11 | 1.65 |
| p | strong | 126 | 0.885 | 0.76 | - | 5.73 | 2.68 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.810).
