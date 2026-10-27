# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_16-13-42_u14_u6_overpower600/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.62 ± 0.55 (1.53) |
| Direction error [°] | 6.24 ± 15.46 (3.68) |
| Avg ball speed [m/s] | 1.79 ± 0.34 (1.78) |
| Peak ball speed [m/s] | 4.57 ± 0.87 (4.67) |
| Distance [m] | 1.84 ± 0.52 (1.80) |
| Path length [m] | 1.84 ± 0.53 (1.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.824 | 50/50 | 0 | 48 | 1.17 ± 0.48 (1.11) | 7.34 ± 14.05 (4.68) | 1.62 ± 0.29 (1.55) | 4.14 ± 0.72 (3.88) | 1.54 ± 0.47 (1.42) |
| left | p | 0.874 | 50/50 | 0 | 50 | 1.51 ± 0.32 (1.50) | 4.57 ± 2.64 (3.88) | 1.87 ± 0.27 (1.92) | 4.76 ± 0.71 (4.90) | 1.95 ± 0.47 (1.90) |
| back | p | 0.851 | 50/50 | 0 | 48 | 2.23 ± 0.26 (2.19) | 5.73 ± 14.45 (2.46) | 1.83 ± 0.43 (1.91) | 4.71 ± 1.08 (5.15) | 1.94 ± 0.55 (1.97) |
| right | p | 0.846 | 50/50 | 0 | 49 | 1.59 ± 0.48 (1.50) | 7.31 ± 23.20 (3.66) | 1.84 ± 0.29 (1.76) | 4.66 ± 0.77 (4.78) | 1.91 ± 0.49 (1.79) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.851 | 100/100 | 0 | 98 | 1.62 ± 0.53 (1.54) | 6.37 ± 14.05 (3.92) | 1.82 ± 0.33 (1.88) | 4.63 ± 0.87 (4.85) | 1.87 ± 0.51 (1.88) |
| right | p | 0.846 | 100/100 | 0 | 97 | 1.63 ± 0.57 (1.52) | 6.11 ± 16.76 (3.33) | 1.75 ± 0.34 (1.74) | 4.50 ± 0.87 (4.45) | 1.80 ± 0.53 (1.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.821 | 25/25 | 0 | 24 | 1.21 ± 0.51 (1.12) | 9.30 ± 19.18 (5.61) | 1.68 ± 0.22 (1.71) | 4.21 ± 0.63 (4.01) | 1.58 ± 0.42 (1.50) |
| forward/right | p | 0.827 | 25/25 | 0 | 24 | 1.14 ± 0.44 (1.10) | 5.38 ± 4.39 (3.23) | 1.55 ± 0.32 (1.52) | 4.08 ± 0.79 (3.87) | 1.50 ± 0.51 (1.39) |
| left/left | p | 0.872 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.46) | 4.50 ± 2.81 (3.73) | 1.83 ± 0.28 (1.92) | 4.66 ± 0.75 (4.80) | 1.87 ± 0.45 (1.85) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.60 ± 0.29 (1.58) | 4.64 ± 2.46 (4.10) | 1.91 ± 0.24 (1.94) | 4.85 ± 0.66 (4.96) | 2.04 ± 0.47 (2.01) |
| back/left | p | 0.847 | 25/25 | 0 | 24 | 2.23 ± 0.26 (2.16) | 7.71 ± 19.69 (2.69) | 1.86 ± 0.43 (1.95) | 4.81 ± 1.08 (5.17) | 2.00 ± 0.54 (2.09) |
| back/right | p | 0.854 | 25/25 | 0 | 24 | 2.22 ± 0.26 (2.20) | 3.74 ± 4.68 (2.38) | 1.79 ± 0.42 (1.87) | 4.61 ± 1.08 (4.80) | 1.88 ± 0.55 (1.94) |
| right/left | p | 0.865 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.58) | 3.95 ± 2.45 (4.12) | 1.92 ± 0.29 (1.88) | 4.86 ± 0.80 (5.08) | 2.04 ± 0.51 (1.90) |
| right/right | p | 0.827 | 25/25 | 0 | 24 | 1.54 ± 0.59 (1.46) | 10.67 ± 32.37 (3.42) | 1.75 ± 0.26 (1.71) | 4.47 ± 0.69 (4.36) | 1.77 ± 0.44 (1.73) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.880 | 4.9 | 5.00 | 2.07 |
| p | normal | 0.818 | 7.6 | 4.13 | 1.60 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.757 | 0.10 | 2.38 ± 0.85 (2.24) | 3.74 | 1.37 |
| p | medium | 16 | 0.905 | 0.78 | 1.18 ± 0.18 (1.19) | 3.83 | 1.43 |
| p | strong | 126 | 0.884 | 0.67 | - | 5.04 | 2.10 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector forward (0.824).
