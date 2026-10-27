# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v3_s8_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.858** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.84 ± 0.57 (1.72) |
| Direction error [°] | 6.14 ± 12.55 (4.85) |
| Avg ball speed [m/s] | 2.53 ± 0.52 (2.69) |
| Peak ball speed [m/s] | 5.40 ± 1.29 (6.07) |
| Distance [m] | 2.62 ± 0.92 (2.97) |
| Path length [m] | 2.64 ± 0.93 (2.99) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.883 | 50/50 | 0 | 50 | 1.26 ± 0.25 (1.27) | 4.34 ± 3.34 (3.34) | 2.46 ± 0.43 (2.62) | 5.33 ± 1.16 (5.97) | 2.52 ± 0.82 (2.85) |
| left | p | 0.869 | 50/50 | 0 | 49 | 1.77 ± 0.36 (1.72) | 5.57 ± 4.50 (5.17) | 2.51 ± 0.55 (2.74) | 5.32 ± 1.36 (6.11) | 2.60 ± 0.96 (3.00) |
| back | p | 0.816 | 50/50 | 0 | 47 | 2.53 ± 0.39 (2.52) | 10.18 ± 23.79 (6.62) | 2.69 ± 0.61 (2.90) | 5.70 ± 1.41 (6.38) | 2.91 ± 0.99 (3.39) |
| right | p | 0.865 | 50/50 | 0 | 49 | 1.78 ± 0.36 (1.75) | 4.46 ± 3.18 (3.64) | 2.45 ± 0.42 (2.57) | 5.22 ± 1.15 (5.83) | 2.47 ± 0.85 (2.80) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.855 | 100/100 | 0 | 99 | 1.84 ± 0.57 (1.72) | 5.39 ± 3.98 (4.57) | 2.52 ± 0.51 (2.72) | 5.43 ± 1.27 (6.11) | 2.64 ± 0.92 (2.96) |
| right | p | 0.862 | 100/100 | 0 | 96 | 1.83 ± 0.57 (1.71) | 6.89 ± 17.27 (5.17) | 2.53 ± 0.53 (2.66) | 5.36 ± 1.30 (5.99) | 2.61 ± 0.93 (2.97) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.880 | 25/25 | 0 | 25 | 1.23 ± 0.25 (1.24) | 4.24 ± 3.37 (3.29) | 2.39 ± 0.41 (2.56) | 5.24 ± 1.16 (5.95) | 2.44 ± 0.81 (2.83) |
| forward/right | p | 0.886 | 25/25 | 0 | 25 | 1.29 ± 0.25 (1.30) | 4.43 ± 3.30 (4.98) | 2.52 ± 0.44 (2.69) | 5.43 ± 1.15 (5.98) | 2.60 ± 0.82 (2.88) |
| left/left | p | 0.859 | 25/25 | 0 | 24 | 1.68 ± 0.35 (1.66) | 6.75 ± 5.36 (5.40) | 2.51 ± 0.63 (2.75) | 5.35 ± 1.53 (6.14) | 2.65 ± 1.03 (3.29) |
| left/right | p | 0.879 | 25/25 | 0 | 25 | 1.86 ± 0.35 (1.84) | 4.39 ± 3.00 (5.07) | 2.52 ± 0.45 (2.58) | 5.30 ± 1.16 (5.95) | 2.55 ± 0.88 (2.97) |
| back/left | p | 0.819 | 25/25 | 0 | 25 | 2.57 ± 0.26 (2.52) | 6.63 ± 3.24 (6.82) | 2.74 ± 0.47 (2.91) | 5.85 ± 1.12 (6.43) | 2.98 ± 0.88 (3.43) |
| back/right | p | 0.814 | 25/25 | 0 | 22 | 2.50 ± 0.49 (2.40) | 13.74 ± 33.12 (6.12) | 2.63 ± 0.72 (2.82) | 5.56 ± 1.64 (6.25) | 2.84 ± 1.09 (3.31) |
| right/left | p | 0.862 | 25/25 | 0 | 25 | 1.86 ± 0.36 (1.80) | 3.94 ± 2.47 (3.10) | 2.46 ± 0.42 (2.54) | 5.28 ± 1.14 (5.78) | 2.49 ± 0.84 (2.71) |
| right/right | p | 0.869 | 25/25 | 0 | 24 | 1.69 ± 0.33 (1.62) | 4.99 ± 3.69 (3.66) | 2.44 ± 0.42 (2.61) | 5.16 ± 1.15 (5.91) | 2.45 ± 0.86 (2.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.891 | 6.0 | 6.24 | 3.23 |
| p | normal | 0.826 | 6.3 | 4.55 | 2.02 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.771 | 0.11 | 2.50 ± 0.87 (2.42) | 3.88 | 1.52 |
| p | medium | 20 | 0.891 | 0.75 | 1.25 ± 0.17 (1.29) | 3.99 | 1.60 |
| p | strong | 126 | 0.891 | 0.84 | - | 6.27 | 3.26 |

## Notes

- p: score 0.858, 200/200 kicked, 0 fell; worst sector back (0.816).
