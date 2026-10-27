# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.53 (1.52) |
| Direction error [°] | 5.14 ± 9.46 (3.63) |
| Avg ball speed [m/s] | 1.88 ± 0.35 (1.89) |
| Peak ball speed [m/s] | 4.39 ± 0.85 (4.53) |
| Distance [m] | 1.67 ± 0.51 (1.69) |
| Path length [m] | 1.68 ± 0.51 (1.70) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.855 | 50/50 | 0 | 48 | 1.09 ± 0.37 (1.05) | 4.68 ± 4.03 (3.31) | 1.76 ± 0.31 (1.75) | 4.12 ± 0.76 (4.03) | 1.46 ± 0.45 (1.51) |
| left | p | 0.866 | 50/50 | 0 | 50 | 1.50 ± 0.31 (1.49) | 4.36 ± 3.00 (3.74) | 1.91 ± 0.30 (1.90) | 4.49 ± 0.77 (4.77) | 1.73 ± 0.47 (1.73) |
| back | p | 0.844 | 50/50 | 0 | 48 | 2.23 ± 0.33 (2.23) | 6.66 ± 17.94 (2.88) | 1.97 ± 0.41 (2.02) | 4.55 ± 0.98 (4.90) | 1.81 ± 0.55 (1.90) |
| right | p | 0.848 | 50/50 | 0 | 50 | 1.51 ± 0.30 (1.52) | 4.89 ± 2.74 (4.35) | 1.91 ± 0.33 (2.00) | 4.42 ± 0.83 (4.68) | 1.68 ± 0.50 (1.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.858 | 100/100 | 0 | 99 | 1.59 ± 0.53 (1.54) | 4.38 ± 3.15 (3.54) | 1.91 ± 0.33 (1.89) | 4.43 ± 0.81 (4.64) | 1.70 ± 0.52 (1.63) |
| right | p | 0.849 | 100/100 | 0 | 97 | 1.58 ± 0.52 (1.52) | 5.91 ± 12.95 (3.87) | 1.86 ± 0.36 (1.89) | 4.35 ± 0.89 (4.49) | 1.65 ± 0.49 (1.72) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.861 | 25/25 | 0 | 25 | 1.11 ± 0.37 (1.04) | 4.09 ± 2.44 (3.61) | 1.76 ± 0.32 (1.83) | 4.14 ± 0.78 (4.07) | 1.48 ± 0.48 (1.51) |
| forward/right | p | 0.850 | 25/25 | 0 | 23 | 1.08 ± 0.37 (1.08) | 5.26 ± 5.07 (3.11) | 1.75 ± 0.30 (1.74) | 4.10 ± 0.73 (3.99) | 1.45 ± 0.42 (1.52) |
| left/left | p | 0.868 | 25/25 | 0 | 25 | 1.41 ± 0.30 (1.42) | 3.97 ± 2.64 (3.30) | 1.93 ± 0.30 (1.89) | 4.47 ± 0.75 (4.80) | 1.72 ± 0.47 (1.71) |
| left/right | p | 0.864 | 25/25 | 0 | 25 | 1.58 ± 0.31 (1.54) | 4.74 ± 3.28 (4.79) | 1.89 ± 0.30 (1.91) | 4.51 ± 0.79 (4.57) | 1.74 ± 0.46 (1.84) |
| back/left | p | 0.859 | 25/25 | 0 | 24 | 2.25 ± 0.33 (2.22) | 4.21 ± 4.24 (2.28) | 2.00 ± 0.31 (2.04) | 4.64 ± 0.80 (4.99) | 1.85 ± 0.52 (1.84) |
| back/right | p | 0.830 | 25/25 | 0 | 24 | 2.21 ± 0.33 (2.24) | 9.10 ± 24.78 (4.18) | 1.93 ± 0.48 (1.95) | 4.45 ± 1.13 (4.88) | 1.78 ± 0.57 (1.94) |
| right/left | p | 0.843 | 25/25 | 0 | 25 | 1.59 ± 0.28 (1.60) | 5.23 ± 2.81 (4.24) | 1.92 ± 0.34 (1.98) | 4.49 ± 0.84 (4.68) | 1.74 ± 0.54 (1.86) |
| right/right | p | 0.854 | 25/25 | 0 | 25 | 1.43 ± 0.30 (1.36) | 4.54 ± 2.62 (4.72) | 1.89 ± 0.31 (2.06) | 4.36 ± 0.81 (4.68) | 1.63 ± 0.44 (1.73) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 4.1 | 4.93 | 1.97 |
| p | normal | 0.822 | 6.2 | 3.86 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.773 | 0.16 | 2.18 ± 0.67 (2.11) | 3.48 | 1.15 |
| p | medium | 18 | 0.897 | 0.82 | 1.15 ± 0.17 (1.18) | 3.66 | 1.26 |
| p | strong | 124 | 0.885 | 0.66 | - | 4.93 | 1.98 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector back (0.844).
