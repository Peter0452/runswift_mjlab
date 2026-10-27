# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v3_s8_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.858** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 6 |
| Time to kick [s] | 1.60 ± 0.53 (1.50) |
| Direction error [°] | 5.30 ± 3.35 (4.82) |
| Avg ball speed [m/s] | 1.82 ± 0.49 (2.00) |
| Peak ball speed [m/s] | 3.97 ± 1.14 (4.41) |
| Distance [m] | 1.40 ± 0.64 (1.53) |
| Path length [m] | 1.41 ± 0.64 (1.54) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.860 | 50/50 | 0 | 49 | 1.05 ± 0.22 (1.09) | 4.60 ± 3.30 (3.94) | 1.51 ± 0.52 (1.45) | 3.27 ± 1.11 (3.07) | 1.01 ± 0.59 (0.82) |
| left | p | 0.874 | 50/50 | 0 | 49 | 1.54 ± 0.35 (1.53) | 5.21 ± 3.55 (4.70) | 1.92 ± 0.46 (2.08) | 4.25 ± 1.07 (4.76) | 1.55 ± 0.60 (1.68) |
| back | p | 0.847 | 50/50 | 0 | 50 | 2.28 ± 0.26 (2.27) | 5.60 ± 2.52 (5.69) | 2.03 ± 0.38 (2.24) | 4.41 ± 0.95 (4.97) | 1.68 ± 0.56 (1.88) |
| right | p | 0.853 | 50/50 | 0 | 49 | 1.53 ± 0.35 (1.49) | 5.79 ± 3.77 (4.95) | 1.80 ± 0.45 (1.99) | 3.94 ± 1.07 (4.38) | 1.39 ± 0.59 (1.51) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.856 | 100/100 | 0 | 99 | 1.60 ± 0.53 (1.51) | 5.41 ± 3.37 (5.06) | 1.84 ± 0.47 (2.01) | 4.00 ± 1.12 (4.47) | 1.43 ± 0.63 (1.57) |
| right | p | 0.861 | 100/100 | 0 | 98 | 1.60 ± 0.53 (1.50) | 5.19 ± 3.32 (4.39) | 1.80 ± 0.51 (1.93) | 3.93 ± 1.16 (4.27) | 1.38 ± 0.64 (1.46) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.853 | 25/25 | 0 | 25 | 1.05 ± 0.21 (1.08) | 4.99 ± 3.18 (4.26) | 1.58 ± 0.45 (1.52) | 3.37 ± 0.99 (3.24) | 1.06 ± 0.54 (0.98) |
| forward/right | p | 0.866 | 25/25 | 0 | 24 | 1.05 ± 0.23 (1.10) | 4.21 ± 3.37 (3.86) | 1.45 ± 0.58 (1.36) | 3.18 ± 1.21 (2.99) | 0.95 ± 0.62 (0.80) |
| left/left | p | 0.865 | 25/25 | 0 | 24 | 1.43 ± 0.33 (1.50) | 5.54 ± 4.10 (4.47) | 1.83 ± 0.50 (2.02) | 4.02 ± 1.17 (4.54) | 1.44 ± 0.65 (1.57) |
| left/right | p | 0.884 | 25/25 | 0 | 25 | 1.66 ± 0.33 (1.64) | 4.89 ± 2.85 (4.92) | 2.02 ± 0.39 (2.17) | 4.47 ± 0.91 (4.88) | 1.66 ± 0.53 (1.87) |
| back/left | p | 0.846 | 25/25 | 0 | 25 | 2.28 ± 0.25 (2.20) | 5.46 ± 2.57 (5.61) | 2.06 ± 0.32 (2.19) | 4.48 ± 0.87 (4.96) | 1.72 ± 0.52 (1.97) |
| back/right | p | 0.849 | 25/25 | 0 | 25 | 2.27 ± 0.26 (2.30) | 5.74 ± 2.46 (5.89) | 1.99 ± 0.43 (2.24) | 4.34 ± 1.01 (4.99) | 1.63 ± 0.60 (1.80) |
| right/left | p | 0.858 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.60) | 5.65 ± 3.41 (5.18) | 1.88 ± 0.46 (2.14) | 4.13 ± 1.13 (4.78) | 1.50 ± 0.61 (1.70) |
| right/right | p | 0.847 | 25/25 | 0 | 24 | 1.43 ± 0.35 (1.42) | 5.93 ± 4.09 (4.37) | 1.73 ± 0.42 (1.80) | 3.75 ± 0.98 (3.84) | 1.28 ± 0.54 (1.37) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.866 | 5.4 | 4.68 | 1.78 |
| p | normal | 0.851 | 5.2 | 3.25 | 1.03 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.832 | 0.43 | 1.70 ± 0.58 (1.58) | 2.72 | 0.74 |
| p | medium | 16 | 0.886 | 0.76 | 0.82 ± 0.25 (0.81) | 2.65 | 0.72 |
| p | strong | 126 | 0.867 | 0.63 | - | 4.71 | 1.80 |

## Notes

- p: score 0.858, 200/200 kicked, 0 fell; worst sector back (0.847).
