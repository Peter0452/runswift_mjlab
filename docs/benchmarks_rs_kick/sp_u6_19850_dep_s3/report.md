# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u6_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.04 ± 1.58 (1.77) |
| Direction error [°] | 15.49 ± 32.63 (4.88) |
| Avg ball speed [m/s] | 2.12 ± 0.69 (2.32) |
| Peak ball speed [m/s] | 4.68 ± 1.65 (5.32) |
| Distance [m] | 1.96 ± 0.89 (2.07) |
| Path length [m] | 1.97 ± 0.89 (2.08) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.800 | 48/50 | 0 | 43 | 1.37 ± 0.82 (1.30) | 9.08 ± 15.99 (4.50) | 2.13 ± 0.67 (2.35) | 4.73 ± 1.64 (5.05) | 1.96 ± 0.89 (1.90) |
| left | p | 0.820 | 50/50 | 0 | 43 | 1.73 ± 0.56 (1.74) | 15.38 ± 30.71 (5.30) | 2.10 ± 0.70 (2.35) | 4.67 ± 1.67 (5.49) | 1.94 ± 0.87 (2.15) |
| back | p | 0.750 | 49/50 | 0 | 41 | 2.71 ± 1.51 (2.52) | 17.84 ± 36.35 (5.54) | 2.24 ± 0.63 (2.32) | 4.86 ± 1.50 (5.41) | 2.11 ± 0.89 (2.23) |
| right | p | 0.758 | 49/50 | 0 | 41 | 2.36 ± 2.39 (1.82) | 19.52 ± 40.76 (4.99) | 2.01 ± 0.74 (2.27) | 4.44 ± 1.75 (4.52) | 1.83 ± 0.87 (1.94) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 100/100 | 0 | 86 | 1.86 ± 0.84 (1.75) | 14.80 ± 32.55 (4.25) | 2.12 ± 0.70 (2.35) | 4.69 ± 1.68 (5.49) | 1.97 ± 0.92 (2.14) |
| right | p | 0.752 | 96/100 | 0 | 82 | 2.24 ± 2.08 (1.79) | 16.20 ± 32.69 (5.50) | 2.12 ± 0.68 (2.31) | 4.66 ± 1.62 (5.15) | 1.95 ± 0.85 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 22 | 1.48 ± 1.09 (1.30) | 9.39 ± 15.61 (5.23) | 2.03 ± 0.72 (2.17) | 4.52 ± 1.75 (4.39) | 1.85 ± 0.93 (1.83) |
| forward/right | p | 0.781 | 23/25 | 0 | 21 | 1.25 ± 0.25 (1.30) | 8.74 ± 16.39 (4.11) | 2.24 ± 0.58 (2.40) | 4.96 ± 1.47 (5.61) | 2.09 ± 0.84 (1.95) |
| left/left | p | 0.818 | 25/25 | 0 | 21 | 1.59 ± 0.40 (1.60) | 12.71 ± 21.23 (4.27) | 2.05 ± 0.74 (2.35) | 4.56 ± 1.77 (5.48) | 1.88 ± 0.93 (2.07) |
| left/right | p | 0.822 | 25/25 | 0 | 22 | 1.87 ± 0.65 (1.84) | 18.05 ± 37.70 (5.91) | 2.16 ± 0.64 (2.39) | 4.78 ± 1.56 (5.57) | 1.99 ± 0.81 (2.25) |
| back/left | p | 0.811 | 25/25 | 0 | 22 | 2.48 ± 0.47 (2.46) | 10.97 ± 24.82 (4.62) | 2.37 ± 0.48 (2.50) | 5.16 ± 1.27 (5.71) | 2.29 ± 0.83 (2.29) |
| back/right | p | 0.689 | 24/25 | 0 | 19 | 2.96 ± 2.08 (2.60) | 25.00 ± 44.22 (5.65) | 2.11 ± 0.72 (2.27) | 4.55 ± 1.65 (4.47) | 1.92 ± 0.91 (1.89) |
| right/left | p | 0.799 | 25/25 | 0 | 21 | 1.88 ± 0.79 (1.80) | 26.15 ± 52.43 (3.48) | 2.04 ± 0.74 (2.33) | 4.51 ± 1.78 (4.52) | 1.85 ± 0.91 (1.91) |
| right/right | p | 0.717 | 24/25 | 0 | 20 | 2.86 ± 3.24 (1.85) | 12.62 ± 20.84 (6.22) | 1.97 ± 0.73 (2.25) | 4.37 ± 1.73 (4.83) | 1.80 ± 0.83 (2.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.828 | 12.2 | 5.30 | 2.31 |
| p | normal | 0.736 | 18.8 | 4.04 | 1.60 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.709 | 0.09 | 2.37 ± 1.01 (2.40) | 3.78 | 1.45 |
| p | medium | 18 | 0.822 | 0.66 | 1.12 ± 0.38 (1.22) | 3.62 | 1.35 |
| p | strong | 124 | 0.810 | 0.70 | - | 5.26 | 2.29 |

## Notes

- p: score 0.782, 196/200 kicked, 0 fell; worst sector back (0.750).
