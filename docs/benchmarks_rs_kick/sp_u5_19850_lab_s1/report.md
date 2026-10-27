# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u5_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.57 ± 0.56 (1.50) |
| Direction error [°] | 4.96 ± 3.35 (4.27) |
| Avg ball speed [m/s] | 2.18 ± 0.35 (2.19) |
| Peak ball speed [m/s] | 4.65 ± 0.83 (4.78) |
| Distance [m] | 2.02 ± 0.57 (2.10) |
| Path length [m] | 2.03 ± 0.58 (2.11) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.852 | 50/50 | 0 | 50 | 1.06 ± 0.40 (1.05) | 5.25 ± 3.56 (4.74) | 2.03 ± 0.33 (2.02) | 4.40 ± 0.79 (4.47) | 1.83 ± 0.54 (1.84) |
| left | p | 0.863 | 50/50 | 0 | 50 | 1.50 ± 0.36 (1.43) | 5.20 ± 3.40 (4.26) | 2.16 ± 0.38 (2.17) | 4.60 ± 0.88 (4.81) | 1.99 ± 0.59 (2.05) |
| back | p | 0.857 | 50/50 | 0 | 50 | 2.26 ± 0.28 (2.24) | 4.16 ± 2.47 (3.64) | 2.35 ± 0.28 (2.35) | 5.00 ± 0.70 (5.18) | 2.27 ± 0.52 (2.32) |
| right | p | 0.847 | 50/50 | 0 | 50 | 1.48 ± 0.34 (1.50) | 5.25 ± 3.72 (4.97) | 2.17 ± 0.33 (2.17) | 4.61 ± 0.81 (4.75) | 1.99 ± 0.55 (2.15) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 100 | 1.58 ± 0.57 (1.47) | 4.93 ± 3.45 (4.12) | 2.17 ± 0.37 (2.17) | 4.65 ± 0.86 (4.75) | 2.02 ± 0.59 (2.12) |
| right | p | 0.859 | 100/100 | 0 | 100 | 1.57 ± 0.54 (1.53) | 5.00 ± 3.26 (4.79) | 2.18 ± 0.33 (2.19) | 4.66 ± 0.79 (4.80) | 2.02 ± 0.55 (2.03) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.09 ± 0.51 (1.00) | 5.10 ± 3.57 (4.20) | 1.98 ± 0.34 (1.91) | 4.30 ± 0.82 (4.04) | 1.77 ± 0.56 (1.72) |
| forward/right | p | 0.856 | 25/25 | 0 | 25 | 1.02 ± 0.25 (1.10) | 5.39 ± 3.55 (5.46) | 2.08 ± 0.31 (2.10) | 4.49 ± 0.75 (4.59) | 1.88 ± 0.52 (1.90) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.34) | 5.45 ± 3.85 (4.10) | 2.11 ± 0.38 (2.15) | 4.51 ± 0.89 (4.80) | 1.93 ± 0.57 (2.05) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.58 ± 0.35 (1.56) | 4.95 ± 2.87 (5.14) | 2.20 ± 0.37 (2.19) | 4.69 ± 0.85 (4.82) | 2.06 ± 0.59 (2.05) |
| back/left | p | 0.857 | 25/25 | 0 | 25 | 2.26 ± 0.25 (2.28) | 4.15 ± 2.73 (3.66) | 2.39 ± 0.31 (2.41) | 5.10 ± 0.75 (5.37) | 2.35 ± 0.56 (2.53) |
| back/right | p | 0.857 | 25/25 | 0 | 25 | 2.26 ± 0.30 (2.24) | 4.16 ± 2.18 (3.63) | 2.30 ± 0.23 (2.30) | 4.91 ± 0.64 (5.07) | 2.20 ± 0.47 (2.30) |
| right/left | p | 0.839 | 25/25 | 0 | 25 | 1.56 ± 0.33 (1.50) | 5.02 ± 3.42 (4.91) | 2.20 ± 0.32 (2.14) | 4.69 ± 0.76 (4.72) | 2.05 ± 0.52 (2.14) |
| right/right | p | 0.854 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.50) | 5.47 ± 3.98 (4.99) | 2.13 ± 0.34 (2.18) | 4.53 ± 0.85 (4.94) | 1.94 ± 0.58 (2.21) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.882 | 4.9 | 5.17 | 2.37 |
| p | normal | 0.827 | 5.1 | 4.14 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.769 | 0.13 | 2.40 ± 0.74 (2.24) | 3.74 | 1.39 |
| p | medium | 20 | 0.906 | 0.77 | 1.20 ± 0.17 (1.25) | 3.83 | 1.45 |
| p | strong | 126 | 0.883 | 0.69 | - | 5.18 | 2.38 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector right (0.847).
