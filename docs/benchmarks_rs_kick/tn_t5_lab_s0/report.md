# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-21-20_t5_n7_stand01/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.78 ± 0.58 (1.73) |
| Direction error [°] | 5.84 ± 11.72 (4.64) |
| Avg ball speed [m/s] | 1.71 ± 0.38 (1.74) |
| Peak ball speed [m/s] | 3.67 ± 0.89 (3.61) |
| Distance [m] | 1.24 ± 0.49 (1.19) |
| Path length [m] | 1.24 ± 0.49 (1.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.837 | 50/50 | 0 | 48 | 1.17 ± 0.27 (1.18) | 4.86 ± 3.79 (3.22) | 1.45 ± 0.31 (1.42) | 3.07 ± 0.68 (2.88) | 0.90 ± 0.36 (0.83) |
| left | p | 0.859 | 50/50 | 0 | 50 | 1.74 ± 0.38 (1.76) | 5.21 ± 2.92 (5.05) | 1.77 ± 0.32 (1.78) | 3.83 ± 0.77 (4.01) | 1.32 ± 0.44 (1.25) |
| back | p | 0.813 | 50/50 | 0 | 47 | 2.49 ± 0.30 (2.45) | 8.30 ± 22.53 (3.75) | 1.88 ± 0.39 (2.02) | 4.09 ± 0.93 (4.52) | 1.48 ± 0.50 (1.62) |
| right | p | 0.852 | 50/50 | 0 | 50 | 1.71 ± 0.38 (1.68) | 5.01 ± 3.27 (4.69) | 1.72 ± 0.35 (1.77) | 3.70 ± 0.85 (3.78) | 1.24 ± 0.47 (1.21) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.836 | 100/100 | 0 | 98 | 1.78 ± 0.58 (1.74) | 6.60 ± 16.15 (4.16) | 1.70 ± 0.38 (1.73) | 3.64 ± 0.90 (3.54) | 1.22 ± 0.49 (1.19) |
| right | p | 0.844 | 100/100 | 0 | 97 | 1.78 ± 0.58 (1.71) | 5.08 ± 3.56 (4.77) | 1.72 ± 0.38 (1.74) | 3.70 ± 0.88 (3.61) | 1.25 ± 0.50 (1.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 25 | 1.17 ± 0.27 (1.14) | 4.56 ± 3.65 (2.95) | 1.45 ± 0.34 (1.38) | 3.06 ± 0.74 (2.94) | 0.90 ± 0.40 (0.79) |
| forward/right | p | 0.835 | 25/25 | 0 | 23 | 1.17 ± 0.28 (1.20) | 5.15 ± 3.90 (5.17) | 1.46 ± 0.27 (1.42) | 3.08 ± 0.61 (2.88) | 0.90 ± 0.31 (0.87) |
| left/left | p | 0.850 | 25/25 | 0 | 25 | 1.62 ± 0.39 (1.68) | 5.33 ± 3.23 (5.10) | 1.65 ± 0.28 (1.60) | 3.53 ± 0.67 (3.42) | 1.14 ± 0.36 (1.16) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.85 ± 0.34 (1.84) | 5.09 ± 2.58 (5.01) | 1.90 ± 0.31 (1.91) | 4.13 ± 0.74 (4.20) | 1.49 ± 0.45 (1.49) |
| back/left | p | 0.804 | 25/25 | 0 | 23 | 2.49 ± 0.29 (2.48) | 11.31 ± 31.30 (3.80) | 1.87 ± 0.42 (2.02) | 4.07 ± 0.98 (4.49) | 1.49 ± 0.51 (1.63) |
| back/right | p | 0.821 | 25/25 | 0 | 24 | 2.50 ± 0.30 (2.38) | 5.29 ± 4.18 (3.71) | 1.90 ± 0.36 (2.03) | 4.10 ± 0.87 (4.55) | 1.47 ± 0.49 (1.58) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.84 ± 0.34 (1.84) | 5.21 ± 3.16 (4.85) | 1.81 ± 0.33 (1.90) | 3.91 ± 0.83 (4.16) | 1.35 ± 0.45 (1.34) |
| right/right | p | 0.853 | 25/25 | 0 | 25 | 1.59 ± 0.38 (1.60) | 4.81 ± 3.36 (4.50) | 1.63 ± 0.35 (1.53) | 3.49 ± 0.81 (3.20) | 1.14 ± 0.46 (0.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.844 | 5.1 | 4.07 | 1.43 |
| p | normal | 0.836 | 6.6 | 3.28 | 1.04 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.806 | 0.34 | 1.82 ± 0.62 (1.65) | 2.86 | 0.82 |
| p | medium | 16 | 0.913 | 0.87 | 0.93 ± 0.15 (0.94) | 3.00 | 0.90 |
| p | strong | 126 | 0.846 | 0.55 | - | 4.13 | 1.47 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector back (0.813).
