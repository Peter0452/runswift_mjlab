# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s5_ctl7_t4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 1.94 ± 1.39 (1.67) |
| Direction error [°] | 15.33 ± 31.75 (5.23) |
| Avg ball speed [m/s] | 2.17 ± 0.66 (2.37) |
| Peak ball speed [m/s] | 4.72 ± 1.50 (5.16) |
| Distance [m] | 2.03 ± 0.81 (2.16) |
| Path length [m] | 2.04 ± 0.81 (2.16) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 44 | 1.77 ± 2.18 (1.29) | 9.11 ± 15.11 (3.79) | 2.07 ± 0.73 (2.30) | 4.55 ± 1.69 (4.81) | 1.91 ± 0.84 (2.06) |
| left | p | 0.812 | 49/50 | 0 | 44 | 1.71 ± 0.47 (1.70) | 12.75 ± 25.41 (5.33) | 2.23 ± 0.58 (2.41) | 4.84 ± 1.34 (5.33) | 2.10 ± 0.76 (2.20) |
| back | p | 0.742 | 49/50 | 0 | 41 | 2.60 ± 1.41 (2.40) | 26.08 ± 47.47 (8.26) | 2.26 ± 0.68 (2.45) | 4.89 ± 1.52 (5.50) | 2.17 ± 0.87 (2.39) |
| right | p | 0.814 | 50/50 | 0 | 43 | 1.69 ± 0.39 (1.75) | 13.55 ± 27.57 (4.15) | 2.14 ± 0.61 (2.31) | 4.62 ± 1.39 (4.83) | 1.95 ± 0.74 (2.00) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 99/100 | 0 | 84 | 1.85 ± 1.18 (1.62) | 16.81 ± 34.26 (5.08) | 2.16 ± 0.67 (2.37) | 4.71 ± 1.51 (5.23) | 2.02 ± 0.82 (2.17) |
| right | p | 0.790 | 99/100 | 0 | 88 | 2.03 ± 1.57 (1.72) | 13.85 ± 28.94 (5.27) | 2.18 ± 0.65 (2.37) | 4.74 ± 1.48 (5.00) | 2.04 ± 0.80 (2.14) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.813 | 25/25 | 0 | 22 | 1.58 ± 1.91 (1.26) | 9.34 ± 16.31 (3.58) | 2.08 ± 0.69 (2.25) | 4.57 ± 1.56 (4.89) | 1.90 ± 0.77 (2.00) |
| forward/right | p | 0.794 | 25/25 | 0 | 22 | 1.96 ± 2.41 (1.30) | 8.87 ± 13.79 (4.78) | 2.07 ± 0.78 (2.31) | 4.54 ± 1.81 (4.68) | 1.92 ± 0.90 (2.12) |
| left/left | p | 0.825 | 24/25 | 0 | 23 | 1.67 ± 0.39 (1.61) | 5.94 ± 4.52 (5.17) | 2.36 ± 0.42 (2.42) | 5.15 ± 1.01 (5.51) | 2.28 ± 0.63 (2.49) |
| left/right | p | 0.798 | 25/25 | 0 | 21 | 1.74 ± 0.53 (1.76) | 19.28 ± 34.04 (5.36) | 2.10 ± 0.68 (2.33) | 4.55 ± 1.54 (4.76) | 1.93 ± 0.83 (2.01) |
| back/left | p | 0.752 | 25/25 | 0 | 19 | 2.37 ± 1.09 (2.34) | 33.25 ± 52.19 (8.43) | 2.18 ± 0.78 (2.42) | 4.71 ± 1.72 (5.42) | 2.08 ± 0.99 (2.39) |
| back/right | p | 0.731 | 24/25 | 0 | 22 | 2.85 ± 1.63 (2.50) | 18.61 ± 40.68 (7.82) | 2.34 ± 0.54 (2.46) | 5.08 ± 1.25 (5.56) | 2.26 ± 0.71 (2.38) |
| right/left | p | 0.791 | 25/25 | 0 | 20 | 1.78 ± 0.39 (1.80) | 18.26 ± 34.61 (4.37) | 2.05 ± 0.68 (2.30) | 4.42 ± 1.55 (4.72) | 1.85 ± 0.77 (1.99) |
| right/right | p | 0.837 | 25/25 | 0 | 23 | 1.60 ± 0.37 (1.54) | 8.83 ± 16.67 (3.77) | 2.23 ± 0.53 (2.33) | 4.81 ± 1.18 (4.95) | 2.04 ± 0.68 (2.12) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.816 | 13.7 | 5.16 | 2.27 |
| p | normal | 0.769 | 16.9 | 4.30 | 1.79 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.723 | 0.10 | 2.58 ± 1.10 (2.48) | 4.03 | 1.63 |
| p | medium | 20 | 0.848 | 0.61 | 1.37 ± 0.18 (1.39) | 4.41 | 1.84 |
| p | strong | 126 | 0.814 | 0.68 | - | 5.08 | 2.23 |

## Notes

- p: score 0.793, 198/200 kicked, 0 fell; worst sector back (0.742).
