# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.12 ± 1.85 (1.76) |
| Direction error [°] | 16.89 ± 35.01 (5.00) |
| Avg ball speed [m/s] | 2.08 ± 0.66 (2.27) |
| Peak ball speed [m/s] | 4.54 ± 1.54 (4.95) |
| Distance [m] | 1.89 ± 0.84 (1.91) |
| Path length [m] | 1.90 ± 0.84 (1.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.822 | 50/50 | 0 | 45 | 1.66 ± 1.97 (1.30) | 8.81 ± 14.56 (4.61) | 2.14 ± 0.62 (2.34) | 4.67 ± 1.44 (4.97) | 1.96 ± 0.83 (1.99) |
| left | p | 0.811 | 49/50 | 0 | 42 | 1.68 ± 0.44 (1.72) | 14.23 ± 29.96 (3.87) | 2.10 ± 0.57 (2.27) | 4.62 ± 1.37 (5.17) | 1.90 ± 0.78 (1.97) |
| back | p | 0.749 | 50/50 | 0 | 43 | 2.81 ± 1.83 (2.56) | 23.16 ± 44.54 (6.56) | 2.17 ± 0.65 (2.36) | 4.66 ± 1.51 (5.40) | 2.01 ± 0.85 (2.25) |
| right | p | 0.734 | 48/50 | 0 | 38 | 2.33 ± 2.32 (1.84) | 21.49 ± 41.08 (5.29) | 1.91 ± 0.76 (2.17) | 4.19 ± 1.76 (4.39) | 1.68 ± 0.87 (1.78) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 100/100 | 0 | 87 | 1.83 ± 0.70 (1.76) | 15.37 ± 32.64 (5.08) | 2.09 ± 0.65 (2.29) | 4.54 ± 1.52 (4.97) | 1.90 ± 0.84 (1.90) |
| right | p | 0.755 | 97/100 | 0 | 81 | 2.42 ± 2.50 (1.80) | 18.46 ± 37.22 (4.76) | 2.08 ± 0.67 (2.25) | 4.53 ± 1.55 (4.93) | 1.87 ± 0.84 (1.91) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 22 | 1.29 ± 0.31 (1.34) | 9.07 ± 13.49 (5.17) | 2.08 ± 0.72 (2.29) | 4.48 ± 1.66 (4.38) | 1.91 ± 0.94 (1.75) |
| forward/right | p | 0.816 | 25/25 | 0 | 23 | 2.03 ± 2.72 (1.30) | 8.55 ± 15.56 (4.60) | 2.21 ± 0.49 (2.37) | 4.86 ± 1.15 (5.29) | 2.01 ± 0.70 (2.12) |
| left/left | p | 0.811 | 25/25 | 0 | 21 | 1.58 ± 0.42 (1.62) | 13.37 ± 21.91 (5.00) | 2.04 ± 0.60 (2.31) | 4.47 ± 1.41 (5.23) | 1.83 ± 0.78 (2.06) |
| left/right | p | 0.810 | 24/25 | 0 | 21 | 1.78 ± 0.45 (1.82) | 15.12 ± 36.48 (3.06) | 2.16 ± 0.53 (2.27) | 4.78 ± 1.30 (5.16) | 1.98 ± 0.77 (1.91) |
| back/left | p | 0.798 | 25/25 | 0 | 24 | 2.57 ± 0.50 (2.56) | 11.00 ± 26.81 (4.66) | 2.36 ± 0.40 (2.50) | 5.08 ± 1.05 (5.58) | 2.23 ± 0.66 (2.43) |
| back/right | p | 0.701 | 25/25 | 0 | 19 | 3.05 ± 2.51 (2.52) | 35.33 ± 54.35 (7.45) | 1.99 ± 0.78 (2.25) | 4.25 ± 1.77 (4.46) | 1.78 ± 0.95 (1.91) |
| right/left | p | 0.773 | 25/25 | 0 | 20 | 1.88 ± 0.75 (1.84) | 28.05 ± 51.55 (6.53) | 1.88 ± 0.74 (2.10) | 4.15 ± 1.72 (4.33) | 1.64 ± 0.85 (1.76) |
| right/right | p | 0.695 | 23/25 | 0 | 18 | 2.82 ± 3.18 (1.84) | 14.36 ± 23.16 (4.49) | 1.95 ± 0.78 (2.22) | 4.23 ± 1.79 (4.46) | 1.72 ± 0.88 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.818 | 13.6 | 5.06 | 2.18 |
| p | normal | 0.740 | 20.2 | 4.01 | 1.59 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.705 | 0.12 | 2.39 ± 0.96 (2.39) | 3.79 | 1.47 |
| p | medium | 18 | 0.844 | 0.68 | 1.12 ± 0.36 (1.25) | 3.60 | 1.33 |
| p | strong | 124 | 0.804 | 0.67 | - | 5.02 | 2.17 |

## Notes

- p: score 0.779, 197/200 kicked, 0 fell; worst sector right (0.734).
