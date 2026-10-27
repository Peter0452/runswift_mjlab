# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.03 ± 1.45 (1.78) |
| Direction error [°] | 16.40 ± 34.88 (5.66) |
| Avg ball speed [m/s] | 1.99 ± 0.59 (2.16) |
| Peak ball speed [m/s] | 4.47 ± 1.50 (5.11) |
| Distance [m] | 1.76 ± 0.79 (1.89) |
| Path length [m] | 1.77 ± 0.79 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.786 | 49/50 | 0 | 41 | 1.78 ± 1.89 (1.36) | 8.76 ± 11.04 (5.35) | 1.86 ± 0.63 (2.01) | 4.15 ± 1.60 (4.03) | 1.56 ± 0.80 (1.54) |
| left | p | 0.798 | 48/50 | 0 | 41 | 1.71 ± 0.50 (1.78) | 16.81 ± 32.18 (4.86) | 1.99 ± 0.59 (2.21) | 4.54 ± 1.50 (5.25) | 1.78 ± 0.78 (2.01) |
| back | p | 0.728 | 48/50 | 0 | 41 | 2.52 ± 0.66 (2.62) | 25.30 ± 51.05 (6.50) | 2.12 ± 0.61 (2.30) | 4.72 ± 1.51 (5.28) | 1.95 ± 0.83 (2.20) |
| right | p | 0.811 | 50/50 | 0 | 44 | 2.12 ± 1.91 (1.79) | 14.93 ± 31.52 (4.99) | 2.00 ± 0.52 (2.12) | 4.47 ± 1.33 (4.94) | 1.74 ± 0.70 (1.89) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 99/100 | 0 | 88 | 1.91 ± 1.08 (1.78) | 15.55 ± 35.22 (5.33) | 2.03 ± 0.55 (2.17) | 4.56 ± 1.40 (5.16) | 1.79 ± 0.74 (1.89) |
| right | p | 0.753 | 96/100 | 0 | 79 | 2.16 ± 1.74 (1.79) | 17.27 ± 34.50 (5.83) | 1.95 ± 0.64 (2.12) | 4.38 ± 1.59 (5.04) | 1.72 ± 0.84 (1.84) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.815 | 25/25 | 0 | 22 | 1.69 ± 1.81 (1.34) | 8.20 ± 10.81 (5.42) | 1.93 ± 0.60 (2.05) | 4.33 ± 1.52 (4.07) | 1.63 ± 0.74 (1.68) |
| forward/right | p | 0.757 | 24/25 | 0 | 19 | 1.87 ± 1.97 (1.40) | 9.35 ± 11.24 (4.81) | 1.79 ± 0.65 (1.93) | 3.97 ± 1.66 (3.72) | 1.49 ± 0.85 (1.36) |
| left/left | p | 0.857 | 25/25 | 0 | 23 | 1.65 ± 0.43 (1.74) | 11.33 ± 22.86 (4.65) | 2.07 ± 0.53 (2.25) | 4.68 ± 1.35 (5.29) | 1.87 ± 0.68 (2.03) |
| left/right | p | 0.738 | 23/25 | 0 | 18 | 1.78 ± 0.56 (1.86) | 22.76 ± 39.05 (5.08) | 1.91 ± 0.64 (2.14) | 4.38 ± 1.64 (5.05) | 1.69 ± 0.86 (1.89) |
| back/left | p | 0.743 | 24/25 | 0 | 21 | 2.48 ± 0.72 (2.62) | 24.47 ± 51.69 (6.06) | 2.14 ± 0.51 (2.28) | 4.83 ± 1.31 (5.28) | 1.97 ± 0.79 (2.20) |
| back/right | p | 0.713 | 24/25 | 0 | 20 | 2.57 ± 0.59 (2.63) | 26.13 ± 50.39 (8.17) | 2.09 ± 0.70 (2.30) | 4.61 ± 1.67 (5.27) | 1.94 ± 0.86 (2.19) |
| right/left | p | 0.817 | 25/25 | 0 | 22 | 1.86 ± 0.48 (1.84) | 18.54 ± 39.37 (4.75) | 1.97 ± 0.53 (2.11) | 4.41 ± 1.36 (4.75) | 1.70 ± 0.69 (1.89) |
| right/right | p | 0.806 | 25/25 | 0 | 22 | 2.38 ± 2.63 (1.68) | 11.32 ± 20.26 (5.66) | 2.03 ± 0.50 (2.16) | 4.54 ± 1.29 (5.19) | 1.77 ± 0.71 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.798 | 14.4 | 5.18 | 2.13 |
| p | normal | 0.763 | 18.3 | 3.78 | 1.39 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.732 | 0.21 | 2.14 ± 0.87 (1.95) | 3.39 | 1.17 |
| p | medium | 16 | 0.820 | 0.76 | 1.19 ± 0.20 (1.21) | 3.86 | 1.44 |
| p | strong | 126 | 0.798 | 0.67 | - | 5.06 | 2.08 |

## Notes

- p: score 0.781, 195/200 kicked, 0 fell; worst sector back (0.728).
