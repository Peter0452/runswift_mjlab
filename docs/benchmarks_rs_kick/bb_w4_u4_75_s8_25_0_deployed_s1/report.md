# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w4_u4_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.86 ± 0.58 (1.78) |
| Direction error [°] | 6.29 ± 12.37 (4.68) |
| Avg ball speed [m/s] | 2.47 ± 0.53 (2.62) |
| Peak ball speed [m/s] | 5.31 ± 1.32 (5.93) |
| Distance [m] | 2.56 ± 0.94 (2.86) |
| Path length [m] | 2.57 ± 0.94 (2.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.880 | 50/50 | 0 | 50 | 1.27 ± 0.26 (1.28) | 4.69 ± 2.90 (4.12) | 2.42 ± 0.45 (2.58) | 5.26 ± 1.19 (5.89) | 2.46 ± 0.84 (2.80) |
| left | p | 0.862 | 50/50 | 0 | 49 | 1.80 ± 0.38 (1.73) | 6.13 ± 4.30 (5.51) | 2.44 ± 0.55 (2.62) | 5.20 ± 1.37 (5.87) | 2.49 ± 0.95 (2.87) |
| back | p | 0.816 | 50/50 | 0 | 49 | 2.56 ± 0.40 (2.57) | 9.72 ± 23.63 (5.89) | 2.61 ± 0.60 (2.75) | 5.59 ± 1.42 (6.15) | 2.82 ± 1.00 (3.20) |
| right | p | 0.865 | 50/50 | 0 | 50 | 1.81 ± 0.38 (1.81) | 4.62 ± 3.10 (3.62) | 2.42 ± 0.48 (2.58) | 5.18 ± 1.24 (5.85) | 2.45 ± 0.92 (2.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 99 | 1.86 ± 0.58 (1.78) | 5.48 ± 3.98 (4.20) | 2.47 ± 0.53 (2.63) | 5.34 ± 1.31 (5.97) | 2.57 ± 0.93 (2.88) |
| right | p | 0.859 | 100/100 | 0 | 99 | 1.87 ± 0.59 (1.77) | 7.10 ± 17.00 (5.13) | 2.47 ± 0.52 (2.62) | 5.28 ± 1.32 (5.87) | 2.54 ± 0.95 (2.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.881 | 25/25 | 0 | 25 | 1.24 ± 0.25 (1.28) | 4.30 ± 3.18 (3.24) | 2.38 ± 0.45 (2.61) | 5.19 ± 1.20 (5.91) | 2.41 ± 0.84 (2.80) |
| forward/right | p | 0.880 | 25/25 | 0 | 25 | 1.30 ± 0.27 (1.32) | 5.07 ± 2.52 (5.15) | 2.46 ± 0.44 (2.57) | 5.33 ± 1.17 (5.87) | 2.52 ± 0.84 (2.79) |
| left/left | p | 0.857 | 25/25 | 0 | 24 | 1.69 ± 0.34 (1.64) | 6.88 ± 4.68 (6.30) | 2.41 ± 0.61 (2.63) | 5.20 ± 1.49 (6.01) | 2.51 ± 0.97 (2.91) |
| left/right | p | 0.868 | 25/25 | 0 | 25 | 1.92 ± 0.38 (1.98) | 5.39 ± 3.73 (5.10) | 2.47 ± 0.47 (2.61) | 5.21 ± 1.23 (5.78) | 2.47 ± 0.94 (2.79) |
| back/left | p | 0.812 | 25/25 | 0 | 25 | 2.60 ± 0.26 (2.60) | 6.90 ± 3.68 (6.08) | 2.67 ± 0.50 (2.75) | 5.71 ± 1.22 (6.34) | 2.88 ± 0.92 (3.34) |
| back/right | p | 0.820 | 25/25 | 0 | 24 | 2.53 ± 0.50 (2.52) | 12.55 ± 32.98 (5.39) | 2.55 ± 0.67 (2.73) | 5.47 ± 1.58 (6.08) | 2.76 ± 1.06 (3.02) |
| right/left | p | 0.861 | 25/25 | 0 | 25 | 1.91 ± 0.37 (1.92) | 3.84 ± 3.14 (2.82) | 2.44 ± 0.48 (2.62) | 5.26 ± 1.24 (5.88) | 2.49 ± 0.92 (2.78) |
| right/right | p | 0.869 | 25/25 | 0 | 25 | 1.71 ± 0.36 (1.64) | 5.39 ± 2.86 (5.29) | 2.41 ± 0.47 (2.39) | 5.10 ± 1.23 (5.59) | 2.42 ± 0.92 (2.71) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.889 | 6.1 | 6.20 | 3.19 |
| p | normal | 0.824 | 6.5 | 4.42 | 1.92 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.764 | 0.13 | 2.40 ± 0.82 (2.32) | 3.72 | 1.41 |
| p | medium | 20 | 0.892 | 0.78 | 1.22 ± 0.12 (1.24) | 3.90 | 1.53 |
| p | strong | 126 | 0.890 | 0.83 | - | 6.21 | 3.21 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.816).
