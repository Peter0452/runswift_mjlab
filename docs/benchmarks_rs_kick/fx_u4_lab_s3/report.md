# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.861** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.63 ± 0.56 (1.61) |
| Direction error [°] | 5.24 ± 3.28 (4.78) |
| Avg ball speed [m/s] | 2.06 ± 0.51 (2.25) |
| Peak ball speed [m/s] | 4.44 ± 1.18 (4.97) |
| Distance [m] | 1.88 ± 0.79 (2.20) |
| Path length [m] | 1.89 ± 0.79 (2.21) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.869 | 50/50 | 0 | 49 | 1.04 ± 0.23 (1.03) | 5.26 ± 3.32 (4.62) | 1.88 ± 0.49 (2.03) | 4.08 ± 1.12 (4.60) | 1.62 ± 0.72 (1.83) |
| left | p | 0.866 | 50/50 | 0 | 50 | 1.59 ± 0.35 (1.60) | 5.50 ± 3.53 (4.83) | 2.16 ± 0.47 (2.31) | 4.67 ± 1.10 (5.17) | 2.05 ± 0.75 (2.25) |
| back | p | 0.845 | 50/50 | 0 | 50 | 2.33 ± 0.32 (2.30) | 5.41 ± 2.68 (5.57) | 2.12 ± 0.49 (2.42) | 4.54 ± 1.17 (5.24) | 1.97 ± 0.80 (2.37) |
| right | p | 0.863 | 50/50 | 0 | 49 | 1.58 ± 0.33 (1.62) | 4.77 ± 3.48 (4.03) | 2.07 ± 0.54 (2.37) | 4.45 ± 1.24 (5.27) | 1.89 ± 0.81 (2.26) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.865 | 100/100 | 0 | 100 | 1.63 ± 0.54 (1.61) | 5.04 ± 2.99 (4.73) | 2.06 ± 0.51 (2.29) | 4.45 ± 1.18 (5.00) | 1.90 ± 0.79 (2.23) |
| right | p | 0.857 | 100/100 | 0 | 98 | 1.64 ± 0.57 (1.61) | 5.43 ± 3.54 (4.79) | 2.06 ± 0.51 (2.24) | 4.42 ± 1.18 (4.96) | 1.87 ± 0.78 (2.16) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.877 | 25/25 | 0 | 25 | 1.05 ± 0.23 (1.02) | 4.75 ± 2.73 (4.56) | 1.88 ± 0.49 (2.09) | 4.09 ± 1.11 (4.67) | 1.63 ± 0.73 (1.85) |
| forward/right | p | 0.861 | 25/25 | 0 | 24 | 1.03 ± 0.22 (1.08) | 5.77 ± 3.74 (4.86) | 1.88 ± 0.49 (1.98) | 4.06 ± 1.12 (4.40) | 1.61 ± 0.70 (1.71) |
| left/left | p | 0.868 | 25/25 | 0 | 25 | 1.47 ± 0.32 (1.50) | 5.43 ± 3.58 (4.80) | 2.18 ± 0.46 (2.35) | 4.71 ± 1.07 (5.17) | 2.07 ± 0.73 (2.35) |
| left/right | p | 0.865 | 25/25 | 0 | 25 | 1.72 ± 0.34 (1.72) | 5.57 ± 3.48 (4.97) | 2.15 ± 0.48 (2.24) | 4.64 ± 1.12 (4.97) | 2.04 ± 0.78 (2.21) |
| back/left | p | 0.853 | 25/25 | 0 | 25 | 2.32 ± 0.30 (2.28) | 5.49 ± 2.65 (5.38) | 2.15 ± 0.49 (2.39) | 4.60 ± 1.17 (5.22) | 2.02 ± 0.83 (2.39) |
| back/right | p | 0.837 | 25/25 | 0 | 25 | 2.34 ± 0.35 (2.32) | 5.34 ± 2.71 (5.78) | 2.10 ± 0.49 (2.43) | 4.47 ± 1.17 (5.26) | 1.92 ± 0.76 (2.36) |
| right/left | p | 0.861 | 25/25 | 0 | 25 | 1.68 ± 0.29 (1.72) | 4.51 ± 2.76 (4.56) | 2.05 ± 0.55 (2.36) | 4.40 ± 1.26 (5.28) | 1.87 ± 0.81 (2.38) |
| right/right | p | 0.864 | 25/25 | 0 | 24 | 1.48 ± 0.34 (1.38) | 5.03 ± 4.06 (3.00) | 2.09 ± 0.53 (2.38) | 4.50 ± 1.22 (5.19) | 1.92 ± 0.80 (2.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 5.1 | 5.31 | 2.45 |
| p | normal | 0.837 | 5.4 | 3.56 | 1.31 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.795 | 0.28 | 1.88 ± 0.53 (1.89) | 2.99 | 0.94 |
| p | medium | 18 | 0.908 | 0.89 | 0.97 ± 0.14 (1.00) | 3.10 | 0.99 |
| p | strong | 124 | 0.885 | 0.71 | - | 5.31 | 2.45 |

## Notes

- p: score 0.861, 200/200 kicked, 0 fell; worst sector back (0.845).
