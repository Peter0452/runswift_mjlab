# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-06-39_t4_n7_control/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.838** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.55 ± 0.49 (1.52) |
| Direction error [°] | 5.06 ± 3.21 (4.71) |
| Avg ball speed [m/s] | 1.94 ± 0.29 (1.99) |
| Peak ball speed [m/s] | 4.19 ± 0.64 (4.22) |
| Distance [m] | 1.58 ± 0.41 (1.59) |
| Path length [m] | 1.59 ± 0.41 (1.60) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.830 | 50/50 | 0 | 49 | 1.04 ± 0.24 (1.07) | 4.08 ± 3.34 (3.19) | 1.66 ± 0.29 (1.69) | 3.55 ± 0.57 (3.63) | 1.19 ± 0.36 (1.20) |
| left | p | 0.855 | 50/50 | 0 | 50 | 1.51 ± 0.33 (1.53) | 5.17 ± 3.21 (5.05) | 2.00 ± 0.24 (2.05) | 4.37 ± 0.56 (4.40) | 1.68 ± 0.39 (1.68) |
| back | p | 0.844 | 50/50 | 0 | 50 | 2.14 ± 0.25 (2.10) | 4.85 ± 2.82 (4.93) | 2.13 ± 0.15 (2.14) | 4.56 ± 0.40 (4.64) | 1.82 ± 0.26 (1.81) |
| right | p | 0.823 | 50/50 | 0 | 50 | 1.53 ± 0.33 (1.51) | 6.15 ± 3.11 (6.42) | 1.99 ± 0.21 (2.00) | 4.30 ± 0.51 (4.24) | 1.65 ± 0.31 (1.61) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.839 | 100/100 | 0 | 100 | 1.55 ± 0.49 (1.54) | 5.10 ± 3.10 (4.80) | 1.95 ± 0.26 (1.96) | 4.21 ± 0.59 (4.26) | 1.59 ± 0.38 (1.58) |
| right | p | 0.837 | 100/100 | 0 | 99 | 1.55 ± 0.49 (1.51) | 5.03 ± 3.32 (4.32) | 1.94 ± 0.31 (2.01) | 4.18 ± 0.69 (4.20) | 1.58 ± 0.44 (1.62) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 25 | 1.05 ± 0.25 (1.10) | 4.34 ± 3.00 (3.40) | 1.73 ± 0.27 (1.80) | 3.68 ± 0.52 (3.68) | 1.27 ± 0.35 (1.27) |
| forward/right | p | 0.827 | 25/25 | 0 | 24 | 1.03 ± 0.23 (1.06) | 3.83 ± 3.63 (2.29) | 1.59 ± 0.30 (1.60) | 3.41 ± 0.58 (3.43) | 1.10 ± 0.34 (1.11) |
| left/left | p | 0.849 | 25/25 | 0 | 25 | 1.39 ± 0.31 (1.46) | 5.39 ± 3.23 (5.33) | 1.93 ± 0.25 (1.95) | 4.20 ± 0.57 (4.26) | 1.57 ± 0.37 (1.57) |
| left/right | p | 0.862 | 25/25 | 0 | 25 | 1.62 ± 0.31 (1.60) | 4.95 ± 3.17 (3.46) | 2.06 ± 0.21 (2.09) | 4.54 ± 0.50 (4.65) | 1.79 ± 0.38 (1.75) |
| back/left | p | 0.843 | 25/25 | 0 | 25 | 2.15 ± 0.26 (2.08) | 4.79 ± 3.03 (5.05) | 2.13 ± 0.13 (2.16) | 4.57 ± 0.36 (4.64) | 1.84 ± 0.25 (1.84) |
| back/right | p | 0.845 | 25/25 | 0 | 25 | 2.13 ± 0.25 (2.12) | 4.92 ± 2.59 (4.70) | 2.13 ± 0.16 (2.13) | 4.55 ± 0.43 (4.64) | 1.81 ± 0.26 (1.77) |
| right/left | p | 0.833 | 25/25 | 0 | 25 | 1.62 ± 0.30 (1.58) | 5.88 ± 2.89 (5.96) | 2.01 ± 0.17 (2.01) | 4.40 ± 0.46 (4.39) | 1.69 ± 0.28 (1.61) |
| right/right | p | 0.813 | 25/25 | 0 | 25 | 1.44 ± 0.34 (1.48) | 6.41 ± 3.30 (6.83) | 1.96 ± 0.25 (2.00) | 4.21 ± 0.54 (4.15) | 1.61 ± 0.32 (1.61) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.858 | 5.4 | 4.30 | 1.62 |
| p | normal | 0.818 | 4.7 | 4.09 | 1.55 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.773 | 0.09 | 2.45 ± 0.72 (2.25) | 3.91 | 1.45 |
| p | medium | 16 | 0.899 | 0.77 | 1.18 ± 0.21 (1.21) | 3.82 | 1.41 |
| p | strong | 126 | 0.860 | 0.58 | - | 4.37 | 1.67 |

## Notes

- p: score 0.838, 200/200 kicked, 0 fell; worst sector right (0.823).
