# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-47-18_e4_yaw_cap/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.82 ± 0.59 (1.72) |
| Direction error [°] | 5.36 ± 3.55 (4.75) |
| Avg ball speed [m/s] | 2.33 ± 0.29 (2.33) |
| Peak ball speed [m/s] | 5.10 ± 0.83 (5.44) |
| Distance [m] | 2.15 ± 0.54 (2.21) |
| Path length [m] | 2.16 ± 0.54 (2.22) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.870 | 50/50 | 0 | 49 | 1.24 ± 0.27 (1.27) | 4.79 ± 3.87 (3.55) | 2.29 ± 0.35 (2.36) | 5.07 ± 0.95 (5.46) | 2.10 ± 0.60 (2.28) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.75 ± 0.37 (1.72) | 5.29 ± 3.22 (4.83) | 2.32 ± 0.26 (2.31) | 5.05 ± 0.76 (5.30) | 2.11 ± 0.49 (2.08) |
| back | p | 0.810 | 50/50 | 0 | 50 | 2.57 ± 0.38 (2.49) | 5.90 ± 2.86 (5.84) | 2.43 ± 0.26 (2.44) | 5.29 ± 0.73 (5.59) | 2.31 ± 0.49 (2.33) |
| right | p | 0.847 | 50/50 | 0 | 49 | 1.72 ± 0.35 (1.68) | 5.45 ± 4.02 (4.08) | 2.28 ± 0.26 (2.29) | 4.97 ± 0.82 (5.29) | 2.07 ± 0.53 (2.06) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 99 | 1.82 ± 0.57 (1.70) | 5.27 ± 3.70 (4.54) | 2.33 ± 0.31 (2.35) | 5.11 ± 0.83 (5.45) | 2.16 ± 0.54 (2.24) |
| right | p | 0.848 | 100/100 | 0 | 99 | 1.82 ± 0.61 (1.75) | 5.45 ± 3.38 (4.89) | 2.33 ± 0.28 (2.32) | 5.08 ± 0.82 (5.40) | 2.14 ± 0.53 (2.15) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 25 | 1.22 ± 0.26 (1.24) | 5.07 ± 3.84 (4.03) | 2.25 ± 0.37 (2.35) | 5.01 ± 0.98 (5.45) | 2.06 ± 0.61 (2.30) |
| forward/right | p | 0.876 | 25/25 | 0 | 24 | 1.26 ± 0.27 (1.30) | 4.52 ± 3.87 (3.23) | 2.32 ± 0.33 (2.40) | 5.12 ± 0.92 (5.47) | 2.14 ± 0.59 (2.26) |
| left/left | p | 0.866 | 25/25 | 0 | 25 | 1.69 ± 0.36 (1.62) | 4.81 ± 3.40 (3.59) | 2.34 ± 0.23 (2.29) | 5.14 ± 0.72 (5.31) | 2.17 ± 0.47 (2.22) |
| left/right | p | 0.855 | 25/25 | 0 | 25 | 1.80 ± 0.36 (1.80) | 5.77 ± 2.96 (5.84) | 2.29 ± 0.27 (2.31) | 4.97 ± 0.80 (5.28) | 2.05 ± 0.51 (2.00) |
| back/left | p | 0.811 | 25/25 | 0 | 25 | 2.55 ± 0.28 (2.50) | 6.02 ± 3.18 (5.66) | 2.44 ± 0.31 (2.43) | 5.32 ± 0.76 (5.58) | 2.34 ± 0.52 (2.33) |
| back/right | p | 0.810 | 25/25 | 0 | 25 | 2.59 ± 0.46 (2.48) | 5.79 ± 2.49 (6.03) | 2.42 ± 0.21 (2.44) | 5.26 ± 0.70 (5.60) | 2.28 ± 0.46 (2.22) |
| right/left | p | 0.843 | 25/25 | 0 | 24 | 1.79 ± 0.35 (1.80) | 5.18 ± 4.18 (3.83) | 2.27 ± 0.26 (2.31) | 4.98 ± 0.81 (5.29) | 2.06 ± 0.52 (2.09) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.65 ± 0.33 (1.58) | 5.71 ± 3.83 (4.32) | 2.28 ± 0.27 (2.26) | 4.96 ± 0.83 (5.28) | 2.08 ± 0.53 (2.00) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.880 | 5.5 | 5.67 | 2.47 |
| p | normal | 0.814 | 5.2 | 4.52 | 1.83 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.754 | 0.08 | 2.62 ± 0.83 (2.42) | 4.07 | 1.55 |
| p | medium | 20 | 0.890 | 0.71 | 1.29 ± 0.16 (1.26) | 4.14 | 1.61 |
| p | strong | 126 | 0.880 | 0.76 | - | 5.69 | 2.49 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.810).
