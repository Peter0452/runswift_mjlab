# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.83 ± 0.60 (1.68) |
| Direction error [°] | 5.40 ± 3.62 (4.87) |
| Avg ball speed [m/s] | 2.41 ± 0.29 (2.42) |
| Peak ball speed [m/s] | 5.29 ± 0.84 (5.61) |
| Distance [m] | 2.35 ± 0.57 (2.40) |
| Path length [m] | 2.36 ± 0.57 (2.41) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.866 | 50/50 | 0 | 48 | 1.25 ± 0.26 (1.26) | 4.91 ± 4.13 (3.63) | 2.35 ± 0.31 (2.38) | 5.21 ± 0.86 (5.51) | 2.26 ± 0.55 (2.44) |
| left | p | 0.864 | 50/50 | 0 | 49 | 1.73 ± 0.35 (1.68) | 5.30 ± 3.43 (4.57) | 2.38 ± 0.27 (2.42) | 5.23 ± 0.81 (5.60) | 2.31 ± 0.55 (2.36) |
| back | p | 0.808 | 50/50 | 0 | 48 | 2.59 ± 0.45 (2.50) | 6.51 ± 3.48 (5.82) | 2.56 ± 0.26 (2.60) | 5.57 ± 0.79 (5.86) | 2.58 ± 0.55 (2.74) |
| right | p | 0.852 | 50/50 | 0 | 50 | 1.73 ± 0.36 (1.67) | 4.88 ± 3.12 (4.19) | 2.37 ± 0.28 (2.37) | 5.15 ± 0.84 (5.48) | 2.24 ± 0.56 (2.31) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 98 | 1.81 ± 0.56 (1.67) | 5.62 ± 3.85 (5.05) | 2.40 ± 0.29 (2.43) | 5.30 ± 0.83 (5.63) | 2.35 ± 0.56 (2.42) |
| right | p | 0.851 | 100/100 | 0 | 97 | 1.84 ± 0.64 (1.74) | 5.18 ± 3.37 (4.58) | 2.43 ± 0.29 (2.41) | 5.28 ± 0.85 (5.59) | 2.35 ± 0.58 (2.39) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.861 | 25/25 | 0 | 24 | 1.23 ± 0.26 (1.24) | 4.99 ± 4.40 (3.62) | 2.31 ± 0.27 (2.42) | 5.17 ± 0.83 (5.58) | 2.22 ± 0.51 (2.41) |
| forward/right | p | 0.872 | 25/25 | 0 | 24 | 1.27 ± 0.26 (1.30) | 4.84 ± 3.85 (3.65) | 2.38 ± 0.34 (2.35) | 5.24 ± 0.88 (5.47) | 2.29 ± 0.58 (2.47) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.67 ± 0.34 (1.62) | 5.71 ± 3.47 (5.09) | 2.39 ± 0.22 (2.42) | 5.27 ± 0.74 (5.61) | 2.34 ± 0.51 (2.37) |
| left/right | p | 0.866 | 25/25 | 0 | 24 | 1.80 ± 0.35 (1.82) | 4.89 ± 3.33 (4.21) | 2.38 ± 0.31 (2.37) | 5.18 ± 0.87 (5.56) | 2.28 ± 0.58 (2.27) |
| back/left | p | 0.810 | 25/25 | 0 | 24 | 2.53 ± 0.25 (2.48) | 6.95 ± 3.90 (6.36) | 2.58 ± 0.29 (2.61) | 5.61 ± 0.81 (5.88) | 2.63 ± 0.57 (2.76) |
| back/right | p | 0.806 | 25/25 | 0 | 24 | 2.65 ± 0.58 (2.52) | 6.07 ± 2.94 (5.69) | 2.54 ± 0.21 (2.55) | 5.52 ± 0.76 (5.85) | 2.53 ± 0.54 (2.49) |
| right/left | p | 0.845 | 25/25 | 0 | 25 | 1.81 ± 0.37 (1.74) | 4.83 ± 3.13 (4.14) | 2.33 ± 0.28 (2.35) | 5.13 ± 0.84 (5.48) | 2.21 ± 0.56 (2.24) |
| right/right | p | 0.859 | 25/25 | 0 | 25 | 1.65 ± 0.32 (1.60) | 4.92 ± 3.12 (4.24) | 2.41 ± 0.27 (2.38) | 5.17 ± 0.84 (5.53) | 2.28 ± 0.56 (2.38) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.886 | 5.5 | 5.87 | 2.69 |
| p | normal | 0.809 | 5.3 | 4.70 | 2.01 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.750 | 0.06 | 2.73 ± 0.86 (2.48) | 4.24 | 1.69 |
| p | medium | 20 | 0.875 | 0.65 | 1.35 ± 0.15 (1.35) | 4.33 | 1.78 |
| p | strong | 126 | 0.885 | 0.79 | - | 5.89 | 2.72 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.808).
