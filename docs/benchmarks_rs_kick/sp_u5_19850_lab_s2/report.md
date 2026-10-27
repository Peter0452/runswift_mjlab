# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u5_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.55 (1.53) |
| Direction error [°] | 5.18 ± 11.72 (3.33) |
| Avg ball speed [m/s] | 1.84 ± 0.34 (1.88) |
| Peak ball speed [m/s] | 4.50 ± 0.81 (4.69) |
| Distance [m] | 1.88 ± 0.70 (1.86) |
| Path length [m] | 1.90 ± 0.71 (1.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.834 | 50/50 | 0 | 46 | 1.08 ± 0.45 (1.01) | 6.15 ± 4.81 (4.16) | 1.70 ± 0.33 (1.71) | 4.23 ± 0.81 (4.25) | 1.71 ± 0.73 (1.53) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.49 ± 0.35 (1.47) | 3.58 ± 2.71 (2.85) | 1.84 ± 0.30 (1.89) | 4.47 ± 0.70 (4.66) | 1.85 ± 0.62 (1.79) |
| back | p | 0.843 | 50/50 | 0 | 48 | 2.24 ± 0.30 (2.23) | 7.16 ± 22.46 (2.90) | 1.95 ± 0.41 (2.00) | 4.72 ± 0.87 (4.97) | 2.06 ± 0.64 (2.10) |
| right | p | 0.874 | 50/50 | 0 | 50 | 1.50 ± 0.32 (1.58) | 3.84 ± 2.21 (3.39) | 1.87 ± 0.28 (1.89) | 4.56 ± 0.75 (4.79) | 1.91 ± 0.74 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.861 | 100/100 | 0 | 99 | 1.60 ± 0.57 (1.58) | 4.19 ± 3.12 (3.33) | 1.87 ± 0.33 (1.89) | 4.56 ± 0.75 (4.76) | 1.93 ± 0.70 (1.94) |
| right | p | 0.848 | 100/100 | 0 | 95 | 1.55 ± 0.53 (1.51) | 6.17 ± 16.21 (3.36) | 1.81 ± 0.36 (1.82) | 4.43 ± 0.85 (4.66) | 1.84 ± 0.68 (1.77) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.828 | 25/25 | 0 | 24 | 1.15 ± 0.58 (1.04) | 5.89 ± 4.11 (5.12) | 1.73 ± 0.35 (1.67) | 4.19 ± 0.81 (4.24) | 1.67 ± 0.56 (1.47) |
| forward/right | p | 0.839 | 25/25 | 0 | 22 | 1.01 ± 0.24 (0.96) | 6.40 ± 5.41 (4.15) | 1.68 ± 0.31 (1.72) | 4.26 ± 0.81 (4.37) | 1.75 ± 0.86 (1.55) |
| left/left | p | 0.871 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.38) | 3.60 ± 3.11 (2.66) | 1.81 ± 0.30 (1.89) | 4.43 ± 0.69 (4.56) | 1.80 ± 0.63 (1.74) |
| left/right | p | 0.860 | 25/25 | 0 | 25 | 1.57 ± 0.34 (1.54) | 3.56 ± 2.23 (3.44) | 1.86 ± 0.30 (1.92) | 4.52 ± 0.71 (4.67) | 1.90 ± 0.61 (1.88) |
| back/left | p | 0.866 | 25/25 | 0 | 25 | 2.26 ± 0.29 (2.28) | 3.40 ± 2.00 (2.67) | 2.03 ± 0.32 (2.10) | 4.90 ± 0.63 (5.17) | 2.13 ± 0.55 (2.13) |
| back/right | p | 0.821 | 25/25 | 0 | 23 | 2.22 ± 0.31 (2.22) | 10.93 ± 31.25 (2.99) | 1.88 ± 0.46 (1.95) | 4.55 ± 1.03 (4.79) | 1.99 ± 0.70 (2.06) |
| right/left | p | 0.877 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.60) | 3.88 ± 2.13 (3.43) | 1.89 ± 0.27 (1.89) | 4.72 ± 0.67 (4.95) | 2.12 ± 0.90 (1.98) |
| right/right | p | 0.871 | 25/25 | 0 | 25 | 1.41 ± 0.31 (1.48) | 3.80 ± 2.28 (3.06) | 1.84 ± 0.29 (1.90) | 4.39 ± 0.79 (4.74) | 1.71 ± 0.46 (1.79) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.877 | 6.1 | 4.89 | 2.14 |
| p | normal | 0.831 | 4.2 | 4.10 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.787 | 0.17 | 2.27 ± 0.72 (2.14) | 3.73 | 1.37 |
| p | medium | 15 | 0.911 | 0.78 | 1.17 ± 0.16 (1.21) | 3.83 | 1.43 |
| p | strong | 125 | 0.880 | 0.66 | - | 4.94 | 2.19 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector forward (0.834).
