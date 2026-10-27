# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_21450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.809** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 179 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.95 ± 1.10 (1.74) |
| Direction error [°] | 12.79 ± 26.88 (5.42) |
| Avg ball speed [m/s] | 2.28 ± 0.66 (2.50) |
| Peak ball speed [m/s] | 4.89 ± 1.54 (5.70) |
| Distance [m] | 2.18 ± 0.92 (2.53) |
| Path length [m] | 2.19 ± 0.92 (2.55) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.821 | 50/50 | 0 | 46 | 1.55 ± 1.27 (1.34) | 8.32 ± 11.37 (5.02) | 2.17 ± 0.70 (2.42) | 4.72 ± 1.63 (5.60) | 2.05 ± 0.91 (2.36) |
| left | p | 0.843 | 50/50 | 0 | 45 | 1.75 ± 0.51 (1.71) | 12.20 ± 26.82 (4.76) | 2.25 ± 0.62 (2.50) | 4.83 ± 1.46 (5.60) | 2.15 ± 0.89 (2.45) |
| back | p | 0.759 | 50/50 | 0 | 43 | 2.75 ± 1.39 (2.55) | 21.45 ± 40.84 (7.62) | 2.37 ± 0.74 (2.65) | 5.05 ± 1.67 (5.90) | 2.34 ± 0.99 (2.75) |
| right | p | 0.814 | 49/50 | 0 | 45 | 1.74 ± 0.38 (1.82) | 9.09 ± 15.98 (4.68) | 2.32 ± 0.54 (2.49) | 4.94 ± 1.34 (5.63) | 2.20 ± 0.85 (2.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 99/100 | 0 | 91 | 1.88 ± 0.78 (1.68) | 11.01 ± 22.50 (4.93) | 2.30 ± 0.64 (2.50) | 4.95 ± 1.50 (5.70) | 2.22 ± 0.89 (2.54) |
| right | p | 0.806 | 100/100 | 0 | 88 | 2.02 ± 1.34 (1.76) | 14.54 ± 30.50 (5.51) | 2.25 ± 0.67 (2.43) | 4.82 ± 1.57 (5.68) | 2.15 ± 0.94 (2.47) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.840 | 25/25 | 0 | 24 | 1.36 ± 0.51 (1.34) | 6.79 ± 8.32 (4.39) | 2.19 ± 0.63 (2.46) | 4.80 ± 1.49 (5.51) | 2.08 ± 0.85 (2.40) |
| forward/right | p | 0.801 | 25/25 | 0 | 22 | 1.75 ± 1.70 (1.40) | 9.86 ± 13.58 (5.16) | 2.14 ± 0.77 (2.41) | 4.64 ± 1.76 (5.73) | 2.01 ± 0.96 (2.32) |
| left/left | p | 0.847 | 25/25 | 0 | 23 | 1.75 ± 0.53 (1.60) | 6.97 ± 7.46 (5.15) | 2.32 ± 0.62 (2.54) | 5.00 ± 1.43 (5.77) | 2.26 ± 0.84 (2.64) |
| left/right | p | 0.838 | 25/25 | 0 | 22 | 1.75 ± 0.48 (1.78) | 17.43 ± 36.45 (4.47) | 2.18 ± 0.60 (2.22) | 4.66 ± 1.46 (4.40) | 2.03 ± 0.93 (1.86) |
| back/left | p | 0.774 | 25/25 | 0 | 22 | 2.55 ± 0.99 (2.54) | 18.98 ± 36.59 (7.43) | 2.39 ± 0.72 (2.64) | 5.10 ± 1.63 (5.90) | 2.36 ± 0.99 (2.64) |
| back/right | p | 0.743 | 25/25 | 0 | 21 | 2.94 ± 1.68 (2.56) | 23.92 ± 44.55 (8.72) | 2.35 ± 0.76 (2.68) | 5.00 ± 1.71 (5.96) | 2.32 ± 1.00 (2.78) |
| right/left | p | 0.785 | 24/25 | 0 | 22 | 1.84 ± 0.39 (1.91) | 11.31 ± 21.49 (4.05) | 2.29 ± 0.59 (2.47) | 4.90 ± 1.44 (5.62) | 2.16 ± 0.86 (2.33) |
| right/right | p | 0.842 | 25/25 | 0 | 23 | 1.64 ± 0.34 (1.60) | 6.96 ± 6.91 (4.92) | 2.35 ± 0.49 (2.51) | 4.99 ± 1.23 (5.73) | 2.24 ± 0.83 (2.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.837 | 13.7 | 5.51 | 2.60 |
| p | normal | 0.781 | 11.8 | 4.26 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.729 | 0.11 | 2.50 ± 0.93 (2.40) | 3.85 | 1.47 |
| p | medium | 20 | 0.882 | 0.73 | 1.25 ± 0.17 (1.27) | 4.01 | 1.56 |
| p | strong | 126 | 0.832 | 0.73 | - | 5.46 | 2.58 |

## Notes

- p: score 0.809, 199/200 kicked, 0 fell; worst sector back (0.759).
