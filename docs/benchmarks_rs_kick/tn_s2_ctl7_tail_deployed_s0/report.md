# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s2_ctl7_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.763** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 152 |
| Weak kicks (< 0.3 m) | 22 |
| Time to kick [s] | 2.13 ± 1.98 (1.71) |
| Direction error [°] | 24.97 ± 42.61 (8.26) |
| Avg ball speed [m/s] | 2.22 ± 0.93 (2.40) |
| Peak ball speed [m/s] | 4.58 ± 1.96 (4.82) |
| Distance [m] | 2.21 ± 1.23 (2.08) |
| Path length [m] | 2.22 ± 1.23 (2.09) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.770 | 50/50 | 0 | 39 | 1.69 ± 1.81 (1.31) | 12.96 ± 20.32 (5.84) | 2.06 ± 0.90 (2.22) | 4.23 ± 1.91 (4.40) | 1.95 ± 1.14 (1.90) |
| left | p | 0.803 | 50/50 | 0 | 38 | 1.97 ± 1.94 (1.75) | 21.39 ± 35.76 (7.05) | 2.39 ± 0.85 (2.81) | 4.92 ± 1.80 (5.90) | 2.41 ± 1.17 (2.96) |
| back | p | 0.705 | 50/50 | 0 | 37 | 2.90 ± 2.14 (2.43) | 40.78 ± 61.07 (10.96) | 2.25 ± 1.04 (2.80) | 4.64 ± 2.19 (5.97) | 2.33 ± 1.38 (3.15) |
| right | p | 0.774 | 50/50 | 0 | 38 | 1.96 ± 1.78 (1.72) | 24.74 ± 37.87 (7.34) | 2.19 ± 0.88 (2.37) | 4.53 ± 1.84 (4.56) | 2.15 ± 1.16 (2.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.784 | 100/100 | 0 | 78 | 1.85 ± 1.27 (1.68) | 22.63 ± 39.07 (8.46) | 2.30 ± 0.90 (2.60) | 4.74 ± 1.91 (5.69) | 2.31 ± 1.21 (2.71) |
| right | p | 0.742 | 100/100 | 0 | 74 | 2.41 ± 2.46 (1.72) | 27.30 ± 45.76 (7.69) | 2.15 ± 0.94 (2.34) | 4.42 ± 1.99 (4.57) | 2.11 ± 1.23 (1.99) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.805 | 25/25 | 0 | 21 | 1.56 ± 1.54 (1.28) | 9.22 ± 12.60 (4.39) | 2.23 ± 0.85 (2.34) | 4.59 ± 1.83 (4.55) | 2.16 ± 1.13 (1.95) |
| forward/right | p | 0.735 | 25/25 | 0 | 18 | 1.83 ± 2.03 (1.32) | 16.70 ± 25.29 (6.31) | 1.89 ± 0.91 (2.16) | 3.86 ± 1.92 (4.20) | 1.73 ± 1.10 (1.77) |
| left/left | p | 0.838 | 25/25 | 0 | 20 | 1.55 ± 0.43 (1.74) | 16.47 ± 24.44 (8.29) | 2.54 ± 0.73 (2.89) | 5.24 ± 1.57 (6.05) | 2.61 ± 1.07 (3.16) |
| left/right | p | 0.767 | 25/25 | 0 | 18 | 2.40 ± 2.64 (1.76) | 26.31 ± 43.73 (6.80) | 2.24 ± 0.93 (2.67) | 4.61 ± 1.96 (5.74) | 2.20 ± 1.22 (2.75) |
| back/left | p | 0.718 | 25/25 | 0 | 18 | 2.65 ± 1.69 (2.40) | 36.16 ± 55.67 (10.95) | 2.27 ± 1.03 (2.80) | 4.69 ± 2.17 (5.99) | 2.36 ± 1.38 (3.21) |
| back/right | p | 0.693 | 25/25 | 0 | 19 | 3.16 ± 2.49 (2.46) | 45.40 ± 65.72 (10.98) | 2.24 ± 1.05 (2.81) | 4.60 ± 2.20 (5.94) | 2.30 ± 1.38 (3.09) |
| right/left | p | 0.775 | 25/25 | 0 | 19 | 1.65 ± 0.47 (1.72) | 28.68 ± 42.60 (7.44) | 2.17 ± 0.93 (2.33) | 4.45 ± 1.93 (4.50) | 2.10 ± 1.19 (1.98) |
| right/right | p | 0.773 | 25/25 | 0 | 19 | 2.27 ± 2.43 (1.72) | 20.80 ± 31.97 (7.16) | 2.22 ± 0.82 (2.54) | 4.62 ± 1.75 (5.41) | 2.20 ± 1.12 (2.56) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.787 | 25.8 | 5.21 | 2.68 |
| p | normal | 0.739 | 24.2 | 3.95 | 1.74 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.689 | 0.18 | 2.24 ± 1.19 (2.16) | 3.48 | 1.40 |
| p | medium | 16 | 0.820 | 0.67 | 1.19 ± 0.33 (1.25) | 3.85 | 1.59 |
| p | strong | 126 | 0.790 | 0.69 | - | 5.18 | 2.66 |

## Notes

- p: score 0.763, 200/200 kicked, 0 fell; worst sector back (0.705).
