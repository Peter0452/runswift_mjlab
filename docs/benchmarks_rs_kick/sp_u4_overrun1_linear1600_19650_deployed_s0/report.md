# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 1.87 ± 0.89 (1.78) |
| Direction error [°] | 17.03 ± 35.17 (4.63) |
| Avg ball speed [m/s] | 2.09 ± 0.69 (2.29) |
| Peak ball speed [m/s] | 4.51 ± 1.61 (5.24) |
| Distance [m] | 1.88 ± 0.90 (2.03) |
| Path length [m] | 1.89 ± 0.90 (2.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.792 | 49/50 | 0 | 40 | 1.57 ± 1.31 (1.40) | 10.39 ± 16.81 (4.20) | 1.87 ± 0.76 (1.89) | 4.05 ± 1.77 (3.76) | 1.59 ± 0.90 (1.40) |
| left | p | 0.799 | 48/50 | 0 | 40 | 1.70 ± 0.47 (1.81) | 18.45 ± 35.30 (3.91) | 2.12 ± 0.62 (2.32) | 4.63 ± 1.49 (5.36) | 1.91 ± 0.84 (2.09) |
| back | p | 0.738 | 48/50 | 0 | 39 | 2.49 ± 0.66 (2.56) | 23.72 ± 48.39 (6.57) | 2.25 ± 0.69 (2.46) | 4.78 ± 1.59 (5.61) | 2.11 ± 0.94 (2.43) |
| right | p | 0.792 | 48/50 | 0 | 42 | 1.75 ± 0.47 (1.78) | 15.70 ± 31.69 (4.15) | 2.13 ± 0.61 (2.38) | 4.59 ± 1.47 (5.51) | 1.91 ± 0.81 (2.14) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.819 | 99/100 | 0 | 86 | 1.82 ± 0.63 (1.78) | 15.28 ± 35.14 (3.78) | 2.18 ± 0.60 (2.33) | 4.69 ± 1.44 (5.39) | 1.98 ± 0.84 (2.22) |
| right | p | 0.742 | 94/100 | 0 | 75 | 1.93 ± 1.09 (1.78) | 18.88 ± 35.11 (5.36) | 1.99 ± 0.75 (2.15) | 4.32 ± 1.76 (4.80) | 1.77 ± 0.94 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.856 | 25/25 | 0 | 23 | 1.38 ± 0.32 (1.40) | 5.73 ± 9.66 (3.08) | 2.08 ± 0.66 (2.21) | 4.51 ± 1.61 (4.42) | 1.85 ± 0.86 (1.85) |
| forward/right | p | 0.728 | 24/25 | 0 | 17 | 1.76 ± 1.82 (1.40) | 15.25 ± 20.81 (7.18) | 1.65 ± 0.79 (1.83) | 3.58 ± 1.81 (3.68) | 1.33 ± 0.87 (1.35) |
| left/left | p | 0.855 | 25/25 | 0 | 22 | 1.64 ± 0.40 (1.78) | 11.79 ± 21.84 (4.79) | 2.21 ± 0.54 (2.31) | 4.81 ± 1.30 (5.36) | 2.03 ± 0.76 (2.27) |
| left/right | p | 0.744 | 23/25 | 0 | 18 | 1.76 ± 0.53 (1.92) | 25.69 ± 44.51 (3.54) | 2.03 ± 0.68 (2.35) | 4.43 ± 1.66 (5.29) | 1.79 ± 0.91 (1.99) |
| back/left | p | 0.757 | 24/25 | 0 | 19 | 2.42 ± 0.71 (2.46) | 24.32 ± 51.85 (4.00) | 2.33 ± 0.60 (2.53) | 4.90 ± 1.39 (5.77) | 2.18 ± 0.93 (2.55) |
| back/right | p | 0.720 | 24/25 | 0 | 20 | 2.55 ± 0.60 (2.63) | 23.12 ± 44.65 (7.07) | 2.17 ± 0.76 (2.43) | 4.66 ± 1.76 (5.58) | 2.04 ± 0.95 (2.36) |
| right/left | p | 0.809 | 25/25 | 0 | 22 | 1.86 ± 0.47 (1.92) | 19.62 ± 39.21 (5.16) | 2.12 ± 0.57 (2.27) | 4.56 ± 1.40 (5.24) | 1.87 ± 0.76 (2.11) |
| right/right | p | 0.775 | 23/25 | 0 | 20 | 1.62 ± 0.44 (1.72) | 11.43 ± 19.76 (2.70) | 2.13 ± 0.65 (2.44) | 4.62 ± 1.55 (5.60) | 1.95 ± 0.86 (2.21) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.806 | 16.2 | 5.23 | 2.29 |
| p | normal | 0.754 | 17.8 | 3.80 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.717 | 0.21 | 2.14 ± 0.91 (2.03) | 3.39 | 1.22 |
| p | medium | 16 | 0.818 | 0.73 | 1.20 ± 0.23 (1.19) | 3.89 | 1.51 |
| p | strong | 126 | 0.805 | 0.68 | - | 5.10 | 2.23 |

## Notes

- p: score 0.780, 193/200 kicked, 0 fell; worst sector back (0.738).
