# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.833** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.57 ± 0.54 (1.47) |
| Direction error [°] | 6.66 ± 4.20 (6.28) |
| Avg ball speed [m/s] | 1.67 ± 0.34 (1.78) |
| Peak ball speed [m/s] | 3.66 ± 0.79 (3.89) |
| Distance [m] | 1.19 ± 0.41 (1.24) |
| Path length [m] | 1.20 ± 0.41 (1.24) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.841 | 50/50 | 0 | 46 | 1.01 ± 0.23 (1.03) | 5.91 ± 4.48 (5.08) | 1.45 ± 0.39 (1.60) | 3.14 ± 0.81 (3.40) | 0.92 ± 0.41 (0.98) |
| left | p | 0.850 | 50/50 | 0 | 49 | 1.50 ± 0.34 (1.48) | 6.43 ± 4.38 (5.25) | 1.71 ± 0.30 (1.82) | 3.80 ± 0.72 (4.02) | 1.26 ± 0.38 (1.34) |
| back | p | 0.808 | 50/50 | 0 | 50 | 2.27 ± 0.27 (2.23) | 7.74 ± 3.33 (8.23) | 1.85 ± 0.20 (1.93) | 4.06 ± 0.54 (4.28) | 1.43 ± 0.30 (1.45) |
| right | p | 0.833 | 50/50 | 0 | 49 | 1.50 ± 0.35 (1.46) | 6.54 ± 4.30 (5.05) | 1.66 ± 0.31 (1.77) | 3.62 ± 0.75 (3.90) | 1.17 ± 0.37 (1.20) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.828 | 100/100 | 0 | 96 | 1.57 ± 0.54 (1.49) | 6.90 ± 4.37 (6.40) | 1.67 ± 0.34 (1.77) | 3.65 ± 0.79 (3.77) | 1.19 ± 0.41 (1.22) |
| right | p | 0.838 | 100/100 | 0 | 98 | 1.57 ± 0.54 (1.47) | 6.42 ± 4.01 (5.71) | 1.67 ± 0.34 (1.78) | 3.67 ± 0.79 (3.90) | 1.20 ± 0.41 (1.25) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.828 | 25/25 | 0 | 22 | 1.01 ± 0.22 (1.06) | 6.82 ± 4.87 (5.98) | 1.47 ± 0.40 (1.65) | 3.16 ± 0.81 (3.44) | 0.94 ± 0.42 (1.08) |
| forward/right | p | 0.855 | 25/25 | 0 | 24 | 1.00 ± 0.23 (1.02) | 5.01 ± 3.84 (4.03) | 1.42 ± 0.37 (1.47) | 3.12 ± 0.82 (3.10) | 0.89 ± 0.39 (0.93) |
| left/left | p | 0.832 | 25/25 | 0 | 24 | 1.40 ± 0.33 (1.44) | 7.34 ± 4.89 (7.09) | 1.65 ± 0.30 (1.81) | 3.61 ± 0.70 (3.80) | 1.17 ± 0.36 (1.28) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.62) | 5.52 ± 3.57 (4.86) | 1.78 ± 0.29 (1.86) | 3.98 ± 0.69 (4.27) | 1.35 ± 0.37 (1.41) |
| back/left | p | 0.808 | 25/25 | 0 | 25 | 2.28 ± 0.27 (2.18) | 7.60 ± 3.64 (8.60) | 1.85 ± 0.22 (1.93) | 4.09 ± 0.58 (4.32) | 1.44 ± 0.34 (1.60) |
| back/right | p | 0.808 | 25/25 | 0 | 25 | 2.26 ± 0.28 (2.24) | 7.88 ± 2.98 (8.10) | 1.84 ± 0.17 (1.91) | 4.04 ± 0.50 (4.18) | 1.42 ± 0.26 (1.43) |
| right/left | p | 0.846 | 25/25 | 0 | 25 | 1.59 ± 0.32 (1.56) | 5.82 ± 3.67 (4.88) | 1.69 ± 0.29 (1.80) | 3.72 ± 0.74 (3.98) | 1.21 ± 0.36 (1.33) |
| right/right | p | 0.820 | 25/25 | 0 | 24 | 1.40 ± 0.35 (1.42) | 7.26 ± 4.74 (5.80) | 1.63 ± 0.32 (1.73) | 3.52 ± 0.75 (3.67) | 1.13 ± 0.38 (1.13) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.837 | 6.6 | 4.06 | 1.39 |
| p | normal | 0.829 | 6.7 | 3.25 | 1.00 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.811 | 0.38 | 1.80 ± 0.67 (1.63) | 2.86 | 0.80 |
| p | medium | 16 | 0.878 | 0.83 | 0.97 ± 0.20 (1.01) | 3.12 | 0.96 |
| p | strong | 126 | 0.837 | 0.55 | - | 4.09 | 1.41 |

## Notes

- p: score 0.833, 200/200 kicked, 0 fell; worst sector back (0.808).
