# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u5_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.816** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 177 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.88 ± 1.24 (1.64) |
| Direction error [°] | 11.98 ± 25.99 (4.59) |
| Avg ball speed [m/s] | 2.38 ± 0.73 (2.53) |
| Peak ball speed [m/s] | 5.05 ± 1.65 (5.75) |
| Distance [m] | 2.43 ± 1.06 (2.75) |
| Path length [m] | 2.44 ± 1.06 (2.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.832 | 50/50 | 0 | 44 | 1.42 ± 1.41 (1.28) | 8.22 ± 13.64 (4.25) | 2.26 ± 0.81 (2.38) | 4.82 ± 1.83 (5.07) | 2.28 ± 1.09 (2.25) |
| left | p | 0.843 | 50/50 | 0 | 45 | 1.88 ± 1.49 (1.63) | 11.60 ± 24.29 (4.28) | 2.38 ± 0.69 (2.55) | 5.06 ± 1.58 (5.76) | 2.43 ± 1.05 (2.68) |
| back | p | 0.771 | 49/50 | 0 | 43 | 2.52 ± 1.07 (2.48) | 20.04 ± 40.40 (5.70) | 2.46 ± 0.80 (2.76) | 5.18 ± 1.79 (5.99) | 2.56 ± 1.15 (2.88) |
| right | p | 0.820 | 49/50 | 0 | 45 | 1.72 ± 0.38 (1.74) | 8.16 ± 14.56 (4.35) | 2.44 ± 0.57 (2.49) | 5.13 ± 1.33 (5.62) | 2.46 ± 0.90 (2.66) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.815 | 99/100 | 0 | 88 | 1.85 ± 1.18 (1.60) | 13.10 ± 28.15 (4.32) | 2.39 ± 0.78 (2.62) | 5.06 ± 1.76 (5.88) | 2.46 ± 1.08 (2.86) |
| right | p | 0.818 | 99/100 | 0 | 89 | 1.91 ± 1.30 (1.68) | 10.87 ± 23.59 (4.84) | 2.38 ± 0.68 (2.48) | 5.03 ± 1.54 (5.62) | 2.41 ± 1.03 (2.68) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 22 | 1.22 ± 0.25 (1.28) | 8.55 ± 15.11 (4.17) | 2.25 ± 0.83 (2.32) | 4.79 ± 1.86 (4.77) | 2.25 ± 1.06 (2.24) |
| forward/right | p | 0.827 | 25/25 | 0 | 22 | 1.62 ± 1.96 (1.30) | 7.90 ± 11.97 (4.53) | 2.27 ± 0.80 (2.43) | 4.86 ± 1.80 (5.38) | 2.30 ± 1.11 (2.25) |
| left/left | p | 0.847 | 25/25 | 0 | 23 | 2.07 ± 2.03 (1.60) | 8.11 ± 14.91 (3.51) | 2.49 ± 0.69 (2.70) | 5.31 ± 1.59 (6.04) | 2.62 ± 1.03 (2.88) |
| left/right | p | 0.838 | 25/25 | 0 | 22 | 1.68 ± 0.48 (1.76) | 15.08 ± 30.56 (5.32) | 2.26 ± 0.67 (2.38) | 4.82 ± 1.54 (4.45) | 2.24 ± 1.05 (1.95) |
| back/left | p | 0.782 | 25/25 | 0 | 21 | 2.32 ± 0.68 (2.48) | 25.29 ± 46.11 (5.70) | 2.38 ± 0.91 (2.71) | 5.02 ± 2.00 (5.99) | 2.48 ± 1.25 (2.91) |
| back/right | p | 0.759 | 24/25 | 0 | 22 | 2.73 ± 1.32 (2.48) | 14.58 ± 32.54 (5.56) | 2.55 ± 0.66 (2.76) | 5.35 ± 1.53 (6.04) | 2.65 ± 1.03 (2.87) |
| right/left | p | 0.793 | 24/25 | 0 | 22 | 1.81 ± 0.39 (1.96) | 10.35 ± 19.37 (4.24) | 2.43 ± 0.64 (2.56) | 5.13 ± 1.46 (5.80) | 2.47 ± 0.94 (2.77) |
| right/right | p | 0.848 | 25/25 | 0 | 23 | 1.63 ± 0.35 (1.52) | 6.06 ± 6.79 (4.84) | 2.45 ± 0.50 (2.47) | 5.13 ± 1.18 (5.42) | 2.44 ± 0.86 (2.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.848 | 12.2 | 5.61 | 2.85 |
| p | normal | 0.785 | 11.8 | 4.49 | 2.01 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.733 | 0.09 | 2.61 ± 0.99 (2.47) | 4.02 | 1.65 |
| p | medium | 20 | 0.873 | 0.66 | 1.29 ± 0.22 (1.31) | 4.16 | 1.74 |
| p | strong | 126 | 0.843 | 0.75 | - | 5.63 | 2.87 |

## Notes

- p: score 0.816, 198/200 kicked, 0 fell; worst sector back (0.771).
