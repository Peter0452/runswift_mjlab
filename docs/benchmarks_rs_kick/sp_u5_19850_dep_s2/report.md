# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u5_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.788** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.01 ± 1.65 (1.74) |
| Direction error [°] | 18.29 ± 35.80 (5.89) |
| Avg ball speed [m/s] | 2.16 ± 0.78 (2.36) |
| Peak ball speed [m/s] | 4.63 ± 1.76 (5.35) |
| Distance [m] | 2.10 ± 1.01 (2.34) |
| Path length [m] | 2.11 ± 1.01 (2.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 43 | 1.64 ± 1.99 (1.24) | 11.63 ± 21.08 (5.17) | 2.15 ± 0.74 (2.27) | 4.60 ± 1.70 (4.86) | 2.04 ± 0.94 (2.14) |
| left | p | 0.813 | 50/50 | 0 | 44 | 2.05 ± 1.77 (1.82) | 13.91 ± 25.41 (5.07) | 2.18 ± 0.73 (2.39) | 4.70 ± 1.66 (5.45) | 2.13 ± 0.96 (2.29) |
| back | p | 0.744 | 49/50 | 0 | 40 | 2.65 ± 1.63 (2.44) | 25.98 ± 48.04 (6.43) | 2.29 ± 0.83 (2.55) | 4.86 ± 1.83 (5.75) | 2.30 ± 1.10 (2.74) |
| right | p | 0.789 | 49/50 | 0 | 40 | 1.69 ± 0.67 (1.74) | 21.86 ± 40.28 (5.34) | 2.03 ± 0.81 (2.24) | 4.34 ± 1.82 (4.89) | 1.93 ± 0.99 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 99/100 | 0 | 82 | 1.82 ± 1.02 (1.66) | 20.07 ± 37.18 (5.86) | 2.17 ± 0.82 (2.41) | 4.68 ± 1.83 (5.46) | 2.15 ± 1.03 (2.50) |
| right | p | 0.781 | 99/100 | 0 | 85 | 2.19 ± 2.08 (1.78) | 16.51 ± 34.28 (5.91) | 2.15 ± 0.75 (2.31) | 4.57 ± 1.69 (4.54) | 2.05 ± 0.98 (2.02) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.806 | 25/25 | 0 | 22 | 1.25 ± 0.26 (1.24) | 15.10 ± 27.21 (5.86) | 2.12 ± 0.75 (2.24) | 4.53 ± 1.71 (4.50) | 2.02 ± 0.95 (1.97) |
| forward/right | p | 0.802 | 25/25 | 0 | 21 | 2.03 ± 2.75 (1.22) | 8.15 ± 11.13 (3.87) | 2.18 ± 0.73 (2.50) | 4.66 ± 1.69 (5.65) | 2.06 ± 0.92 (2.46) |
| left/left | p | 0.828 | 25/25 | 0 | 22 | 1.92 ± 1.56 (1.62) | 11.60 ± 19.35 (5.02) | 2.30 ± 0.72 (2.53) | 4.97 ± 1.61 (5.53) | 2.31 ± 0.94 (2.60) |
| left/right | p | 0.798 | 25/25 | 0 | 22 | 2.18 ± 1.96 (1.90) | 16.22 ± 30.11 (5.11) | 2.07 ± 0.73 (2.26) | 4.42 ± 1.66 (4.48) | 1.94 ± 0.95 (1.99) |
| back/left | p | 0.748 | 24/25 | 0 | 19 | 2.31 ± 0.62 (2.43) | 22.09 ± 38.46 (7.25) | 2.30 ± 0.82 (2.60) | 4.96 ± 1.82 (5.86) | 2.35 ± 1.07 (2.80) |
| back/right | p | 0.740 | 25/25 | 0 | 21 | 2.98 ± 2.15 (2.44) | 29.71 ± 55.45 (6.08) | 2.27 ± 0.83 (2.37) | 4.77 ± 1.84 (4.68) | 2.25 ± 1.13 (2.04) |
| right/left | p | 0.796 | 25/25 | 0 | 19 | 1.82 ± 0.83 (1.76) | 31.55 ± 52.02 (4.35) | 1.98 ± 0.92 (2.39) | 4.27 ± 2.06 (5.46) | 1.91 ± 1.10 (2.48) |
| right/right | p | 0.781 | 24/25 | 0 | 21 | 1.56 ± 0.42 (1.65) | 11.76 ± 17.15 (6.41) | 2.09 ± 0.66 (2.22) | 4.43 ± 1.53 (4.28) | 1.95 ± 0.86 (1.79) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.819 | 19.0 | 5.10 | 2.42 |
| p | normal | 0.756 | 17.6 | 4.14 | 1.77 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.713 | 0.19 | 2.22 ± 0.99 (2.12) | 3.71 | 1.48 |
| p | medium | 15 | 0.827 | 0.61 | 1.08 ± 0.46 (1.22) | 3.47 | 1.36 |
| p | strong | 125 | 0.819 | 0.69 | - | 5.20 | 2.48 |

## Notes

- p: score 0.788, 198/200 kicked, 0 fell; worst sector back (0.744).
