# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.841** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.53 (1.50) |
| Direction error [°] | 6.28 ± 4.14 (5.96) |
| Avg ball speed [m/s] | 1.72 ± 0.37 (1.82) |
| Peak ball speed [m/s] | 3.77 ± 0.89 (4.06) |
| Distance [m] | 1.32 ± 0.50 (1.43) |
| Path length [m] | 1.33 ± 0.50 (1.44) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 49 | 1.06 ± 0.24 (1.11) | 4.86 ± 3.87 (3.29) | 1.52 ± 0.39 (1.53) | 3.31 ± 0.86 (3.14) | 1.04 ± 0.46 (0.92) |
| left | p | 0.852 | 50/50 | 0 | 47 | 1.49 ± 0.34 (1.50) | 6.74 ± 4.26 (6.43) | 1.81 ± 0.36 (1.97) | 3.97 ± 0.87 (4.36) | 1.44 ± 0.49 (1.58) |
| back | p | 0.826 | 50/50 | 0 | 50 | 2.25 ± 0.29 (2.23) | 6.88 ± 3.47 (7.70) | 1.89 ± 0.28 (1.99) | 4.16 ± 0.75 (4.49) | 1.56 ± 0.44 (1.62) |
| right | p | 0.835 | 50/50 | 0 | 49 | 1.51 ± 0.34 (1.48) | 6.66 ± 4.57 (5.29) | 1.68 ± 0.34 (1.77) | 3.66 ± 0.82 (3.90) | 1.25 ± 0.44 (1.36) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.840 | 100/100 | 0 | 98 | 1.59 ± 0.54 (1.50) | 6.25 ± 4.10 (5.98) | 1.76 ± 0.36 (1.87) | 3.87 ± 0.88 (4.16) | 1.38 ± 0.51 (1.49) |
| right | p | 0.842 | 100/100 | 0 | 97 | 1.57 ± 0.52 (1.50) | 6.32 ± 4.19 (5.84) | 1.68 ± 0.37 (1.74) | 3.68 ± 0.88 (3.73) | 1.26 ± 0.48 (1.28) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.854 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.12) | 4.80 ± 3.72 (2.41) | 1.57 ± 0.36 (1.63) | 3.43 ± 0.84 (3.52) | 1.10 ± 0.47 (1.09) |
| forward/right | p | 0.848 | 25/25 | 0 | 24 | 1.06 ± 0.24 (1.10) | 4.91 ± 4.00 (3.60) | 1.46 ± 0.41 (1.38) | 3.19 ± 0.87 (3.06) | 0.97 ± 0.44 (0.76) |
| left/left | p | 0.844 | 25/25 | 0 | 23 | 1.38 ± 0.33 (1.42) | 6.97 ± 4.63 (6.51) | 1.78 ± 0.37 (1.94) | 3.88 ± 0.90 (4.31) | 1.40 ± 0.50 (1.60) |
| left/right | p | 0.859 | 25/25 | 0 | 24 | 1.60 ± 0.33 (1.56) | 6.52 ± 3.85 (6.11) | 1.84 ± 0.34 (1.98) | 4.07 ± 0.82 (4.51) | 1.48 ± 0.47 (1.57) |
| back/left | p | 0.820 | 25/25 | 0 | 25 | 2.28 ± 0.28 (2.22) | 7.13 ± 3.65 (7.77) | 1.94 ± 0.28 (2.02) | 4.28 ± 0.75 (4.57) | 1.64 ± 0.46 (1.73) |
| back/right | p | 0.831 | 25/25 | 0 | 25 | 2.23 ± 0.30 (2.24) | 6.63 ± 3.26 (7.11) | 1.84 ± 0.27 (1.98) | 4.03 ± 0.73 (4.38) | 1.48 ± 0.41 (1.53) |
| right/left | p | 0.842 | 25/25 | 0 | 25 | 1.62 ± 0.33 (1.58) | 6.11 ± 3.92 (5.17) | 1.77 ± 0.34 (1.89) | 3.87 ± 0.82 (4.20) | 1.37 ± 0.46 (1.58) |
| right/right | p | 0.829 | 25/25 | 0 | 24 | 1.41 ± 0.32 (1.42) | 7.21 ± 5.07 (5.97) | 1.59 ± 0.31 (1.55) | 3.44 ± 0.76 (3.21) | 1.12 ± 0.38 (0.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.851 | 6.0 | 4.28 | 1.58 |
| p | normal | 0.831 | 6.6 | 3.27 | 1.06 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.812 | 0.38 | 1.78 ± 0.60 (1.58) | 2.83 | 0.80 |
| p | medium | 16 | 0.876 | 0.83 | 0.87 ± 0.19 (0.94) | 2.82 | 0.82 |
| p | strong | 126 | 0.850 | 0.58 | - | 4.33 | 1.62 |

## Notes

- p: score 0.841, 200/200 kicked, 0 fell; worst sector back (0.826).
