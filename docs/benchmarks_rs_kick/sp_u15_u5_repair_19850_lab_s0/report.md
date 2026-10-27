# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-26-24_u15_u5_repair/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.65 ± 0.59 (1.52) |
| Direction error [°] | 6.00 ± 16.95 (3.00) |
| Avg ball speed [m/s] | 1.76 ± 0.32 (1.78) |
| Peak ball speed [m/s] | 4.55 ± 0.82 (4.67) |
| Distance [m] | 1.81 ± 0.49 (1.79) |
| Path length [m] | 1.81 ± 0.49 (1.79) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.826 | 50/50 | 0 | 49 | 1.28 ± 0.72 (1.11) | 7.06 ± 21.05 (2.98) | 1.59 ± 0.27 (1.56) | 4.07 ± 0.70 (3.85) | 1.49 ± 0.38 (1.41) |
| left | p | 0.866 | 50/50 | 0 | 50 | 1.55 ± 0.43 (1.51) | 4.82 ± 2.96 (4.91) | 1.78 ± 0.26 (1.81) | 4.68 ± 0.70 (4.74) | 1.90 ± 0.45 (1.89) |
| back | p | 0.864 | 50/50 | 0 | 49 | 2.21 ± 0.24 (2.18) | 6.02 ± 20.55 (2.13) | 1.88 ± 0.33 (1.94) | 4.82 ± 0.88 (5.14) | 1.98 ± 0.48 (2.04) |
| right | p | 0.852 | 50/50 | 0 | 49 | 1.55 ± 0.41 (1.47) | 6.09 ± 16.49 (3.12) | 1.80 ± 0.32 (1.78) | 4.63 ± 0.75 (4.73) | 1.86 ± 0.47 (1.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 99 | 1.63 ± 0.59 (1.52) | 5.43 ± 15.04 (3.09) | 1.78 ± 0.30 (1.78) | 4.56 ± 0.77 (4.66) | 1.82 ± 0.48 (1.82) |
| right | p | 0.848 | 100/100 | 0 | 98 | 1.67 ± 0.60 (1.52) | 6.56 ± 18.64 (2.77) | 1.75 ± 0.33 (1.78) | 4.54 ± 0.86 (4.68) | 1.79 ± 0.49 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 24 | 1.26 ± 0.73 (1.12) | 10.46 ± 29.17 (3.56) | 1.59 ± 0.24 (1.62) | 4.04 ± 0.63 (3.96) | 1.47 ± 0.35 (1.43) |
| forward/right | p | 0.832 | 25/25 | 0 | 25 | 1.30 ± 0.71 (1.10) | 3.65 ± 3.47 (2.08) | 1.58 ± 0.30 (1.50) | 4.09 ± 0.77 (3.83) | 1.50 ± 0.41 (1.40) |
| left/left | p | 0.865 | 25/25 | 0 | 25 | 1.41 ± 0.32 (1.44) | 4.81 ± 2.97 (4.76) | 1.75 ± 0.25 (1.78) | 4.52 ± 0.69 (4.65) | 1.79 ± 0.42 (1.84) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.69 ± 0.49 (1.60) | 4.83 ± 2.94 (4.98) | 1.82 ± 0.27 (1.82) | 4.84 ± 0.68 (5.08) | 2.00 ± 0.45 (2.14) |
| back/left | p | 0.870 | 25/25 | 0 | 25 | 2.25 ± 0.27 (2.22) | 2.61 ± 2.04 (2.02) | 1.94 ± 0.24 (1.97) | 4.95 ± 0.63 (5.16) | 2.07 ± 0.40 (2.16) |
| back/right | p | 0.858 | 25/25 | 0 | 24 | 2.17 ± 0.20 (2.16) | 9.43 ± 28.59 (2.14) | 1.83 ± 0.40 (1.85) | 4.70 ± 1.06 (5.12) | 1.90 ± 0.54 (1.99) |
| right/left | p | 0.867 | 25/25 | 0 | 25 | 1.58 ± 0.30 (1.58) | 3.83 ± 2.14 (3.74) | 1.84 ± 0.33 (1.79) | 4.74 ± 0.80 (4.92) | 1.94 ± 0.50 (2.01) |
| right/right | p | 0.836 | 25/25 | 0 | 24 | 1.51 ± 0.50 (1.44) | 8.34 ± 23.01 (2.84) | 1.76 ± 0.29 (1.74) | 4.52 ± 0.69 (4.53) | 1.77 ± 0.41 (1.69) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 4.2 | 5.02 | 2.05 |
| p | normal | 0.819 | 7.8 | 4.08 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.768 | 0.12 | 2.35 ± 0.79 (2.17) | 3.72 | 1.36 |
| p | medium | 16 | 0.910 | 0.77 | 1.19 ± 0.19 (1.18) | 3.84 | 1.45 |
| p | strong | 126 | 0.883 | 0.67 | - | 5.02 | 2.06 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector forward (0.826).
