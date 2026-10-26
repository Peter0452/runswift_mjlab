# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_21-10-41_control_h022_500/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.53 ± 0.50 (1.46) |
| Direction error [°] | 6.07 ± 3.87 (5.11) |
| Avg ball speed [m/s] | 1.78 ± 0.32 (1.85) |
| Peak ball speed [m/s] | 3.91 ± 0.75 (4.04) |
| Distance [m] | 1.33 ± 0.43 (1.38) |
| Path length [m] | 1.34 ± 0.43 (1.38) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.842 | 50/50 | 0 | 49 | 1.02 ± 0.23 (1.04) | 5.10 ± 3.53 (4.03) | 1.54 ± 0.36 (1.58) | 3.40 ± 0.73 (3.49) | 1.02 ± 0.42 (1.03) |
| left | p | 0.856 | 50/50 | 0 | 48 | 1.45 ± 0.32 (1.47) | 6.04 ± 4.27 (4.63) | 1.86 ± 0.27 (1.91) | 4.09 ± 0.67 (4.28) | 1.44 ± 0.37 (1.51) |
| back | p | 0.830 | 50/50 | 0 | 50 | 2.18 ± 0.24 (2.13) | 6.60 ± 3.20 (7.29) | 1.93 ± 0.23 (2.03) | 4.25 ± 0.61 (4.54) | 1.54 ± 0.36 (1.59) |
| right | p | 0.832 | 50/50 | 0 | 48 | 1.46 ± 0.32 (1.46) | 6.55 ± 4.19 (5.84) | 1.79 ± 0.27 (1.86) | 3.90 ± 0.69 (4.05) | 1.33 ± 0.36 (1.39) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.839 | 100/100 | 0 | 99 | 1.53 ± 0.50 (1.47) | 6.09 ± 3.79 (4.79) | 1.80 ± 0.30 (1.84) | 3.95 ± 0.71 (4.02) | 1.35 ± 0.41 (1.38) |
| right | p | 0.840 | 100/100 | 0 | 96 | 1.53 ± 0.50 (1.46) | 6.06 ± 3.95 (5.44) | 1.76 ± 0.34 (1.85) | 3.87 ± 0.78 (4.05) | 1.31 ± 0.44 (1.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 25 | 1.02 ± 0.22 (1.04) | 5.54 ± 3.14 (4.71) | 1.55 ± 0.34 (1.67) | 3.41 ± 0.68 (3.57) | 1.03 ± 0.41 (1.04) |
| forward/right | p | 0.846 | 25/25 | 0 | 24 | 1.03 ± 0.24 (1.04) | 4.66 ± 3.82 (3.43) | 1.53 ± 0.38 (1.56) | 3.38 ± 0.77 (3.34) | 1.01 ± 0.42 (1.03) |
| left/left | p | 0.843 | 25/25 | 0 | 24 | 1.37 ± 0.32 (1.42) | 6.72 ± 4.71 (4.65) | 1.83 ± 0.22 (1.85) | 4.01 ± 0.59 (4.14) | 1.39 ± 0.32 (1.40) |
| left/right | p | 0.869 | 25/25 | 0 | 24 | 1.53 ± 0.30 (1.50) | 5.36 ± 3.66 (4.01) | 1.88 ± 0.31 (1.99) | 4.16 ± 0.73 (4.50) | 1.49 ± 0.41 (1.53) |
| back/left | p | 0.832 | 25/25 | 0 | 25 | 2.19 ± 0.23 (2.12) | 6.41 ± 3.26 (5.35) | 1.98 ± 0.17 (2.06) | 4.33 ± 0.51 (4.58) | 1.60 ± 0.32 (1.75) |
| back/right | p | 0.828 | 25/25 | 0 | 25 | 2.17 ± 0.26 (2.14) | 6.79 ± 3.12 (7.62) | 1.89 ± 0.27 (1.97) | 4.17 ± 0.69 (4.37) | 1.48 ± 0.39 (1.54) |
| right/left | p | 0.845 | 25/25 | 0 | 25 | 1.54 ± 0.30 (1.52) | 5.67 ± 3.71 (4.01) | 1.83 ± 0.28 (1.96) | 4.03 ± 0.71 (4.33) | 1.39 ± 0.37 (1.40) |
| right/right | p | 0.818 | 25/25 | 0 | 23 | 1.39 ± 0.33 (1.42) | 7.44 ± 4.46 (6.38) | 1.74 ± 0.26 (1.78) | 3.78 ± 0.63 (3.83) | 1.27 ± 0.34 (1.25) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.850 | 6.2 | 4.31 | 1.54 |
| p | normal | 0.829 | 6.0 | 3.51 | 1.13 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.797 | 0.29 | 1.97 ± 0.68 (1.83) | 3.12 | 0.92 |
| p | medium | 16 | 0.893 | 0.84 | 1.02 ± 0.19 (1.07) | 3.33 | 1.05 |
| p | strong | 126 | 0.852 | 0.58 | - | 4.35 | 1.56 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector back (0.830).
