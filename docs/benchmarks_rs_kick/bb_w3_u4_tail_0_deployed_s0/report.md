# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.90 ± 0.55 (1.81) |
| Direction error [°] | 5.10 ± 3.82 (3.99) |
| Avg ball speed [m/s] | 2.28 ± 0.44 (2.42) |
| Peak ball speed [m/s] | 4.98 ± 1.14 (5.55) |
| Distance [m] | 2.11 ± 0.73 (2.38) |
| Path length [m] | 2.12 ± 0.73 (2.39) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.869 | 50/50 | 0 | 49 | 1.32 ± 0.25 (1.32) | 4.33 ± 3.41 (3.26) | 2.10 ± 0.49 (2.18) | 4.64 ± 1.26 (5.11) | 1.86 ± 0.76 (1.90) |
| left | p | 0.876 | 50/50 | 0 | 49 | 1.84 ± 0.36 (1.87) | 5.43 ± 4.20 (3.85) | 2.33 ± 0.36 (2.42) | 5.15 ± 0.97 (5.56) | 2.20 ± 0.62 (2.40) |
| back | p | 0.818 | 50/50 | 0 | 47 | 2.58 ± 0.30 (2.57) | 5.56 ± 3.88 (4.21) | 2.37 ± 0.40 (2.48) | 5.15 ± 1.07 (5.68) | 2.26 ± 0.71 (2.53) |
| right | p | 0.857 | 50/50 | 0 | 49 | 1.84 ± 0.36 (1.78) | 5.09 ± 3.62 (4.26) | 2.30 ± 0.46 (2.38) | 4.97 ± 1.15 (5.53) | 2.12 ± 0.76 (2.25) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.857 | 100/100 | 0 | 96 | 1.91 ± 0.56 (1.89) | 5.11 ± 4.13 (3.65) | 2.29 ± 0.44 (2.40) | 5.01 ± 1.13 (5.51) | 2.13 ± 0.74 (2.38) |
| right | p | 0.854 | 100/100 | 0 | 98 | 1.88 ± 0.55 (1.77) | 5.10 ± 3.48 (4.24) | 2.26 ± 0.44 (2.43) | 4.95 ± 1.14 (5.61) | 2.09 ± 0.73 (2.35) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.876 | 25/25 | 0 | 24 | 1.34 ± 0.24 (1.32) | 4.56 ± 3.95 (3.22) | 2.13 ± 0.52 (2.29) | 4.71 ± 1.34 (5.24) | 1.92 ± 0.81 (2.15) |
| forward/right | p | 0.861 | 25/25 | 0 | 25 | 1.30 ± 0.25 (1.32) | 4.10 ± 2.76 (3.48) | 2.08 ± 0.45 (2.17) | 4.57 ± 1.18 (4.72) | 1.81 ± 0.69 (1.86) |
| left/left | p | 0.867 | 25/25 | 0 | 24 | 1.71 ± 0.36 (1.82) | 6.09 ± 4.88 (3.76) | 2.28 ± 0.33 (2.37) | 5.00 ± 0.95 (5.45) | 2.11 ± 0.60 (2.35) |
| left/right | p | 0.885 | 25/25 | 0 | 25 | 1.96 ± 0.32 (1.98) | 4.77 ± 3.26 (4.64) | 2.38 ± 0.38 (2.49) | 5.29 ± 0.97 (5.66) | 2.28 ± 0.63 (2.41) |
| back/left | p | 0.823 | 25/25 | 0 | 24 | 2.61 ± 0.31 (2.60) | 5.00 ± 3.58 (4.10) | 2.39 ± 0.39 (2.46) | 5.21 ± 1.06 (5.69) | 2.30 ± 0.74 (2.50) |
| back/right | p | 0.814 | 25/25 | 0 | 23 | 2.56 ± 0.29 (2.54) | 6.12 ± 4.08 (5.45) | 2.34 ± 0.41 (2.50) | 5.10 ± 1.08 (5.67) | 2.22 ± 0.69 (2.58) |
| right/left | p | 0.860 | 25/25 | 0 | 24 | 1.98 ± 0.33 (1.94) | 4.79 ± 3.84 (3.63) | 2.35 ± 0.44 (2.43) | 5.11 ± 1.08 (5.60) | 2.20 ± 0.72 (2.31) |
| right/right | p | 0.855 | 25/25 | 0 | 25 | 1.70 ± 0.33 (1.76) | 5.39 ± 3.37 (5.21) | 2.26 ± 0.48 (2.34) | 4.83 ± 1.21 (5.32) | 2.05 ± 0.80 (2.13) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.887 | 5.3 | 5.82 | 2.62 |
| p | normal | 0.823 | 4.9 | 4.13 | 1.60 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.771 | 0.18 | 2.21 ± 0.67 (2.06) | 3.50 | 1.21 |
| p | medium | 16 | 0.901 | 0.83 | 1.15 ± 0.14 (1.16) | 3.73 | 1.38 |
| p | strong | 126 | 0.888 | 0.77 | - | 5.81 | 2.62 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector back (0.818).
