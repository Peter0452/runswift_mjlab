# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r5_u5_u0_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 1.94 ± 1.30 (1.78) |
| Direction error [°] | 19.08 ± 37.51 (6.17) |
| Avg ball speed [m/s] | 2.13 ± 0.76 (2.28) |
| Peak ball speed [m/s] | 4.59 ± 1.72 (5.18) |
| Distance [m] | 2.02 ± 0.96 (2.07) |
| Path length [m] | 2.03 ± 0.96 (2.07) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.786 | 48/50 | 0 | 42 | 1.26 ± 0.27 (1.25) | 12.48 ± 23.22 (6.42) | 2.09 ± 0.68 (2.25) | 4.53 ± 1.59 (4.82) | 1.92 ± 0.89 (1.95) |
| left | p | 0.773 | 48/50 | 0 | 41 | 1.93 ± 0.96 (1.85) | 13.96 ± 24.19 (5.83) | 2.14 ± 0.77 (2.27) | 4.58 ± 1.71 (4.94) | 2.02 ± 0.96 (2.02) |
| back | p | 0.752 | 50/50 | 0 | 41 | 2.70 ± 1.70 (2.50) | 28.58 ± 51.97 (6.65) | 2.21 ± 0.76 (2.40) | 4.78 ± 1.74 (5.66) | 2.18 ± 1.00 (2.46) |
| right | p | 0.804 | 50/50 | 0 | 40 | 1.83 ± 1.33 (1.79) | 20.82 ± 39.70 (4.60) | 2.08 ± 0.81 (2.32) | 4.46 ± 1.81 (5.24) | 1.95 ± 0.96 (2.29) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.784 | 99/100 | 0 | 82 | 1.92 ± 1.21 (1.76) | 20.94 ± 39.06 (6.34) | 2.14 ± 0.82 (2.29) | 4.61 ± 1.83 (5.30) | 2.05 ± 1.01 (2.30) |
| right | p | 0.773 | 97/100 | 0 | 82 | 1.96 ± 1.38 (1.82) | 17.17 ± 35.76 (5.76) | 2.13 ± 0.69 (2.26) | 4.57 ± 1.60 (4.61) | 1.98 ± 0.91 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.801 | 25/25 | 0 | 21 | 1.29 ± 0.27 (1.36) | 16.40 ± 30.04 (6.34) | 2.05 ± 0.75 (2.19) | 4.40 ± 1.71 (4.41) | 1.88 ± 0.93 (1.94) |
| forward/right | p | 0.771 | 23/25 | 0 | 21 | 1.24 ± 0.27 (1.20) | 8.21 ± 10.47 (6.51) | 2.15 ± 0.58 (2.27) | 4.68 ± 1.42 (5.09) | 1.96 ± 0.85 (1.96) |
| left/left | p | 0.763 | 24/25 | 0 | 20 | 2.02 ± 1.27 (1.81) | 13.96 ± 21.47 (6.27) | 2.15 ± 0.88 (2.27) | 4.58 ± 1.90 (5.26) | 2.06 ± 1.05 (2.21) |
| left/right | p | 0.783 | 24/25 | 0 | 21 | 1.83 ± 0.47 (1.86) | 13.95 ± 26.63 (5.03) | 2.14 ± 0.65 (2.27) | 4.58 ± 1.49 (4.52) | 1.97 ± 0.85 (1.94) |
| back/left | p | 0.774 | 25/25 | 0 | 21 | 2.30 ± 0.64 (2.50) | 24.98 ± 44.65 (6.38) | 2.27 ± 0.73 (2.50) | 4.94 ± 1.69 (5.75) | 2.28 ± 0.98 (2.74) |
| back/right | p | 0.730 | 25/25 | 0 | 20 | 3.10 ± 2.25 (2.50) | 32.19 ± 58.15 (6.95) | 2.15 ± 0.79 (2.29) | 4.61 ± 1.78 (5.17) | 2.08 ± 1.01 (2.30) |
| right/left | p | 0.799 | 25/25 | 0 | 20 | 2.07 ± 1.80 (1.82) | 28.14 ± 50.67 (6.71) | 2.08 ± 0.88 (2.40) | 4.52 ± 1.97 (5.55) | 2.00 ± 1.02 (2.35) |
| right/right | p | 0.809 | 25/25 | 0 | 20 | 1.59 ± 0.42 (1.74) | 13.50 ± 21.83 (4.32) | 2.09 ± 0.72 (2.21) | 4.40 ± 1.63 (4.37) | 1.91 ± 0.90 (1.90) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.802 | 16.4 | 5.16 | 2.33 |
| p | normal | 0.755 | 21.7 | 4.03 | 1.71 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.710 | 0.19 | 2.17 ± 1.00 (2.17) | 3.65 | 1.45 |
| p | medium | 15 | 0.819 | 0.56 | 1.03 ± 0.51 (1.19) | 3.32 | 1.29 |
| p | strong | 125 | 0.807 | 0.69 | - | 5.20 | 2.38 |

## Notes

- p: score 0.779, 196/200 kicked, 0 fell; worst sector back (0.752).
