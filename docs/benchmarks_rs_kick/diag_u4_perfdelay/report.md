# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.861** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.90 ± 0.58 (1.87) |
| Direction error [°] | 5.60 ± 12.21 (4.42) |
| Avg ball speed [m/s] | 2.17 ± 0.52 (2.33) |
| Peak ball speed [m/s] | 4.88 ± 1.35 (5.43) |
| Distance [m] | 1.92 ± 0.79 (2.11) |
| Path length [m] | 1.93 ± 0.79 (2.13) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.877 | 50/50 | 0 | 50 | 1.27 ± 0.25 (1.29) | 4.35 ± 2.44 (4.14) | 2.08 ± 0.63 (2.33) | 4.68 ± 1.58 (5.45) | 1.80 ± 0.92 (1.98) |
| left | p | 0.897 | 50/50 | 0 | 50 | 1.85 ± 0.38 (1.90) | 3.80 ± 2.64 (3.30) | 2.27 ± 0.40 (2.35) | 5.13 ± 1.12 (5.50) | 2.05 ± 0.65 (2.23) |
| back | p | 0.805 | 50/50 | 0 | 49 | 2.61 ± 0.32 (2.58) | 9.34 ± 23.51 (6.53) | 2.18 ± 0.50 (2.34) | 4.90 ± 1.30 (5.51) | 1.95 ± 0.74 (2.14) |
| right | p | 0.864 | 50/50 | 0 | 49 | 1.86 ± 0.37 (1.85) | 4.91 ± 3.44 (4.50) | 2.15 ± 0.52 (2.23) | 4.79 ± 1.35 (5.30) | 1.88 ± 0.80 (1.94) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.861 | 100/100 | 0 | 98 | 1.90 ± 0.58 (1.87) | 6.30 ± 16.98 (4.28) | 2.17 ± 0.51 (2.35) | 4.87 ± 1.33 (5.48) | 1.92 ± 0.77 (2.12) |
| right | p | 0.861 | 100/100 | 0 | 100 | 1.90 ± 0.58 (1.86) | 4.90 ± 3.01 (4.56) | 2.17 ± 0.54 (2.31) | 4.88 ± 1.38 (5.39) | 1.92 ± 0.82 (2.11) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.880 | 25/25 | 0 | 25 | 1.28 ± 0.26 (1.28) | 4.26 ± 2.37 (4.12) | 2.10 ± 0.58 (2.31) | 4.72 ± 1.48 (5.37) | 1.82 ± 0.88 (1.97) |
| forward/right | p | 0.874 | 25/25 | 0 | 25 | 1.27 ± 0.24 (1.30) | 4.44 ± 2.51 (4.16) | 2.05 ± 0.67 (2.39) | 4.64 ± 1.67 (5.71) | 1.78 ± 0.96 (2.09) |
| left/left | p | 0.897 | 25/25 | 0 | 25 | 1.73 ± 0.38 (1.78) | 3.63 ± 2.45 (3.30) | 2.26 ± 0.37 (2.35) | 5.04 ± 1.07 (5.43) | 2.03 ± 0.64 (2.14) |
| left/right | p | 0.898 | 25/25 | 0 | 25 | 1.98 ± 0.34 (2.00) | 3.97 ± 2.81 (3.30) | 2.28 ± 0.43 (2.35) | 5.22 ± 1.15 (5.52) | 2.08 ± 0.67 (2.26) |
| back/left | p | 0.800 | 25/25 | 0 | 24 | 2.60 ± 0.35 (2.60) | 12.61 ± 32.80 (6.53) | 2.18 ± 0.53 (2.42) | 4.92 ± 1.39 (5.63) | 1.98 ± 0.78 (2.30) |
| back/right | p | 0.810 | 25/25 | 0 | 25 | 2.62 ± 0.29 (2.58) | 6.06 ± 2.90 (6.54) | 2.17 ± 0.45 (2.28) | 4.88 ± 1.20 (5.35) | 1.91 ± 0.71 (2.12) |
| right/left | p | 0.867 | 25/25 | 0 | 24 | 1.99 ± 0.33 (1.96) | 4.69 ± 3.51 (4.34) | 2.15 ± 0.50 (2.29) | 4.80 ± 1.30 (5.38) | 1.86 ± 0.73 (2.10) |
| right/right | p | 0.861 | 25/25 | 0 | 25 | 1.73 ± 0.37 (1.76) | 5.13 ± 3.35 (4.62) | 2.15 ± 0.53 (2.21) | 4.78 ± 1.39 (5.23) | 1.90 ± 0.87 (1.82) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.890 | 5.1 | 5.88 | 2.47 |
| p | normal | 0.832 | 6.1 | 3.87 | 1.37 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.785 | 0.24 | 2.00 ± 0.63 (1.91) | 3.16 | 0.97 |
| p | medium | 16 | 0.922 | 0.88 | 1.06 ± 0.14 (1.03) | 3.47 | 1.17 |
| p | strong | 126 | 0.888 | 0.78 | - | 5.85 | 2.45 |

## Notes

- p: score 0.861, 200/200 kicked, 0 fell; worst sector back (0.805).
