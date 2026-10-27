# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r6_u5_75_u0_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.785** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 22 |
| Time to kick [s] | 1.96 ± 1.46 (1.77) |
| Direction error [°] | 18.94 ± 37.53 (5.32) |
| Avg ball speed [m/s] | 2.28 ± 0.84 (2.46) |
| Peak ball speed [m/s] | 4.80 ± 1.85 (5.45) |
| Distance [m] | 2.29 ± 1.12 (2.61) |
| Path length [m] | 2.29 ± 1.13 (2.62) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.789 | 48/50 | 0 | 40 | 1.26 ± 0.28 (1.26) | 11.59 ± 19.55 (4.36) | 2.26 ± 0.81 (2.37) | 4.74 ± 1.79 (4.70) | 2.20 ± 1.07 (2.07) |
| left | p | 0.803 | 49/50 | 0 | 42 | 2.10 ± 1.70 (1.90) | 13.33 ± 25.03 (4.20) | 2.32 ± 0.78 (2.55) | 4.93 ± 1.73 (5.65) | 2.36 ± 1.05 (2.81) |
| back | p | 0.735 | 49/50 | 0 | 41 | 2.73 ± 1.83 (2.50) | 29.59 ± 52.71 (7.28) | 2.37 ± 0.90 (2.67) | 4.98 ± 1.96 (5.91) | 2.46 ± 1.23 (2.93) |
| right | p | 0.812 | 50/50 | 0 | 41 | 1.76 ± 1.01 (1.78) | 21.05 ± 40.25 (3.97) | 2.17 ± 0.86 (2.39) | 4.57 ± 1.89 (4.87) | 2.13 ± 1.11 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 99/100 | 0 | 82 | 1.96 ± 1.45 (1.72) | 20.51 ± 39.32 (4.93) | 2.29 ± 0.90 (2.59) | 4.85 ± 1.97 (5.81) | 2.34 ± 1.19 (2.83) |
| right | p | 0.773 | 97/100 | 0 | 82 | 1.97 ± 1.47 (1.80) | 17.34 ± 35.55 (5.42) | 2.27 ± 0.78 (2.40) | 4.76 ± 1.72 (4.64) | 2.23 ± 1.05 (2.06) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.804 | 25/25 | 0 | 21 | 1.29 ± 0.29 (1.36) | 14.45 ± 24.11 (4.44) | 2.16 ± 0.93 (2.31) | 4.50 ± 2.03 (4.35) | 2.11 ± 1.19 (1.87) |
| forward/right | p | 0.775 | 23/25 | 0 | 19 | 1.23 ± 0.27 (1.18) | 8.47 ± 12.16 (3.95) | 2.36 ± 0.64 (2.46) | 5.00 ± 1.44 (5.43) | 2.31 ± 0.91 (2.71) |
| left/left | p | 0.820 | 25/25 | 0 | 21 | 2.31 ± 2.32 (1.70) | 11.57 ± 21.66 (4.92) | 2.38 ± 0.81 (2.60) | 5.08 ± 1.77 (5.80) | 2.47 ± 1.08 (2.85) |
| left/right | p | 0.785 | 24/25 | 0 | 21 | 1.88 ± 0.46 (1.92) | 15.18 ± 27.99 (4.03) | 2.25 ± 0.74 (2.36) | 4.78 ± 1.68 (4.91) | 2.24 ± 1.00 (2.20) |
| back/left | p | 0.749 | 24/25 | 0 | 20 | 2.27 ± 0.66 (2.52) | 27.36 ± 47.33 (6.97) | 2.43 ± 0.89 (2.77) | 5.17 ± 1.93 (6.11) | 2.59 ± 1.23 (3.20) |
| back/right | p | 0.721 | 25/25 | 0 | 21 | 3.16 ± 2.41 (2.48) | 31.73 ± 57.32 (7.28) | 2.32 ± 0.91 (2.40) | 4.80 ± 1.96 (4.64) | 2.34 ± 1.23 (2.06) |
| right/left | p | 0.810 | 25/25 | 0 | 20 | 1.97 ± 1.33 (1.78) | 28.92 ± 51.86 (3.82) | 2.20 ± 0.94 (2.58) | 4.66 ± 2.05 (5.86) | 2.21 ± 1.18 (2.83) |
| right/right | p | 0.813 | 25/25 | 0 | 21 | 1.55 ± 0.42 (1.70) | 13.18 ± 20.66 (5.42) | 2.14 ± 0.78 (2.27) | 4.48 ± 1.71 (4.37) | 2.04 ± 1.02 (1.94) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.818 | 18.8 | 5.42 | 2.71 |
| p | normal | 0.752 | 19.1 | 4.19 | 1.87 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.700 | 0.17 | 2.22 ± 1.01 (2.14) | 3.72 | 1.52 |
| p | medium | 15 | 0.831 | 0.62 | 1.18 ± 0.39 (1.24) | 3.80 | 1.54 |
| p | strong | 125 | 0.820 | 0.73 | - | 5.44 | 2.74 |

## Notes

- p: score 0.785, 196/200 kicked, 0 fell; worst sector back (0.735).
