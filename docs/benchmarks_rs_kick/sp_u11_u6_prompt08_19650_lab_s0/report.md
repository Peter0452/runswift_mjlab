# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_14-36-37_u11_u6_prompt08/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.59 ± 0.54 (1.50) |
| Direction error [°] | 4.94 ± 3.04 (4.54) |
| Avg ball speed [m/s] | 2.04 ± 0.34 (2.12) |
| Peak ball speed [m/s] | 4.39 ± 0.80 (4.61) |
| Distance [m] | 1.73 ± 0.51 (1.75) |
| Path length [m] | 1.73 ± 0.52 (1.77) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 50 | 1.05 ± 0.23 (1.06) | 4.52 ± 3.20 (3.57) | 1.82 ± 0.37 (1.72) | 3.91 ± 0.85 (3.61) | 1.40 ± 0.50 (1.25) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.54) | 5.68 ± 3.08 (5.21) | 2.10 ± 0.27 (2.15) | 4.52 ± 0.66 (4.78) | 1.80 ± 0.42 (1.84) |
| back | p | 0.847 | 50/50 | 0 | 50 | 2.29 ± 0.30 (2.24) | 4.70 ± 2.41 (4.66) | 2.19 ± 0.29 (2.28) | 4.68 ± 0.74 (4.97) | 1.95 ± 0.51 (2.04) |
| right | p | 0.849 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.49) | 4.87 ± 3.27 (4.13) | 2.06 ± 0.29 (2.14) | 4.45 ± 0.74 (4.65) | 1.75 ± 0.45 (1.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 100 | 1.59 ± 0.54 (1.53) | 4.85 ± 2.89 (4.79) | 2.04 ± 0.31 (2.09) | 4.40 ± 0.77 (4.62) | 1.73 ± 0.49 (1.77) |
| right | p | 0.849 | 100/100 | 0 | 100 | 1.59 ± 0.54 (1.49) | 5.04 ± 3.19 (4.49) | 2.04 ± 0.36 (2.14) | 4.38 ± 0.83 (4.60) | 1.73 ± 0.53 (1.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.06) | 4.60 ± 2.83 (4.29) | 1.86 ± 0.33 (1.85) | 3.96 ± 0.77 (3.77) | 1.44 ± 0.47 (1.25) |
| forward/right | p | 0.848 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.06) | 4.44 ± 3.54 (3.20) | 1.79 ± 0.40 (1.68) | 3.85 ± 0.92 (3.60) | 1.36 ± 0.53 (1.22) |
| left/left | p | 0.857 | 25/25 | 0 | 25 | 1.43 ± 0.35 (1.50) | 5.71 ± 3.26 (5.43) | 2.04 ± 0.27 (2.09) | 4.41 ± 0.68 (4.72) | 1.72 ± 0.42 (1.81) |
| left/right | p | 0.862 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.62) | 5.66 ± 2.89 (4.93) | 2.15 ± 0.26 (2.21) | 4.63 ± 0.61 (4.83) | 1.88 ± 0.41 (1.91) |
| back/left | p | 0.843 | 25/25 | 0 | 25 | 2.30 ± 0.29 (2.24) | 4.78 ± 2.38 (4.85) | 2.18 ± 0.23 (2.21) | 4.68 ± 0.64 (4.94) | 1.94 ± 0.46 (2.04) |
| back/right | p | 0.850 | 25/25 | 0 | 25 | 2.28 ± 0.30 (2.24) | 4.62 ± 2.43 (4.47) | 2.20 ± 0.34 (2.31) | 4.69 ± 0.83 (5.05) | 1.96 ± 0.55 (2.04) |
| right/left | p | 0.861 | 25/25 | 0 | 25 | 1.61 ± 0.32 (1.56) | 4.32 ± 2.81 (3.99) | 2.09 ± 0.31 (2.17) | 4.53 ± 0.80 (4.82) | 1.80 ± 0.48 (1.79) |
| right/right | p | 0.836 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.44) | 5.42 ± 3.58 (5.05) | 2.04 ± 0.25 (2.11) | 4.37 ± 0.67 (4.57) | 1.70 ± 0.42 (1.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.876 | 4.8 | 4.88 | 2.00 |
| p | normal | 0.825 | 5.0 | 3.90 | 1.45 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.778 | 0.17 | 2.21 ± 0.68 (2.12) | 3.52 | 1.22 |
| p | medium | 16 | 0.903 | 0.83 | 1.12 ± 0.16 (1.13) | 3.65 | 1.31 |
| p | strong | 126 | 0.877 | 0.65 | - | 4.88 | 2.01 |

## Notes

- p: score 0.851, 200/200 kicked, 0 fell; worst sector back (0.847).
