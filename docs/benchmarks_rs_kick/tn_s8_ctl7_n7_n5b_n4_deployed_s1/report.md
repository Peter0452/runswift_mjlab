# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.799** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 175 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.01 ± 1.49 (1.71) |
| Direction error [°] | 13.43 ± 28.42 (4.88) |
| Avg ball speed [m/s] | 2.26 ± 0.65 (2.37) |
| Peak ball speed [m/s] | 4.82 ± 1.47 (5.29) |
| Distance [m] | 2.15 ± 0.87 (2.29) |
| Path length [m] | 2.16 ± 0.88 (2.30) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.807 | 49/50 | 0 | 43 | 1.65 ± 1.92 (1.30) | 9.53 ± 17.83 (4.93) | 2.23 ± 0.66 (2.38) | 4.82 ± 1.53 (5.26) | 2.12 ± 0.86 (2.42) |
| left | p | 0.828 | 50/50 | 0 | 44 | 1.92 ± 1.47 (1.70) | 11.43 ± 22.99 (4.24) | 2.23 ± 0.61 (2.31) | 4.77 ± 1.40 (5.02) | 2.11 ± 0.85 (2.06) |
| back | p | 0.754 | 50/50 | 0 | 43 | 2.74 ± 1.44 (2.57) | 23.01 ± 44.03 (6.10) | 2.30 ± 0.74 (2.45) | 4.89 ± 1.63 (5.47) | 2.23 ± 0.98 (2.47) |
| right | p | 0.807 | 49/50 | 0 | 45 | 1.73 ± 0.40 (1.74) | 9.60 ± 17.35 (4.85) | 2.29 ± 0.55 (2.34) | 4.81 ± 1.30 (5.24) | 2.12 ± 0.79 (2.23) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.794 | 98/100 | 0 | 87 | 1.93 ± 1.31 (1.65) | 14.24 ± 29.74 (4.63) | 2.26 ± 0.66 (2.37) | 4.84 ± 1.50 (5.37) | 2.16 ± 0.89 (2.37) |
| right | p | 0.805 | 100/100 | 0 | 88 | 2.09 ± 1.64 (1.76) | 12.65 ± 27.05 (5.14) | 2.26 ± 0.64 (2.31) | 4.81 ± 1.45 (5.24) | 2.13 ± 0.86 (2.20) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.812 | 24/25 | 0 | 22 | 1.24 ± 0.26 (1.28) | 10.98 ± 23.52 (3.63) | 2.19 ± 0.72 (2.38) | 4.73 ± 1.64 (5.33) | 2.09 ± 0.91 (2.47) |
| forward/right | p | 0.803 | 25/25 | 0 | 21 | 2.05 ± 2.61 (1.38) | 8.14 ± 9.39 (5.25) | 2.27 ± 0.60 (2.30) | 4.90 ± 1.41 (5.26) | 2.16 ± 0.81 (2.38) |
| left/left | p | 0.845 | 25/25 | 0 | 23 | 2.08 ± 2.02 (1.60) | 6.16 ± 6.03 (4.02) | 2.36 ± 0.41 (2.37) | 5.09 ± 1.00 (5.34) | 2.27 ± 0.67 (2.40) |
| left/right | p | 0.812 | 25/25 | 0 | 21 | 1.76 ± 0.48 (1.84) | 16.70 ± 31.07 (5.75) | 2.10 ± 0.74 (2.23) | 4.45 ± 1.65 (4.41) | 1.95 ± 0.97 (1.86) |
| back/left | p | 0.745 | 25/25 | 0 | 21 | 2.55 ± 1.26 (2.54) | 26.82 ± 46.19 (7.40) | 2.28 ± 0.79 (2.44) | 4.86 ± 1.74 (5.44) | 2.25 ± 1.05 (2.47) |
| back/right | p | 0.764 | 25/25 | 0 | 22 | 2.93 ± 1.58 (2.64) | 19.20 ± 41.40 (3.93) | 2.31 ± 0.68 (2.46) | 4.93 ± 1.52 (5.49) | 2.22 ± 0.89 (2.48) |
| right/left | p | 0.773 | 24/25 | 0 | 21 | 1.83 ± 0.43 (1.87) | 12.79 ± 23.48 (3.66) | 2.20 ± 0.63 (2.27) | 4.65 ± 1.48 (4.86) | 2.02 ± 0.85 (2.08) |
| right/right | p | 0.841 | 25/25 | 0 | 24 | 1.64 ± 0.33 (1.58) | 6.54 ± 6.44 (5.06) | 2.36 ± 0.45 (2.39) | 4.96 ± 1.09 (5.40) | 2.21 ± 0.72 (2.23) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.832 | 13.2 | 5.28 | 2.45 |
| p | normal | 0.767 | 13.6 | 4.36 | 1.84 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.711 | 0.10 | 2.60 ± 0.96 (2.40) | 4.02 | 1.60 |
| p | medium | 20 | 0.871 | 0.69 | 1.29 ± 0.18 (1.31) | 4.12 | 1.67 |
| p | strong | 126 | 0.826 | 0.70 | - | 5.26 | 2.44 |

## Notes

- p: score 0.799, 198/200 kicked, 0 fell; worst sector back (0.754).
