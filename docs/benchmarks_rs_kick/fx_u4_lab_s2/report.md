# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.862** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.63 ± 0.54 (1.62) |
| Direction error [°] | 7.42 ± 19.29 (4.67) |
| Avg ball speed [m/s] | 2.03 ± 0.59 (2.26) |
| Peak ball speed [m/s] | 4.37 ± 1.33 (5.03) |
| Distance [m] | 1.85 ± 0.84 (2.17) |
| Path length [m] | 1.85 ± 0.84 (2.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.879 | 50/50 | 0 | 50 | 1.07 ± 0.27 (1.04) | 4.38 ± 2.80 (3.68) | 1.88 ± 0.53 (1.95) | 4.10 ± 1.23 (4.39) | 1.62 ± 0.77 (1.68) |
| left | p | 0.871 | 50/50 | 0 | 50 | 1.58 ± 0.39 (1.63) | 4.63 ± 3.00 (3.57) | 2.06 ± 0.53 (2.33) | 4.44 ± 1.21 (5.03) | 1.87 ± 0.79 (2.22) |
| back | p | 0.823 | 50/50 | 0 | 47 | 2.27 ± 0.31 (2.27) | 15.56 ± 37.05 (6.31) | 2.10 ± 0.68 (2.46) | 4.52 ± 1.53 (5.36) | 2.01 ± 0.91 (2.43) |
| right | p | 0.877 | 50/50 | 0 | 50 | 1.60 ± 0.36 (1.64) | 5.10 ± 3.18 (4.76) | 2.07 ± 0.56 (2.34) | 4.44 ± 1.28 (5.18) | 1.88 ± 0.84 (2.28) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.871 | 100/100 | 0 | 99 | 1.63 ± 0.54 (1.65) | 6.46 ± 14.92 (4.35) | 2.08 ± 0.58 (2.35) | 4.50 ± 1.31 (5.17) | 1.93 ± 0.84 (2.29) |
| right | p | 0.854 | 100/100 | 0 | 98 | 1.62 ± 0.55 (1.61) | 8.38 ± 22.80 (4.90) | 1.97 ± 0.59 (2.11) | 4.25 ± 1.34 (4.65) | 1.77 ± 0.83 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.881 | 25/25 | 0 | 25 | 1.07 ± 0.26 (1.06) | 3.91 ± 2.48 (2.93) | 1.83 ± 0.53 (1.94) | 4.01 ± 1.26 (4.38) | 1.56 ± 0.78 (1.67) |
| forward/right | p | 0.876 | 25/25 | 0 | 25 | 1.07 ± 0.29 (1.00) | 4.86 ± 3.02 (4.55) | 1.92 ± 0.52 (2.00) | 4.18 ± 1.19 (4.52) | 1.67 ± 0.74 (1.70) |
| left/left | p | 0.876 | 25/25 | 0 | 25 | 1.46 ± 0.35 (1.44) | 4.83 ± 2.93 (3.60) | 2.02 ± 0.57 (2.34) | 4.40 ± 1.28 (5.04) | 1.85 ± 0.81 (2.20) |
| left/right | p | 0.866 | 25/25 | 0 | 25 | 1.69 ± 0.39 (1.64) | 4.43 ± 3.05 (3.42) | 2.10 ± 0.48 (2.28) | 4.47 ± 1.13 (5.03) | 1.90 ± 0.76 (2.25) |
| back/left | p | 0.837 | 25/25 | 0 | 24 | 2.29 ± 0.27 (2.30) | 12.09 ± 28.70 (6.33) | 2.26 ± 0.60 (2.51) | 4.86 ± 1.34 (5.46) | 2.22 ± 0.80 (2.50) |
| back/right | p | 0.808 | 25/25 | 0 | 23 | 2.25 ± 0.34 (2.24) | 19.03 ± 43.56 (6.29) | 1.94 ± 0.73 (2.24) | 4.19 ± 1.64 (5.06) | 1.80 ± 0.97 (2.11) |
| right/left | p | 0.888 | 25/25 | 0 | 25 | 1.71 ± 0.33 (1.74) | 5.02 ± 3.05 (5.21) | 2.20 ± 0.51 (2.46) | 4.72 ± 1.20 (5.42) | 2.07 ± 0.81 (2.48) |
| right/right | p | 0.865 | 25/25 | 0 | 25 | 1.49 ± 0.35 (1.56) | 5.18 ± 3.31 (4.20) | 1.94 ± 0.57 (2.05) | 4.15 ± 1.31 (4.48) | 1.70 ± 0.82 (1.95) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.884 | 6.6 | 5.26 | 2.40 |
| p | normal | 0.841 | 8.2 | 3.49 | 1.29 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.810 | 0.36 | 1.73 ± 0.63 (1.62) | 2.83 | 0.87 |
| p | medium | 15 | 0.904 | 0.82 | 0.90 ± 0.24 (0.88) | 2.93 | 0.91 |
| p | strong | 125 | 0.882 | 0.71 | - | 5.29 | 2.42 |

## Notes

- p: score 0.862, 200/200 kicked, 0 fell; worst sector back (0.823).
