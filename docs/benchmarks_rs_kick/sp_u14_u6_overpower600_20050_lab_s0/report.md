# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_16-13-42_u14_u6_overpower600/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.52 (1.50) |
| Direction error [°] | 5.15 ± 3.06 (4.87) |
| Avg ball speed [m/s] | 1.81 ± 0.36 (1.87) |
| Peak ball speed [m/s] | 3.97 ± 0.88 (4.11) |
| Distance [m] | 1.38 ± 0.50 (1.44) |
| Path length [m] | 1.39 ± 0.50 (1.44) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 50 | 1.05 ± 0.22 (1.07) | 4.70 ± 3.36 (3.19) | 1.52 ± 0.37 (1.46) | 3.28 ± 0.83 (3.10) | 1.00 ± 0.44 (0.97) |
| left | p | 0.866 | 50/50 | 0 | 50 | 1.54 ± 0.33 (1.55) | 5.38 ± 2.77 (5.43) | 1.91 ± 0.31 (2.03) | 4.24 ± 0.78 (4.64) | 1.53 ± 0.46 (1.59) |
| back | p | 0.846 | 50/50 | 0 | 50 | 2.25 ± 0.27 (2.20) | 4.89 ± 2.55 (4.23) | 2.00 ± 0.26 (2.09) | 4.41 ± 0.71 (4.74) | 1.64 ± 0.42 (1.74) |
| right | p | 0.843 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.46) | 5.63 ± 3.40 (5.22) | 1.80 ± 0.30 (1.84) | 3.94 ± 0.76 (3.98) | 1.35 ± 0.39 (1.35) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.59 ± 0.52 (1.53) | 5.20 ± 2.90 (4.99) | 1.83 ± 0.34 (1.90) | 4.02 ± 0.86 (4.16) | 1.41 ± 0.49 (1.47) |
| right | p | 0.853 | 100/100 | 0 | 100 | 1.58 ± 0.52 (1.48) | 5.09 ± 3.22 (4.49) | 1.79 ± 0.38 (1.86) | 3.91 ± 0.90 (4.02) | 1.35 ± 0.50 (1.40) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.841 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 5.17 ± 3.42 (3.78) | 1.58 ± 0.37 (1.62) | 3.39 ± 0.82 (3.15) | 1.07 ± 0.47 (0.97) |
| forward/right | p | 0.854 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.06) | 4.23 ± 3.22 (2.28) | 1.46 ± 0.37 (1.44) | 3.17 ± 0.83 (3.00) | 0.93 ± 0.41 (0.90) |
| left/left | p | 0.855 | 25/25 | 0 | 25 | 1.44 ± 0.33 (1.50) | 6.12 ± 2.74 (5.60) | 1.85 ± 0.30 (1.91) | 4.08 ± 0.77 (4.29) | 1.44 ± 0.45 (1.49) |
| left/right | p | 0.878 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.62) | 4.63 ± 2.59 (4.90) | 1.98 ± 0.31 (2.10) | 4.40 ± 0.76 (4.71) | 1.62 ± 0.46 (1.71) |
| back/left | p | 0.845 | 25/25 | 0 | 25 | 2.27 ± 0.27 (2.20) | 4.52 ± 1.95 (4.18) | 2.04 ± 0.23 (2.15) | 4.50 ± 0.65 (4.77) | 1.70 ± 0.41 (1.78) |
| back/right | p | 0.847 | 25/25 | 0 | 25 | 2.22 ± 0.27 (2.24) | 5.26 ± 2.98 (5.06) | 1.97 ± 0.29 (2.06) | 4.31 ± 0.74 (4.58) | 1.59 ± 0.43 (1.69) |
| right/left | p | 0.852 | 25/25 | 0 | 25 | 1.60 ± 0.29 (1.58) | 5.00 ± 3.05 (5.20) | 1.86 ± 0.29 (1.98) | 4.10 ± 0.77 (4.46) | 1.42 ± 0.39 (1.53) |
| right/right | p | 0.835 | 25/25 | 0 | 25 | 1.41 ± 0.35 (1.42) | 6.25 ± 3.61 (7.21) | 1.75 ± 0.30 (1.78) | 3.77 ± 0.71 (3.74) | 1.27 ± 0.38 (1.27) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.861 | 5.2 | 4.42 | 1.61 |
| p | normal | 0.840 | 5.1 | 3.51 | 1.15 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.806 | 0.31 | 1.91 ± 0.60 (1.72) | 3.06 | 0.91 |
| p | medium | 16 | 0.908 | 0.85 | 1.00 ± 0.18 (0.96) | 3.25 | 1.02 |
| p | strong | 126 | 0.864 | 0.60 | - | 4.47 | 1.64 |

## Notes

- p: score 0.851, 200/200 kicked, 0 fell; worst sector right (0.843).
