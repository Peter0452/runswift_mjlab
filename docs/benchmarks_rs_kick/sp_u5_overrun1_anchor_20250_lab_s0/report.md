# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.56 ± 0.52 (1.48) |
| Direction error [°] | 6.14 ± 10.94 (4.98) |
| Avg ball speed [m/s] | 1.90 ± 0.35 (1.94) |
| Peak ball speed [m/s] | 4.08 ± 0.81 (4.25) |
| Distance [m] | 1.53 ± 0.48 (1.50) |
| Path length [m] | 1.54 ± 0.49 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.848 | 50/50 | 0 | 50 | 1.03 ± 0.23 (1.06) | 4.60 ± 3.37 (3.78) | 1.68 ± 0.35 (1.75) | 3.62 ± 0.77 (3.66) | 1.22 ± 0.44 (1.31) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.51) | 5.70 ± 3.67 (5.11) | 1.99 ± 0.32 (2.04) | 4.31 ± 0.76 (4.53) | 1.67 ± 0.48 (1.71) |
| back | p | 0.838 | 50/50 | 0 | 49 | 2.23 ± 0.25 (2.21) | 8.21 ± 20.82 (5.68) | 2.04 ± 0.34 (2.08) | 4.38 ± 0.82 (4.54) | 1.74 ± 0.47 (1.76) |
| right | p | 0.832 | 50/50 | 0 | 50 | 1.49 ± 0.34 (1.45) | 6.06 ± 3.60 (5.15) | 1.88 ± 0.28 (1.93) | 4.03 ± 0.68 (4.23) | 1.48 ± 0.37 (1.49) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 100 | 1.57 ± 0.53 (1.50) | 5.52 ± 3.32 (5.27) | 1.92 ± 0.29 (1.91) | 4.13 ± 0.70 (4.20) | 1.55 ± 0.43 (1.50) |
| right | p | 0.845 | 100/100 | 0 | 99 | 1.56 ± 0.51 (1.47) | 6.76 ± 15.08 (4.76) | 1.87 ± 0.40 (1.97) | 4.04 ± 0.91 (4.30) | 1.51 ± 0.53 (1.50) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.06) | 4.52 ± 2.74 (3.98) | 1.73 ± 0.23 (1.80) | 3.71 ± 0.52 (3.76) | 1.27 ± 0.30 (1.31) |
| forward/right | p | 0.848 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.04) | 4.67 ± 3.89 (3.36) | 1.63 ± 0.44 (1.65) | 3.52 ± 0.94 (3.47) | 1.18 ± 0.54 (1.26) |
| left/left | p | 0.852 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.48) | 6.19 ± 4.02 (5.95) | 1.94 ± 0.34 (1.94) | 4.19 ± 0.79 (4.29) | 1.60 ± 0.49 (1.63) |
| left/right | p | 0.868 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.60) | 5.21 ± 3.21 (4.78) | 2.03 ± 0.28 (2.12) | 4.42 ± 0.71 (4.67) | 1.73 ± 0.46 (1.76) |
| back/left | p | 0.836 | 25/25 | 0 | 25 | 2.26 ± 0.27 (2.24) | 5.58 ± 2.64 (5.85) | 2.08 ± 0.20 (2.09) | 4.47 ± 0.57 (4.63) | 1.77 ± 0.38 (1.87) |
| back/right | p | 0.839 | 25/25 | 0 | 24 | 2.20 ± 0.22 (2.14) | 10.83 ± 29.10 (4.98) | 2.00 ± 0.43 (2.08) | 4.29 ± 1.00 (4.54) | 1.71 ± 0.54 (1.74) |
| right/left | p | 0.840 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.56) | 5.79 ± 3.44 (5.15) | 1.92 ± 0.27 (1.97) | 4.13 ± 0.65 (4.27) | 1.55 ± 0.36 (1.63) |
| right/right | p | 0.824 | 25/25 | 0 | 25 | 1.40 ± 0.34 (1.42) | 6.32 ± 3.74 (4.98) | 1.84 ± 0.29 (1.89) | 3.93 ± 0.68 (4.07) | 1.42 ± 0.38 (1.47) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.863 | 5.2 | 4.51 | 1.76 |
| p | normal | 0.825 | 7.0 | 3.66 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.782 | 0.22 | 2.06 ± 0.70 (1.87) | 3.28 | 1.09 |
| p | medium | 16 | 0.904 | 0.86 | 1.01 ± 0.16 (1.04) | 3.30 | 1.10 |
| p | strong | 126 | 0.865 | 0.61 | - | 4.55 | 1.79 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector right (0.832).
