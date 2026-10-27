# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_14-36-37_u11_u6_prompt08/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.59 ± 0.53 (1.52) |
| Direction error [°] | 4.76 ± 3.00 (4.22) |
| Avg ball speed [m/s] | 1.89 ± 0.32 (1.97) |
| Peak ball speed [m/s] | 4.09 ± 0.77 (4.37) |
| Distance [m] | 1.46 ± 0.45 (1.50) |
| Path length [m] | 1.46 ± 0.45 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.853 | 50/50 | 0 | 50 | 1.04 ± 0.24 (1.08) | 4.23 ± 2.82 (3.41) | 1.70 ± 0.30 (1.76) | 3.62 ± 0.67 (3.69) | 1.18 ± 0.36 (1.25) |
| left | p | 0.873 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.54) | 4.59 ± 2.99 (4.08) | 1.93 ± 0.31 (2.03) | 4.22 ± 0.75 (4.51) | 1.53 ± 0.44 (1.63) |
| back | p | 0.842 | 50/50 | 0 | 50 | 2.27 ± 0.26 (2.23) | 5.22 ± 3.08 (4.64) | 2.02 ± 0.26 (2.12) | 4.40 ± 0.67 (4.70) | 1.66 ± 0.40 (1.85) |
| right | p | 0.849 | 50/50 | 0 | 50 | 1.52 ± 0.35 (1.49) | 4.99 ± 3.00 (4.38) | 1.89 ± 0.32 (2.07) | 4.10 ± 0.78 (4.52) | 1.46 ± 0.43 (1.53) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 100 | 1.59 ± 0.54 (1.53) | 4.71 ± 2.94 (4.01) | 1.89 ± 0.30 (1.95) | 4.10 ± 0.74 (4.23) | 1.46 ± 0.44 (1.49) |
| right | p | 0.856 | 100/100 | 0 | 100 | 1.59 ± 0.53 (1.51) | 4.81 ± 3.05 (4.51) | 1.88 ± 0.34 (2.02) | 4.07 ± 0.80 (4.43) | 1.45 ± 0.45 (1.50) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.854 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.12) | 3.89 ± 2.74 (2.73) | 1.72 ± 0.29 (1.76) | 3.66 ± 0.62 (3.73) | 1.19 ± 0.36 (1.31) |
| forward/right | p | 0.852 | 25/25 | 0 | 25 | 1.04 ± 0.25 (1.04) | 4.57 ± 2.86 (4.09) | 1.69 ± 0.31 (1.77) | 3.59 ± 0.71 (3.69) | 1.16 ± 0.36 (1.21) |
| left/left | p | 0.855 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.48) | 5.68 ± 3.08 (6.01) | 1.87 ± 0.29 (1.93) | 4.06 ± 0.72 (4.35) | 1.43 ± 0.43 (1.45) |
| left/right | p | 0.891 | 25/25 | 0 | 25 | 1.62 ± 0.31 (1.60) | 3.50 ± 2.45 (2.38) | 2.00 ± 0.32 (2.14) | 4.38 ± 0.74 (4.74) | 1.63 ± 0.43 (1.67) |
| back/left | p | 0.842 | 25/25 | 0 | 25 | 2.29 ± 0.26 (2.22) | 5.00 ± 3.10 (4.20) | 2.03 ± 0.22 (2.11) | 4.43 ± 0.61 (4.71) | 1.69 ± 0.39 (1.88) |
| back/right | p | 0.842 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.24) | 5.44 ± 3.04 (4.91) | 2.00 ± 0.29 (2.12) | 4.37 ± 0.72 (4.69) | 1.63 ± 0.41 (1.83) |
| right/left | p | 0.859 | 25/25 | 0 | 25 | 1.62 ± 0.33 (1.60) | 4.28 ± 2.49 (3.62) | 1.94 ± 0.30 (2.09) | 4.25 ± 0.78 (4.69) | 1.53 ± 0.41 (1.57) |
| right/right | p | 0.839 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.44) | 5.71 ± 3.28 (4.88) | 1.84 ± 0.33 (2.01) | 3.95 ± 0.75 (4.39) | 1.38 ± 0.43 (1.46) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.869 | 4.7 | 4.57 | 1.71 |
| p | normal | 0.839 | 4.8 | 3.60 | 1.20 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.798 | 0.25 | 2.01 ± 0.66 (1.88) | 3.20 | 0.97 |
| p | medium | 16 | 0.932 | 0.90 | 1.01 ± 0.12 (1.02) | 3.27 | 1.03 |
| p | strong | 126 | 0.870 | 0.61 | - | 4.60 | 1.73 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.842).
