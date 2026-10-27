# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_14-36-37_u11_u6_prompt08/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.766** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 2.14 ± 1.78 (1.74) |
| Direction error [°] | 20.39 ± 39.75 (5.82) |
| Avg ball speed [m/s] | 1.88 ± 0.60 (2.08) |
| Peak ball speed [m/s] | 4.39 ± 1.42 (4.76) |
| Distance [m] | 1.74 ± 0.75 (1.89) |
| Path length [m] | 1.75 ± 0.75 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.794 | 50/50 | 0 | 44 | 1.86 ± 2.11 (1.35) | 7.80 ± 10.62 (4.51) | 1.93 ± 0.54 (2.09) | 4.44 ± 1.30 (4.59) | 1.74 ± 0.70 (1.93) |
| left | p | 0.793 | 50/50 | 0 | 40 | 2.00 ± 1.83 (1.75) | 21.68 ± 37.00 (6.12) | 1.84 ± 0.63 (2.06) | 4.38 ± 1.51 (4.84) | 1.72 ± 0.79 (1.82) |
| back | p | 0.722 | 50/50 | 0 | 41 | 2.79 ± 1.57 (2.62) | 32.07 ± 56.70 (6.64) | 1.92 ± 0.66 (2.15) | 4.43 ± 1.52 (4.86) | 1.82 ± 0.79 (2.04) |
| right | p | 0.756 | 48/50 | 0 | 40 | 1.88 ± 1.35 (1.73) | 19.98 ± 36.29 (5.73) | 1.84 ± 0.57 (2.01) | 4.31 ± 1.34 (4.71) | 1.68 ± 0.70 (1.75) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.797 | 100/100 | 0 | 85 | 1.90 ± 1.21 (1.70) | 19.65 ± 40.06 (4.93) | 1.91 ± 0.56 (2.09) | 4.49 ± 1.32 (4.83) | 1.78 ± 0.73 (1.90) |
| right | p | 0.736 | 98/100 | 0 | 80 | 2.38 ± 2.19 (1.76) | 21.14 ± 39.43 (6.50) | 1.86 ± 0.64 (2.07) | 4.29 ± 1.52 (4.70) | 1.70 ± 0.77 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.823 | 25/25 | 0 | 23 | 1.60 ± 1.62 (1.30) | 6.89 ± 10.34 (3.70) | 2.03 ± 0.47 (2.13) | 4.69 ± 1.09 (4.71) | 1.86 ± 0.64 (2.02) |
| forward/right | p | 0.765 | 25/25 | 0 | 21 | 2.12 ± 2.48 (1.36) | 8.72 ± 10.81 (6.43) | 1.83 ± 0.59 (2.01) | 4.18 ± 1.44 (4.49) | 1.62 ± 0.74 (1.80) |
| left/left | p | 0.831 | 25/25 | 0 | 21 | 1.54 ± 0.43 (1.64) | 15.52 ± 27.18 (5.84) | 1.87 ± 0.59 (2.06) | 4.44 ± 1.38 (4.81) | 1.76 ± 0.73 (1.84) |
| left/right | p | 0.755 | 25/25 | 0 | 19 | 2.47 ± 2.47 (1.96) | 27.83 ± 43.86 (6.49) | 1.81 ± 0.67 (2.07) | 4.32 ± 1.63 (5.07) | 1.69 ± 0.85 (1.80) |
| back/left | p | 0.744 | 25/25 | 0 | 21 | 2.68 ± 1.41 (2.56) | 30.10 ± 56.83 (5.82) | 1.97 ± 0.48 (2.14) | 4.60 ± 1.10 (4.86) | 1.87 ± 0.69 (1.99) |
| back/right | p | 0.701 | 25/25 | 0 | 20 | 2.91 ± 1.71 (2.72) | 34.04 ± 56.51 (7.59) | 1.87 ± 0.80 (2.20) | 4.27 ± 1.83 (4.70) | 1.78 ± 0.88 (2.06) |
| right/left | p | 0.789 | 25/25 | 0 | 20 | 1.79 ± 0.51 (1.78) | 26.09 ± 44.85 (4.75) | 1.78 ± 0.66 (2.00) | 4.21 ± 1.58 (4.80) | 1.63 ± 0.80 (1.76) |
| right/right | p | 0.723 | 23/25 | 0 | 20 | 1.98 ± 1.88 (1.70) | 13.34 ± 21.83 (5.99) | 1.91 ± 0.43 (2.01) | 4.42 ± 1.01 (4.70) | 1.73 ± 0.55 (1.74) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.797 | 20.2 | 4.84 | 1.97 |
| p | normal | 0.736 | 20.5 | 3.94 | 1.51 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.709 | 0.15 | 2.31 ± 0.94 (2.23) | 3.67 | 1.36 |
| p | medium | 16 | 0.814 | 0.59 | 1.27 ± 0.37 (1.39) | 4.12 | 1.65 |
| p | strong | 126 | 0.787 | 0.63 | - | 4.76 | 1.93 |

## Notes

- p: score 0.766, 198/200 kicked, 0 fell; worst sector back (0.722).
