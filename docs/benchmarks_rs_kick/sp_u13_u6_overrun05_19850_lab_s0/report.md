# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-32-24_u13_u6_overrun05/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.54 (1.52) |
| Direction error [°] | 4.82 ± 3.11 (4.09) |
| Avg ball speed [m/s] | 2.03 ± 0.33 (2.09) |
| Peak ball speed [m/s] | 4.35 ± 0.79 (4.38) |
| Distance [m] | 1.71 ± 0.50 (1.68) |
| Path length [m] | 1.72 ± 0.50 (1.69) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.837 | 50/50 | 0 | 50 | 1.05 ± 0.23 (1.06) | 5.00 ± 3.17 (4.88) | 1.77 ± 0.32 (1.75) | 3.76 ± 0.70 (3.58) | 1.32 ± 0.43 (1.24) |
| left | p | 0.876 | 50/50 | 0 | 50 | 1.54 ± 0.34 (1.53) | 4.25 ± 2.86 (3.98) | 2.14 ± 0.28 (2.21) | 4.60 ± 0.70 (4.88) | 1.87 ± 0.44 (1.96) |
| back | p | 0.848 | 50/50 | 0 | 50 | 2.30 ± 0.28 (2.26) | 4.10 ± 2.41 (3.44) | 2.23 ± 0.21 (2.30) | 4.75 ± 0.64 (5.02) | 1.97 ± 0.41 (2.08) |
| right | p | 0.837 | 50/50 | 0 | 50 | 1.54 ± 0.35 (1.51) | 5.91 ± 3.56 (5.92) | 2.00 ± 0.30 (1.99) | 4.28 ± 0.74 (4.18) | 1.66 ± 0.44 (1.57) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 100 | 1.61 ± 0.55 (1.52) | 4.61 ± 3.01 (4.01) | 2.03 ± 0.32 (2.10) | 4.35 ± 0.78 (4.37) | 1.71 ± 0.50 (1.69) |
| right | p | 0.848 | 100/100 | 0 | 100 | 1.60 ± 0.53 (1.52) | 5.02 ± 3.20 (4.80) | 2.04 ± 0.34 (2.08) | 4.35 ± 0.81 (4.42) | 1.71 ± 0.50 (1.66) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 4.99 ± 2.93 (4.77) | 1.76 ± 0.29 (1.75) | 3.73 ± 0.65 (3.53) | 1.31 ± 0.43 (1.17) |
| forward/right | p | 0.838 | 25/25 | 0 | 25 | 1.05 ± 0.23 (1.04) | 5.02 ± 3.39 (4.99) | 1.78 ± 0.34 (1.72) | 3.79 ± 0.75 (3.65) | 1.34 ± 0.44 (1.25) |
| left/left | p | 0.871 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.50) | 4.29 ± 2.94 (3.38) | 2.05 ± 0.25 (2.14) | 4.41 ± 0.66 (4.69) | 1.74 ± 0.40 (1.81) |
| left/right | p | 0.882 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.62) | 4.22 ± 2.77 (3.99) | 2.24 ± 0.28 (2.33) | 4.79 ± 0.69 (5.11) | 2.01 ± 0.44 (2.15) |
| back/left | p | 0.855 | 25/25 | 0 | 25 | 2.32 ± 0.28 (2.26) | 3.53 ± 2.23 (3.01) | 2.25 ± 0.19 (2.32) | 4.80 ± 0.63 (5.08) | 2.02 ± 0.43 (2.17) |
| back/right | p | 0.842 | 25/25 | 0 | 25 | 2.28 ± 0.27 (2.26) | 4.67 ± 2.45 (3.88) | 2.20 ± 0.23 (2.30) | 4.70 ± 0.65 (5.01) | 1.92 ± 0.39 (2.07) |
| right/left | p | 0.845 | 25/25 | 0 | 25 | 1.64 ± 0.32 (1.60) | 5.65 ± 3.39 (5.61) | 2.06 ± 0.31 (2.09) | 4.46 ± 0.75 (4.72) | 1.77 ± 0.45 (1.83) |
| right/right | p | 0.829 | 25/25 | 0 | 25 | 1.43 ± 0.35 (1.48) | 6.17 ± 3.71 (5.93) | 1.94 ± 0.27 (1.92) | 4.11 ± 0.69 (3.87) | 1.56 ± 0.40 (1.47) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.870 | 5.0 | 4.72 | 1.92 |
| p | normal | 0.829 | 4.7 | 3.97 | 1.50 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.775 | 0.15 | 2.25 ± 0.70 (2.03) | 3.58 | 1.26 |
| p | medium | 16 | 0.913 | 0.85 | 1.10 ± 0.14 (1.16) | 3.58 | 1.26 |
| p | strong | 126 | 0.876 | 0.64 | - | 4.80 | 1.97 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector right (0.837).
