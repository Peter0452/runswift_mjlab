# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-47-18_e4_yaw_cap/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.842** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.83 ± 0.56 (1.74) |
| Direction error [°] | 5.26 ± 3.39 (4.75) |
| Avg ball speed [m/s] | 2.12 ± 0.28 (2.15) |
| Peak ball speed [m/s] | 5.06 ± 0.74 (5.19) |
| Distance [m] | 2.05 ± 0.47 (2.03) |
| Path length [m] | 2.06 ± 0.47 (2.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.850 | 50/50 | 0 | 50 | 1.27 ± 0.24 (1.30) | 4.61 ± 3.02 (4.06) | 2.07 ± 0.35 (2.13) | 4.94 ± 0.87 (5.11) | 1.95 ± 0.55 (1.98) |
| left | p | 0.871 | 50/50 | 0 | 50 | 1.76 ± 0.36 (1.72) | 5.04 ± 3.40 (4.81) | 2.13 ± 0.21 (2.14) | 5.12 ± 0.63 (5.22) | 2.06 ± 0.36 (2.04) |
| back | p | 0.798 | 50/50 | 0 | 48 | 2.54 ± 0.36 (2.50) | 6.36 ± 3.78 (5.75) | 2.18 ± 0.21 (2.20) | 5.16 ± 0.60 (5.28) | 2.14 ± 0.39 (2.11) |
| right | p | 0.847 | 50/50 | 0 | 50 | 1.76 ± 0.36 (1.74) | 5.03 ± 3.02 (4.65) | 2.09 ± 0.33 (2.17) | 5.01 ± 0.81 (5.17) | 2.03 ± 0.52 (1.97) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 100 | 1.85 ± 0.59 (1.75) | 5.13 ± 3.11 (4.69) | 2.10 ± 0.29 (2.14) | 5.01 ± 0.74 (5.17) | 2.01 ± 0.47 (2.02) |
| right | p | 0.840 | 100/100 | 0 | 98 | 1.82 ± 0.53 (1.73) | 5.39 ± 3.64 (4.80) | 2.14 ± 0.28 (2.17) | 5.11 ± 0.74 (5.23) | 2.08 ± 0.46 (2.05) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.28) | 4.74 ± 3.14 (3.85) | 2.08 ± 0.33 (2.17) | 4.93 ± 0.85 (5.18) | 1.96 ± 0.53 (2.04) |
| forward/right | p | 0.847 | 25/25 | 0 | 25 | 1.27 ± 0.24 (1.32) | 4.48 ± 2.90 (4.33) | 2.07 ± 0.36 (2.13) | 4.96 ± 0.89 (5.10) | 1.94 ± 0.56 (1.97) |
| left/left | p | 0.868 | 25/25 | 0 | 25 | 1.64 ± 0.35 (1.68) | 4.89 ± 3.40 (4.39) | 2.06 ± 0.19 (2.10) | 4.92 ± 0.60 (5.11) | 1.95 ± 0.34 (1.92) |
| left/right | p | 0.874 | 25/25 | 0 | 25 | 1.88 ± 0.32 (1.96) | 5.19 ± 3.40 (5.22) | 2.20 ± 0.20 (2.18) | 5.31 ± 0.59 (5.43) | 2.18 ± 0.34 (2.11) |
| back/left | p | 0.803 | 25/25 | 0 | 25 | 2.60 ± 0.42 (2.54) | 5.22 ± 2.64 (4.80) | 2.13 ± 0.20 (2.13) | 5.07 ± 0.52 (5.21) | 2.06 ± 0.34 (2.06) |
| back/right | p | 0.794 | 25/25 | 0 | 23 | 2.49 ± 0.27 (2.50) | 7.50 ± 4.36 (6.92) | 2.22 ± 0.21 (2.25) | 5.24 ± 0.66 (5.31) | 2.22 ± 0.43 (2.23) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.88 ± 0.35 (1.78) | 5.66 ± 3.14 (6.21) | 2.12 ± 0.38 (2.20) | 5.10 ± 0.90 (5.30) | 2.09 ± 0.58 (2.10) |
| right/right | p | 0.845 | 25/25 | 0 | 25 | 1.65 ± 0.33 (1.66) | 4.39 ± 2.75 (4.27) | 2.05 ± 0.26 (2.08) | 4.92 ± 0.69 (5.10) | 1.98 ± 0.43 (1.90) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.884 | 5.2 | 5.57 | 2.31 |
| p | normal | 0.799 | 5.3 | 4.55 | 1.78 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.747 | 0.06 | 2.64 ± 0.79 (2.40) | 4.20 | 1.58 |
| p | medium | 16 | 0.859 | 0.66 | 1.34 ± 0.15 (1.33) | 4.35 | 1.72 |
| p | strong | 126 | 0.883 | 0.74 | - | 5.54 | 2.30 |

## Notes

- p: score 0.842, 200/200 kicked, 0 fell; worst sector back (0.798).
