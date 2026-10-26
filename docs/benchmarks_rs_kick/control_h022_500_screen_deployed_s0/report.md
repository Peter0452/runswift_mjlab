# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_21-10-41_control_h022_500/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.769** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.18 ± 2.06 (1.72) |
| Direction error [°] | 18.23 ± 35.54 (6.57) |
| Avg ball speed [m/s] | 1.98 ± 0.55 (2.15) |
| Peak ball speed [m/s] | 4.39 ± 1.34 (4.75) |
| Distance [m] | 1.66 ± 0.70 (1.75) |
| Path length [m] | 1.67 ± 0.70 (1.76) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.782 | 49/50 | 0 | 43 | 1.88 ± 2.37 (1.36) | 8.28 ± 10.26 (4.83) | 1.93 ± 0.54 (2.03) | 4.23 ± 1.29 (4.28) | 1.58 ± 0.68 (1.67) |
| left | p | 0.801 | 50/50 | 0 | 43 | 1.99 ± 1.81 (1.72) | 19.20 ± 34.40 (6.58) | 2.01 ± 0.59 (2.17) | 4.50 ± 1.44 (5.02) | 1.73 ± 0.71 (1.92) |
| back | p | 0.721 | 49/50 | 0 | 42 | 2.93 ± 2.26 (2.54) | 25.56 ± 48.76 (9.13) | 2.06 ± 0.48 (2.20) | 4.57 ± 1.19 (4.87) | 1.77 ± 0.67 (1.90) |
| right | p | 0.770 | 49/50 | 0 | 41 | 1.91 ± 1.51 (1.72) | 19.88 ± 35.08 (6.32) | 1.91 ± 0.58 (2.06) | 4.26 ± 1.40 (4.61) | 1.58 ± 0.71 (1.69) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.797 | 99/100 | 0 | 88 | 1.82 ± 1.09 (1.70) | 16.87 ± 34.59 (6.57) | 2.02 ± 0.49 (2.14) | 4.50 ± 1.21 (4.78) | 1.71 ± 0.64 (1.76) |
| right | p | 0.740 | 98/100 | 0 | 81 | 2.54 ± 2.66 (1.74) | 19.61 ± 36.42 (6.59) | 1.93 ± 0.60 (2.16) | 4.27 ± 1.45 (4.72) | 1.61 ± 0.74 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.821 | 25/25 | 0 | 23 | 1.67 ± 1.88 (1.28) | 7.40 ± 10.44 (4.26) | 2.04 ± 0.42 (2.12) | 4.49 ± 1.05 (4.73) | 1.69 ± 0.56 (1.69) |
| forward/right | p | 0.744 | 24/25 | 0 | 20 | 2.09 ± 2.76 (1.36) | 9.21 ± 9.99 (5.27) | 1.83 ± 0.62 (1.88) | 3.96 ± 1.45 (3.97) | 1.46 ± 0.77 (1.41) |
| left/left | p | 0.841 | 25/25 | 0 | 23 | 1.56 ± 0.39 (1.64) | 11.56 ± 20.10 (5.79) | 2.08 ± 0.50 (2.19) | 4.64 ± 1.25 (4.92) | 1.80 ± 0.62 (1.89) |
| left/right | p | 0.762 | 25/25 | 0 | 20 | 2.41 ± 2.45 (1.90) | 26.83 ± 42.96 (6.92) | 1.94 ± 0.66 (2.16) | 4.36 ± 1.61 (5.04) | 1.65 ± 0.77 (1.93) |
| back/left | p | 0.730 | 24/25 | 0 | 21 | 2.32 ± 0.66 (2.47) | 26.78 ± 50.65 (9.39) | 2.06 ± 0.48 (2.15) | 4.59 ± 1.18 (4.83) | 1.77 ± 0.67 (1.76) |
| back/right | p | 0.713 | 25/25 | 0 | 21 | 3.52 ± 2.98 (2.58) | 24.39 ± 46.84 (8.99) | 2.06 ± 0.49 (2.20) | 4.55 ± 1.20 (4.98) | 1.76 ± 0.66 (1.96) |
| right/left | p | 0.797 | 25/25 | 0 | 21 | 1.74 ± 0.49 (1.80) | 22.14 ± 39.00 (7.08) | 1.93 ± 0.54 (2.06) | 4.30 ± 1.33 (4.66) | 1.59 ± 0.69 (1.70) |
| right/right | p | 0.743 | 24/25 | 0 | 20 | 2.08 ± 2.08 (1.63) | 17.52 ± 30.29 (5.68) | 1.89 ± 0.61 (2.09) | 4.21 ± 1.47 (4.53) | 1.56 ± 0.73 (1.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.796 | 15.4 | 4.98 | 1.95 |
| p | normal | 0.741 | 21.1 | 3.80 | 1.37 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.709 | 0.20 | 2.23 ± 0.89 (2.11) | 3.54 | 1.22 |
| p | medium | 16 | 0.830 | 0.69 | 1.28 ± 0.21 (1.29) | 4.16 | 1.60 |
| p | strong | 126 | 0.789 | 0.64 | - | 4.81 | 1.87 |

## Notes

- p: score 0.769, 197/200 kicked, 0 fell; worst sector back (0.721).
