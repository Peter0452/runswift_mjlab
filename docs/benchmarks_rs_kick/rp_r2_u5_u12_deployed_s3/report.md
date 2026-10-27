# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r2_u5_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.19 ± 1.99 (1.76) |
| Direction error [°] | 14.87 ± 30.77 (4.79) |
| Avg ball speed [m/s] | 2.13 ± 0.65 (2.30) |
| Peak ball speed [m/s] | 4.62 ± 1.54 (5.18) |
| Distance [m] | 1.94 ± 0.83 (1.99) |
| Path length [m] | 1.95 ± 0.83 (2.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.835 | 50/50 | 0 | 45 | 1.48 ± 1.38 (1.30) | 8.31 ± 15.29 (4.02) | 2.12 ± 0.61 (2.30) | 4.66 ± 1.50 (5.14) | 1.91 ± 0.83 (1.93) |
| left | p | 0.819 | 50/50 | 0 | 45 | 2.01 ± 1.70 (1.76) | 11.81 ± 25.86 (4.34) | 2.18 ± 0.56 (2.34) | 4.81 ± 1.36 (5.32) | 2.02 ± 0.76 (2.22) |
| back | p | 0.726 | 50/50 | 0 | 43 | 3.14 ± 2.42 (2.55) | 19.15 ± 35.93 (6.79) | 2.20 ± 0.64 (2.33) | 4.69 ± 1.47 (4.90) | 2.02 ± 0.82 (2.07) |
| right | p | 0.758 | 49/50 | 0 | 40 | 2.13 ± 1.94 (1.82) | 20.31 ± 38.79 (4.79) | 2.00 ± 0.77 (2.23) | 4.32 ± 1.76 (4.70) | 1.79 ± 0.89 (1.86) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 99/100 | 0 | 89 | 1.86 ± 0.87 (1.74) | 12.65 ± 28.84 (4.71) | 2.17 ± 0.59 (2.30) | 4.72 ± 1.43 (5.22) | 1.98 ± 0.80 (2.06) |
| right | p | 0.761 | 100/100 | 0 | 84 | 2.52 ± 2.63 (1.80) | 17.07 ± 32.42 (5.56) | 2.08 ± 0.70 (2.29) | 4.53 ± 1.64 (5.07) | 1.90 ± 0.86 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 22 | 1.34 ± 0.52 (1.30) | 8.49 ± 15.11 (4.66) | 2.03 ± 0.68 (2.24) | 4.47 ± 1.66 (4.37) | 1.83 ± 0.91 (1.84) |
| forward/right | p | 0.837 | 25/25 | 0 | 23 | 1.62 ± 1.87 (1.30) | 8.14 ± 15.47 (3.99) | 2.20 ± 0.53 (2.32) | 4.84 ± 1.29 (5.40) | 2.00 ± 0.72 (2.04) |
| left/left | p | 0.814 | 25/25 | 0 | 22 | 1.86 ± 1.29 (1.64) | 9.87 ± 14.99 (5.43) | 2.16 ± 0.63 (2.36) | 4.75 ± 1.50 (5.29) | 2.01 ± 0.84 (2.22) |
| left/right | p | 0.824 | 25/25 | 0 | 23 | 2.16 ± 2.02 (1.84) | 13.76 ± 33.24 (4.27) | 2.20 ± 0.48 (2.34) | 4.88 ± 1.20 (5.35) | 2.03 ± 0.67 (2.22) |
| back/left | p | 0.802 | 25/25 | 0 | 24 | 2.49 ± 0.50 (2.46) | 11.23 ± 25.73 (5.02) | 2.36 ± 0.37 (2.38) | 5.09 ± 0.96 (5.37) | 2.21 ± 0.59 (2.28) |
| back/right | p | 0.650 | 25/25 | 0 | 19 | 3.78 ± 3.26 (2.62) | 27.07 ± 42.36 (8.04) | 2.03 ± 0.79 (2.25) | 4.30 ± 1.76 (4.39) | 1.84 ± 0.96 (1.83) |
| right/left | p | 0.784 | 24/25 | 0 | 21 | 1.73 ± 0.40 (1.77) | 21.35 ± 46.54 (4.18) | 2.11 ± 0.60 (2.25) | 4.56 ± 1.42 (4.90) | 1.87 ± 0.78 (1.90) |
| right/right | p | 0.731 | 25/25 | 0 | 19 | 2.52 ± 2.63 (1.86) | 19.31 ± 29.47 (8.31) | 1.90 ± 0.89 (2.20) | 4.10 ± 2.01 (4.47) | 1.72 ± 0.98 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 12.6 | 5.14 | 2.23 |
| p | normal | 0.746 | 17.1 | 4.11 | 1.65 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.713 | 0.09 | 2.48 ± 1.00 (2.42) | 3.89 | 1.53 |
| p | medium | 18 | 0.815 | 0.66 | 1.17 ± 0.34 (1.25) | 3.77 | 1.43 |
| p | strong | 124 | 0.813 | 0.68 | - | 5.09 | 2.20 |

## Notes

- p: score 0.784, 199/200 kicked, 0 fell; worst sector back (0.726).
