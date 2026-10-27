# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.88 ± 0.60 (1.84) |
| Direction error [°] | 5.20 ± 3.58 (4.46) |
| Avg ball speed [m/s] | 2.34 ± 0.42 (2.46) |
| Peak ball speed [m/s] | 5.09 ± 1.10 (5.64) |
| Distance [m] | 2.25 ± 0.74 (2.45) |
| Path length [m] | 2.26 ± 0.74 (2.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.871 | 50/50 | 0 | 50 | 1.30 ± 0.25 (1.25) | 4.66 ± 3.12 (3.85) | 2.24 ± 0.39 (2.35) | 4.96 ± 1.09 (5.45) | 2.10 ± 0.68 (2.28) |
| left | p | 0.864 | 50/50 | 0 | 49 | 1.78 ± 0.39 (1.80) | 4.92 ± 3.27 (4.27) | 2.30 ± 0.42 (2.45) | 5.02 ± 1.09 (5.66) | 2.19 ± 0.74 (2.47) |
| back | p | 0.802 | 50/50 | 0 | 49 | 2.65 ± 0.38 (2.58) | 5.83 ± 4.02 (5.29) | 2.50 ± 0.42 (2.59) | 5.34 ± 1.09 (5.87) | 2.48 ± 0.77 (2.70) |
| right | p | 0.871 | 50/50 | 0 | 50 | 1.79 ± 0.36 (1.84) | 5.38 ± 3.71 (5.30) | 2.32 ± 0.39 (2.43) | 5.05 ± 1.08 (5.63) | 2.22 ± 0.71 (2.44) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.856 | 100/100 | 0 | 98 | 1.88 ± 0.59 (1.84) | 5.47 ± 3.79 (4.65) | 2.39 ± 0.42 (2.50) | 5.22 ± 1.09 (5.69) | 2.35 ± 0.75 (2.55) |
| right | p | 0.847 | 100/100 | 0 | 100 | 1.89 ± 0.61 (1.83) | 4.92 ± 3.33 (4.29) | 2.28 ± 0.41 (2.40) | 4.97 ± 1.09 (5.43) | 2.15 ± 0.72 (2.21) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.864 | 25/25 | 0 | 25 | 1.31 ± 0.26 (1.28) | 4.84 ± 3.23 (4.18) | 2.26 ± 0.36 (2.37) | 4.97 ± 1.09 (5.57) | 2.13 ± 0.69 (2.40) |
| forward/right | p | 0.877 | 25/25 | 0 | 25 | 1.29 ± 0.23 (1.24) | 4.47 ± 2.99 (3.65) | 2.21 ± 0.40 (2.31) | 4.96 ± 1.10 (5.42) | 2.06 ± 0.67 (2.23) |
| left/left | p | 0.872 | 25/25 | 0 | 24 | 1.69 ± 0.37 (1.68) | 5.29 ± 3.83 (4.06) | 2.39 ± 0.42 (2.50) | 5.16 ± 1.08 (5.70) | 2.32 ± 0.76 (2.54) |
| left/right | p | 0.855 | 25/25 | 0 | 25 | 1.87 ± 0.38 (1.86) | 4.55 ± 2.55 (4.45) | 2.21 ± 0.41 (2.39) | 4.88 ± 1.08 (5.63) | 2.07 ± 0.71 (2.16) |
| back/left | p | 0.807 | 25/25 | 0 | 24 | 2.62 ± 0.38 (2.54) | 6.67 ± 4.32 (5.79) | 2.57 ± 0.42 (2.68) | 5.56 ± 1.02 (5.89) | 2.64 ± 0.75 (2.73) |
| back/right | p | 0.796 | 25/25 | 0 | 25 | 2.68 ± 0.38 (2.60) | 5.00 ± 3.50 (4.13) | 2.42 ± 0.41 (2.49) | 5.12 ± 1.10 (5.37) | 2.32 ± 0.76 (2.25) |
| right/left | p | 0.881 | 25/25 | 0 | 25 | 1.89 ± 0.33 (1.94) | 5.09 ± 3.42 (4.33) | 2.35 ± 0.39 (2.50) | 5.19 ± 1.06 (5.77) | 2.30 ± 0.69 (2.54) |
| right/right | p | 0.860 | 25/25 | 0 | 25 | 1.70 ± 0.36 (1.78) | 5.66 ± 3.96 (5.69) | 2.29 ± 0.39 (2.41) | 4.92 ± 1.07 (5.48) | 2.14 ± 0.72 (2.18) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 5.6 | 5.88 | 2.73 |
| p | normal | 0.818 | 4.8 | 4.30 | 1.77 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.773 | 0.16 | 2.27 ± 0.72 (2.10) | 3.73 | 1.38 |
| p | medium | 15 | 0.909 | 0.79 | 1.17 ± 0.17 (1.15) | 3.80 | 1.42 |
| p | strong | 125 | 0.882 | 0.79 | - | 5.90 | 2.76 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector back (0.802).
