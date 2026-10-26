# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s3_ctl7_n7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.92 ± 1.39 (1.70) |
| Direction error [°] | 17.95 ± 36.60 (4.77) |
| Avg ball speed [m/s] | 2.06 ± 0.62 (2.20) |
| Peak ball speed [m/s] | 4.49 ± 1.46 (5.05) |
| Distance [m] | 1.83 ± 0.79 (1.87) |
| Path length [m] | 1.84 ± 0.79 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.800 | 49/50 | 0 | 43 | 1.60 ± 1.64 (1.28) | 7.31 ± 11.30 (3.35) | 1.96 ± 0.66 (2.13) | 4.21 ± 1.54 (4.23) | 1.65 ± 0.78 (1.69) |
| left | p | 0.800 | 49/50 | 0 | 41 | 1.84 ± 1.53 (1.72) | 19.66 ± 36.27 (5.06) | 2.13 ± 0.56 (2.24) | 4.66 ± 1.36 (5.05) | 1.92 ± 0.77 (1.93) |
| back | p | 0.745 | 49/50 | 0 | 42 | 2.59 ± 1.33 (2.60) | 26.20 ± 51.50 (5.97) | 2.10 ± 0.65 (2.30) | 4.60 ± 1.50 (5.25) | 1.92 ± 0.79 (2.13) |
| right | p | 0.775 | 48/50 | 0 | 40 | 1.63 ± 0.46 (1.72) | 18.64 ± 32.77 (4.63) | 2.04 ± 0.59 (2.17) | 4.50 ± 1.41 (5.02) | 1.81 ± 0.78 (1.87) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 100/100 | 0 | 86 | 1.88 ± 1.29 (1.68) | 18.03 ± 37.67 (4.77) | 2.09 ± 0.60 (2.22) | 4.56 ± 1.41 (5.10) | 1.86 ± 0.77 (1.98) |
| right | p | 0.753 | 95/100 | 0 | 80 | 1.95 ± 1.48 (1.72) | 17.86 ± 35.45 (5.06) | 2.03 ± 0.64 (2.18) | 4.42 ± 1.51 (5.00) | 1.79 ± 0.80 (1.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 23 | 1.54 ± 1.47 (1.26) | 6.97 ± 12.55 (3.35) | 2.06 ± 0.63 (2.25) | 4.45 ± 1.50 (4.30) | 1.79 ± 0.77 (1.85) |
| forward/right | p | 0.770 | 24/25 | 0 | 20 | 1.65 ± 1.80 (1.31) | 7.66 ± 9.81 (3.31) | 1.85 ± 0.66 (2.05) | 3.97 ± 1.55 (4.09) | 1.51 ± 0.76 (1.61) |
| left/left | p | 0.843 | 25/25 | 0 | 22 | 1.56 ± 0.40 (1.68) | 13.05 ± 23.09 (5.17) | 2.22 ± 0.45 (2.32) | 4.88 ± 1.13 (5.20) | 2.04 ± 0.65 (2.21) |
| left/right | p | 0.757 | 24/25 | 0 | 19 | 2.13 ± 2.11 (1.80) | 26.54 ± 45.14 (4.53) | 2.04 ± 0.65 (2.21) | 4.43 ± 1.54 (4.99) | 1.80 ± 0.86 (1.87) |
| back/left | p | 0.753 | 25/25 | 0 | 21 | 2.72 ± 1.77 (2.46) | 29.35 ± 55.43 (5.37) | 2.12 ± 0.61 (2.29) | 4.61 ± 1.41 (5.25) | 1.92 ± 0.80 (2.13) |
| back/right | p | 0.736 | 24/25 | 0 | 21 | 2.45 ± 0.55 (2.63) | 22.91 ± 46.84 (6.04) | 2.09 ± 0.68 (2.36) | 4.59 ± 1.59 (5.36) | 1.93 ± 0.77 (2.17) |
| right/left | p | 0.802 | 25/25 | 0 | 20 | 1.71 ± 0.48 (1.74) | 22.74 ± 40.20 (3.65) | 1.96 ± 0.64 (2.15) | 4.31 ± 1.51 (4.52) | 1.70 ± 0.80 (1.82) |
| right/right | p | 0.747 | 23/25 | 0 | 20 | 1.55 ± 0.42 (1.50) | 14.18 ± 21.13 (7.14) | 2.13 ± 0.51 (2.18) | 4.69 ± 1.25 (5.05) | 1.94 ± 0.73 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.802 | 15.8 | 5.08 | 2.14 |
| p | normal | 0.757 | 20.0 | 3.92 | 1.52 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.722 | 0.18 | 2.28 ± 1.02 (2.19) | 3.59 | 1.34 |
| p | medium | 16 | 0.828 | 0.69 | 1.27 ± 0.22 (1.30) | 4.12 | 1.66 |
| p | strong | 126 | 0.800 | 0.66 | - | 4.96 | 2.08 |

## Notes

- p: score 0.780, 195/200 kicked, 0 fell; worst sector back (0.745).
