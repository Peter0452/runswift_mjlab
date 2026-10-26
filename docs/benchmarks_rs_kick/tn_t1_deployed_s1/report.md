# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t1_stand03/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.753** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 159 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 2.23 ± 0.91 (2.00) |
| Direction error [°] | 14.51 ± 22.71 (9.43) |
| Avg ball speed [m/s] | 2.08 ± 0.75 (2.35) |
| Peak ball speed [m/s] | 4.27 ± 1.60 (4.95) |
| Distance [m] | 1.92 ± 0.93 (2.21) |
| Path length [m] | 1.92 ± 0.93 (2.21) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.824 | 50/50 | 0 | 45 | 1.61 ± 0.46 (1.63) | 8.57 ± 9.54 (6.38) | 2.04 ± 0.67 (2.20) | 4.24 ± 1.48 (4.81) | 1.82 ± 0.83 (2.06) |
| left | p | 0.791 | 50/50 | 0 | 42 | 2.06 ± 0.56 (1.99) | 12.37 ± 16.76 (8.88) | 2.05 ± 0.74 (2.25) | 4.22 ± 1.59 (4.87) | 1.88 ± 0.90 (2.19) |
| back | p | 0.610 | 49/50 | 0 | 29 | 3.19 ± 1.12 (3.20) | 26.00 ± 36.97 (13.25) | 2.00 ± 0.98 (2.55) | 4.09 ± 2.02 (5.18) | 1.93 ± 1.15 (2.47) |
| right | p | 0.786 | 50/50 | 0 | 43 | 2.10 ± 0.48 (2.10) | 11.32 ± 12.73 (9.32) | 2.21 ± 0.52 (2.38) | 4.51 ± 1.16 (4.97) | 2.02 ± 0.79 (2.32) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.761 | 100/100 | 0 | 81 | 2.15 ± 0.80 (1.97) | 14.86 ± 24.78 (8.94) | 2.09 ± 0.72 (2.35) | 4.32 ± 1.53 (4.98) | 1.93 ± 0.91 (2.21) |
| right | p | 0.745 | 99/100 | 0 | 78 | 2.32 ± 1.01 (2.12) | 14.15 ± 20.40 (9.76) | 2.06 ± 0.78 (2.34) | 4.21 ± 1.66 (4.93) | 1.90 ± 0.95 (2.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 23 | 1.48 ± 0.34 (1.54) | 7.36 ± 6.22 (5.74) | 2.07 ± 0.55 (2.16) | 4.33 ± 1.26 (4.84) | 1.85 ± 0.77 (2.14) |
| forward/right | p | 0.809 | 25/25 | 0 | 22 | 1.74 ± 0.52 (1.72) | 9.78 ± 11.84 (7.64) | 2.01 ± 0.77 (2.33) | 4.14 ± 1.67 (4.76) | 1.80 ± 0.89 (2.06) |
| left/left | p | 0.806 | 25/25 | 0 | 22 | 1.97 ± 0.48 (1.92) | 9.65 ± 9.50 (8.75) | 2.05 ± 0.80 (2.40) | 4.23 ± 1.69 (5.03) | 1.91 ± 0.91 (2.37) |
| left/right | p | 0.776 | 25/25 | 0 | 20 | 2.15 ± 0.62 (2.24) | 15.10 ± 21.38 (9.00) | 2.05 ± 0.69 (2.03) | 4.21 ± 1.48 (3.93) | 1.86 ± 0.89 (1.59) |
| back/left | p | 0.633 | 25/25 | 0 | 15 | 2.93 ± 0.92 (3.18) | 29.82 ± 41.87 (13.37) | 2.02 ± 0.88 (2.55) | 4.14 ± 1.82 (4.95) | 1.90 ± 1.09 (2.19) |
| back/right | p | 0.586 | 24/25 | 0 | 14 | 3.46 ± 1.24 (3.26) | 22.02 ± 30.56 (13.10) | 1.98 ± 1.07 (2.55) | 4.05 ± 2.21 (5.26) | 1.96 ± 1.21 (2.55) |
| right/left | p | 0.765 | 25/25 | 0 | 21 | 2.23 ± 0.49 (2.26) | 12.63 ± 16.21 (8.27) | 2.23 ± 0.56 (2.40) | 4.57 ± 1.22 (5.14) | 2.07 ± 0.82 (2.51) |
| right/right | p | 0.808 | 25/25 | 0 | 22 | 1.96 ± 0.43 (1.96) | 10.01 ± 7.61 (10.18) | 2.20 ± 0.48 (2.37) | 4.45 ± 1.08 (4.70) | 1.97 ± 0.77 (2.17) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.761 | 15.1 | 4.91 | 2.36 |
| p | normal | 0.745 | 13.9 | 3.61 | 1.46 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.714 | 0.17 | 2.09 ± 1.02 (2.04) | 3.14 | 1.13 |
| p | medium | 20 | 0.854 | 0.79 | 1.05 ± 0.29 (1.13) | 3.36 | 1.25 |
| p | strong | 126 | 0.753 | 0.65 | - | 4.90 | 2.36 |

## Notes

- p: score 0.753, 199/200 kicked, 0 fell; worst sector back (0.610).
