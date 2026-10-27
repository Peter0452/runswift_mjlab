# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_16-13-42_u14_u6_overpower600/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 1.98 ± 1.50 (1.74) |
| Direction error [°] | 18.31 ± 37.07 (4.93) |
| Avg ball speed [m/s] | 2.08 ± 0.66 (2.26) |
| Peak ball speed [m/s] | 4.50 ± 1.55 (5.09) |
| Distance [m] | 1.87 ± 0.86 (1.97) |
| Path length [m] | 1.88 ± 0.86 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.792 | 49/50 | 0 | 43 | 1.65 ± 1.75 (1.34) | 7.81 ± 9.89 (4.06) | 2.04 ± 0.61 (2.11) | 4.38 ± 1.42 (4.19) | 1.77 ± 0.78 (1.74) |
| left | p | 0.805 | 48/50 | 0 | 42 | 1.69 ± 0.48 (1.79) | 16.46 ± 33.49 (4.33) | 2.15 ± 0.57 (2.34) | 4.73 ± 1.39 (5.39) | 1.96 ± 0.78 (2.05) |
| back | p | 0.744 | 50/50 | 0 | 40 | 2.69 ± 1.65 (2.44) | 30.18 ± 53.49 (6.21) | 2.04 ± 0.74 (2.26) | 4.41 ± 1.72 (5.13) | 1.86 ± 0.91 (2.04) |
| right | p | 0.788 | 49/50 | 0 | 40 | 1.87 ± 1.50 (1.74) | 18.50 ± 33.50 (4.66) | 2.09 ± 0.71 (2.33) | 4.48 ± 1.63 (5.25) | 1.88 ± 0.92 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.816 | 100/100 | 0 | 87 | 1.93 ± 1.34 (1.75) | 16.77 ± 36.72 (4.65) | 2.18 ± 0.58 (2.34) | 4.69 ± 1.39 (5.29) | 1.97 ± 0.81 (2.07) |
| right | p | 0.749 | 96/100 | 0 | 78 | 2.03 ± 1.65 (1.74) | 19.91 ± 37.36 (5.50) | 1.98 ± 0.72 (2.19) | 4.29 ± 1.69 (4.74) | 1.76 ± 0.89 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 23 | 1.67 ± 1.85 (1.30) | 6.61 ± 10.45 (3.34) | 2.21 ± 0.44 (2.20) | 4.75 ± 1.12 (4.98) | 1.99 ± 0.67 (1.88) |
| forward/right | p | 0.753 | 24/25 | 0 | 20 | 1.64 ± 1.63 (1.35) | 9.07 ± 9.10 (5.92) | 1.86 ± 0.70 (1.88) | 3.99 ± 1.60 (3.89) | 1.55 ± 0.83 (1.50) |
| left/left | p | 0.873 | 25/25 | 0 | 24 | 1.64 ± 0.39 (1.78) | 7.80 ± 15.25 (4.44) | 2.27 ± 0.43 (2.38) | 4.98 ± 1.10 (5.42) | 2.11 ± 0.63 (2.25) |
| left/right | p | 0.737 | 23/25 | 0 | 18 | 1.74 ± 0.56 (1.92) | 25.87 ± 43.80 (4.18) | 2.03 ± 0.67 (2.25) | 4.46 ± 1.61 (5.10) | 1.79 ± 0.89 (1.93) |
| back/left | p | 0.755 | 25/25 | 0 | 20 | 2.68 ± 1.61 (2.44) | 29.21 ± 54.41 (6.09) | 2.15 ± 0.63 (2.32) | 4.63 ± 1.47 (5.28) | 1.94 ± 0.87 (2.07) |
| back/right | p | 0.732 | 25/25 | 0 | 20 | 2.70 ± 1.68 (2.44) | 31.15 ± 52.55 (7.32) | 1.94 ± 0.83 (2.25) | 4.20 ± 1.91 (5.10) | 1.78 ± 0.95 (1.97) |
| right/left | p | 0.804 | 25/25 | 0 | 20 | 1.74 ± 0.49 (1.80) | 23.45 ± 41.33 (3.75) | 2.07 ± 0.76 (2.30) | 4.43 ± 1.72 (4.56) | 1.85 ± 0.98 (2.02) |
| right/right | p | 0.773 | 24/25 | 0 | 20 | 2.01 ± 2.07 (1.68) | 13.35 ± 21.45 (4.85) | 2.11 ± 0.66 (2.40) | 4.54 ± 1.54 (5.26) | 1.91 ± 0.86 (2.06) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 17.6 | 5.12 | 2.22 |
| p | normal | 0.760 | 19.0 | 3.90 | 1.52 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.728 | 0.18 | 2.24 ± 0.99 (2.08) | 3.53 | 1.31 |
| p | medium | 16 | 0.811 | 0.72 | 1.23 ± 0.22 (1.25) | 3.98 | 1.56 |
| p | strong | 126 | 0.803 | 0.67 | - | 5.02 | 2.17 |

## Notes

- p: score 0.782, 196/200 kicked, 0 fell; worst sector back (0.744).
