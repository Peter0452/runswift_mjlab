# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.57 (1.51) |
| Direction error [°] | 5.45 ± 13.37 (3.49) |
| Avg ball speed [m/s] | 1.70 ± 0.27 (1.74) |
| Peak ball speed [m/s] | 4.52 ± 0.70 (4.68) |
| Distance [m] | 1.78 ± 0.44 (1.79) |
| Path length [m] | 1.78 ± 0.44 (1.80) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.821 | 50/50 | 0 | 46 | 1.19 ± 0.62 (1.07) | 10.16 ± 25.80 (3.83) | 1.57 ± 0.30 (1.53) | 4.13 ± 0.74 (3.81) | 1.53 ± 0.47 (1.45) |
| left | p | 0.877 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.52) | 4.33 ± 2.45 (4.10) | 1.76 ± 0.25 (1.81) | 4.74 ± 0.68 (5.02) | 1.91 ± 0.43 (1.92) |
| back | p | 0.857 | 50/50 | 0 | 50 | 2.25 ± 0.27 (2.19) | 3.29 ± 2.60 (2.55) | 1.76 ± 0.24 (1.81) | 4.75 ± 0.57 (4.91) | 1.95 ± 0.38 (1.91) |
| right | p | 0.851 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.46) | 4.02 ± 2.49 (3.52) | 1.69 ± 0.23 (1.71) | 4.47 ± 0.63 (4.46) | 1.73 ± 0.36 (1.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 97 | 1.65 ± 0.61 (1.54) | 6.88 ± 18.55 (3.45) | 1.69 ± 0.24 (1.75) | 4.53 ± 0.65 (4.69) | 1.77 ± 0.42 (1.79) |
| right | p | 0.857 | 100/100 | 0 | 99 | 1.57 ± 0.52 (1.46) | 4.02 ± 2.99 (3.63) | 1.70 ± 0.29 (1.73) | 4.52 ± 0.76 (4.67) | 1.79 ± 0.47 (1.80) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.801 | 25/25 | 0 | 22 | 1.34 ± 0.82 (1.14) | 15.68 ± 35.43 (5.09) | 1.56 ± 0.25 (1.52) | 4.15 ± 0.63 (3.82) | 1.51 ± 0.41 (1.41) |
| forward/right | p | 0.840 | 25/25 | 0 | 24 | 1.03 ± 0.22 (1.04) | 4.63 ± 3.83 (3.79) | 1.59 ± 0.33 (1.55) | 4.12 ± 0.84 (3.80) | 1.55 ± 0.51 (1.54) |
| left/left | p | 0.874 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.50) | 4.31 ± 2.24 (3.68) | 1.71 ± 0.23 (1.78) | 4.63 ± 0.66 (4.78) | 1.83 ± 0.41 (1.90) |
| left/right | p | 0.881 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.58) | 4.35 ± 2.64 (4.22) | 1.82 ± 0.27 (1.86) | 4.85 ± 0.67 (5.14) | 1.98 ± 0.44 (2.05) |
| back/left | p | 0.859 | 25/25 | 0 | 25 | 2.26 ± 0.27 (2.20) | 3.02 ± 2.20 (2.67) | 1.81 ± 0.22 (1.88) | 4.82 ± 0.50 (4.93) | 1.98 ± 0.35 (1.95) |
| back/right | p | 0.856 | 25/25 | 0 | 25 | 2.23 ± 0.26 (2.18) | 3.56 ± 2.92 (2.42) | 1.71 ± 0.25 (1.81) | 4.67 ± 0.63 (4.89) | 1.92 ± 0.40 (1.88) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.59 ± 0.32 (1.58) | 4.49 ± 2.68 (3.66) | 1.70 ± 0.21 (1.75) | 4.52 ± 0.60 (4.59) | 1.75 ± 0.34 (1.80) |
| right/right | p | 0.853 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.42) | 3.55 ± 2.19 (3.20) | 1.67 ± 0.25 (1.63) | 4.43 ± 0.65 (4.38) | 1.71 ± 0.38 (1.68) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.879 | 4.7 | 4.90 | 1.98 |
| p | normal | 0.824 | 6.2 | 4.15 | 1.58 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.764 | 0.10 | 2.37 ± 0.70 (2.14) | 3.78 | 1.37 |
| p | medium | 16 | 0.930 | 0.81 | 1.18 ± 0.14 (1.17) | 3.85 | 1.49 |
| p | strong | 126 | 0.882 | 0.66 | - | 4.95 | 2.00 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector forward (0.821).
