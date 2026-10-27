# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-47-18_e4_yaw_cap/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.84 ± 0.56 (1.74) |
| Direction error [°] | 4.81 ± 3.34 (4.35) |
| Avg ball speed [m/s] | 2.08 ± 0.31 (2.11) |
| Peak ball speed [m/s] | 5.01 ± 0.77 (5.23) |
| Distance [m] | 1.99 ± 0.50 (1.98) |
| Path length [m] | 2.00 ± 0.50 (1.99) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.853 | 50/50 | 0 | 50 | 1.27 ± 0.25 (1.29) | 4.48 ± 2.72 (4.41) | 2.02 ± 0.40 (2.09) | 4.84 ± 0.93 (4.99) | 1.89 ± 0.61 (1.75) |
| left | p | 0.876 | 50/50 | 0 | 49 | 1.77 ± 0.36 (1.78) | 4.53 ± 3.85 (3.16) | 2.12 ± 0.24 (2.14) | 5.16 ± 0.62 (5.40) | 2.07 ± 0.40 (2.08) |
| back | p | 0.809 | 50/50 | 0 | 50 | 2.55 ± 0.32 (2.50) | 5.56 ± 3.60 (5.33) | 2.13 ± 0.24 (2.12) | 5.13 ± 0.67 (5.31) | 2.10 ± 0.44 (1.99) |
| right | p | 0.849 | 50/50 | 0 | 49 | 1.77 ± 0.34 (1.74) | 4.67 ± 2.95 (4.41) | 2.06 ± 0.32 (2.06) | 4.90 ± 0.78 (5.13) | 1.91 ± 0.48 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 98 | 1.85 ± 0.57 (1.78) | 5.19 ± 3.91 (4.42) | 2.12 ± 0.32 (2.13) | 5.03 ± 0.76 (5.28) | 2.02 ± 0.49 (2.02) |
| right | p | 0.849 | 100/100 | 0 | 100 | 1.83 ± 0.55 (1.74) | 4.43 ± 2.61 (4.20) | 2.05 ± 0.30 (2.07) | 4.98 ± 0.78 (5.17) | 1.96 ± 0.50 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.855 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.28) | 4.60 ± 3.08 (4.45) | 2.09 ± 0.36 (2.12) | 4.94 ± 0.88 (5.34) | 1.97 ± 0.56 (2.10) |
| forward/right | p | 0.850 | 25/25 | 0 | 25 | 1.26 ± 0.24 (1.30) | 4.37 ± 2.31 (4.37) | 1.95 ± 0.43 (1.91) | 4.75 ± 0.97 (4.78) | 1.81 ± 0.64 (1.66) |
| left/left | p | 0.865 | 25/25 | 0 | 24 | 1.68 ± 0.37 (1.76) | 5.60 ± 4.54 (4.34) | 2.10 ± 0.27 (2.13) | 5.10 ± 0.66 (5.32) | 2.08 ± 0.41 (2.10) |
| left/right | p | 0.887 | 25/25 | 0 | 25 | 1.87 ± 0.32 (1.94) | 3.45 ± 2.60 (2.68) | 2.14 ± 0.20 (2.15) | 5.23 ± 0.57 (5.46) | 2.06 ± 0.39 (2.06) |
| back/left | p | 0.806 | 25/25 | 0 | 25 | 2.58 ± 0.32 (2.56) | 5.51 ± 4.30 (4.14) | 2.18 ± 0.24 (2.12) | 5.15 ± 0.57 (5.25) | 2.12 ± 0.42 (1.99) |
| back/right | p | 0.813 | 25/25 | 0 | 25 | 2.52 ± 0.32 (2.36) | 5.62 ± 2.74 (5.91) | 2.09 ± 0.24 (2.11) | 5.11 ± 0.75 (5.39) | 2.07 ± 0.46 (1.99) |
| right/left | p | 0.853 | 25/25 | 0 | 24 | 1.88 ± 0.31 (1.82) | 5.07 ± 3.45 (4.79) | 2.10 ± 0.37 (2.16) | 4.95 ± 0.85 (5.29) | 1.93 ± 0.55 (1.91) |
| right/right | p | 0.846 | 25/25 | 0 | 25 | 1.66 ± 0.32 (1.72) | 4.27 ± 2.28 (3.98) | 2.02 ± 0.26 (2.03) | 4.85 ± 0.69 (4.84) | 1.90 ± 0.41 (1.84) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.887 | 4.8 | 5.54 | 2.29 |
| p | normal | 0.807 | 4.8 | 4.47 | 1.70 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.758 | 0.07 | 2.56 ± 0.76 (2.36) | 4.08 | 1.47 |
| p | medium | 16 | 0.861 | 0.67 | 1.33 ± 0.15 (1.32) | 4.31 | 1.66 |
| p | strong | 126 | 0.886 | 0.74 | - | 5.52 | 2.27 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.809).
