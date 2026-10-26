# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.63 ± 0.57 (1.59) |
| Direction error [°] | 5.40 ± 4.02 (4.77) |
| Avg ball speed [m/s] | 1.85 ± 0.33 (1.81) |
| Peak ball speed [m/s] | 3.95 ± 0.76 (3.90) |
| Distance [m] | 1.52 ± 0.46 (1.45) |
| Path length [m] | 1.53 ± 0.47 (1.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.846 | 50/50 | 0 | 49 | 1.07 ± 0.25 (1.06) | 4.99 ± 3.34 (4.38) | 1.70 ± 0.22 (1.68) | 3.64 ± 0.54 (3.55) | 1.31 ± 0.36 (1.19) |
| left | p | 0.847 | 50/50 | 0 | 50 | 1.54 ± 0.38 (1.55) | 5.43 ± 2.90 (4.85) | 1.89 ± 0.28 (1.84) | 4.03 ± 0.67 (4.07) | 1.57 ± 0.44 (1.55) |
| back | p | 0.809 | 50/50 | 0 | 49 | 2.36 ± 0.30 (2.33) | 6.18 ± 5.83 (5.33) | 1.92 ± 0.44 (2.01) | 4.08 ± 0.99 (4.40) | 1.64 ± 0.54 (1.73) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.54 ± 0.33 (1.62) | 4.99 ± 3.18 (4.54) | 1.89 ± 0.27 (1.87) | 4.05 ± 0.66 (4.09) | 1.58 ± 0.42 (1.54) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.63 ± 0.56 (1.62) | 5.28 ± 3.03 (4.91) | 1.85 ± 0.32 (1.81) | 3.96 ± 0.76 (3.89) | 1.53 ± 0.47 (1.48) |
| right | p | 0.836 | 100/100 | 0 | 99 | 1.63 ± 0.57 (1.57) | 5.52 ± 4.81 (4.68) | 1.85 ± 0.33 (1.80) | 3.93 ± 0.76 (3.94) | 1.52 ± 0.45 (1.45) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 24 | 1.07 ± 0.24 (1.06) | 5.19 ± 2.99 (5.14) | 1.65 ± 0.20 (1.64) | 3.52 ± 0.53 (3.36) | 1.24 ± 0.35 (1.15) |
| forward/right | p | 0.853 | 25/25 | 0 | 25 | 1.07 ± 0.26 (1.00) | 4.79 ± 3.64 (3.89) | 1.75 ± 0.23 (1.73) | 3.75 ± 0.53 (3.74) | 1.37 ± 0.36 (1.39) |
| left/left | p | 0.847 | 25/25 | 0 | 25 | 1.45 ± 0.36 (1.40) | 6.15 ± 2.92 (6.17) | 1.87 ± 0.29 (1.81) | 3.98 ± 0.68 (3.89) | 1.55 ± 0.44 (1.45) |
| left/right | p | 0.848 | 25/25 | 0 | 25 | 1.63 ± 0.37 (1.60) | 4.71 ± 2.70 (4.37) | 1.91 ± 0.27 (1.93) | 4.07 ± 0.66 (4.16) | 1.60 ± 0.44 (1.67) |
| back/left | p | 0.824 | 25/25 | 0 | 25 | 2.35 ± 0.30 (2.36) | 5.15 ± 2.99 (4.77) | 1.94 ± 0.42 (2.04) | 4.15 ± 0.95 (4.44) | 1.67 ± 0.55 (1.81) |
| back/right | p | 0.793 | 25/25 | 0 | 24 | 2.38 ± 0.31 (2.32) | 7.21 ± 7.55 (5.61) | 1.90 ± 0.46 (1.94) | 4.01 ± 1.02 (4.19) | 1.61 ± 0.53 (1.71) |
| right/left | p | 0.866 | 25/25 | 0 | 25 | 1.64 ± 0.31 (1.66) | 4.63 ± 3.02 (4.10) | 1.96 ± 0.25 (1.92) | 4.19 ± 0.61 (4.25) | 1.66 ± 0.40 (1.63) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.44 ± 0.32 (1.54) | 5.36 ± 3.30 (4.67) | 1.83 ± 0.28 (1.85) | 3.90 ± 0.68 (4.02) | 1.49 ± 0.42 (1.47) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.854 | 5.5 | 4.34 | 1.75 |
| p | normal | 0.827 | 5.3 | 3.55 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.796 | 0.26 | 2.02 ± 0.65 (1.95) | 3.32 | 1.14 |
| p | medium | 15 | 0.898 | 0.84 | 0.97 ± 0.28 (1.01) | 3.15 | 1.07 |
| p | strong | 125 | 0.854 | 0.58 | - | 4.35 | 1.76 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector back (0.809).
