# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w2_u4_u6.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.851** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.86 ± 0.55 (1.76) |
| Direction error [°] | 5.61 ± 10.81 (4.26) |
| Avg ball speed [m/s] | 2.31 ± 0.41 (2.45) |
| Peak ball speed [m/s] | 5.10 ± 1.13 (5.68) |
| Distance [m] | 2.16 ± 0.69 (2.35) |
| Path length [m] | 2.18 ± 0.69 (2.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.865 | 50/50 | 0 | 50 | 1.29 ± 0.26 (1.30) | 4.12 ± 2.85 (3.45) | 2.25 ± 0.44 (2.39) | 4.96 ± 1.21 (5.40) | 2.07 ± 0.75 (2.17) |
| left | p | 0.878 | 50/50 | 0 | 47 | 1.80 ± 0.37 (1.83) | 5.31 ± 3.98 (4.40) | 2.35 ± 0.29 (2.45) | 5.28 ± 0.91 (5.77) | 2.24 ± 0.54 (2.40) |
| back | p | 0.803 | 49/50 | 0 | 48 | 2.54 ± 0.32 (2.48) | 8.18 ± 20.74 (5.12) | 2.35 ± 0.48 (2.51) | 5.12 ± 1.25 (5.79) | 2.24 ± 0.75 (2.52) |
| right | p | 0.858 | 50/50 | 0 | 50 | 1.81 ± 0.35 (1.75) | 4.89 ± 3.21 (4.09) | 2.28 ± 0.40 (2.37) | 5.03 ± 1.09 (5.59) | 2.11 ± 0.66 (2.24) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 99/100 | 0 | 97 | 1.86 ± 0.55 (1.78) | 6.48 ± 14.91 (4.15) | 2.31 ± 0.43 (2.44) | 5.09 ± 1.15 (5.68) | 2.17 ± 0.70 (2.38) |
| right | p | 0.857 | 100/100 | 0 | 98 | 1.86 ± 0.55 (1.76) | 4.76 ± 3.29 (4.50) | 2.31 ± 0.40 (2.45) | 5.11 ± 1.10 (5.67) | 2.16 ± 0.68 (2.31) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.869 | 25/25 | 0 | 25 | 1.30 ± 0.26 (1.30) | 4.25 ± 3.00 (3.61) | 2.27 ± 0.42 (2.42) | 4.97 ± 1.17 (5.68) | 2.08 ± 0.72 (2.39) |
| forward/right | p | 0.861 | 25/25 | 0 | 25 | 1.28 ± 0.25 (1.30) | 3.98 ± 2.67 (3.30) | 2.23 ± 0.46 (2.35) | 4.95 ± 1.24 (5.13) | 2.06 ± 0.78 (2.09) |
| left/left | p | 0.875 | 25/25 | 0 | 24 | 1.69 ± 0.37 (1.76) | 5.48 ± 3.49 (5.25) | 2.32 ± 0.32 (2.44) | 5.17 ± 0.96 (5.75) | 2.19 ± 0.56 (2.38) |
| left/right | p | 0.881 | 25/25 | 0 | 23 | 1.92 ± 0.33 (2.00) | 5.15 ± 4.40 (3.45) | 2.38 ± 0.26 (2.48) | 5.40 ± 0.84 (5.79) | 2.30 ± 0.52 (2.41) |
| back/left | p | 0.778 | 24/25 | 0 | 23 | 2.55 ± 0.30 (2.56) | 11.03 ± 29.25 (5.21) | 2.37 ± 0.51 (2.46) | 5.14 ± 1.27 (5.71) | 2.27 ± 0.76 (2.53) |
| back/right | p | 0.828 | 25/25 | 0 | 25 | 2.53 ± 0.33 (2.46) | 5.45 ± 2.44 (5.12) | 2.34 ± 0.46 (2.52) | 5.11 ± 1.22 (5.85) | 2.21 ± 0.73 (2.48) |
| right/left | p | 0.858 | 25/25 | 0 | 25 | 1.92 ± 0.32 (1.78) | 5.34 ± 3.28 (3.99) | 2.28 ± 0.43 (2.47) | 5.08 ± 1.16 (5.68) | 2.12 ± 0.71 (2.26) |
| right/right | p | 0.857 | 25/25 | 0 | 25 | 1.70 ± 0.34 (1.74) | 4.45 ± 3.07 (4.15) | 2.27 ± 0.37 (2.31) | 4.98 ± 1.01 (5.57) | 2.09 ± 0.61 (2.04) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.888 | 4.9 | 5.93 | 2.66 |
| p | normal | 0.814 | 6.4 | 4.27 | 1.68 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.765 | 0.12 | 2.31 ± 0.75 (2.16) | 3.65 | 1.31 |
| p | medium | 16 | 0.883 | 0.76 | 1.24 ± 0.16 (1.22) | 4.01 | 1.54 |
| p | strong | 126 | 0.886 | 0.79 | - | 5.91 | 2.64 |

## Notes

- p: score 0.851, 199/200 kicked, 0 fell; worst sector back (0.803).
