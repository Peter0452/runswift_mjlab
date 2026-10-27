# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w1_u6_tail19850_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.857** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.56 (1.49) |
| Direction error [°] | 4.82 ± 11.52 (3.23) |
| Avg ball speed [m/s] | 1.72 ± 0.32 (1.73) |
| Peak ball speed [m/s] | 4.44 ± 0.83 (4.66) |
| Distance [m] | 1.74 ± 0.49 (1.77) |
| Path length [m] | 1.75 ± 0.50 (1.77) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.843 | 50/50 | 0 | 49 | 1.03 ± 0.22 (1.06) | 4.57 ± 3.38 (3.17) | 1.55 ± 0.31 (1.53) | 4.01 ± 0.74 (3.83) | 1.47 ± 0.47 (1.33) |
| left | p | 0.871 | 50/50 | 0 | 50 | 1.60 ± 0.57 (1.52) | 3.95 ± 2.44 (3.66) | 1.80 ± 0.31 (1.89) | 4.61 ± 0.78 (4.94) | 1.87 ± 0.48 (1.97) |
| back | p | 0.867 | 50/50 | 0 | 49 | 2.20 ± 0.25 (2.16) | 5.77 ± 22.43 (2.15) | 1.80 ± 0.30 (1.82) | 4.73 ± 0.87 (5.06) | 1.93 ± 0.47 (2.03) |
| right | p | 0.848 | 50/50 | 0 | 50 | 1.48 ± 0.33 (1.46) | 4.98 ± 2.94 (4.53) | 1.71 ± 0.27 (1.71) | 4.40 ± 0.74 (4.68) | 1.72 ± 0.43 (1.71) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.862 | 100/100 | 0 | 100 | 1.56 ± 0.52 (1.51) | 4.04 ± 2.89 (3.16) | 1.73 ± 0.27 (1.74) | 4.50 ± 0.73 (4.71) | 1.77 ± 0.45 (1.79) |
| right | p | 0.853 | 100/100 | 0 | 98 | 1.59 ± 0.59 (1.48) | 5.59 ± 16.00 (3.30) | 1.70 ± 0.36 (1.72) | 4.38 ± 0.91 (4.62) | 1.72 ± 0.53 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 4.59 ± 3.33 (3.13) | 1.59 ± 0.28 (1.62) | 4.10 ± 0.63 (3.91) | 1.51 ± 0.41 (1.35) |
| forward/right | p | 0.839 | 25/25 | 0 | 24 | 1.02 ± 0.22 (1.04) | 4.55 ± 3.43 (3.26) | 1.52 ± 0.33 (1.43) | 3.92 ± 0.83 (3.74) | 1.43 ± 0.52 (1.32) |
| left/left | p | 0.876 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.44) | 3.85 ± 2.65 (2.83) | 1.80 ± 0.25 (1.85) | 4.58 ± 0.69 (4.83) | 1.83 ± 0.44 (1.94) |
| left/right | p | 0.866 | 25/25 | 0 | 25 | 1.80 ± 0.68 (1.62) | 4.04 ± 2.21 (3.76) | 1.81 ± 0.36 (1.93) | 4.65 ± 0.85 (4.95) | 1.90 ± 0.52 (1.98) |
| back/left | p | 0.879 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.18) | 1.95 ± 1.12 (1.76) | 1.85 ± 0.20 (1.80) | 4.92 ± 0.62 (5.14) | 2.03 ± 0.40 (2.11) |
| back/right | p | 0.856 | 25/25 | 0 | 24 | 2.16 ± 0.24 (2.08) | 9.58 ± 31.24 (2.39) | 1.76 ± 0.37 (1.84) | 4.55 ± 1.02 (4.80) | 1.82 ± 0.51 (1.91) |
| right/left | p | 0.844 | 25/25 | 0 | 25 | 1.57 ± 0.29 (1.56) | 5.77 ± 2.50 (5.18) | 1.70 ± 0.25 (1.74) | 4.41 ± 0.74 (4.80) | 1.71 ± 0.39 (1.79) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.42) | 4.19 ± 3.12 (3.65) | 1.72 ± 0.29 (1.67) | 4.39 ± 0.74 (4.40) | 1.73 ± 0.46 (1.65) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.886 | 4.1 | 4.90 | 2.00 |
| p | normal | 0.829 | 5.5 | 3.98 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.781 | 0.14 | 2.27 ± 0.73 (2.10) | 3.61 | 1.28 |
| p | medium | 16 | 0.922 | 0.83 | 1.13 ± 0.15 (1.13) | 3.69 | 1.32 |
| p | strong | 126 | 0.884 | 0.66 | - | 4.92 | 2.01 |

## Notes

- p: score 0.857, 200/200 kicked, 0 fell; worst sector forward (0.843).
