# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_02-42-52_q4_overrun_linear_noanchor/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.833** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.79 ± 0.57 (1.62) |
| Direction error [°] | 9.89 ± 11.70 (9.21) |
| Avg ball speed [m/s] | 2.64 ± 0.78 (2.95) |
| Peak ball speed [m/s] | 5.54 ± 1.72 (6.47) |
| Distance [m] | 2.83 ± 1.27 (3.41) |
| Path length [m] | 2.84 ± 1.27 (3.42) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.868 | 50/50 | 0 | 48 | 1.23 ± 0.25 (1.28) | 6.33 ± 4.07 (5.65) | 2.55 ± 0.60 (2.76) | 5.42 ± 1.40 (5.93) | 2.63 ± 1.04 (2.87) |
| left | p | 0.844 | 50/50 | 0 | 42 | 1.71 ± 0.37 (1.61) | 9.85 ± 5.49 (9.98) | 2.64 ± 0.80 (3.02) | 5.51 ± 1.75 (6.63) | 2.83 ± 1.29 (3.57) |
| back | p | 0.792 | 50/50 | 0 | 37 | 2.50 ± 0.36 (2.50) | 13.46 ± 20.76 (11.38) | 2.79 ± 0.94 (3.27) | 5.80 ± 2.03 (6.87) | 3.15 ± 1.40 (3.92) |
| right | p | 0.825 | 50/50 | 0 | 39 | 1.70 ± 0.36 (1.62) | 9.89 ± 6.67 (9.94) | 2.59 ± 0.71 (2.95) | 5.40 ± 1.60 (6.50) | 2.72 ± 1.24 (3.52) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.835 | 100/100 | 0 | 85 | 1.79 ± 0.57 (1.62) | 8.82 ± 5.51 (9.06) | 2.68 ± 0.69 (2.94) | 5.63 ± 1.56 (6.44) | 2.87 ± 1.20 (3.34) |
| right | p | 0.830 | 100/100 | 0 | 81 | 1.79 ± 0.57 (1.63) | 10.95 ± 15.53 (9.66) | 2.60 ± 0.85 (2.98) | 5.44 ± 1.86 (6.52) | 2.79 ± 1.33 (3.55) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 24 | 1.21 ± 0.26 (1.28) | 6.23 ± 3.75 (5.69) | 2.49 ± 0.56 (2.67) | 5.31 ± 1.37 (5.90) | 2.54 ± 1.00 (2.76) |
| forward/right | p | 0.874 | 25/25 | 0 | 24 | 1.26 ± 0.24 (1.30) | 6.44 ± 4.36 (5.60) | 2.60 ± 0.63 (2.78) | 5.53 ± 1.43 (6.29) | 2.73 ± 1.07 (3.14) |
| left/left | p | 0.844 | 25/25 | 0 | 21 | 1.65 ± 0.35 (1.58) | 10.29 ± 5.55 (10.96) | 2.74 ± 0.75 (3.12) | 5.74 ± 1.65 (6.69) | 2.99 ± 1.26 (3.74) |
| left/right | p | 0.844 | 25/25 | 0 | 21 | 1.78 ± 0.38 (1.78) | 9.41 ± 5.40 (9.20) | 2.55 ± 0.84 (2.91) | 5.29 ± 1.83 (6.30) | 2.66 ± 1.30 (3.26) |
| back/left | p | 0.806 | 25/25 | 0 | 20 | 2.52 ± 0.30 (2.50) | 9.84 ± 5.38 (11.50) | 2.91 ± 0.68 (3.30) | 6.04 ± 1.53 (6.85) | 3.24 ± 1.20 (3.91) |
| back/right | p | 0.779 | 25/25 | 0 | 17 | 2.49 ± 0.41 (2.50) | 17.09 ± 28.41 (11.36) | 2.67 ± 1.13 (3.25) | 5.57 ± 2.41 (6.90) | 3.06 ± 1.57 (3.94) |
| right/left | p | 0.826 | 25/25 | 0 | 20 | 1.79 ± 0.35 (1.78) | 8.93 ± 6.14 (9.05) | 2.60 ± 0.69 (2.94) | 5.43 ± 1.59 (6.40) | 2.71 ± 1.20 (3.38) |
| right/right | p | 0.825 | 25/25 | 0 | 19 | 1.62 ± 0.35 (1.56) | 10.86 ± 7.03 (11.37) | 2.58 ± 0.73 (3.06) | 5.37 ± 1.62 (6.56) | 2.73 ± 1.27 (3.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.852 | 11.5 | 6.77 | 3.74 |
| p | normal | 0.813 | 8.3 | 4.31 | 1.92 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.768 | 0.17 | 2.22 ± 0.82 (2.04) | 3.45 | 1.27 |
| p | medium | 20 | 0.872 | 0.73 | 1.05 ± 0.36 (1.16) | 3.35 | 1.25 |
| p | strong | 126 | 0.854 | 0.90 | - | 6.78 | 3.75 |

## Notes

- p: score 0.833, 200/200 kicked, 0 fell; worst sector back (0.792).
