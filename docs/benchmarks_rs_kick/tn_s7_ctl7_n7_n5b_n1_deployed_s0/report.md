# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s7_ctl7_n7_n5b_n1.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.790** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.99 ± 1.64 (1.67) |
| Direction error [°] | 19.07 ± 37.14 (6.46) |
| Avg ball speed [m/s] | 2.33 ± 0.81 (2.52) |
| Peak ball speed [m/s] | 4.95 ± 1.77 (5.64) |
| Distance [m] | 2.39 ± 1.14 (2.65) |
| Path length [m] | 2.40 ± 1.14 (2.67) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.788 | 50/50 | 0 | 42 | 1.95 ± 2.46 (1.30) | 9.10 ± 11.33 (5.58) | 2.23 ± 0.74 (2.36) | 4.69 ± 1.64 (4.52) | 2.17 ± 1.01 (1.97) |
| left | p | 0.821 | 49/50 | 0 | 42 | 1.83 ± 1.41 (1.70) | 15.14 ± 29.59 (5.75) | 2.43 ± 0.69 (2.62) | 5.21 ± 1.57 (5.95) | 2.53 ± 1.06 (2.97) |
| back | p | 0.738 | 49/50 | 0 | 37 | 2.34 ± 0.73 (2.36) | 35.31 ± 55.94 (10.22) | 2.34 ± 1.00 (2.87) | 4.94 ± 2.16 (6.26) | 2.50 ± 1.36 (3.26) |
| right | p | 0.812 | 50/50 | 0 | 42 | 1.83 ± 1.38 (1.66) | 16.99 ± 32.14 (5.13) | 2.34 ± 0.76 (2.47) | 4.94 ± 1.63 (5.53) | 2.35 ± 1.05 (2.59) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 99/100 | 0 | 84 | 1.78 ± 0.92 (1.66) | 18.53 ± 37.73 (6.32) | 2.37 ± 0.78 (2.60) | 5.03 ± 1.74 (5.78) | 2.44 ± 1.12 (2.90) |
| right | p | 0.772 | 99/100 | 0 | 79 | 2.20 ± 2.10 (1.68) | 19.62 ± 36.54 (6.73) | 2.30 ± 0.83 (2.46) | 4.86 ± 1.81 (5.52) | 2.33 ± 1.16 (2.56) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 23 | 1.54 ± 1.51 (1.28) | 7.08 ± 11.13 (4.27) | 2.28 ± 0.75 (2.35) | 4.80 ± 1.66 (4.49) | 2.25 ± 1.04 (2.00) |
| forward/right | p | 0.745 | 25/25 | 0 | 19 | 2.36 ± 3.08 (1.32) | 11.13 ± 11.17 (7.27) | 2.18 ± 0.72 (2.37) | 4.57 ± 1.62 (4.55) | 2.08 ± 0.98 (1.94) |
| left/left | p | 0.864 | 25/25 | 0 | 23 | 1.57 ± 0.36 (1.64) | 9.71 ± 15.04 (6.40) | 2.55 ± 0.56 (2.62) | 5.47 ± 1.33 (6.23) | 2.72 ± 0.94 (3.20) |
| left/right | p | 0.778 | 24/25 | 0 | 19 | 2.11 ± 1.95 (1.85) | 20.80 ± 38.60 (5.35) | 2.31 ± 0.79 (2.55) | 4.94 ± 1.74 (5.84) | 2.34 ± 1.15 (2.65) |
| back/left | p | 0.725 | 24/25 | 0 | 18 | 2.27 ± 0.65 (2.38) | 36.68 ± 57.61 (10.44) | 2.36 ± 0.94 (2.89) | 5.03 ± 2.05 (6.30) | 2.54 ± 1.33 (3.32) |
| back/right | p | 0.751 | 25/25 | 0 | 19 | 2.40 ± 0.80 (2.36) | 33.99 ± 54.25 (9.09) | 2.33 ± 1.05 (2.84) | 4.87 ± 2.25 (6.19) | 2.46 ± 1.39 (3.19) |
| right/left | p | 0.809 | 25/25 | 0 | 20 | 1.75 ± 0.47 (1.74) | 21.38 ± 39.58 (5.51) | 2.29 ± 0.81 (2.48) | 4.83 ± 1.76 (5.58) | 2.27 ± 1.07 (2.51) |
| right/right | p | 0.815 | 25/25 | 0 | 22 | 1.92 ± 1.88 (1.54) | 12.61 ± 21.46 (3.67) | 2.39 ± 0.69 (2.46) | 5.06 ± 1.47 (5.48) | 2.43 ± 1.04 (2.68) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.817 | 16.0 | 5.84 | 3.00 |
| p | normal | 0.763 | 22.1 | 4.07 | 1.78 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.14 | 2.32 ± 1.19 (2.39) | 3.54 | 1.41 |
| p | medium | 16 | 0.835 | 0.70 | 1.24 ± 0.25 (1.30) | 4.01 | 1.65 |
| p | strong | 126 | 0.818 | 0.76 | - | 5.72 | 2.94 |

## Notes

- p: score 0.790, 198/200 kicked, 0 fell; worst sector back (0.738).
