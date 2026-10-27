# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r5_u5_u0_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.812** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 176 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.88 ± 1.09 (1.68) |
| Direction error [°] | 12.39 ± 25.72 (5.55) |
| Avg ball speed [m/s] | 2.40 ± 0.79 (2.57) |
| Peak ball speed [m/s] | 5.06 ± 1.77 (5.75) |
| Distance [m] | 2.47 ± 1.15 (2.83) |
| Path length [m] | 2.48 ± 1.15 (2.83) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.833 | 50/50 | 0 | 45 | 1.43 ± 1.22 (1.31) | 7.57 ± 9.99 (4.37) | 2.29 ± 0.89 (2.45) | 4.84 ± 1.96 (5.05) | 2.32 ± 1.21 (2.24) |
| left | p | 0.836 | 49/50 | 0 | 45 | 1.71 ± 0.45 (1.66) | 10.38 ± 22.10 (4.21) | 2.42 ± 0.62 (2.53) | 5.15 ± 1.47 (5.60) | 2.48 ± 1.01 (2.60) |
| back | p | 0.764 | 49/50 | 0 | 42 | 2.60 ± 1.42 (2.50) | 20.59 ± 40.54 (7.03) | 2.54 ± 0.86 (2.91) | 5.34 ± 1.89 (6.26) | 2.75 ± 1.23 (3.38) |
| right | p | 0.814 | 50/50 | 0 | 44 | 1.78 ± 0.52 (1.80) | 11.13 ± 18.35 (6.18) | 2.35 ± 0.75 (2.38) | 4.91 ± 1.68 (5.42) | 2.35 ± 1.07 (2.56) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 99/100 | 0 | 87 | 1.79 ± 0.64 (1.64) | 13.91 ± 28.54 (5.69) | 2.39 ± 0.83 (2.64) | 5.06 ± 1.84 (5.98) | 2.48 ± 1.17 (2.94) |
| right | p | 0.812 | 99/100 | 0 | 89 | 1.97 ± 1.39 (1.70) | 10.87 ± 22.46 (5.44) | 2.41 ± 0.76 (2.54) | 5.06 ± 1.70 (5.60) | 2.46 ± 1.13 (2.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.848 | 25/25 | 0 | 23 | 1.27 ± 0.29 (1.28) | 7.03 ± 9.02 (4.23) | 2.36 ± 0.86 (2.66) | 4.98 ± 1.88 (6.16) | 2.40 ± 1.20 (2.93) |
| forward/right | p | 0.819 | 25/25 | 0 | 22 | 1.59 ± 1.68 (1.32) | 8.12 ± 10.86 (4.52) | 2.21 ± 0.92 (2.22) | 4.70 ± 2.02 (4.43) | 2.23 ± 1.23 (1.90) |
| left/left | p | 0.840 | 24/25 | 0 | 23 | 1.67 ± 0.37 (1.60) | 5.81 ± 6.32 (3.92) | 2.54 ± 0.50 (2.68) | 5.43 ± 1.28 (6.10) | 2.67 ± 0.91 (3.05) |
| left/right | p | 0.832 | 25/25 | 0 | 22 | 1.75 ± 0.51 (1.80) | 14.76 ± 29.65 (5.08) | 2.31 ± 0.70 (2.38) | 4.88 ± 1.58 (4.57) | 2.30 ± 1.08 (2.02) |
| back/left | p | 0.770 | 25/25 | 0 | 20 | 2.30 ± 0.67 (2.42) | 27.57 ± 46.92 (8.71) | 2.44 ± 0.94 (2.91) | 5.14 ± 2.02 (6.06) | 2.61 ± 1.30 (3.05) |
| back/right | p | 0.758 | 24/25 | 0 | 22 | 2.91 ± 1.86 (2.57) | 13.32 ± 30.96 (6.47) | 2.65 ± 0.77 (2.94) | 5.55 ± 1.72 (6.33) | 2.89 ± 1.15 (3.43) |
| right/left | p | 0.791 | 25/25 | 0 | 21 | 1.92 ± 0.61 (1.92) | 14.89 ± 24.60 (6.60) | 2.25 ± 0.91 (2.37) | 4.69 ± 1.98 (5.38) | 2.25 ± 1.18 (2.66) |
| right/right | p | 0.838 | 25/25 | 0 | 23 | 1.65 ± 0.37 (1.56) | 7.38 ± 6.33 (5.68) | 2.45 ± 0.51 (2.39) | 5.12 ± 1.27 (5.46) | 2.45 ± 0.94 (2.48) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.841 | 12.1 | 5.77 | 3.00 |
| p | normal | 0.783 | 12.7 | 4.36 | 1.96 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.726 | 0.11 | 2.46 ± 1.14 (2.33) | 3.74 | 1.50 |
| p | medium | 20 | 0.868 | 0.67 | 1.30 ± 0.19 (1.31) | 4.17 | 1.74 |
| p | strong | 126 | 0.840 | 0.77 | - | 5.78 | 3.01 |

## Notes

- p: score 0.812, 198/200 kicked, 0 fell; worst sector back (0.764).
