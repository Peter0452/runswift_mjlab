# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.63 ± 0.52 (1.58) |
| Direction error [°] | 5.64 ± 12.37 (4.18) |
| Avg ball speed [m/s] | 1.71 ± 0.37 (1.76) |
| Peak ball speed [m/s] | 3.66 ± 0.86 (3.67) |
| Distance [m] | 1.23 ± 0.46 (1.23) |
| Path length [m] | 1.23 ± 0.46 (1.23) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.859 | 50/50 | 0 | 50 | 1.09 ± 0.24 (1.14) | 3.94 ± 2.85 (2.59) | 1.41 ± 0.39 (1.39) | 3.01 ± 0.83 (2.95) | 0.86 ± 0.43 (0.83) |
| left | p | 0.858 | 50/50 | 0 | 50 | 1.57 ± 0.35 (1.59) | 5.33 ± 3.45 (4.42) | 1.80 ± 0.26 (1.87) | 3.88 ± 0.66 (4.10) | 1.34 ± 0.37 (1.34) |
| back | p | 0.836 | 50/50 | 0 | 49 | 2.29 ± 0.26 (2.28) | 8.18 ± 23.89 (4.85) | 1.87 ± 0.35 (1.96) | 4.01 ± 0.84 (4.28) | 1.45 ± 0.44 (1.50) |
| right | p | 0.847 | 50/50 | 0 | 50 | 1.57 ± 0.35 (1.57) | 5.10 ± 3.38 (4.37) | 1.75 ± 0.29 (1.77) | 3.74 ± 0.72 (3.68) | 1.26 ± 0.39 (1.23) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 99 | 1.62 ± 0.52 (1.59) | 6.81 ± 17.12 (4.78) | 1.70 ± 0.38 (1.75) | 3.63 ± 0.90 (3.67) | 1.22 ± 0.47 (1.23) |
| right | p | 0.855 | 100/100 | 0 | 100 | 1.64 ± 0.52 (1.57) | 4.46 ± 3.18 (3.67) | 1.72 ± 0.36 (1.77) | 3.69 ± 0.81 (3.68) | 1.24 ± 0.45 (1.23) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.857 | 25/25 | 0 | 25 | 1.08 ± 0.23 (1.12) | 4.34 ± 2.83 (2.89) | 1.39 ± 0.38 (1.37) | 2.92 ± 0.81 (2.92) | 0.84 ± 0.42 (0.82) |
| forward/right | p | 0.861 | 25/25 | 0 | 25 | 1.10 ± 0.25 (1.14) | 3.53 ± 2.83 (2.55) | 1.43 ± 0.41 (1.46) | 3.11 ± 0.84 (3.03) | 0.88 ± 0.43 (0.83) |
| left/left | p | 0.847 | 25/25 | 0 | 25 | 1.46 ± 0.34 (1.52) | 6.05 ± 3.87 (4.63) | 1.72 ± 0.26 (1.77) | 3.68 ± 0.65 (3.86) | 1.23 ± 0.35 (1.26) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.67 ± 0.32 (1.70) | 4.60 ± 2.79 (3.91) | 1.88 ± 0.24 (1.90) | 4.07 ± 0.61 (4.16) | 1.45 ± 0.36 (1.45) |
| back/left | p | 0.823 | 25/25 | 0 | 24 | 2.28 ± 0.25 (2.26) | 12.02 ± 33.25 (5.54) | 1.86 ± 0.41 (1.95) | 3.98 ± 0.94 (4.27) | 1.44 ± 0.48 (1.44) |
| back/right | p | 0.848 | 25/25 | 0 | 25 | 2.29 ± 0.27 (2.30) | 4.34 ± 2.63 (4.14) | 1.88 ± 0.28 (2.00) | 4.05 ± 0.72 (4.36) | 1.45 ± 0.40 (1.67) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.66 ± 0.34 (1.62) | 4.82 ± 2.60 (4.77) | 1.83 ± 0.28 (1.94) | 3.94 ± 0.72 (4.26) | 1.36 ± 0.38 (1.47) |
| right/right | p | 0.841 | 25/25 | 0 | 25 | 1.48 ± 0.34 (1.52) | 5.39 ± 3.98 (4.11) | 1.67 ± 0.27 (1.66) | 3.54 ± 0.65 (3.35) | 1.17 ± 0.36 (1.06) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.853 | 4.9 | 4.07 | 1.43 |
| p | normal | 0.847 | 6.4 | 3.25 | 1.03 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.824 | 0.37 | 1.79 ± 0.68 (1.69) | 2.82 | 0.80 |
| p | medium | 16 | 0.896 | 0.85 | 0.93 ± 0.17 (0.96) | 3.01 | 0.89 |
| p | strong | 126 | 0.856 | 0.55 | - | 4.13 | 1.47 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector back (0.836).
