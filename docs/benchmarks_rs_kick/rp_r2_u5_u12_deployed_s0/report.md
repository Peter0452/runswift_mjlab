# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r2_u5_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.798** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.93 ± 1.46 (1.74) |
| Direction error [°] | 18.91 ± 37.62 (5.48) |
| Avg ball speed [m/s] | 2.36 ± 0.86 (2.54) |
| Peak ball speed [m/s] | 4.97 ± 1.89 (5.73) |
| Distance [m] | 2.46 ± 1.24 (2.75) |
| Path length [m] | 2.47 ± 1.25 (2.77) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.775 | 49/50 | 0 | 41 | 1.84 ± 2.31 (1.32) | 9.69 ± 13.05 (5.46) | 2.23 ± 0.80 (2.28) | 4.65 ± 1.74 (4.48) | 2.17 ± 1.09 (1.97) |
| left | p | 0.843 | 50/50 | 0 | 43 | 1.88 ± 1.50 (1.79) | 14.30 ± 28.69 (4.58) | 2.49 ± 0.68 (2.72) | 5.33 ± 1.59 (6.07) | 2.68 ± 1.10 (3.09) |
| back | p | 0.773 | 50/50 | 0 | 40 | 2.32 ± 0.69 (2.38) | 33.19 ± 56.85 (6.98) | 2.42 ± 1.02 (2.91) | 5.08 ± 2.22 (6.49) | 2.63 ± 1.46 (3.49) |
| right | p | 0.799 | 49/50 | 0 | 40 | 1.66 ± 0.45 (1.74) | 18.25 ± 33.08 (4.49) | 2.28 ± 0.86 (2.51) | 4.82 ± 1.90 (5.51) | 2.36 ± 1.21 (2.76) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.820 | 100/100 | 0 | 86 | 1.81 ± 1.04 (1.69) | 17.62 ± 37.34 (5.49) | 2.43 ± 0.79 (2.55) | 5.14 ± 1.77 (5.80) | 2.56 ± 1.20 (2.91) |
| right | p | 0.775 | 98/100 | 0 | 78 | 2.05 ± 1.77 (1.76) | 20.23 ± 37.86 (5.32) | 2.28 ± 0.91 (2.53) | 4.81 ± 2.00 (5.66) | 2.36 ± 1.28 (2.57) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 22 | 1.61 ± 1.81 (1.28) | 8.06 ± 11.58 (4.84) | 2.31 ± 0.70 (2.38) | 4.87 ± 1.56 (4.53) | 2.30 ± 1.02 (2.01) |
| forward/right | p | 0.732 | 24/25 | 0 | 19 | 2.07 ± 2.72 (1.33) | 11.38 ± 14.22 (5.88) | 2.15 ± 0.89 (2.24) | 4.43 ± 1.87 (4.43) | 2.04 ± 1.15 (1.88) |
| left/left | p | 0.862 | 25/25 | 0 | 23 | 1.60 ± 0.38 (1.68) | 10.10 ± 15.62 (5.43) | 2.61 ± 0.59 (2.74) | 5.56 ± 1.41 (6.16) | 2.84 ± 1.02 (3.27) |
| left/right | p | 0.825 | 25/25 | 0 | 20 | 2.16 ± 2.06 (1.88) | 18.51 ± 36.97 (4.06) | 2.37 ± 0.75 (2.67) | 5.10 ± 1.73 (6.00) | 2.51 ± 1.16 (2.90) |
| back/left | p | 0.783 | 25/25 | 0 | 20 | 2.28 ± 0.64 (2.38) | 32.19 ± 57.64 (7.76) | 2.48 ± 0.97 (2.92) | 5.22 ± 2.11 (6.50) | 2.72 ± 1.43 (3.62) |
| back/right | p | 0.764 | 25/25 | 0 | 20 | 2.36 ± 0.72 (2.30) | 34.19 ± 56.04 (6.70) | 2.35 ± 1.07 (2.82) | 4.94 ± 2.32 (6.15) | 2.55 ± 1.48 (3.37) |
| right/left | p | 0.817 | 25/25 | 0 | 21 | 1.74 ± 0.47 (1.78) | 20.12 ± 38.85 (4.49) | 2.32 ± 0.83 (2.51) | 4.89 ± 1.84 (5.51) | 2.39 ± 1.18 (2.76) |
| right/right | p | 0.781 | 24/25 | 0 | 19 | 1.57 ± 0.41 (1.69) | 16.31 ± 25.60 (4.49) | 2.24 ± 0.90 (2.58) | 4.75 ± 1.95 (5.60) | 2.32 ± 1.25 (2.70) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.836 | 15.7 | 5.84 | 3.10 |
| p | normal | 0.759 | 22.1 | 4.10 | 1.82 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.712 | 0.15 | 2.27 ± 1.18 (2.20) | 3.52 | 1.42 |
| p | medium | 16 | 0.832 | 0.68 | 1.28 ± 0.22 (1.27) | 4.16 | 1.74 |
| p | strong | 126 | 0.833 | 0.77 | - | 5.74 | 3.03 |

## Notes

- p: score 0.798, 198/200 kicked, 0 fell; worst sector back (0.773).
