# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.809** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.99 ± 1.62 (1.74) |
| Direction error [°] | 18.85 ± 40.27 (5.13) |
| Avg ball speed [m/s] | 2.33 ± 0.80 (2.54) |
| Peak ball speed [m/s] | 4.92 ± 1.76 (5.70) |
| Distance [m] | 2.39 ± 1.15 (2.64) |
| Path length [m] | 2.40 ± 1.15 (2.66) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.809 | 50/50 | 0 | 45 | 1.83 ± 2.18 (1.34) | 7.79 ± 11.73 (4.58) | 2.25 ± 0.75 (2.32) | 4.72 ± 1.69 (4.37) | 2.23 ± 1.07 (1.91) |
| left | p | 0.837 | 50/50 | 0 | 44 | 1.85 ± 1.23 (1.76) | 16.85 ± 35.71 (5.14) | 2.40 ± 0.74 (2.58) | 5.12 ± 1.68 (5.86) | 2.54 ± 1.11 (2.85) |
| back | p | 0.774 | 50/50 | 0 | 38 | 2.42 ± 1.43 (2.37) | 35.22 ± 60.91 (5.43) | 2.33 ± 0.94 (2.68) | 4.89 ± 2.02 (5.78) | 2.44 ± 1.31 (2.92) |
| right | p | 0.815 | 50/50 | 0 | 43 | 1.88 ± 1.41 (1.74) | 15.53 ± 30.96 (5.22) | 2.36 ± 0.74 (2.55) | 4.95 ± 1.60 (5.57) | 2.36 ± 1.04 (2.54) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.832 | 100/100 | 0 | 89 | 1.75 ± 0.59 (1.72) | 16.32 ± 37.00 (5.22) | 2.41 ± 0.71 (2.58) | 5.10 ± 1.59 (5.75) | 2.50 ± 1.09 (2.83) |
| right | p | 0.786 | 100/100 | 0 | 81 | 2.24 ± 2.19 (1.75) | 21.38 ± 43.14 (4.94) | 2.25 ± 0.87 (2.45) | 4.74 ± 1.90 (5.53) | 2.29 ± 1.19 (2.54) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.848 | 25/25 | 0 | 23 | 1.32 ± 0.40 (1.28) | 7.06 ± 12.82 (4.51) | 2.25 ± 0.71 (2.37) | 4.76 ± 1.67 (4.43) | 2.23 ± 1.05 (1.89) |
| forward/right | p | 0.771 | 25/25 | 0 | 22 | 2.35 ± 2.97 (1.34) | 8.52 ± 10.46 (5.09) | 2.25 ± 0.78 (2.29) | 4.68 ± 1.72 (4.32) | 2.22 ± 1.09 (1.92) |
| left/left | p | 0.869 | 25/25 | 0 | 24 | 1.60 ± 0.38 (1.68) | 9.22 ± 15.28 (5.29) | 2.56 ± 0.56 (2.69) | 5.46 ± 1.35 (5.88) | 2.77 ± 0.95 (2.99) |
| left/right | p | 0.806 | 25/25 | 0 | 20 | 2.10 ± 1.66 (1.86) | 24.47 ± 46.91 (4.12) | 2.23 ± 0.85 (2.49) | 4.78 ± 1.90 (5.73) | 2.31 ± 1.21 (2.71) |
| back/left | p | 0.796 | 25/25 | 0 | 20 | 2.29 ± 0.64 (2.44) | 29.89 ± 57.49 (5.15) | 2.47 ± 0.79 (2.63) | 5.20 ± 1.72 (5.75) | 2.61 ± 1.21 (2.99) |
| back/right | p | 0.752 | 25/25 | 0 | 18 | 2.54 ± 1.91 (2.32) | 40.54 ± 63.70 (6.41) | 2.18 ± 1.05 (2.73) | 4.57 ± 2.24 (5.82) | 2.28 ± 1.39 (2.61) |
| right/left | p | 0.816 | 25/25 | 0 | 22 | 1.78 ± 0.45 (1.76) | 19.09 ± 38.02 (5.40) | 2.37 ± 0.70 (2.61) | 4.98 ± 1.53 (5.75) | 2.39 ± 1.04 (2.65) |
| right/right | p | 0.815 | 25/25 | 0 | 21 | 1.98 ± 1.94 (1.70) | 11.98 ± 21.11 (4.30) | 2.34 ± 0.77 (2.53) | 4.91 ± 1.66 (5.54) | 2.34 ± 1.05 (2.53) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.850 | 15.8 | 5.77 | 2.99 |
| p | normal | 0.768 | 21.9 | 4.07 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.727 | 0.14 | 2.33 ± 1.11 (2.28) | 3.59 | 1.46 |
| p | medium | 16 | 0.811 | 0.62 | 1.23 ± 0.38 (1.28) | 3.96 | 1.69 |
| p | strong | 126 | 0.846 | 0.75 | - | 5.65 | 2.91 |

## Notes

- p: score 0.809, 200/200 kicked, 0 fell; worst sector back (0.774).
