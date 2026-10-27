# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.799** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.95 ± 1.37 (1.68) |
| Direction error [°] | 13.54 ± 23.47 (7.36) |
| Avg ball speed [m/s] | 2.48 ± 0.75 (2.64) |
| Peak ball speed [m/s] | 5.20 ± 1.64 (5.84) |
| Distance [m] | 2.57 ± 1.10 (2.93) |
| Path length [m] | 2.58 ± 1.10 (2.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.839 | 50/50 | 0 | 46 | 1.63 ± 1.82 (1.30) | 7.88 ± 12.53 (4.90) | 2.50 ± 0.67 (2.64) | 5.27 ± 1.49 (5.89) | 2.56 ± 0.99 (2.82) |
| left | p | 0.812 | 50/50 | 0 | 43 | 1.88 ± 1.46 (1.68) | 13.10 ± 19.97 (7.18) | 2.42 ± 0.81 (2.65) | 5.07 ± 1.76 (5.88) | 2.49 ± 1.16 (2.98) |
| back | p | 0.742 | 49/50 | 0 | 39 | 2.56 ± 1.15 (2.52) | 20.81 ± 35.16 (9.78) | 2.58 ± 0.78 (2.84) | 5.38 ± 1.71 (6.25) | 2.75 ± 1.16 (3.27) |
| right | p | 0.802 | 50/50 | 0 | 41 | 1.74 ± 0.45 (1.78) | 12.53 ± 18.46 (7.60) | 2.43 ± 0.72 (2.58) | 5.08 ± 1.58 (5.74) | 2.47 ± 1.05 (2.67) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.794 | 100/100 | 0 | 80 | 1.87 ± 1.16 (1.64) | 15.22 ± 26.12 (7.65) | 2.41 ± 0.84 (2.64) | 5.06 ± 1.82 (5.81) | 2.50 ± 1.15 (2.96) |
| right | p | 0.803 | 99/100 | 0 | 89 | 2.02 ± 1.55 (1.70) | 11.85 ± 20.31 (7.05) | 2.55 ± 0.63 (2.70) | 5.34 ± 1.43 (5.96) | 2.63 ± 1.04 (2.93) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 22 | 1.25 ± 0.31 (1.26) | 8.02 ± 12.06 (4.42) | 2.42 ± 0.70 (2.59) | 5.09 ± 1.52 (5.64) | 2.44 ± 0.97 (2.57) |
| forward/right | p | 0.832 | 25/25 | 0 | 24 | 2.01 ± 2.50 (1.32) | 7.74 ± 12.99 (5.42) | 2.58 ± 0.62 (2.70) | 5.44 ± 1.43 (5.96) | 2.67 ± 0.99 (2.93) |
| left/left | p | 0.807 | 25/25 | 0 | 21 | 2.05 ± 1.99 (1.62) | 10.39 ± 10.35 (7.36) | 2.48 ± 0.89 (2.75) | 5.17 ± 1.90 (6.18) | 2.61 ± 1.19 (3.27) |
| left/right | p | 0.818 | 25/25 | 0 | 22 | 1.70 ± 0.47 (1.80) | 15.81 ± 25.99 (6.99) | 2.36 ± 0.71 (2.35) | 4.97 ± 1.59 (4.52) | 2.38 ± 1.12 (1.89) |
| back/left | p | 0.745 | 25/25 | 0 | 18 | 2.33 ± 0.66 (2.50) | 26.35 ± 40.92 (9.78) | 2.44 ± 0.93 (2.84) | 5.11 ± 2.01 (6.25) | 2.63 ± 1.29 (3.28) |
| back/right | p | 0.739 | 24/25 | 0 | 21 | 2.79 ± 1.46 (2.57) | 15.04 ± 26.73 (9.65) | 2.72 ± 0.56 (2.87) | 5.65 ± 1.28 (6.22) | 2.88 ± 0.98 (3.18) |
| right/left | p | 0.780 | 25/25 | 0 | 19 | 1.86 ± 0.51 (1.90) | 16.12 ± 24.54 (7.62) | 2.31 ± 0.82 (2.56) | 4.86 ± 1.78 (5.72) | 2.34 ± 1.10 (2.61) |
| right/right | p | 0.824 | 25/25 | 0 | 22 | 1.62 ± 0.34 (1.56) | 8.94 ± 7.31 (7.57) | 2.55 ± 0.57 (2.65) | 5.30 ± 1.30 (5.81) | 2.60 ± 0.98 (2.74) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.829 | 13.7 | 5.87 | 3.08 |
| p | normal | 0.769 | 13.4 | 4.53 | 2.06 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.706 | 0.07 | 2.60 ± 1.06 (2.46) | 3.99 | 1.65 |
| p | medium | 20 | 0.861 | 0.70 | 1.28 ± 0.16 (1.28) | 4.12 | 1.70 |
| p | strong | 126 | 0.829 | 0.79 | - | 5.89 | 3.10 |

## Notes

- p: score 0.799, 199/200 kicked, 0 fell; worst sector back (0.742).
