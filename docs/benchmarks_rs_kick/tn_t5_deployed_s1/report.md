# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-21-20_t5_n7_stand01/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.789** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 22 |
| Time to kick [s] | 2.03 ± 0.71 (1.94) |
| Direction error [°] | 13.10 ± 29.14 (4.42) |
| Avg ball speed [m/s] | 2.13 ± 0.77 (2.29) |
| Peak ball speed [m/s] | 4.49 ± 1.71 (5.13) |
| Distance [m] | 1.98 ± 0.95 (2.08) |
| Path length [m] | 1.98 ± 0.96 (2.09) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.830 | 49/50 | 0 | 45 | 1.38 ± 0.33 (1.42) | 6.50 ± 8.78 (4.02) | 2.11 ± 0.70 (2.19) | 4.45 ± 1.59 (5.11) | 1.90 ± 0.86 (2.05) |
| left | p | 0.823 | 50/50 | 0 | 43 | 1.95 ± 0.49 (1.94) | 11.39 ± 22.59 (5.29) | 2.16 ± 0.67 (2.20) | 4.58 ± 1.51 (5.05) | 1.99 ± 0.87 (2.03) |
| back | p | 0.699 | 48/50 | 0 | 39 | 2.79 ± 0.69 (2.91) | 24.45 ± 48.21 (4.11) | 2.07 ± 0.94 (2.57) | 4.40 ± 2.07 (5.60) | 2.00 ± 1.14 (2.49) |
| right | p | 0.806 | 50/50 | 0 | 44 | 2.04 ± 0.45 (2.04) | 10.37 ± 18.73 (5.18) | 2.17 ± 0.74 (2.22) | 4.54 ± 1.61 (4.58) | 2.00 ± 0.92 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 99/100 | 0 | 88 | 2.06 ± 0.71 (1.92) | 10.60 ± 22.85 (4.60) | 2.22 ± 0.72 (2.41) | 4.67 ± 1.62 (5.41) | 2.09 ± 0.94 (2.43) |
| right | p | 0.780 | 98/100 | 0 | 83 | 2.01 ± 0.71 (1.96) | 15.62 ± 34.16 (4.36) | 2.04 ± 0.80 (2.19) | 4.31 ± 1.78 (4.62) | 1.86 ± 0.95 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.861 | 25/25 | 0 | 24 | 1.37 ± 0.31 (1.40) | 5.50 ± 6.06 (4.93) | 2.22 ± 0.58 (2.37) | 4.66 ± 1.35 (5.40) | 2.02 ± 0.83 (2.33) |
| forward/right | p | 0.800 | 24/25 | 0 | 21 | 1.38 ± 0.35 (1.48) | 7.54 ± 10.82 (3.16) | 2.00 ± 0.79 (2.19) | 4.23 ± 1.78 (4.75) | 1.79 ± 0.88 (1.93) |
| left/left | p | 0.846 | 25/25 | 0 | 22 | 1.86 ± 0.39 (1.82) | 6.49 ± 6.07 (4.95) | 2.33 ± 0.51 (2.44) | 4.95 ± 1.22 (5.46) | 2.22 ± 0.77 (2.58) |
| left/right | p | 0.800 | 25/25 | 0 | 21 | 2.03 ± 0.57 (2.14) | 16.28 ± 30.59 (6.25) | 1.99 ± 0.75 (2.11) | 4.20 ± 1.68 (4.20) | 1.77 ± 0.91 (1.69) |
| back/left | p | 0.714 | 24/25 | 0 | 21 | 2.78 ± 0.76 (2.98) | 17.53 ± 36.51 (4.51) | 2.26 ± 0.76 (2.68) | 4.80 ± 1.70 (5.73) | 2.22 ± 1.02 (2.73) |
| back/right | p | 0.685 | 24/25 | 0 | 18 | 2.81 ± 0.62 (2.83) | 31.37 ± 56.75 (3.23) | 1.88 ± 1.05 (2.39) | 3.99 ± 2.32 (5.35) | 1.79 ± 1.21 (2.25) |
| right/left | p | 0.776 | 25/25 | 0 | 21 | 2.24 ± 0.39 (2.20) | 13.16 ± 24.87 (3.69) | 2.05 ± 0.94 (2.29) | 4.29 ± 2.01 (4.25) | 1.93 ± 1.08 (1.80) |
| right/right | p | 0.835 | 25/25 | 0 | 23 | 1.83 ± 0.40 (1.76) | 7.58 ± 8.23 (5.92) | 2.29 ± 0.44 (2.22) | 4.80 ± 1.02 (4.86) | 2.08 ± 0.71 (2.02) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.814 | 13.5 | 5.07 | 2.35 |
| p | normal | 0.765 | 12.7 | 3.91 | 1.60 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.736 | 0.14 | 2.26 ± 0.98 (2.12) | 3.48 | 1.29 |
| p | medium | 20 | 0.851 | 0.72 | 1.10 ± 0.36 (1.17) | 3.56 | 1.39 |
| p | strong | 126 | 0.803 | 0.68 | - | 5.09 | 2.38 |

## Notes

- p: score 0.789, 197/200 kicked, 0 fell; worst sector back (0.699).
