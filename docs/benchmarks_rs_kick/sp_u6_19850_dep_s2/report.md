# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.792** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 2.05 ± 1.64 (1.77) |
| Direction error [°] | 17.97 ± 37.87 (4.76) |
| Avg ball speed [m/s] | 2.14 ± 0.83 (2.33) |
| Peak ball speed [m/s] | 4.88 ± 1.83 (5.58) |
| Distance [m] | 2.39 ± 1.28 (2.61) |
| Path length [m] | 2.45 ± 1.29 (2.67) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.806 | 49/50 | 0 | 43 | 1.80 ± 2.23 (1.26) | 8.62 ± 15.36 (3.91) | 2.17 ± 0.76 (2.30) | 5.02 ± 1.65 (5.65) | 2.41 ± 1.23 (2.57) |
| left | p | 0.793 | 48/50 | 0 | 41 | 1.95 ± 1.26 (1.81) | 13.35 ± 25.84 (4.85) | 2.19 ± 0.83 (2.36) | 4.99 ± 1.74 (5.54) | 2.40 ± 1.10 (2.67) |
| back | p | 0.757 | 49/50 | 0 | 41 | 2.68 ± 1.78 (2.48) | 27.50 ± 53.21 (5.68) | 2.21 ± 0.85 (2.49) | 5.02 ± 1.87 (5.98) | 2.53 ± 1.34 (2.92) |
| right | p | 0.811 | 50/50 | 0 | 40 | 1.77 ± 0.75 (1.77) | 22.24 ± 41.98 (4.76) | 1.98 ± 0.85 (2.23) | 4.51 ± 1.98 (5.04) | 2.22 ± 1.39 (2.35) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 98/100 | 0 | 85 | 2.05 ± 1.56 (1.77) | 18.80 ± 38.58 (4.72) | 2.18 ± 0.83 (2.45) | 4.99 ± 1.84 (5.87) | 2.46 ± 1.27 (2.67) |
| right | p | 0.787 | 98/100 | 0 | 80 | 2.05 ± 1.72 (1.77) | 17.15 ± 37.14 (4.91) | 2.09 ± 0.83 (2.28) | 4.78 ± 1.81 (4.83) | 2.32 ± 1.28 (2.37) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.813 | 25/25 | 0 | 23 | 1.96 ± 2.36 (1.36) | 9.30 ± 18.56 (3.64) | 2.10 ± 0.78 (2.20) | 4.98 ± 1.69 (5.49) | 2.51 ± 1.39 (2.48) |
| forward/right | p | 0.799 | 24/25 | 0 | 20 | 1.65 ± 2.07 (1.21) | 7.92 ± 11.03 (4.37) | 2.24 ± 0.74 (2.44) | 5.07 ± 1.61 (5.77) | 2.31 ± 1.02 (2.68) |
| left/left | p | 0.794 | 24/25 | 0 | 22 | 2.09 ± 1.71 (1.72) | 12.04 ± 23.84 (4.24) | 2.27 ± 0.79 (2.51) | 5.05 ± 1.71 (5.75) | 2.38 ± 1.02 (2.62) |
| left/right | p | 0.792 | 24/25 | 0 | 19 | 1.81 ± 0.45 (1.86) | 14.66 ± 27.64 (5.80) | 2.11 ± 0.86 (2.33) | 4.92 ± 1.76 (4.99) | 2.43 ± 1.18 (2.95) |
| back/left | p | 0.770 | 24/25 | 0 | 21 | 2.30 ± 0.59 (2.50) | 20.77 ± 41.93 (6.33) | 2.36 ± 0.76 (2.63) | 5.34 ± 1.67 (6.15) | 2.68 ± 1.08 (3.11) |
| back/right | p | 0.743 | 25/25 | 0 | 20 | 3.06 ± 2.37 (2.44) | 33.96 ± 61.45 (5.28) | 2.07 ± 0.90 (2.25) | 4.71 ± 2.00 (4.75) | 2.39 ± 1.54 (2.21) |
| right/left | p | 0.807 | 25/25 | 0 | 19 | 1.87 ± 0.86 (1.78) | 32.89 ± 54.03 (4.83) | 2.02 ± 0.93 (2.48) | 4.59 ± 2.16 (5.89) | 2.28 ± 1.48 (2.82) |
| right/right | p | 0.814 | 25/25 | 0 | 21 | 1.67 ± 0.61 (1.66) | 11.60 ± 19.49 (3.51) | 1.94 ± 0.76 (2.17) | 4.43 ± 1.76 (4.49) | 2.17 ± 1.28 (2.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.825 | 16.0 | 5.61 | 2.88 |
| p | normal | 0.759 | 19.9 | 4.15 | 1.91 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.725 | 0.20 | 2.23 ± 1.06 (2.10) | 3.69 | 1.52 |
| p | medium | 15 | 0.825 | 0.59 | 1.10 ± 0.46 (1.28) | 3.54 | 1.67 |
| p | strong | 125 | 0.820 | 0.75 | - | 5.63 | 2.90 |

## Notes

- p: score 0.792, 196/200 kicked, 0 fell; worst sector back (0.757).
