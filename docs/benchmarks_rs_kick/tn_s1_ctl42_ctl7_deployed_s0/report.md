# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s1_ctl42_ctl7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.762** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.90 ± 1.40 (1.67) |
| Direction error [°] | 19.32 ± 36.23 (7.03) |
| Avg ball speed [m/s] | 1.96 ± 0.59 (2.16) |
| Peak ball speed [m/s] | 4.35 ± 1.42 (4.76) |
| Distance [m] | 1.64 ± 0.73 (1.77) |
| Path length [m] | 1.65 ± 0.73 (1.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.772 | 49/50 | 0 | 42 | 1.66 ± 1.74 (1.30) | 9.66 ± 11.68 (5.20) | 1.84 ± 0.68 (1.95) | 4.04 ± 1.59 (4.00) | 1.48 ± 0.79 (1.47) |
| left | p | 0.783 | 48/50 | 0 | 41 | 1.61 ± 0.46 (1.66) | 19.31 ± 33.44 (6.14) | 2.00 ± 0.59 (2.24) | 4.49 ± 1.46 (5.10) | 1.73 ± 0.74 (1.97) |
| back | p | 0.713 | 48/50 | 0 | 37 | 2.53 ± 1.44 (2.43) | 29.70 ± 51.70 (9.82) | 2.02 ± 0.53 (2.22) | 4.52 ± 1.32 (5.04) | 1.74 ± 0.66 (1.92) |
| right | p | 0.782 | 49/50 | 0 | 41 | 1.82 ± 1.38 (1.72) | 18.83 ± 33.86 (5.29) | 1.96 ± 0.51 (2.08) | 4.35 ± 1.25 (4.65) | 1.63 ± 0.67 (1.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.794 | 99/100 | 0 | 87 | 1.79 ± 0.98 (1.66) | 17.97 ± 35.75 (6.45) | 2.00 ± 0.52 (2.16) | 4.47 ± 1.27 (4.87) | 1.69 ± 0.67 (1.81) |
| right | p | 0.731 | 95/100 | 0 | 74 | 2.02 ± 1.72 (1.68) | 20.73 ± 36.67 (7.50) | 1.90 ± 0.65 (2.13) | 4.22 ± 1.56 (4.67) | 1.60 ± 0.78 (1.75) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.813 | 25/25 | 0 | 24 | 1.58 ± 1.59 (1.26) | 7.49 ± 8.85 (4.19) | 1.96 ± 0.58 (2.02) | 4.32 ± 1.35 (4.25) | 1.59 ± 0.69 (1.56) |
| forward/right | p | 0.731 | 24/25 | 0 | 18 | 1.73 ± 1.87 (1.34) | 11.92 ± 13.68 (7.66) | 1.72 ± 0.76 (1.88) | 3.76 ± 1.77 (3.97) | 1.37 ± 0.88 (1.45) |
| left/left | p | 0.841 | 25/25 | 0 | 23 | 1.54 ± 0.39 (1.60) | 12.54 ± 22.21 (5.54) | 2.06 ± 0.47 (2.21) | 4.60 ± 1.18 (5.05) | 1.77 ± 0.62 (1.93) |
| left/right | p | 0.725 | 23/25 | 0 | 18 | 1.69 ± 0.52 (1.88) | 26.67 ± 41.16 (6.97) | 1.94 ± 0.69 (2.27) | 4.37 ± 1.70 (5.20) | 1.68 ± 0.85 (2.01) |
| back/left | p | 0.723 | 24/25 | 0 | 20 | 2.34 ± 0.68 (2.41) | 27.62 ± 50.53 (10.00) | 2.08 ± 0.43 (2.22) | 4.67 ± 1.09 (5.00) | 1.81 ± 0.62 (1.98) |
| back/right | p | 0.702 | 24/25 | 0 | 17 | 2.73 ± 1.90 (2.44) | 31.78 ± 52.76 (9.02) | 1.96 ± 0.62 (2.21) | 4.36 ± 1.50 (5.04) | 1.68 ± 0.70 (1.82) |
| right/left | p | 0.796 | 25/25 | 0 | 20 | 1.71 ± 0.52 (1.74) | 24.60 ± 42.00 (4.33) | 1.92 ± 0.55 (2.08) | 4.29 ± 1.39 (4.35) | 1.59 ± 0.72 (1.68) |
| right/right | p | 0.767 | 24/25 | 0 | 21 | 1.94 ± 1.90 (1.53) | 12.81 ± 20.79 (6.44) | 2.00 ± 0.46 (2.08) | 4.42 ± 1.08 (4.72) | 1.67 ± 0.61 (1.74) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.779 | 18.1 | 4.90 | 1.92 |
| p | normal | 0.746 | 20.5 | 3.82 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.712 | 0.20 | 2.23 ± 0.94 (2.13) | 3.52 | 1.21 |
| p | medium | 16 | 0.807 | 0.73 | 1.24 ± 0.22 (1.21) | 4.01 | 1.49 |
| p | strong | 126 | 0.780 | 0.64 | - | 4.79 | 1.87 |

## Notes

- p: score 0.762, 194/200 kicked, 0 fell; worst sector back (0.713).
