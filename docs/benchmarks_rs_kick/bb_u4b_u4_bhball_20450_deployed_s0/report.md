# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.80 ± 0.62 (1.72) |
| Direction error [°] | 7.19 ± 15.86 (5.13) |
| Avg ball speed [m/s] | 2.32 ± 0.49 (2.44) |
| Peak ball speed [m/s] | 5.09 ± 1.22 (5.62) |
| Distance [m] | 2.12 ± 0.75 (2.26) |
| Path length [m] | 2.13 ± 0.75 (2.26) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.866 | 50/50 | 0 | 50 | 1.24 ± 0.25 (1.28) | 4.51 ± 3.07 (3.93) | 2.21 ± 0.53 (2.12) | 4.88 ± 1.36 (4.74) | 1.96 ± 0.84 (1.69) |
| left | p | 0.870 | 50/50 | 0 | 48 | 1.71 ± 0.35 (1.75) | 6.28 ± 4.16 (5.78) | 2.40 ± 0.38 (2.48) | 5.32 ± 0.99 (5.73) | 2.23 ± 0.62 (2.35) |
| back | p | 0.809 | 50/50 | 0 | 47 | 2.54 ± 0.61 (2.42) | 12.34 ± 30.46 (5.82) | 2.39 ± 0.57 (2.51) | 5.18 ± 1.35 (5.74) | 2.26 ± 0.79 (2.41) |
| right | p | 0.850 | 50/50 | 0 | 48 | 1.72 ± 0.35 (1.71) | 5.62 ± 3.84 (4.92) | 2.28 ± 0.44 (2.34) | 4.99 ± 1.11 (5.42) | 2.03 ± 0.68 (2.08) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 94 | 1.81 ± 0.57 (1.75) | 7.38 ± 14.37 (5.50) | 2.33 ± 0.50 (2.46) | 5.11 ± 1.20 (5.62) | 2.14 ± 0.73 (2.33) |
| right | p | 0.852 | 100/100 | 0 | 99 | 1.80 ± 0.67 (1.71) | 7.00 ± 17.22 (5.05) | 2.31 ± 0.49 (2.42) | 5.08 ± 1.24 (5.60) | 2.10 ± 0.76 (2.16) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.865 | 25/25 | 0 | 25 | 1.25 ± 0.25 (1.28) | 4.84 ± 3.50 (4.17) | 2.25 ± 0.49 (2.22) | 4.95 ± 1.23 (5.15) | 1.99 ± 0.75 (1.79) |
| forward/right | p | 0.867 | 25/25 | 0 | 25 | 1.23 ± 0.24 (1.28) | 4.19 ± 2.53 (3.79) | 2.18 ± 0.56 (1.89) | 4.81 ± 1.47 (4.01) | 1.93 ± 0.93 (1.43) |
| left/left | p | 0.869 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.74) | 6.23 ± 4.70 (5.13) | 2.37 ± 0.44 (2.48) | 5.24 ± 1.06 (5.76) | 2.20 ± 0.67 (2.35) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.80 ± 0.32 (1.76) | 6.33 ± 3.53 (6.04) | 2.42 ± 0.32 (2.48) | 5.40 ± 0.89 (5.63) | 2.25 ± 0.55 (2.27) |
| back/left | p | 0.802 | 25/25 | 0 | 23 | 2.53 ± 0.39 (2.50) | 11.97 ± 27.35 (5.82) | 2.43 ± 0.56 (2.50) | 5.22 ± 1.32 (5.61) | 2.33 ± 0.77 (2.41) |
| back/right | p | 0.817 | 25/25 | 0 | 24 | 2.55 ± 0.77 (2.36) | 12.71 ± 33.29 (5.63) | 2.35 ± 0.59 (2.54) | 5.13 ± 1.38 (5.83) | 2.20 ± 0.81 (2.40) |
| right/left | p | 0.847 | 25/25 | 0 | 23 | 1.83 ± 0.34 (1.76) | 6.47 ± 3.81 (5.66) | 2.27 ± 0.47 (2.47) | 5.01 ± 1.16 (5.53) | 2.04 ± 0.69 (2.19) |
| right/right | p | 0.853 | 25/25 | 0 | 25 | 1.62 ± 0.32 (1.56) | 4.77 ± 3.68 (4.65) | 2.29 ± 0.40 (2.10) | 4.96 ± 1.06 (4.60) | 2.03 ± 0.66 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.897 | 5.1 | 5.93 | 2.60 |
| p | normal | 0.801 | 9.3 | 4.25 | 1.64 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.748 | 0.14 | 2.26 ± 0.81 (2.07) | 3.59 | 1.26 |
| p | medium | 16 | 0.859 | 0.75 | 1.22 ± 0.17 (1.28) | 3.97 | 1.49 |
| p | strong | 126 | 0.894 | 0.79 | - | 5.92 | 2.60 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector back (0.809).
