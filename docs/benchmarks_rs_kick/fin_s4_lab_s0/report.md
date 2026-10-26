# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.56 ± 0.51 (1.48) |
| Direction error [°] | 6.34 ± 12.52 (4.92) |
| Avg ball speed [m/s] | 1.86 ± 0.38 (1.95) |
| Peak ball speed [m/s] | 4.04 ± 0.91 (4.14) |
| Distance [m] | 1.44 ± 0.51 (1.47) |
| Path length [m] | 1.44 ± 0.51 (1.47) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 50/50 | 0 | 49 | 1.03 ± 0.22 (1.07) | 4.36 ± 3.84 (3.10) | 1.58 ± 0.37 (1.53) | 3.41 ± 0.84 (3.23) | 1.06 ± 0.46 (0.96) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.49) | 5.86 ± 3.75 (5.90) | 1.94 ± 0.30 (2.07) | 4.24 ± 0.75 (4.55) | 1.55 ± 0.44 (1.66) |
| back | p | 0.831 | 50/50 | 0 | 49 | 2.22 ± 0.24 (2.19) | 9.44 ± 23.85 (6.16) | 2.02 ± 0.37 (2.14) | 4.40 ± 0.91 (4.80) | 1.69 ± 0.48 (1.79) |
| right | p | 0.843 | 50/50 | 0 | 49 | 1.50 ± 0.33 (1.46) | 5.72 ± 3.90 (4.46) | 1.88 ± 0.32 (1.95) | 4.09 ± 0.81 (4.18) | 1.45 ± 0.43 (1.44) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 99 | 1.57 ± 0.53 (1.49) | 5.58 ± 3.58 (4.78) | 1.89 ± 0.33 (1.96) | 4.11 ± 0.82 (4.19) | 1.47 ± 0.48 (1.43) |
| right | p | 0.846 | 100/100 | 0 | 98 | 1.55 ± 0.50 (1.46) | 7.11 ± 17.31 (5.15) | 1.82 ± 0.42 (1.93) | 3.96 ± 0.99 (4.08) | 1.40 ± 0.53 (1.49) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.08) | 4.40 ± 2.89 (3.65) | 1.65 ± 0.28 (1.57) | 3.52 ± 0.62 (3.41) | 1.11 ± 0.37 (1.00) |
| forward/right | p | 0.855 | 25/25 | 0 | 24 | 1.02 ± 0.22 (1.06) | 4.32 ± 4.61 (2.55) | 1.51 ± 0.43 (1.43) | 3.31 ± 1.01 (3.08) | 1.01 ± 0.53 (0.87) |
| left/left | p | 0.848 | 25/25 | 0 | 25 | 1.40 ± 0.34 (1.46) | 6.53 ± 4.57 (6.41) | 1.89 ± 0.30 (2.00) | 4.10 ± 0.72 (4.36) | 1.47 ± 0.43 (1.53) |
| left/right | p | 0.871 | 25/25 | 0 | 25 | 1.60 ± 0.30 (1.58) | 5.19 ± 2.52 (5.37) | 1.99 ± 0.30 (2.10) | 4.39 ± 0.76 (4.75) | 1.63 ± 0.43 (1.71) |
| back/left | p | 0.835 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.18) | 6.04 ± 2.41 (5.53) | 2.09 ± 0.24 (2.22) | 4.56 ± 0.67 (4.84) | 1.77 ± 0.42 (1.85) |
| back/right | p | 0.827 | 25/25 | 0 | 24 | 2.19 ± 0.22 (2.20) | 12.84 ± 33.30 (6.32) | 1.95 ± 0.46 (2.11) | 4.24 ± 1.07 (4.78) | 1.60 ± 0.52 (1.70) |
| right/left | p | 0.854 | 25/25 | 0 | 24 | 1.60 ± 0.30 (1.56) | 5.36 ± 3.69 (4.42) | 1.94 ± 0.33 (2.05) | 4.26 ± 0.89 (4.64) | 1.55 ± 0.46 (1.64) |
| right/right | p | 0.831 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.42) | 6.08 ± 4.07 (4.50) | 1.82 ± 0.29 (1.85) | 3.91 ± 0.70 (3.90) | 1.36 ± 0.38 (1.38) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.861 | 5.5 | 4.49 | 1.66 |
| p | normal | 0.831 | 7.2 | 3.58 | 1.21 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.792 | 0.26 | 1.99 ± 0.74 (1.86) | 3.15 | 0.98 |
| p | medium | 16 | 0.910 | 0.86 | 1.02 ± 0.18 (1.03) | 3.32 | 1.06 |
| p | strong | 126 | 0.863 | 0.60 | - | 4.53 | 1.70 |

## Notes

- p: score 0.846, 200/200 kicked, 0 fell; worst sector back (0.831).
