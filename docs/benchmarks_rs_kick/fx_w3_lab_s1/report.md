# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w3_u4_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.862** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.55 (1.53) |
| Direction error [°] | 5.16 ± 3.13 (4.76) |
| Avg ball speed [m/s] | 1.99 ± 0.46 (2.12) |
| Peak ball speed [m/s] | 4.29 ± 1.06 (4.74) |
| Distance [m] | 1.72 ± 0.67 (1.91) |
| Path length [m] | 1.73 ± 0.67 (1.92) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.870 | 50/50 | 0 | 50 | 1.04 ± 0.27 (1.10) | 4.76 ± 3.31 (3.93) | 1.79 ± 0.47 (1.92) | 3.93 ± 1.07 (4.27) | 1.46 ± 0.64 (1.59) |
| left | p | 0.870 | 50/50 | 0 | 50 | 1.56 ± 0.37 (1.46) | 5.59 ± 3.07 (5.39) | 2.00 ± 0.44 (2.20) | 4.30 ± 1.05 (4.76) | 1.74 ± 0.67 (2.03) |
| back | p | 0.849 | 50/50 | 0 | 50 | 2.29 ± 0.27 (2.25) | 5.45 ± 2.91 (5.27) | 2.19 ± 0.37 (2.34) | 4.69 ± 0.90 (5.11) | 1.99 ± 0.60 (2.21) |
| right | p | 0.861 | 50/50 | 0 | 50 | 1.54 ± 0.36 (1.53) | 4.83 ± 3.14 (3.87) | 1.97 ± 0.46 (2.10) | 4.22 ± 1.07 (4.54) | 1.68 ± 0.67 (1.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.858 | 100/100 | 0 | 100 | 1.61 ± 0.55 (1.47) | 5.10 ± 3.03 (5.05) | 1.99 ± 0.46 (2.19) | 4.30 ± 1.07 (4.83) | 1.73 ± 0.67 (1.92) |
| right | p | 0.867 | 100/100 | 0 | 100 | 1.61 ± 0.55 (1.56) | 5.22 ± 3.23 (4.48) | 1.99 ± 0.46 (2.08) | 4.27 ± 1.05 (4.66) | 1.71 ± 0.67 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.869 | 25/25 | 0 | 25 | 1.05 ± 0.28 (1.10) | 5.20 ± 3.31 (4.75) | 1.78 ± 0.49 (1.92) | 3.92 ± 1.13 (4.25) | 1.47 ± 0.68 (1.69) |
| forward/right | p | 0.871 | 25/25 | 0 | 25 | 1.04 ± 0.25 (1.10) | 4.31 ± 3.25 (3.79) | 1.80 ± 0.44 (1.90) | 3.95 ± 1.00 (4.30) | 1.46 ± 0.59 (1.59) |
| left/left | p | 0.870 | 25/25 | 0 | 25 | 1.46 ± 0.35 (1.42) | 5.56 ± 2.83 (6.03) | 1.99 ± 0.46 (2.25) | 4.30 ± 1.08 (4.95) | 1.73 ± 0.68 (2.01) |
| left/right | p | 0.869 | 25/25 | 0 | 25 | 1.66 ± 0.36 (1.60) | 5.62 ± 3.29 (5.10) | 2.02 ± 0.42 (2.17) | 4.30 ± 1.01 (4.69) | 1.74 ± 0.66 (2.05) |
| back/left | p | 0.846 | 25/25 | 0 | 25 | 2.29 ± 0.24 (2.24) | 5.16 ± 3.05 (5.41) | 2.20 ± 0.36 (2.32) | 4.72 ± 0.89 (5.11) | 2.01 ± 0.58 (2.22) |
| back/right | p | 0.852 | 25/25 | 0 | 25 | 2.30 ± 0.29 (2.26) | 5.73 ± 2.74 (5.04) | 2.18 ± 0.38 (2.34) | 4.67 ± 0.91 (5.12) | 1.97 ± 0.62 (2.20) |
| right/left | p | 0.848 | 25/25 | 0 | 25 | 1.64 ± 0.36 (1.58) | 4.47 ± 2.81 (3.35) | 1.99 ± 0.42 (2.13) | 4.28 ± 0.99 (4.88) | 1.70 ± 0.64 (1.83) |
| right/right | p | 0.874 | 25/25 | 0 | 25 | 1.44 ± 0.33 (1.52) | 5.20 ± 3.40 (3.91) | 1.94 ± 0.49 (2.05) | 4.16 ± 1.14 (4.38) | 1.65 ± 0.71 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.879 | 4.9 | 5.02 | 2.16 |
| p | normal | 0.846 | 5.4 | 3.55 | 1.27 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.803 | 0.32 | 1.90 ± 0.64 (1.80) | 2.95 | 0.89 |
| p | medium | 20 | 0.912 | 0.86 | 1.00 ± 0.17 (0.99) | 3.18 | 1.02 |
| p | strong | 126 | 0.880 | 0.67 | - | 5.03 | 2.18 |

## Notes

- p: score 0.862, 200/200 kicked, 0 fell; worst sector back (0.849).
