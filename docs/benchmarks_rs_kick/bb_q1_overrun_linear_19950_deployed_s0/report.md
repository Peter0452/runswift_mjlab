# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.768** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.95 ± 1.51 (1.68) |
| Direction error [°] | 20.84 ± 40.05 (6.47) |
| Avg ball speed [m/s] | 1.99 ± 0.62 (2.17) |
| Peak ball speed [m/s] | 4.41 ± 1.48 (4.79) |
| Distance [m] | 1.75 ± 0.78 (1.81) |
| Path length [m] | 1.76 ± 0.79 (1.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.797 | 50/50 | 0 | 45 | 2.00 ± 2.56 (1.33) | 7.71 ± 12.20 (3.63) | 2.06 ± 0.52 (2.16) | 4.49 ± 1.26 (4.36) | 1.76 ± 0.71 (1.66) |
| left | p | 0.784 | 48/50 | 0 | 40 | 1.63 ± 0.48 (1.73) | 19.68 ± 34.80 (6.63) | 1.99 ± 0.57 (2.15) | 4.48 ± 1.41 (4.96) | 1.76 ± 0.75 (1.85) |
| back | p | 0.721 | 49/50 | 0 | 38 | 2.33 ± 0.73 (2.40) | 35.18 ± 58.07 (8.54) | 2.01 ± 0.72 (2.22) | 4.43 ± 1.67 (5.06) | 1.83 ± 0.85 (2.05) |
| right | p | 0.770 | 49/50 | 0 | 39 | 1.82 ± 1.16 (1.72) | 21.02 ± 36.38 (6.10) | 1.91 ± 0.64 (2.11) | 4.26 ± 1.54 (4.56) | 1.66 ± 0.79 (1.69) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 99/100 | 0 | 84 | 1.80 ± 1.09 (1.64) | 19.52 ± 39.68 (6.25) | 2.04 ± 0.58 (2.22) | 4.51 ± 1.39 (4.93) | 1.80 ± 0.75 (1.89) |
| right | p | 0.740 | 97/100 | 0 | 78 | 2.10 ± 1.83 (1.74) | 22.18 ± 40.39 (6.62) | 1.95 ± 0.66 (2.13) | 4.31 ± 1.57 (4.58) | 1.70 ± 0.81 (1.75) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.835 | 25/25 | 0 | 23 | 1.63 ± 1.88 (1.26) | 6.79 ± 13.56 (2.93) | 2.10 ± 0.49 (2.22) | 4.63 ± 1.18 (4.66) | 1.81 ± 0.66 (1.74) |
| forward/right | p | 0.759 | 25/25 | 0 | 22 | 2.38 ± 3.05 (1.36) | 8.63 ± 10.60 (5.44) | 2.02 ± 0.54 (2.05) | 4.35 ± 1.33 (4.19) | 1.70 ± 0.76 (1.65) |
| left/left | p | 0.840 | 25/25 | 0 | 22 | 1.57 ± 0.40 (1.64) | 12.30 ± 21.78 (6.60) | 2.07 ± 0.47 (2.16) | 4.63 ± 1.19 (5.03) | 1.84 ± 0.62 (1.83) |
| left/right | p | 0.728 | 23/25 | 0 | 18 | 1.70 ± 0.54 (1.84) | 27.69 ± 43.47 (7.00) | 1.90 ± 0.66 (2.10) | 4.31 ± 1.60 (4.85) | 1.67 ± 0.87 (1.88) |
| back/left | p | 0.722 | 24/25 | 0 | 19 | 2.29 ± 0.67 (2.39) | 33.61 ± 57.62 (8.31) | 2.10 ± 0.63 (2.30) | 4.63 ± 1.45 (5.14) | 1.92 ± 0.82 (2.12) |
| back/right | p | 0.721 | 25/25 | 0 | 19 | 2.37 ± 0.79 (2.48) | 36.70 ± 58.46 (9.01) | 1.91 ± 0.79 (2.18) | 4.24 ± 1.84 (4.96) | 1.73 ± 0.88 (2.02) |
| right/left | p | 0.788 | 25/25 | 0 | 20 | 1.73 ± 0.49 (1.72) | 25.95 ± 44.09 (6.26) | 1.88 ± 0.69 (2.16) | 4.17 ± 1.64 (4.56) | 1.64 ± 0.84 (1.78) |
| right/right | p | 0.751 | 24/25 | 0 | 19 | 1.92 ± 1.57 (1.68) | 15.89 ± 25.01 (5.67) | 1.95 ± 0.59 (2.05) | 4.35 ± 1.44 (4.50) | 1.69 ± 0.73 (1.66) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.798 | 18.9 | 5.01 | 2.07 |
| p | normal | 0.738 | 22.7 | 3.83 | 1.44 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.709 | 0.14 | 2.30 ± 0.97 (2.17) | 3.59 | 1.31 |
| p | medium | 16 | 0.785 | 0.69 | 1.24 ± 0.24 (1.34) | 4.01 | 1.55 |
| p | strong | 126 | 0.793 | 0.65 | - | 4.85 | 1.98 |

## Notes

- p: score 0.768, 196/200 kicked, 0 fell; worst sector back (0.721).
