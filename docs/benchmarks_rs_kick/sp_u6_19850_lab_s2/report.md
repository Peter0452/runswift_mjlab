# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.58 ± 0.57 (1.54) |
| Direction error [°] | 6.73 ± 18.52 (3.65) |
| Avg ball speed [m/s] | 2.01 ± 0.42 (2.06) |
| Peak ball speed [m/s] | 4.60 ± 0.96 (4.88) |
| Distance [m] | 1.99 ± 0.71 (2.05) |
| Path length [m] | 2.01 ± 0.72 (2.07) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.834 | 50/50 | 0 | 48 | 1.14 ± 0.57 (1.03) | 6.05 ± 3.96 (4.68) | 1.94 ± 0.31 (1.97) | 4.42 ± 0.75 (4.58) | 1.76 ± 0.48 (1.78) |
| left | p | 0.859 | 50/50 | 0 | 50 | 1.54 ± 0.47 (1.51) | 4.38 ± 2.59 (3.67) | 2.04 ± 0.37 (2.03) | 4.69 ± 0.81 (4.99) | 2.13 ± 0.86 (2.10) |
| back | p | 0.835 | 50/50 | 0 | 47 | 2.17 ± 0.31 (2.16) | 12.87 ± 35.93 (2.71) | 2.01 ± 0.60 (2.12) | 4.66 ± 1.29 (5.03) | 2.13 ± 0.82 (2.19) |
| right | p | 0.881 | 50/50 | 0 | 50 | 1.48 ± 0.32 (1.56) | 3.64 ± 2.42 (2.86) | 2.06 ± 0.34 (2.16) | 4.64 ± 0.87 (4.98) | 1.95 ± 0.56 (2.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.862 | 100/100 | 0 | 99 | 1.57 ± 0.55 (1.56) | 5.70 ± 14.66 (3.54) | 2.02 ± 0.40 (2.06) | 4.65 ± 0.91 (4.94) | 2.03 ± 0.74 (2.07) |
| right | p | 0.842 | 100/100 | 0 | 96 | 1.59 ± 0.59 (1.51) | 7.77 ± 21.66 (3.77) | 2.01 ± 0.44 (2.05) | 4.56 ± 1.00 (4.75) | 1.95 ± 0.69 (2.03) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 25 | 1.14 ± 0.57 (1.04) | 5.64 ± 3.48 (4.72) | 1.91 ± 0.34 (1.94) | 4.34 ± 0.75 (4.48) | 1.71 ± 0.49 (1.79) |
| forward/right | p | 0.834 | 25/25 | 0 | 23 | 1.13 ± 0.56 (0.98) | 6.47 ± 4.35 (4.63) | 1.97 ± 0.27 (1.99) | 4.50 ± 0.73 (4.69) | 1.80 ± 0.46 (1.77) |
| left/left | p | 0.876 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.38) | 4.22 ± 2.35 (3.65) | 2.01 ± 0.39 (2.01) | 4.69 ± 0.83 (5.00) | 2.14 ± 0.92 (2.09) |
| left/right | p | 0.842 | 25/25 | 0 | 25 | 1.68 ± 0.53 (1.56) | 4.54 ± 2.80 (3.72) | 2.07 ± 0.34 (2.03) | 4.70 ± 0.79 (4.75) | 2.12 ± 0.78 (2.11) |
| back/left | p | 0.850 | 25/25 | 0 | 24 | 2.18 ± 0.33 (2.24) | 9.59 ± 28.54 (2.37) | 2.05 ± 0.52 (2.08) | 4.81 ± 1.13 (5.19) | 2.24 ± 0.80 (2.21) |
| back/right | p | 0.819 | 25/25 | 0 | 23 | 2.17 ± 0.29 (2.14) | 16.15 ± 41.78 (3.27) | 1.98 ± 0.67 (2.18) | 4.52 ± 1.42 (4.85) | 2.03 ± 0.82 (2.17) |
| right/left | p | 0.888 | 25/25 | 0 | 25 | 1.57 ± 0.30 (1.60) | 3.37 ± 2.25 (2.71) | 2.11 ± 0.30 (2.16) | 4.77 ± 0.82 (5.07) | 2.03 ± 0.55 (2.06) |
| right/right | p | 0.874 | 25/25 | 0 | 25 | 1.39 ± 0.32 (1.44) | 3.91 ± 2.55 (2.99) | 2.01 ± 0.37 (2.14) | 4.51 ± 0.90 (4.90) | 1.86 ± 0.56 (2.02) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.878 | 7.5 | 5.11 | 2.35 |
| p | normal | 0.827 | 5.9 | 4.10 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.789 | 0.17 | 2.26 ± 0.70 (2.09) | 3.73 | 1.37 |
| p | medium | 15 | 0.893 | 0.73 | 1.12 ± 0.32 (1.23) | 3.64 | 1.46 |
| p | strong | 125 | 0.878 | 0.69 | - | 5.14 | 2.35 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector forward (0.834).
