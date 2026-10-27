# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w1_u6_tail19850_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.785** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.01 ± 1.65 (1.74) |
| Direction error [°] | 17.87 ± 36.58 (5.33) |
| Avg ball speed [m/s] | 2.03 ± 0.62 (2.18) |
| Peak ball speed [m/s] | 4.53 ± 1.54 (5.05) |
| Distance [m] | 1.75 ± 0.81 (1.82) |
| Path length [m] | 1.76 ± 0.81 (1.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.766 | 48/50 | 0 | 40 | 1.67 ± 1.94 (1.34) | 9.22 ± 10.72 (5.39) | 1.98 ± 0.62 (2.04) | 4.38 ± 1.53 (4.12) | 1.66 ± 0.82 (1.55) |
| left | p | 0.814 | 49/50 | 0 | 43 | 1.87 ± 1.52 (1.76) | 17.36 ± 34.06 (4.87) | 2.10 ± 0.63 (2.28) | 4.75 ± 1.59 (5.38) | 1.87 ± 0.86 (2.10) |
| back | p | 0.767 | 50/50 | 0 | 43 | 2.60 ± 1.46 (2.50) | 25.53 ± 50.42 (5.56) | 2.09 ± 0.63 (2.34) | 4.68 ± 1.52 (5.46) | 1.86 ± 0.78 (2.17) |
| right | p | 0.792 | 49/50 | 0 | 41 | 1.88 ± 1.51 (1.76) | 19.02 ± 36.76 (5.09) | 1.93 ± 0.60 (2.13) | 4.32 ± 1.48 (5.01) | 1.61 ± 0.73 (1.73) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.818 | 100/100 | 0 | 88 | 1.93 ± 1.41 (1.71) | 15.78 ± 35.20 (4.78) | 2.09 ± 0.58 (2.24) | 4.68 ± 1.44 (5.22) | 1.82 ± 0.79 (1.90) |
| right | p | 0.752 | 96/100 | 0 | 79 | 2.10 ± 1.87 (1.76) | 20.04 ± 37.84 (5.97) | 1.97 ± 0.66 (2.15) | 4.39 ± 1.63 (4.59) | 1.67 ± 0.82 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.818 | 25/25 | 0 | 22 | 1.61 ± 1.68 (1.34) | 7.28 ± 9.85 (3.44) | 2.07 ± 0.63 (2.09) | 4.62 ± 1.54 (4.48) | 1.79 ± 0.83 (1.83) |
| forward/right | p | 0.713 | 23/25 | 0 | 18 | 1.74 ± 2.19 (1.34) | 11.33 ± 11.21 (7.05) | 1.89 ± 0.59 (1.95) | 4.12 ± 1.47 (3.98) | 1.51 ± 0.78 (1.44) |
| left/left | p | 0.860 | 25/25 | 0 | 23 | 1.59 ± 0.40 (1.64) | 11.32 ± 22.19 (5.26) | 2.18 ± 0.54 (2.33) | 4.90 ± 1.34 (5.37) | 1.96 ± 0.77 (2.15) |
| left/right | p | 0.769 | 24/25 | 0 | 20 | 2.16 ± 2.09 (1.96) | 23.64 ± 42.16 (4.86) | 2.02 ± 0.71 (2.24) | 4.60 ± 1.80 (5.38) | 1.78 ± 0.93 (2.05) |
| back/left | p | 0.774 | 25/25 | 0 | 22 | 2.74 ± 1.97 (2.46) | 23.79 ± 50.42 (4.80) | 2.19 ± 0.47 (2.35) | 4.87 ± 1.18 (5.49) | 1.93 ± 0.70 (2.18) |
| back/right | p | 0.759 | 25/25 | 0 | 21 | 2.46 ± 0.56 (2.50) | 27.27 ± 50.36 (5.93) | 2.00 ± 0.74 (2.25) | 4.50 ± 1.77 (5.45) | 1.78 ± 0.85 (2.15) |
| right/left | p | 0.819 | 25/25 | 0 | 21 | 1.77 ± 0.47 (1.80) | 20.72 ± 40.56 (5.09) | 1.91 ± 0.63 (2.13) | 4.32 ± 1.58 (5.05) | 1.61 ± 0.81 (1.73) |
| right/right | p | 0.765 | 24/25 | 0 | 20 | 2.00 ± 2.09 (1.67) | 17.26 ± 32.23 (5.14) | 1.95 ± 0.57 (2.15) | 4.31 ± 1.36 (4.91) | 1.61 ± 0.65 (1.73) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.810 | 15.5 | 5.22 | 2.11 |
| p | normal | 0.759 | 20.2 | 3.86 | 1.40 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.714 | 0.19 | 2.19 ± 0.97 (2.01) | 3.46 | 1.18 |
| p | medium | 16 | 0.839 | 0.74 | 1.21 ± 0.21 (1.21) | 3.95 | 1.45 |
| p | strong | 126 | 0.810 | 0.68 | - | 5.11 | 2.05 |

## Notes

- p: score 0.785, 196/200 kicked, 0 fell; worst sector forward (0.766).
