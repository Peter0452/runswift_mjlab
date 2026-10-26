# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_21-10-41_control_h022_500/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.53 ± 0.52 (1.47) |
| Direction error [°] | 4.67 ± 3.39 (3.81) |
| Avg ball speed [m/s] | 1.69 ± 0.26 (1.73) |
| Peak ball speed [m/s] | 4.38 ± 0.66 (4.55) |
| Distance [m] | 1.69 ± 0.41 (1.72) |
| Path length [m] | 1.69 ± 0.41 (1.73) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.850 | 50/50 | 0 | 49 | 1.05 ± 0.36 (1.08) | 5.55 ± 4.05 (3.94) | 1.60 ± 0.30 (1.61) | 4.15 ± 0.74 (4.07) | 1.51 ± 0.43 (1.51) |
| left | p | 0.859 | 50/50 | 0 | 50 | 1.44 ± 0.32 (1.37) | 5.27 ± 3.38 (5.15) | 1.68 ± 0.25 (1.74) | 4.38 ± 0.63 (4.46) | 1.69 ± 0.39 (1.71) |
| back | p | 0.867 | 50/50 | 0 | 50 | 2.18 ± 0.27 (2.16) | 2.99 ± 1.78 (2.66) | 1.79 ± 0.18 (1.79) | 4.64 ± 0.51 (4.80) | 1.85 ± 0.32 (1.87) |
| right | p | 0.845 | 50/50 | 0 | 50 | 1.44 ± 0.32 (1.47) | 4.86 ± 3.29 (4.35) | 1.69 ± 0.24 (1.67) | 4.37 ± 0.66 (4.62) | 1.70 ± 0.41 (1.80) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 99 | 1.53 ± 0.52 (1.41) | 4.53 ± 3.37 (3.53) | 1.68 ± 0.26 (1.72) | 4.37 ± 0.68 (4.52) | 1.68 ± 0.42 (1.73) |
| right | p | 0.857 | 100/100 | 0 | 100 | 1.52 ± 0.52 (1.49) | 4.80 ± 3.40 (3.89) | 1.70 ± 0.25 (1.75) | 4.40 ± 0.65 (4.59) | 1.70 ± 0.40 (1.71) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.849 | 25/25 | 0 | 24 | 1.09 ± 0.44 (1.08) | 5.49 ± 4.07 (3.70) | 1.56 ± 0.30 (1.57) | 4.04 ± 0.75 (3.99) | 1.46 ± 0.43 (1.40) |
| forward/right | p | 0.850 | 25/25 | 0 | 25 | 1.01 ± 0.25 (1.08) | 5.61 ± 4.03 (4.00) | 1.64 ± 0.30 (1.73) | 4.26 ± 0.71 (4.45) | 1.57 ± 0.42 (1.70) |
| left/left | p | 0.854 | 25/25 | 0 | 25 | 1.37 ± 0.32 (1.32) | 5.46 ± 3.55 (5.14) | 1.67 ± 0.24 (1.72) | 4.36 ± 0.57 (4.45) | 1.67 ± 0.35 (1.73) |
| left/right | p | 0.864 | 25/25 | 0 | 25 | 1.51 ± 0.31 (1.52) | 5.09 ± 3.19 (5.16) | 1.70 ± 0.25 (1.80) | 4.40 ± 0.68 (4.47) | 1.71 ± 0.43 (1.70) |
| back/left | p | 0.868 | 25/25 | 0 | 25 | 2.17 ± 0.22 (2.14) | 2.79 ± 1.71 (2.20) | 1.78 ± 0.19 (1.79) | 4.65 ± 0.54 (4.82) | 1.85 ± 0.35 (1.85) |
| back/right | p | 0.866 | 25/25 | 0 | 25 | 2.19 ± 0.31 (2.18) | 3.19 ± 1.82 (3.09) | 1.80 ± 0.16 (1.80) | 4.64 ± 0.47 (4.74) | 1.85 ± 0.28 (1.88) |
| right/left | p | 0.842 | 25/25 | 0 | 25 | 1.51 ± 0.32 (1.48) | 4.40 ± 2.92 (3.78) | 1.71 ± 0.24 (1.71) | 4.42 ± 0.68 (4.64) | 1.74 ± 0.43 (1.81) |
| right/right | p | 0.849 | 25/25 | 0 | 25 | 1.37 ± 0.31 (1.34) | 5.33 ± 3.57 (4.54) | 1.68 ± 0.25 (1.67) | 4.32 ± 0.63 (4.41) | 1.65 ± 0.39 (1.69) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.881 | 4.2 | 4.78 | 1.90 |
| p | normal | 0.830 | 5.2 | 3.99 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.776 | 0.16 | 2.33 ± 0.78 (2.06) | 3.62 | 1.24 |
| p | medium | 20 | 0.896 | 0.80 | 1.19 ± 0.15 (1.23) | 3.80 | 1.38 |
| p | strong | 126 | 0.883 | 0.64 | - | 4.81 | 1.93 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector right (0.845).
