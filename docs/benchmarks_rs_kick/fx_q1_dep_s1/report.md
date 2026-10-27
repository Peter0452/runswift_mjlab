# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.835** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 189 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.81 ± 0.58 (1.69) |
| Direction error [°] | 7.44 ± 4.59 (7.25) |
| Avg ball speed [m/s] | 2.68 ± 0.45 (2.77) |
| Peak ball speed [m/s] | 5.62 ± 1.07 (6.14) |
| Distance [m] | 2.80 ± 0.83 (3.15) |
| Path length [m] | 2.81 ± 0.83 (3.17) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.870 | 50/50 | 0 | 49 | 1.24 ± 0.26 (1.26) | 5.22 ± 4.07 (3.98) | 2.60 ± 0.45 (2.64) | 5.49 ± 1.04 (5.86) | 2.66 ± 0.77 (2.84) |
| left | p | 0.847 | 50/50 | 0 | 47 | 1.74 ± 0.36 (1.71) | 7.92 ± 4.54 (7.46) | 2.70 ± 0.49 (2.92) | 5.62 ± 1.14 (6.29) | 2.80 ± 0.87 (3.23) |
| back | p | 0.795 | 50/50 | 0 | 48 | 2.56 ± 0.34 (2.56) | 8.66 ± 4.05 (9.02) | 2.83 ± 0.40 (2.96) | 5.91 ± 0.98 (6.43) | 3.05 ± 0.78 (3.39) |
| right | p | 0.829 | 50/50 | 0 | 45 | 1.71 ± 0.36 (1.63) | 7.96 ± 4.89 (8.37) | 2.59 ± 0.42 (2.68) | 5.46 ± 1.04 (6.02) | 2.68 ± 0.81 (3.05) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.834 | 100/100 | 0 | 97 | 1.81 ± 0.58 (1.63) | 7.25 ± 4.55 (7.05) | 2.68 ± 0.43 (2.76) | 5.64 ± 1.02 (6.14) | 2.80 ± 0.78 (3.16) |
| right | p | 0.836 | 100/100 | 0 | 92 | 1.82 ± 0.58 (1.70) | 7.63 ± 4.63 (7.35) | 2.68 ± 0.47 (2.79) | 5.61 ± 1.11 (6.15) | 2.79 ± 0.86 (3.15) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 25 | 1.22 ± 0.26 (1.26) | 5.15 ± 4.12 (3.52) | 2.53 ± 0.40 (2.60) | 5.39 ± 0.95 (5.77) | 2.58 ± 0.68 (2.72) |
| forward/right | p | 0.876 | 25/25 | 0 | 24 | 1.27 ± 0.26 (1.32) | 5.30 ± 4.01 (4.21) | 2.66 ± 0.49 (2.72) | 5.59 ± 1.11 (6.05) | 2.74 ± 0.85 (3.13) |
| left/left | p | 0.845 | 25/25 | 0 | 23 | 1.66 ± 0.34 (1.56) | 8.36 ± 5.38 (7.22) | 2.78 ± 0.47 (2.93) | 5.76 ± 1.10 (6.32) | 2.91 ± 0.84 (3.37) |
| left/right | p | 0.848 | 25/25 | 0 | 24 | 1.82 ± 0.35 (1.80) | 7.48 ± 3.45 (7.69) | 2.63 ± 0.50 (2.88) | 5.49 ± 1.17 (6.20) | 2.69 ± 0.89 (2.97) |
| back/left | p | 0.798 | 25/25 | 0 | 25 | 2.56 ± 0.28 (2.56) | 8.30 ± 3.55 (8.94) | 2.82 ± 0.38 (2.93) | 5.94 ± 0.93 (6.41) | 3.05 ± 0.74 (3.39) |
| back/right | p | 0.792 | 25/25 | 0 | 23 | 2.57 ± 0.38 (2.58) | 9.01 ± 4.48 (9.23) | 2.84 ± 0.42 (2.99) | 5.89 ± 1.03 (6.48) | 3.05 ± 0.82 (3.38) |
| right/left | p | 0.829 | 25/25 | 0 | 24 | 1.79 ± 0.37 (1.76) | 7.18 ± 4.18 (8.15) | 2.58 ± 0.40 (2.67) | 5.46 ± 1.00 (5.98) | 2.66 ± 0.78 (3.06) |
| right/right | p | 0.828 | 25/25 | 0 | 21 | 1.63 ± 0.33 (1.56) | 8.74 ± 5.39 (8.58) | 2.61 ± 0.44 (2.69) | 5.46 ± 1.09 (6.06) | 2.70 ± 0.85 (3.04) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.882 | 7.3 | 6.39 | 3.38 |
| p | normal | 0.788 | 7.6 | 4.85 | 2.22 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.717 | 0.04 | 2.75 ± 0.83 (2.51) | 4.29 | 1.78 |
| p | medium | 20 | 0.854 | 0.65 | 1.35 ± 0.16 (1.37) | 4.32 | 1.82 |
| p | strong | 126 | 0.883 | 0.85 | - | 6.40 | 3.39 |

## Notes

- p: score 0.835, 200/200 kicked, 0 fell; worst sector back (0.795).
