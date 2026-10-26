# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s3_ctl7_n7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.838** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.64 ± 0.61 (1.58) |
| Direction error [°] | 7.14 ± 19.30 (3.99) |
| Avg ball speed [m/s] | 1.75 ± 0.31 (1.74) |
| Peak ball speed [m/s] | 4.33 ± 0.75 (4.29) |
| Distance [m] | 1.67 ± 0.47 (1.60) |
| Path length [m] | 1.68 ± 0.47 (1.61) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.822 | 50/50 | 0 | 46 | 1.26 ± 0.75 (1.08) | 11.13 ± 29.27 (4.17) | 1.60 ± 0.26 (1.62) | 4.04 ± 0.66 (3.94) | 1.44 ± 0.41 (1.38) |
| left | p | 0.851 | 50/50 | 0 | 48 | 1.51 ± 0.33 (1.51) | 5.30 ± 4.28 (4.47) | 1.80 ± 0.31 (1.84) | 4.47 ± 0.73 (4.47) | 1.77 ± 0.47 (1.74) |
| back | p | 0.830 | 50/50 | 0 | 49 | 2.29 ± 0.33 (2.25) | 7.72 ± 24.08 (3.07) | 1.82 ± 0.33 (1.84) | 4.45 ± 0.82 (4.41) | 1.79 ± 0.46 (1.73) |
| right | p | 0.849 | 50/50 | 0 | 50 | 1.52 ± 0.31 (1.54) | 4.39 ± 2.91 (3.92) | 1.77 ± 0.29 (1.75) | 4.38 ± 0.70 (4.36) | 1.69 ± 0.45 (1.62) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.64 ± 0.57 (1.59) | 6.22 ± 17.26 (3.82) | 1.73 ± 0.34 (1.72) | 4.29 ± 0.82 (4.12) | 1.66 ± 0.52 (1.56) |
| right | p | 0.832 | 100/100 | 0 | 94 | 1.64 ± 0.64 (1.51) | 8.05 ± 21.11 (4.03) | 1.77 ± 0.27 (1.76) | 4.38 ± 0.67 (4.39) | 1.68 ± 0.41 (1.62) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.28 ± 0.67 (1.08) | 4.15 ± 3.56 (2.24) | 1.57 ± 0.28 (1.56) | 3.95 ± 0.70 (3.82) | 1.40 ± 0.46 (1.35) |
| forward/right | p | 0.798 | 25/25 | 0 | 21 | 1.24 ± 0.83 (1.08) | 18.11 ± 40.03 (5.73) | 1.64 ± 0.23 (1.68) | 4.12 ± 0.61 (4.21) | 1.48 ± 0.36 (1.47) |
| left/left | p | 0.847 | 25/25 | 0 | 25 | 1.41 ± 0.32 (1.46) | 5.39 ± 3.09 (4.68) | 1.75 ± 0.34 (1.74) | 4.37 ± 0.74 (4.11) | 1.70 ± 0.51 (1.49) |
| left/right | p | 0.855 | 25/25 | 0 | 23 | 1.60 ± 0.31 (1.54) | 5.21 ± 5.21 (3.84) | 1.86 ± 0.26 (1.87) | 4.57 ± 0.71 (4.59) | 1.83 ± 0.42 (1.96) |
| back/left | p | 0.832 | 25/25 | 0 | 24 | 2.27 ± 0.32 (2.24) | 11.34 ± 33.56 (3.14) | 1.79 ± 0.39 (1.84) | 4.37 ± 0.96 (4.35) | 1.75 ± 0.52 (1.74) |
| back/right | p | 0.829 | 25/25 | 0 | 25 | 2.30 ± 0.34 (2.30) | 4.11 ± 2.79 (3.00) | 1.85 ± 0.25 (1.84) | 4.54 ± 0.64 (4.65) | 1.82 ± 0.39 (1.72) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.60 ± 0.27 (1.64) | 4.02 ± 2.65 (3.78) | 1.81 ± 0.30 (1.78) | 4.46 ± 0.76 (4.31) | 1.77 ± 0.52 (1.70) |
| right/right | p | 0.848 | 25/25 | 0 | 25 | 1.43 ± 0.32 (1.46) | 4.76 ± 3.10 (4.03) | 1.73 ± 0.26 (1.74) | 4.30 ± 0.63 (4.38) | 1.61 ± 0.36 (1.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.873 | 5.9 | 4.68 | 1.87 |
| p | normal | 0.804 | 8.3 | 3.99 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.754 | 0.14 | 2.39 ± 0.73 (2.30) | 3.74 | 1.33 |
| p | medium | 18 | 0.879 | 0.78 | 1.19 ± 0.16 (1.20) | 3.80 | 1.37 |
| p | strong | 124 | 0.872 | 0.63 | - | 4.69 | 1.87 |

## Notes

- p: score 0.838, 200/200 kicked, 0 fell; worst sector forward (0.822).
