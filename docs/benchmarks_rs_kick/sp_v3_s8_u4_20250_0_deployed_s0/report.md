# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v3_s8_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.773** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.93 ± 1.30 (1.74) |
| Direction error [°] | 20.12 ± 40.09 (5.49) |
| Avg ball speed [m/s] | 2.04 ± 0.67 (2.18) |
| Peak ball speed [m/s] | 4.45 ± 1.61 (5.03) |
| Distance [m] | 1.82 ± 0.89 (1.88) |
| Path length [m] | 1.83 ± 0.89 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.770 | 47/50 | 0 | 40 | 1.49 ± 1.40 (1.32) | 8.41 ± 11.51 (4.65) | 1.99 ± 0.66 (1.95) | 4.31 ± 1.61 (3.90) | 1.72 ± 0.89 (1.56) |
| left | p | 0.793 | 49/50 | 0 | 40 | 1.85 ± 1.31 (1.78) | 22.52 ± 39.40 (5.50) | 2.07 ± 0.64 (2.34) | 4.54 ± 1.55 (5.33) | 1.87 ± 0.88 (2.09) |
| back | p | 0.734 | 49/50 | 0 | 40 | 2.62 ± 1.46 (2.60) | 32.61 ± 57.39 (6.74) | 2.04 ± 0.75 (2.31) | 4.46 ± 1.77 (5.45) | 1.87 ± 0.96 (2.17) |
| right | p | 0.794 | 48/50 | 0 | 41 | 1.73 ± 0.48 (1.77) | 16.38 ± 32.75 (3.65) | 2.05 ± 0.61 (2.25) | 4.50 ± 1.49 (5.18) | 1.80 ± 0.81 (1.87) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.806 | 99/100 | 0 | 85 | 1.88 ± 1.17 (1.78) | 18.77 ± 39.89 (5.38) | 2.10 ± 0.62 (2.31) | 4.60 ± 1.50 (5.29) | 1.89 ± 0.84 (2.08) |
| right | p | 0.739 | 94/100 | 0 | 76 | 1.98 ± 1.43 (1.74) | 21.54 ± 40.26 (5.65) | 1.97 ± 0.71 (2.09) | 4.30 ± 1.71 (4.22) | 1.74 ± 0.93 (1.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 24/25 | 0 | 22 | 1.29 ± 0.28 (1.29) | 6.21 ± 9.56 (2.82) | 2.16 ± 0.56 (2.23) | 4.71 ± 1.38 (4.72) | 1.94 ± 0.83 (1.83) |
| forward/right | p | 0.721 | 23/25 | 0 | 18 | 1.70 ± 1.97 (1.34) | 10.70 ± 12.85 (5.63) | 1.81 ± 0.72 (1.87) | 3.89 ± 1.71 (3.80) | 1.50 ± 0.90 (1.39) |
| left/left | p | 0.853 | 25/25 | 0 | 22 | 1.61 ± 0.42 (1.66) | 12.25 ± 22.75 (5.18) | 2.17 ± 0.52 (2.34) | 4.75 ± 1.24 (5.33) | 1.98 ± 0.73 (2.09) |
| left/right | p | 0.732 | 24/25 | 0 | 18 | 2.10 ± 1.78 (1.94) | 33.22 ± 49.06 (7.79) | 1.96 ± 0.73 (2.23) | 4.32 ± 1.79 (4.82) | 1.76 ± 1.00 (1.94) |
| back/left | p | 0.735 | 25/25 | 0 | 20 | 2.78 ± 1.92 (2.60) | 36.12 ± 60.07 (7.44) | 2.08 ± 0.71 (2.37) | 4.58 ± 1.69 (5.62) | 1.93 ± 0.97 (2.22) |
| back/right | p | 0.733 | 24/25 | 0 | 20 | 2.46 ± 0.68 (2.59) | 28.96 ± 54.23 (5.81) | 2.00 ± 0.79 (2.28) | 4.35 ± 1.83 (5.23) | 1.82 ± 0.96 (2.13) |
| right/left | p | 0.817 | 25/25 | 0 | 21 | 1.82 ± 0.49 (1.84) | 20.01 ± 39.89 (3.55) | 2.00 ± 0.65 (2.30) | 4.35 ± 1.58 (5.16) | 1.72 ± 0.81 (1.86) |
| right/right | p | 0.771 | 23/25 | 0 | 20 | 1.63 ± 0.44 (1.74) | 12.45 ± 21.89 (4.15) | 2.11 ± 0.56 (2.20) | 4.65 ± 1.37 (5.20) | 1.89 ± 0.79 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.795 | 17.6 | 5.23 | 2.25 |
| p | normal | 0.750 | 22.6 | 3.70 | 1.40 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.709 | 0.22 | 2.10 ± 0.96 (2.02) | 3.28 | 1.15 |
| p | medium | 16 | 0.820 | 0.73 | 1.11 ± 0.31 (1.19) | 3.59 | 1.34 |
| p | strong | 126 | 0.796 | 0.68 | - | 5.11 | 2.19 |

## Notes

- p: score 0.773, 193/200 kicked, 0 fell; worst sector back (0.734).
