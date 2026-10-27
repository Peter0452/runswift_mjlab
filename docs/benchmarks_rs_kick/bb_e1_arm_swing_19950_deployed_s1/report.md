# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-03-35_e1_arm_swing/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 24 |
| Time to kick [s] | 2.00 ± 1.45 (1.70) |
| Direction error [°] | 16.17 ± 30.88 (6.20) |
| Avg ball speed [m/s] | 2.14 ± 0.71 (2.28) |
| Peak ball speed [m/s] | 4.58 ± 1.61 (5.11) |
| Distance [m] | 1.93 ± 0.87 (2.00) |
| Path length [m] | 1.94 ± 0.87 (2.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.808 | 50/50 | 0 | 44 | 1.76 ± 1.96 (1.34) | 9.43 ± 14.60 (4.37) | 2.08 ± 0.74 (2.22) | 4.54 ± 1.67 (4.88) | 1.88 ± 0.85 (1.93) |
| left | p | 0.809 | 50/50 | 0 | 43 | 1.91 ± 1.50 (1.72) | 16.20 ± 29.30 (6.11) | 2.11 ± 0.74 (2.26) | 4.49 ± 1.66 (4.79) | 1.88 ± 0.88 (1.87) |
| back | p | 0.731 | 49/50 | 0 | 41 | 2.62 ± 1.27 (2.60) | 26.09 ± 46.75 (8.45) | 2.24 ± 0.73 (2.38) | 4.77 ± 1.65 (5.35) | 2.10 ± 0.91 (2.23) |
| right | p | 0.785 | 49/50 | 0 | 41 | 1.72 ± 0.39 (1.72) | 13.09 ± 20.49 (6.64) | 2.12 ± 0.62 (2.23) | 4.53 ± 1.42 (4.87) | 1.87 ± 0.80 (1.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.779 | 99/100 | 0 | 84 | 1.97 ± 1.42 (1.66) | 16.70 ± 30.43 (6.21) | 2.09 ± 0.73 (2.29) | 4.52 ± 1.64 (5.16) | 1.88 ± 0.85 (2.07) |
| right | p | 0.787 | 99/100 | 0 | 85 | 2.03 ± 1.48 (1.76) | 15.64 ± 31.32 (6.19) | 2.18 ± 0.69 (2.28) | 4.65 ± 1.58 (4.95) | 1.98 ± 0.87 (1.99) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.803 | 25/25 | 0 | 21 | 1.45 ± 0.80 (1.30) | 11.27 ± 17.29 (3.88) | 1.94 ± 0.81 (2.20) | 4.30 ± 1.84 (4.84) | 1.74 ± 0.89 (1.77) |
| forward/right | p | 0.812 | 25/25 | 0 | 23 | 2.07 ± 2.63 (1.44) | 7.59 ± 10.99 (4.77) | 2.22 ± 0.62 (2.29) | 4.79 ± 1.44 (4.95) | 2.03 ± 0.78 (2.04) |
| left/left | p | 0.826 | 25/25 | 0 | 23 | 2.09 ± 2.05 (1.66) | 8.77 ± 12.67 (5.69) | 2.28 ± 0.65 (2.44) | 4.85 ± 1.46 (5.55) | 2.09 ± 0.76 (2.43) |
| left/right | p | 0.792 | 25/25 | 0 | 20 | 1.73 ± 0.49 (1.78) | 23.63 ± 38.03 (6.35) | 1.93 ± 0.78 (2.21) | 4.14 ± 1.77 (4.25) | 1.67 ± 0.93 (1.68) |
| back/left | p | 0.736 | 25/25 | 0 | 20 | 2.53 ± 1.55 (2.44) | 31.65 ± 48.64 (8.50) | 2.11 ± 0.79 (2.32) | 4.53 ± 1.75 (5.27) | 1.94 ± 0.95 (2.15) |
| back/right | p | 0.725 | 24/25 | 0 | 21 | 2.71 ± 0.87 (2.61) | 20.30 ± 43.96 (7.40) | 2.38 ± 0.64 (2.53) | 5.02 ± 1.51 (5.69) | 2.26 ± 0.84 (2.41) |
| right/left | p | 0.752 | 24/25 | 0 | 20 | 1.81 ± 0.39 (1.92) | 15.06 ± 23.34 (6.55) | 2.04 ± 0.59 (2.23) | 4.38 ± 1.39 (4.68) | 1.75 ± 0.74 (1.81) |
| right/right | p | 0.817 | 25/25 | 0 | 21 | 1.63 ± 0.38 (1.58) | 11.21 ± 17.12 (6.64) | 2.20 ± 0.64 (2.28) | 4.68 ± 1.43 (4.87) | 1.99 ± 0.83 (1.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.810 | 17.2 | 5.01 | 2.19 |
| p | normal | 0.756 | 15.1 | 4.15 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.702 | 0.11 | 2.38 ± 1.05 (2.35) | 3.70 | 1.40 |
| p | medium | 20 | 0.856 | 0.69 | 1.26 ± 0.24 (1.27) | 4.04 | 1.58 |
| p | strong | 126 | 0.806 | 0.67 | - | 5.05 | 2.21 |

## Notes

- p: score 0.783, 198/200 kicked, 0 fell; worst sector back (0.731).
