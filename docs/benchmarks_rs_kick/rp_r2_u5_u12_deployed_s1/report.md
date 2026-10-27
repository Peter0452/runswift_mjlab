# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r2_u5_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.797** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 174 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.96 ± 1.37 (1.66) |
| Direction error [°] | 12.49 ± 25.69 (5.52) |
| Avg ball speed [m/s] | 2.19 ± 0.61 (2.33) |
| Peak ball speed [m/s] | 4.81 ± 1.46 (5.37) |
| Distance [m] | 2.07 ± 0.82 (2.22) |
| Path length [m] | 2.08 ± 0.82 (2.23) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.814 | 50/50 | 0 | 44 | 1.71 ± 1.88 (1.32) | 8.39 ± 11.81 (4.21) | 2.15 ± 0.63 (2.33) | 4.76 ± 1.50 (5.33) | 2.03 ± 0.83 (2.18) |
| left | p | 0.822 | 49/50 | 0 | 44 | 1.70 ± 0.43 (1.68) | 11.18 ± 23.07 (5.24) | 2.18 ± 0.59 (2.33) | 4.80 ± 1.44 (5.37) | 2.06 ± 0.81 (2.26) |
| back | p | 0.751 | 49/50 | 0 | 42 | 2.72 ± 1.68 (2.40) | 20.40 ± 40.01 (6.38) | 2.25 ± 0.68 (2.39) | 4.93 ± 1.57 (5.53) | 2.18 ± 0.89 (2.54) |
| right | p | 0.802 | 49/50 | 0 | 44 | 1.71 ± 0.38 (1.78) | 10.09 ± 17.06 (5.99) | 2.20 ± 0.51 (2.28) | 4.76 ± 1.29 (5.10) | 2.02 ± 0.74 (2.03) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.793 | 98/100 | 0 | 86 | 1.87 ± 1.06 (1.64) | 13.82 ± 28.49 (5.24) | 2.19 ± 0.60 (2.34) | 4.81 ± 1.45 (5.45) | 2.06 ± 0.82 (2.28) |
| right | p | 0.801 | 99/100 | 0 | 88 | 2.05 ± 1.61 (1.76) | 11.18 ± 22.50 (5.57) | 2.20 ± 0.61 (2.32) | 4.81 ± 1.46 (5.27) | 2.08 ± 0.82 (2.20) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.818 | 25/25 | 0 | 21 | 1.42 ± 1.01 (1.26) | 8.80 ± 13.04 (3.64) | 2.09 ± 0.60 (2.35) | 4.63 ± 1.45 (5.18) | 1.93 ± 0.79 (2.06) |
| forward/right | p | 0.809 | 25/25 | 0 | 23 | 2.00 ± 2.43 (1.40) | 7.98 ± 10.43 (4.96) | 2.21 ± 0.65 (2.32) | 4.88 ± 1.54 (5.38) | 2.12 ± 0.85 (2.20) |
| left/left | p | 0.832 | 24/25 | 0 | 23 | 1.67 ± 0.36 (1.61) | 5.93 ± 6.17 (5.19) | 2.34 ± 0.39 (2.35) | 5.19 ± 1.05 (5.56) | 2.27 ± 0.65 (2.40) |
| left/right | p | 0.812 | 25/25 | 0 | 21 | 1.73 ± 0.48 (1.80) | 16.21 ± 30.89 (5.56) | 2.03 ± 0.71 (2.25) | 4.42 ± 1.64 (4.47) | 1.86 ± 0.89 (1.79) |
| back/left | p | 0.750 | 25/25 | 0 | 21 | 2.57 ± 1.54 (2.48) | 27.01 ± 46.88 (6.60) | 2.19 ± 0.74 (2.46) | 4.80 ± 1.69 (5.59) | 2.11 ± 0.96 (2.56) |
| back/right | p | 0.752 | 24/25 | 0 | 21 | 2.87 ± 1.79 (2.38) | 13.51 ± 29.76 (5.88) | 2.31 ± 0.60 (2.36) | 5.07 ± 1.42 (5.52) | 2.26 ± 0.80 (2.52) |
| right/left | p | 0.772 | 24/25 | 0 | 21 | 1.80 ± 0.40 (1.93) | 13.20 ± 23.22 (4.92) | 2.13 ± 0.58 (2.29) | 4.62 ± 1.45 (4.83) | 1.93 ± 0.80 (1.93) |
| right/right | p | 0.831 | 25/25 | 0 | 23 | 1.62 ± 0.33 (1.56) | 7.10 ± 5.88 (6.13) | 2.26 ± 0.42 (2.28) | 4.90 ± 1.10 (5.10) | 2.10 ± 0.67 (2.13) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.824 | 12.2 | 5.32 | 2.37 |
| p | normal | 0.770 | 12.7 | 4.31 | 1.78 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.709 | 0.08 | 2.52 ± 1.02 (2.31) | 3.88 | 1.51 |
| p | medium | 20 | 0.873 | 0.71 | 1.29 ± 0.16 (1.28) | 4.14 | 1.63 |
| p | strong | 126 | 0.823 | 0.71 | - | 5.32 | 2.38 |

## Notes

- p: score 0.797, 197/200 kicked, 0 fell; worst sector back (0.751).
