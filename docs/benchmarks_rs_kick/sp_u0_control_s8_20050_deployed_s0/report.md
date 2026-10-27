# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u0_control_s8/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.772** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.93 ± 0.98 (1.82) |
| Direction error [°] | 17.11 ± 34.81 (5.79) |
| Avg ball speed [m/s] | 2.25 ± 0.75 (2.35) |
| Peak ball speed [m/s] | 4.72 ± 1.64 (5.16) |
| Distance [m] | 2.09 ± 1.00 (2.18) |
| Path length [m] | 2.10 ± 1.01 (2.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.782 | 48/50 | 0 | 42 | 1.37 ± 0.32 (1.37) | 9.30 ± 12.57 (5.57) | 2.03 ± 0.73 (2.15) | 4.28 ± 1.66 (4.26) | 1.78 ± 0.93 (1.70) |
| left | p | 0.793 | 48/50 | 0 | 40 | 1.74 ± 0.55 (1.85) | 17.91 ± 33.68 (6.15) | 2.29 ± 0.73 (2.38) | 4.80 ± 1.58 (5.39) | 2.12 ± 0.96 (2.34) |
| back | p | 0.721 | 48/50 | 0 | 41 | 2.61 ± 0.66 (2.76) | 24.81 ± 49.46 (6.57) | 2.45 ± 0.78 (2.62) | 5.09 ± 1.69 (5.78) | 2.41 ± 1.07 (2.75) |
| right | p | 0.792 | 49/50 | 0 | 41 | 2.01 ± 1.47 (1.82) | 16.43 ± 31.48 (3.38) | 2.24 ± 0.69 (2.34) | 4.71 ± 1.53 (4.90) | 2.07 ± 0.94 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 98/100 | 0 | 86 | 1.88 ± 0.69 (1.83) | 15.54 ± 34.68 (5.64) | 2.33 ± 0.67 (2.40) | 4.88 ± 1.48 (5.39) | 2.18 ± 0.95 (2.33) |
| right | p | 0.745 | 95/100 | 0 | 78 | 1.99 ± 1.21 (1.76) | 18.72 ± 34.87 (5.89) | 2.17 ± 0.82 (2.25) | 4.55 ± 1.77 (4.75) | 2.00 ± 1.05 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 23 | 1.36 ± 0.33 (1.30) | 7.47 ± 10.50 (6.14) | 2.18 ± 0.66 (2.26) | 4.63 ± 1.52 (4.57) | 1.97 ± 0.89 (1.95) |
| forward/right | p | 0.727 | 23/25 | 0 | 19 | 1.37 ± 0.31 (1.38) | 11.29 ± 14.22 (5.00) | 1.86 ± 0.77 (2.02) | 3.90 ± 1.72 (4.11) | 1.57 ± 0.94 (1.60) |
| left/left | p | 0.850 | 25/25 | 0 | 22 | 1.68 ± 0.46 (1.78) | 11.86 ± 21.73 (6.19) | 2.40 ± 0.62 (2.41) | 4.99 ± 1.33 (5.34) | 2.24 ± 0.83 (2.39) |
| left/right | p | 0.736 | 23/25 | 0 | 18 | 1.81 ± 0.62 (1.96) | 24.48 ± 42.08 (6.11) | 2.18 ± 0.81 (2.36) | 4.59 ± 1.79 (5.43) | 1.98 ± 1.06 (2.31) |
| back/left | p | 0.695 | 23/25 | 0 | 19 | 2.58 ± 0.75 (2.78) | 26.76 ± 52.69 (7.11) | 2.50 ± 0.71 (2.50) | 5.21 ± 1.55 (5.60) | 2.47 ± 1.11 (2.52) |
| back/right | p | 0.746 | 25/25 | 0 | 22 | 2.64 ± 0.57 (2.74) | 23.01 ± 46.21 (5.93) | 2.40 ± 0.84 (2.69) | 4.98 ± 1.81 (5.85) | 2.35 ± 1.03 (2.83) |
| right/left | p | 0.816 | 25/25 | 0 | 22 | 1.94 ± 0.54 (1.92) | 16.98 ± 37.15 (2.77) | 2.25 ± 0.63 (2.37) | 4.73 ± 1.46 (5.46) | 2.06 ± 0.86 (2.18) |
| right/right | p | 0.769 | 24/25 | 0 | 19 | 2.09 ± 2.03 (1.75) | 15.86 ± 24.17 (3.70) | 2.23 ± 0.74 (2.22) | 4.69 ± 1.59 (4.85) | 2.07 ± 1.01 (1.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.799 | 14.4 | 5.47 | 2.57 |
| p | normal | 0.745 | 19.7 | 4.00 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.707 | 0.18 | 2.28 ± 1.02 (2.11) | 3.61 | 1.37 |
| p | medium | 16 | 0.795 | 0.67 | 1.26 ± 0.25 (1.30) | 4.09 | 1.62 |
| p | strong | 126 | 0.799 | 0.71 | - | 5.32 | 2.49 |

## Notes

- p: score 0.772, 193/200 kicked, 0 fell; worst sector back (0.721).
