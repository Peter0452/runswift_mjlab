# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_16-13-42_u14_u6_overpower600/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.56 ± 0.51 (1.48) |
| Direction error [°] | 5.18 ± 3.21 (4.46) |
| Avg ball speed [m/s] | 1.82 ± 0.35 (1.92) |
| Peak ball speed [m/s] | 3.99 ± 0.86 (4.27) |
| Distance [m] | 1.39 ± 0.47 (1.44) |
| Path length [m] | 1.39 ± 0.47 (1.45) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.865 | 50/50 | 0 | 49 | 1.04 ± 0.22 (1.08) | 4.29 ± 3.22 (2.77) | 1.62 ± 0.41 (1.74) | 3.46 ± 0.90 (3.53) | 1.10 ± 0.45 (1.17) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.51 ± 0.33 (1.50) | 5.32 ± 2.81 (4.56) | 1.89 ± 0.31 (2.00) | 4.17 ± 0.78 (4.48) | 1.48 ± 0.44 (1.51) |
| back | p | 0.841 | 50/50 | 0 | 50 | 2.22 ± 0.25 (2.18) | 5.82 ± 2.86 (5.46) | 1.98 ± 0.26 (2.07) | 4.36 ± 0.70 (4.68) | 1.61 ± 0.42 (1.76) |
| right | p | 0.848 | 50/50 | 0 | 50 | 1.49 ± 0.32 (1.44) | 5.30 ± 3.67 (4.73) | 1.80 ± 0.30 (1.89) | 3.94 ± 0.77 (4.25) | 1.35 ± 0.41 (1.35) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 100 | 1.57 ± 0.51 (1.48) | 5.24 ± 3.07 (5.00) | 1.83 ± 0.33 (1.93) | 4.00 ± 0.81 (4.31) | 1.39 ± 0.46 (1.47) |
| right | p | 0.859 | 100/100 | 0 | 99 | 1.56 ± 0.51 (1.48) | 5.12 ± 3.34 (4.09) | 1.81 ± 0.37 (1.91) | 3.97 ± 0.90 (4.25) | 1.38 ± 0.48 (1.40) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.856 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 4.27 ± 2.88 (2.74) | 1.66 ± 0.34 (1.77) | 3.55 ± 0.74 (3.63) | 1.14 ± 0.41 (1.23) |
| forward/right | p | 0.874 | 25/25 | 0 | 24 | 1.04 ± 0.23 (1.06) | 4.30 ± 3.53 (2.99) | 1.57 ± 0.47 (1.65) | 3.38 ± 1.02 (3.38) | 1.06 ± 0.49 (1.12) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.50 ± 3.15 (4.36) | 1.83 ± 0.33 (1.94) | 4.02 ± 0.82 (4.42) | 1.40 ± 0.46 (1.50) |
| left/right | p | 0.872 | 25/25 | 0 | 25 | 1.60 ± 0.30 (1.60) | 5.15 ± 2.42 (5.01) | 1.95 ± 0.28 (2.03) | 4.33 ± 0.70 (4.62) | 1.55 ± 0.40 (1.63) |
| back/left | p | 0.836 | 25/25 | 0 | 25 | 2.23 ± 0.26 (2.18) | 5.99 ± 2.57 (5.78) | 1.99 ± 0.21 (2.07) | 4.39 ± 0.61 (4.69) | 1.63 ± 0.37 (1.76) |
| back/right | p | 0.846 | 25/25 | 0 | 25 | 2.21 ± 0.24 (2.18) | 5.66 ± 3.11 (4.82) | 1.97 ± 0.29 (2.08) | 4.33 ± 0.79 (4.67) | 1.59 ± 0.45 (1.77) |
| right/left | p | 0.852 | 25/25 | 0 | 25 | 1.58 ± 0.28 (1.58) | 5.21 ± 3.38 (5.88) | 1.84 ± 0.33 (1.99) | 4.05 ± 0.83 (4.34) | 1.41 ± 0.43 (1.59) |
| right/right | p | 0.843 | 25/25 | 0 | 25 | 1.40 ± 0.34 (1.44) | 5.39 ± 3.94 (3.59) | 1.77 ± 0.27 (1.86) | 3.84 ± 0.69 (3.98) | 1.30 ± 0.37 (1.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.864 | 5.3 | 4.51 | 1.65 |
| p | normal | 0.845 | 5.0 | 3.46 | 1.12 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.814 | 0.33 | 1.87 ± 0.63 (1.71) | 3.00 | 0.87 |
| p | medium | 16 | 0.916 | 0.87 | 0.97 ± 0.17 (0.99) | 3.15 | 0.97 |
| p | strong | 126 | 0.866 | 0.61 | - | 4.55 | 1.67 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector back (0.841).
