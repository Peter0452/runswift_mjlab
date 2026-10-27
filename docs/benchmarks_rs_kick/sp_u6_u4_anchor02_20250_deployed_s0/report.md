# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 1.98 ± 1.51 (1.74) |
| Direction error [°] | 17.89 ± 36.21 (5.14) |
| Avg ball speed [m/s] | 2.27 ± 0.85 (2.55) |
| Peak ball speed [m/s] | 4.77 ± 1.84 (5.58) |
| Distance [m] | 2.30 ± 1.16 (2.71) |
| Path length [m] | 2.31 ± 1.16 (2.72) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.770 | 48/50 | 0 | 40 | 1.53 ± 1.47 (1.35) | 9.34 ± 13.65 (4.54) | 2.11 ± 0.78 (2.16) | 4.42 ± 1.71 (4.28) | 2.02 ± 1.04 (1.79) |
| left | p | 0.817 | 50/50 | 0 | 42 | 1.91 ± 1.47 (1.77) | 15.80 ± 29.35 (6.20) | 2.33 ± 0.88 (2.59) | 4.87 ± 1.93 (5.80) | 2.39 ± 1.16 (2.91) |
| back | p | 0.758 | 50/50 | 0 | 38 | 2.54 ± 1.47 (2.51) | 29.55 ± 52.77 (7.30) | 2.27 ± 0.94 (2.66) | 4.78 ± 2.03 (5.83) | 2.36 ± 1.28 (2.90) |
| right | p | 0.826 | 50/50 | 0 | 43 | 1.90 ± 1.45 (1.74) | 16.52 ± 33.99 (4.12) | 2.37 ± 0.75 (2.66) | 5.01 ± 1.63 (5.88) | 2.41 ± 1.09 (2.86) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.819 | 100/100 | 0 | 87 | 1.80 ± 0.65 (1.73) | 15.79 ± 34.80 (4.97) | 2.37 ± 0.79 (2.61) | 4.96 ± 1.73 (5.79) | 2.41 ± 1.12 (2.84) |
| right | p | 0.767 | 98/100 | 0 | 76 | 2.15 ± 2.03 (1.75) | 20.03 ± 37.47 (5.45) | 2.18 ± 0.89 (2.32) | 4.58 ± 1.94 (4.99) | 2.18 ± 1.19 (2.23) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.818 | 25/25 | 0 | 21 | 1.37 ± 0.52 (1.32) | 9.68 ± 16.14 (2.22) | 2.17 ± 0.84 (2.27) | 4.56 ± 1.83 (4.37) | 2.13 ± 1.10 (1.75) |
| forward/right | p | 0.722 | 23/25 | 0 | 19 | 1.71 ± 2.05 (1.36) | 8.98 ± 10.26 (6.04) | 2.04 ± 0.70 (2.12) | 4.27 ± 1.56 (4.24) | 1.90 ± 0.96 (1.82) |
| left/left | p | 0.859 | 25/25 | 0 | 23 | 1.63 ± 0.37 (1.68) | 9.39 ± 15.29 (5.13) | 2.50 ± 0.74 (2.76) | 5.19 ± 1.64 (6.02) | 2.58 ± 1.04 (3.10) |
| left/right | p | 0.775 | 25/25 | 0 | 19 | 2.19 ± 2.01 (1.96) | 22.20 ± 37.51 (7.04) | 2.16 ± 0.98 (2.55) | 4.55 ± 2.13 (5.79) | 2.19 ± 1.25 (2.76) |
| back/left | p | 0.777 | 25/25 | 0 | 21 | 2.41 ± 0.69 (2.58) | 25.40 ± 50.62 (7.33) | 2.42 ± 0.80 (2.66) | 5.10 ± 1.74 (5.93) | 2.54 ± 1.21 (3.02) |
| back/right | p | 0.740 | 25/25 | 0 | 17 | 2.68 ± 1.95 (2.38) | 33.69 ± 54.52 (7.13) | 2.12 ± 1.03 (2.58) | 4.45 ± 2.23 (5.70) | 2.18 ± 1.32 (2.69) |
| right/left | p | 0.823 | 25/25 | 0 | 22 | 1.81 ± 0.47 (1.80) | 18.68 ± 40.12 (3.90) | 2.37 ± 0.74 (2.65) | 4.99 ± 1.62 (5.81) | 2.40 ± 1.05 (2.82) |
| right/right | p | 0.829 | 25/25 | 0 | 21 | 2.00 ± 1.98 (1.72) | 14.36 ± 26.31 (4.29) | 2.37 ± 0.75 (2.67) | 5.02 ± 1.64 (5.99) | 2.42 ± 1.13 (2.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.825 | 15.5 | 5.53 | 2.84 |
| p | normal | 0.761 | 20.2 | 4.04 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.728 | 0.17 | 2.34 ± 1.06 (2.24) | 3.64 | 1.45 |
| p | medium | 16 | 0.822 | 0.64 | 1.20 ± 0.37 (1.28) | 3.89 | 1.63 |
| p | strong | 126 | 0.819 | 0.72 | - | 5.42 | 2.78 |

## Notes

- p: score 0.793, 198/200 kicked, 0 fell; worst sector back (0.758).
