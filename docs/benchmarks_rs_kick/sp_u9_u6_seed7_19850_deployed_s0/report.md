# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u9_u6_seed7/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.772** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 1.97 ± 1.51 (1.68) |
| Direction error [°] | 18.34 ± 35.90 (5.83) |
| Avg ball speed [m/s] | 2.01 ± 0.66 (2.18) |
| Peak ball speed [m/s] | 4.41 ± 1.57 (5.04) |
| Distance [m] | 1.72 ± 0.81 (1.83) |
| Path length [m] | 1.73 ± 0.81 (1.84) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.776 | 50/50 | 0 | 40 | 1.91 ± 2.29 (1.32) | 10.48 ± 13.10 (5.96) | 1.93 ± 0.74 (2.08) | 4.21 ± 1.74 (4.15) | 1.63 ± 0.89 (1.60) |
| left | p | 0.792 | 49/50 | 0 | 41 | 1.79 ± 1.16 (1.68) | 20.85 ± 36.41 (5.93) | 1.99 ± 0.65 (2.25) | 4.42 ± 1.57 (5.14) | 1.71 ± 0.77 (1.98) |
| back | p | 0.728 | 47/50 | 0 | 41 | 2.38 ± 0.59 (2.44) | 25.20 ± 50.50 (6.57) | 2.10 ± 0.59 (2.24) | 4.62 ± 1.38 (5.09) | 1.85 ± 0.76 (1.98) |
| right | p | 0.791 | 49/50 | 0 | 41 | 1.82 ± 1.37 (1.70) | 17.27 ± 32.63 (4.15) | 2.01 ± 0.63 (2.23) | 4.41 ± 1.53 (5.04) | 1.70 ± 0.79 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 99/100 | 0 | 86 | 1.81 ± 1.10 (1.66) | 17.00 ± 35.28 (5.92) | 2.06 ± 0.59 (2.23) | 4.53 ± 1.44 (5.08) | 1.77 ± 0.76 (1.89) |
| right | p | 0.741 | 96/100 | 0 | 77 | 2.13 ± 1.83 (1.72) | 19.73 ± 36.47 (5.81) | 1.95 ± 0.71 (2.13) | 4.29 ± 1.69 (4.52) | 1.67 ± 0.85 (1.70) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.812 | 25/25 | 0 | 22 | 1.66 ± 1.90 (1.30) | 8.40 ± 11.85 (3.89) | 2.08 ± 0.63 (2.20) | 4.56 ± 1.53 (4.40) | 1.79 ± 0.78 (1.84) |
| forward/right | p | 0.740 | 25/25 | 0 | 18 | 2.16 ± 2.59 (1.32) | 12.56 ± 13.94 (6.82) | 1.79 ± 0.81 (1.90) | 3.85 ± 1.86 (3.80) | 1.46 ± 0.96 (1.46) |
| left/left | p | 0.843 | 25/25 | 0 | 23 | 1.55 ± 0.39 (1.64) | 12.26 ± 21.07 (6.41) | 2.11 ± 0.49 (2.27) | 4.64 ± 1.19 (5.14) | 1.83 ± 0.64 (2.01) |
| left/right | p | 0.741 | 24/25 | 0 | 18 | 2.03 ± 1.58 (1.87) | 29.80 ± 45.69 (5.71) | 1.87 ± 0.76 (2.22) | 4.19 ± 1.87 (5.19) | 1.59 ± 0.86 (1.90) |
| back/left | p | 0.747 | 24/25 | 0 | 21 | 2.33 ± 0.66 (2.43) | 25.66 ± 51.40 (7.27) | 2.14 ± 0.46 (2.34) | 4.70 ± 1.16 (5.18) | 1.87 ± 0.71 (2.04) |
| back/right | p | 0.709 | 23/25 | 0 | 20 | 2.43 ± 0.49 (2.48) | 24.72 ± 49.54 (6.39) | 2.07 ± 0.69 (2.16) | 4.53 ± 1.57 (5.09) | 1.84 ± 0.80 (1.73) |
| right/left | p | 0.808 | 25/25 | 0 | 20 | 1.71 ± 0.47 (1.78) | 22.01 ± 40.17 (4.11) | 1.93 ± 0.72 (2.21) | 4.22 ± 1.73 (4.43) | 1.60 ± 0.87 (1.82) |
| right/right | p | 0.774 | 24/25 | 0 | 21 | 1.94 ± 1.90 (1.64) | 12.34 ± 21.11 (4.59) | 2.10 ± 0.50 (2.26) | 4.60 ± 1.26 (5.16) | 1.80 ± 0.68 (1.91) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.791 | 15.4 | 5.10 | 2.09 |
| p | normal | 0.752 | 21.2 | 3.76 | 1.37 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.712 | 0.18 | 2.18 ± 0.95 (2.11) | 3.44 | 1.20 |
| p | medium | 16 | 0.826 | 0.70 | 1.16 ± 0.34 (1.27) | 3.74 | 1.41 |
| p | strong | 126 | 0.793 | 0.66 | - | 4.96 | 2.01 |

## Notes

- p: score 0.772, 195/200 kicked, 0 fell; worst sector back (0.728).
