# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.801** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.90 ± 1.20 (1.68) |
| Direction error [°] | 12.21 ± 25.70 (5.25) |
| Avg ball speed [m/s] | 2.27 ± 0.63 (2.41) |
| Peak ball speed [m/s] | 4.92 ± 1.51 (5.63) |
| Distance [m] | 2.18 ± 0.90 (2.38) |
| Path length [m] | 2.19 ± 0.90 (2.39) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 49/50 | 0 | 41 | 1.51 ± 1.52 (1.32) | 8.94 ± 11.35 (5.11) | 2.21 ± 0.70 (2.44) | 4.85 ± 1.64 (5.68) | 2.13 ± 0.93 (2.33) |
| left | p | 0.819 | 49/50 | 0 | 44 | 1.72 ± 0.44 (1.64) | 11.67 ± 23.02 (5.44) | 2.22 ± 0.63 (2.37) | 4.82 ± 1.53 (5.47) | 2.12 ± 0.90 (2.32) |
| back | p | 0.773 | 49/50 | 0 | 44 | 2.67 ± 1.52 (2.42) | 18.74 ± 40.40 (5.41) | 2.40 ± 0.64 (2.57) | 5.16 ± 1.49 (5.81) | 2.38 ± 0.93 (2.67) |
| right | p | 0.809 | 49/50 | 0 | 44 | 1.72 ± 0.38 (1.70) | 9.49 ± 17.01 (4.91) | 2.25 ± 0.54 (2.33) | 4.85 ± 1.35 (5.36) | 2.11 ± 0.81 (2.07) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 98/100 | 0 | 84 | 1.81 ± 0.76 (1.63) | 13.92 ± 28.24 (5.62) | 2.24 ± 0.68 (2.39) | 4.87 ± 1.60 (5.57) | 2.16 ± 0.94 (2.38) |
| right | p | 0.806 | 98/100 | 0 | 89 | 1.99 ± 1.52 (1.77) | 10.50 ± 22.75 (5.00) | 2.31 ± 0.59 (2.42) | 4.97 ± 1.42 (5.67) | 2.21 ± 0.86 (2.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.821 | 25/25 | 0 | 20 | 1.28 ± 0.35 (1.28) | 9.28 ± 11.73 (4.18) | 2.15 ± 0.77 (2.44) | 4.72 ± 1.78 (5.58) | 2.06 ± 1.00 (2.33) |
| forward/right | p | 0.786 | 24/25 | 0 | 21 | 1.74 ± 2.12 (1.38) | 8.58 ± 10.94 (5.14) | 2.28 ± 0.62 (2.45) | 4.98 ± 1.48 (5.69) | 2.19 ± 0.84 (2.28) |
| left/left | p | 0.821 | 24/25 | 0 | 23 | 1.68 ± 0.37 (1.62) | 6.76 ± 5.11 (6.37) | 2.33 ± 0.45 (2.42) | 5.15 ± 1.19 (5.63) | 2.29 ± 0.74 (2.43) |
| left/right | p | 0.817 | 25/25 | 0 | 21 | 1.76 ± 0.49 (1.80) | 16.39 ± 31.11 (5.37) | 2.11 ± 0.75 (2.26) | 4.51 ± 1.73 (4.27) | 1.95 ± 1.01 (1.73) |
| back/left | p | 0.771 | 25/25 | 0 | 21 | 2.47 ± 1.05 (2.46) | 25.96 ± 47.41 (6.22) | 2.31 ± 0.79 (2.55) | 4.95 ± 1.76 (5.77) | 2.27 ± 1.05 (2.70) |
| back/right | p | 0.774 | 24/25 | 0 | 23 | 2.88 ± 1.87 (2.40) | 11.23 ± 29.67 (4.95) | 2.50 ± 0.41 (2.58) | 5.38 ± 1.10 (5.81) | 2.48 ± 0.76 (2.67) |
| right/left | p | 0.769 | 24/25 | 0 | 20 | 1.82 ± 0.40 (1.95) | 13.37 ± 22.80 (5.32) | 2.16 ± 0.63 (2.22) | 4.68 ± 1.54 (4.91) | 2.00 ± 0.89 (1.94) |
| right/right | p | 0.849 | 25/25 | 0 | 24 | 1.62 ± 0.34 (1.56) | 5.76 ± 6.31 (3.65) | 2.34 ± 0.42 (2.38) | 5.02 ± 1.11 (5.54) | 2.21 ± 0.72 (2.29) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.821 | 12.3 | 5.43 | 2.50 |
| p | normal | 0.782 | 12.1 | 4.42 | 1.87 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.724 | 0.10 | 2.55 ± 0.97 (2.37) | 3.93 | 1.54 |
| p | medium | 20 | 0.879 | 0.71 | 1.28 ± 0.16 (1.31) | 4.10 | 1.63 |
| p | strong | 126 | 0.822 | 0.73 | - | 5.48 | 2.55 |

## Notes

- p: score 0.801, 196/200 kicked, 0 fell; worst sector back (0.773).
