# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r1_u5_u0.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.794** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 174 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 2.04 ± 1.46 (1.75) |
| Direction error [°] | 13.82 ± 30.06 (4.60) |
| Avg ball speed [m/s] | 2.17 ± 0.63 (2.30) |
| Peak ball speed [m/s] | 4.67 ± 1.47 (5.18) |
| Distance [m] | 1.96 ± 0.79 (2.07) |
| Path length [m] | 1.97 ± 0.79 (2.08) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.803 | 49/50 | 0 | 43 | 1.73 ± 2.06 (1.36) | 8.11 ± 10.44 (4.16) | 2.21 ± 0.63 (2.36) | 4.78 ± 1.47 (5.37) | 2.04 ± 0.78 (2.19) |
| left | p | 0.815 | 49/50 | 0 | 43 | 1.75 ± 0.46 (1.76) | 11.09 ± 22.51 (4.60) | 2.16 ± 0.58 (2.36) | 4.67 ± 1.39 (5.25) | 1.94 ± 0.75 (2.08) |
| back | p | 0.744 | 50/50 | 0 | 43 | 2.83 ± 1.67 (2.62) | 23.94 ± 45.63 (6.97) | 2.16 ± 0.72 (2.31) | 4.69 ± 1.62 (5.33) | 1.99 ± 0.86 (2.18) |
| right | p | 0.816 | 50/50 | 0 | 45 | 1.85 ± 0.69 (1.78) | 11.96 ± 27.33 (3.67) | 2.13 ± 0.60 (2.20) | 4.55 ± 1.39 (4.75) | 1.88 ± 0.74 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.788 | 98/100 | 0 | 84 | 1.91 ± 0.96 (1.70) | 15.60 ± 32.71 (4.70) | 2.17 ± 0.65 (2.35) | 4.67 ± 1.51 (5.29) | 1.97 ± 0.80 (2.15) |
| right | p | 0.801 | 100/100 | 0 | 90 | 2.18 ± 1.82 (1.80) | 12.08 ± 27.10 (4.60) | 2.16 ± 0.62 (2.27) | 4.66 ± 1.44 (5.07) | 1.95 ± 0.77 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.810 | 24/25 | 0 | 21 | 1.30 ± 0.27 (1.33) | 7.19 ± 8.73 (4.10) | 2.30 ± 0.44 (2.39) | 4.92 ± 1.12 (5.38) | 2.11 ± 0.66 (2.20) |
| forward/right | p | 0.796 | 25/25 | 0 | 22 | 2.14 ± 2.81 (1.44) | 8.99 ± 11.79 (4.16) | 2.13 ± 0.76 (2.32) | 4.64 ± 1.73 (5.35) | 1.97 ± 0.88 (2.19) |
| left/left | p | 0.818 | 24/25 | 0 | 22 | 1.70 ± 0.36 (1.69) | 6.47 ± 5.55 (4.70) | 2.28 ± 0.42 (2.38) | 4.98 ± 1.09 (5.49) | 2.11 ± 0.63 (2.28) |
| left/right | p | 0.812 | 25/25 | 0 | 21 | 1.80 ± 0.53 (1.88) | 15.52 ± 30.39 (4.60) | 2.04 ± 0.67 (2.24) | 4.36 ± 1.56 (4.47) | 1.78 ± 0.83 (1.85) |
| back/left | p | 0.740 | 25/25 | 0 | 20 | 2.58 ± 1.34 (2.62) | 29.59 ± 48.56 (7.02) | 2.11 ± 0.86 (2.37) | 4.54 ± 1.90 (5.54) | 1.95 ± 1.00 (2.25) |
| back/right | p | 0.747 | 25/25 | 0 | 23 | 3.09 ± 1.91 (2.62) | 18.30 ± 41.74 (6.35) | 2.21 ± 0.54 (2.28) | 4.83 ± 1.26 (5.12) | 2.03 ± 0.69 (2.01) |
| right/left | p | 0.784 | 25/25 | 0 | 21 | 2.02 ± 0.87 (2.02) | 18.43 ± 37.16 (3.46) | 2.00 ± 0.71 (2.20) | 4.27 ± 1.61 (4.55) | 1.74 ± 0.79 (1.94) |
| right/right | p | 0.847 | 25/25 | 0 | 24 | 1.68 ± 0.37 (1.66) | 5.49 ± 5.43 (4.06) | 2.26 ± 0.43 (2.20) | 4.82 ± 1.05 (4.96) | 2.02 ± 0.64 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.821 | 13.4 | 5.08 | 2.19 |
| p | normal | 0.767 | 14.2 | 4.26 | 1.73 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.715 | 0.10 | 2.49 ± 1.00 (2.34) | 3.84 | 1.47 |
| p | medium | 20 | 0.850 | 0.68 | 1.31 ± 0.17 (1.32) | 4.21 | 1.68 |
| p | strong | 126 | 0.820 | 0.68 | - | 5.09 | 2.21 |

## Notes

- p: score 0.794, 198/200 kicked, 0 fell; worst sector back (0.744).
