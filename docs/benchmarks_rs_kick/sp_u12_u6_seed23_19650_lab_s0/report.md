# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-01-05_u12_u6_seed23/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.57 ± 0.51 (1.50) |
| Direction error [°] | 6.00 ± 10.59 (4.88) |
| Avg ball speed [m/s] | 1.84 ± 0.40 (1.93) |
| Peak ball speed [m/s] | 3.98 ± 0.92 (4.15) |
| Distance [m] | 1.41 ± 0.51 (1.45) |
| Path length [m] | 1.41 ± 0.51 (1.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.848 | 50/50 | 0 | 50 | 1.03 ± 0.22 (1.06) | 5.03 ± 3.47 (3.90) | 1.58 ± 0.42 (1.61) | 3.39 ± 0.90 (3.36) | 1.06 ± 0.47 (1.01) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.52 ± 0.33 (1.55) | 5.34 ± 3.43 (5.37) | 1.92 ± 0.33 (2.03) | 4.18 ± 0.78 (4.54) | 1.51 ± 0.47 (1.53) |
| back | p | 0.841 | 50/50 | 0 | 49 | 2.22 ± 0.25 (2.19) | 7.99 ± 20.14 (4.93) | 2.01 ± 0.37 (2.15) | 4.39 ± 0.90 (4.79) | 1.66 ± 0.46 (1.82) |
| right | p | 0.841 | 50/50 | 0 | 50 | 1.49 ± 0.34 (1.46) | 5.65 ± 3.75 (5.39) | 1.84 ± 0.34 (1.96) | 3.98 ± 0.78 (4.30) | 1.39 ± 0.44 (1.51) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.52) | 5.40 ± 3.21 (5.27) | 1.87 ± 0.32 (1.95) | 4.05 ± 0.79 (4.21) | 1.44 ± 0.45 (1.52) |
| right | p | 0.850 | 100/100 | 0 | 99 | 1.56 ± 0.50 (1.48) | 6.61 ± 14.61 (4.79) | 1.80 ± 0.46 (1.91) | 3.91 ± 1.03 (4.05) | 1.37 ± 0.56 (1.40) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 5.16 ± 3.12 (4.18) | 1.71 ± 0.36 (1.72) | 3.64 ± 0.77 (3.61) | 1.20 ± 0.43 (1.24) |
| forward/right | p | 0.852 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 4.91 ± 3.79 (3.19) | 1.45 ± 0.43 (1.44) | 3.13 ± 0.94 (2.93) | 0.91 ± 0.47 (0.92) |
| left/left | p | 0.851 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.50) | 6.26 ± 3.88 (5.79) | 1.85 ± 0.32 (1.78) | 4.00 ± 0.78 (4.03) | 1.41 ± 0.46 (1.34) |
| left/right | p | 0.879 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.60) | 4.42 ± 2.60 (4.75) | 1.99 ± 0.32 (2.09) | 4.35 ± 0.74 (4.60) | 1.61 ± 0.45 (1.64) |
| back/left | p | 0.848 | 25/25 | 0 | 25 | 2.25 ± 0.25 (2.20) | 4.86 ± 2.33 (4.53) | 2.07 ± 0.21 (2.15) | 4.50 ± 0.62 (4.83) | 1.72 ± 0.38 (1.84) |
| back/right | p | 0.834 | 25/25 | 0 | 24 | 2.19 ± 0.24 (2.18) | 11.13 ± 28.04 (4.97) | 1.96 ± 0.47 (2.15) | 4.28 ± 1.10 (4.73) | 1.61 ± 0.51 (1.70) |
| right/left | p | 0.846 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.58) | 5.32 ± 3.16 (5.47) | 1.87 ± 0.29 (1.99) | 4.07 ± 0.73 (4.44) | 1.43 ± 0.38 (1.54) |
| right/right | p | 0.836 | 25/25 | 0 | 25 | 1.40 ± 0.35 (1.44) | 5.98 ± 4.22 (4.86) | 1.80 ± 0.39 (1.92) | 3.89 ± 0.82 (3.99) | 1.36 ± 0.49 (1.40) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.861 | 5.4 | 4.47 | 1.65 |
| p | normal | 0.837 | 6.6 | 3.50 | 1.16 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.805 | 0.29 | 1.92 ± 0.72 (1.74) | 3.06 | 0.93 |
| p | medium | 16 | 0.897 | 0.84 | 0.97 ± 0.19 (0.98) | 3.15 | 0.97 |
| p | strong | 126 | 0.863 | 0.60 | - | 4.52 | 1.68 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector back (0.841).
