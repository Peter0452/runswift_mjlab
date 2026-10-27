# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u5_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.799** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 1.96 ± 1.46 (1.74) |
| Direction error [°] | 16.71 ± 35.34 (5.44) |
| Avg ball speed [m/s] | 2.24 ± 0.79 (2.39) |
| Peak ball speed [m/s] | 4.77 ± 1.78 (5.60) |
| Distance [m] | 2.23 ± 1.06 (2.52) |
| Path length [m] | 2.24 ± 1.06 (2.54) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.840 | 50/50 | 0 | 47 | 1.42 ± 1.30 (1.29) | 8.39 ± 15.27 (4.74) | 2.29 ± 0.66 (2.36) | 4.88 ± 1.54 (5.37) | 2.24 ± 0.93 (2.30) |
| left | p | 0.823 | 50/50 | 0 | 43 | 1.79 ± 0.70 (1.75) | 13.48 ± 27.37 (5.14) | 2.32 ± 0.69 (2.57) | 4.98 ± 1.60 (5.78) | 2.36 ± 1.00 (2.76) |
| back | p | 0.751 | 49/50 | 0 | 40 | 2.30 ± 0.62 (2.40) | 27.89 ± 50.80 (6.25) | 2.16 ± 0.97 (2.33) | 4.53 ± 2.12 (4.62) | 2.16 ± 1.21 (2.03) |
| right | p | 0.781 | 50/50 | 0 | 41 | 2.33 ± 2.31 (1.89) | 17.28 ± 35.44 (5.13) | 2.19 ± 0.80 (2.34) | 4.67 ± 1.78 (4.99) | 2.16 ± 1.06 (2.26) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.821 | 100/100 | 0 | 90 | 1.86 ± 0.92 (1.75) | 12.95 ± 30.47 (5.02) | 2.29 ± 0.74 (2.40) | 4.89 ± 1.69 (5.62) | 2.30 ± 1.02 (2.58) |
| right | p | 0.777 | 99/100 | 0 | 81 | 2.05 ± 1.85 (1.74) | 20.50 ± 39.29 (5.80) | 2.19 ± 0.83 (2.37) | 4.64 ± 1.86 (5.57) | 2.16 ± 1.09 (2.28) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.843 | 25/25 | 0 | 24 | 1.25 ± 0.28 (1.28) | 8.10 ± 14.14 (5.04) | 2.19 ± 0.75 (2.26) | 4.68 ± 1.70 (4.59) | 2.14 ± 0.99 (1.95) |
| forward/right | p | 0.838 | 25/25 | 0 | 23 | 1.60 ± 1.80 (1.30) | 8.68 ± 16.32 (4.27) | 2.38 ± 0.54 (2.41) | 5.09 ± 1.32 (5.60) | 2.34 ± 0.86 (2.35) |
| left/left | p | 0.817 | 25/25 | 0 | 21 | 1.77 ± 0.83 (1.74) | 10.39 ± 16.14 (5.74) | 2.34 ± 0.62 (2.57) | 5.04 ± 1.46 (5.93) | 2.38 ± 0.95 (2.85) |
| left/right | p | 0.828 | 25/25 | 0 | 22 | 1.81 ± 0.54 (1.76) | 16.58 ± 34.91 (4.57) | 2.30 ± 0.76 (2.57) | 4.91 ± 1.73 (5.75) | 2.34 ± 1.04 (2.65) |
| back/left | p | 0.797 | 25/25 | 0 | 22 | 2.43 ± 0.43 (2.46) | 16.82 ± 37.75 (5.46) | 2.26 ± 0.94 (2.53) | 4.79 ± 2.10 (5.72) | 2.33 ± 1.22 (2.69) |
| back/right | p | 0.705 | 24/25 | 0 | 18 | 2.16 ± 0.74 (2.32) | 39.43 ± 59.37 (7.06) | 2.05 ± 0.98 (2.29) | 4.26 ± 2.11 (4.41) | 1.98 ± 1.18 (1.93) |
| right/left | p | 0.826 | 25/25 | 0 | 23 | 2.01 ± 1.31 (1.92) | 16.49 ± 42.06 (3.46) | 2.37 ± 0.59 (2.37) | 5.06 ± 1.37 (5.52) | 2.35 ± 0.88 (2.56) |
| right/right | p | 0.736 | 25/25 | 0 | 18 | 2.65 ± 2.96 (1.88) | 18.07 ± 27.22 (7.11) | 2.02 ± 0.93 (2.14) | 4.29 ± 2.05 (4.18) | 1.97 ± 1.18 (1.75) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.845 | 14.3 | 5.41 | 2.66 |
| p | normal | 0.753 | 19.1 | 4.12 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.710 | 0.10 | 2.38 ± 1.06 (2.46) | 3.78 | 1.55 |
| p | medium | 18 | 0.811 | 0.59 | 1.09 ± 0.47 (1.28) | 3.50 | 1.37 |
| p | strong | 124 | 0.839 | 0.72 | - | 5.40 | 2.66 |

## Notes

- p: score 0.799, 199/200 kicked, 0 fell; worst sector back (0.751).
