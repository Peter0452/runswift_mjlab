# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/x2_u6_u10.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.57 ± 0.52 (1.48) |
| Direction error [°] | 5.08 ± 3.34 (4.30) |
| Avg ball speed [m/s] | 1.96 ± 0.34 (2.01) |
| Peak ball speed [m/s] | 4.23 ± 0.82 (4.43) |
| Distance [m] | 1.61 ± 0.51 (1.60) |
| Path length [m] | 1.62 ± 0.51 (1.62) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 50 | 1.03 ± 0.22 (1.05) | 4.81 ± 3.41 (3.51) | 1.73 ± 0.35 (1.69) | 3.73 ± 0.80 (3.48) | 1.28 ± 0.47 (1.16) |
| left | p | 0.867 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.51) | 5.06 ± 3.47 (4.17) | 2.02 ± 0.31 (2.05) | 4.40 ± 0.76 (4.63) | 1.72 ± 0.49 (1.78) |
| back | p | 0.848 | 50/50 | 0 | 50 | 2.23 ± 0.26 (2.21) | 4.86 ± 3.01 (4.45) | 2.11 ± 0.27 (2.22) | 4.56 ± 0.70 (4.88) | 1.84 ± 0.46 (1.95) |
| right | p | 0.844 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.47) | 5.60 ± 3.39 (5.41) | 1.97 ± 0.31 (2.01) | 4.23 ± 0.78 (4.46) | 1.61 ± 0.46 (1.61) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.48) | 5.27 ± 3.17 (5.21) | 1.95 ± 0.31 (2.01) | 4.23 ± 0.77 (4.48) | 1.61 ± 0.48 (1.60) |
| right | p | 0.855 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.49) | 4.90 ± 3.49 (4.13) | 1.96 ± 0.37 (2.01) | 4.24 ± 0.87 (4.38) | 1.62 ± 0.54 (1.61) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.843 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 5.19 ± 3.37 (3.26) | 1.77 ± 0.30 (1.81) | 3.79 ± 0.71 (3.53) | 1.32 ± 0.43 (1.20) |
| forward/right | p | 0.851 | 25/25 | 0 | 25 | 1.02 ± 0.23 (1.04) | 4.43 ± 3.42 (3.92) | 1.70 ± 0.39 (1.65) | 3.67 ± 0.87 (3.40) | 1.25 ± 0.50 (1.12) |
| left/left | p | 0.864 | 25/25 | 0 | 25 | 1.39 ± 0.33 (1.46) | 4.83 ± 3.32 (3.68) | 1.95 ± 0.31 (2.02) | 4.25 ± 0.76 (4.51) | 1.62 ± 0.45 (1.72) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.62 ± 0.30 (1.56) | 5.28 ± 3.59 (4.48) | 2.08 ± 0.30 (2.13) | 4.56 ± 0.74 (4.82) | 1.82 ± 0.50 (1.80) |
| back/left | p | 0.847 | 25/25 | 0 | 25 | 2.25 ± 0.25 (2.20) | 4.90 ± 2.95 (4.52) | 2.12 ± 0.24 (2.14) | 4.60 ± 0.67 (4.85) | 1.86 ± 0.45 (1.98) |
| back/right | p | 0.850 | 25/25 | 0 | 25 | 2.22 ± 0.26 (2.22) | 4.81 ± 3.07 (4.34) | 2.11 ± 0.29 (2.25) | 4.53 ± 0.72 (4.94) | 1.82 ± 0.47 (1.91) |
| right/left | p | 0.838 | 25/25 | 0 | 25 | 1.59 ± 0.31 (1.58) | 6.14 ± 2.84 (5.79) | 1.97 ± 0.28 (1.98) | 4.28 ± 0.73 (4.53) | 1.64 ± 0.42 (1.58) |
| right/right | p | 0.850 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.44) | 5.07 ± 3.79 (3.85) | 1.96 ± 0.34 (2.01) | 4.18 ± 0.83 (4.43) | 1.59 ± 0.49 (1.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.873 | 4.9 | 4.73 | 1.90 |
| p | normal | 0.830 | 5.3 | 3.73 | 1.33 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.789 | 0.22 | 2.08 ± 0.65 (1.88) | 3.32 | 1.09 |
| p | medium | 16 | 0.908 | 0.84 | 1.05 ± 0.18 (1.09) | 3.40 | 1.14 |
| p | strong | 126 | 0.873 | 0.63 | - | 4.76 | 1.92 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector right (0.844).
