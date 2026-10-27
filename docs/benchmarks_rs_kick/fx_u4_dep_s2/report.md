# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.91 ± 0.58 (1.87) |
| Direction error [°] | 6.66 ± 15.43 (4.18) |
| Avg ball speed [m/s] | 2.32 ± 0.55 (2.51) |
| Peak ball speed [m/s] | 5.05 ± 1.37 (5.76) |
| Distance [m] | 2.32 ± 0.93 (2.64) |
| Path length [m] | 2.33 ± 0.93 (2.64) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.883 | 50/50 | 0 | 50 | 1.29 ± 0.25 (1.24) | 4.13 ± 3.07 (3.18) | 2.26 ± 0.46 (2.45) | 4.98 ± 1.23 (5.62) | 2.20 ± 0.83 (2.59) |
| left | p | 0.863 | 50/50 | 0 | 48 | 1.85 ± 0.38 (1.85) | 5.42 ± 4.34 (4.05) | 2.33 ± 0.57 (2.59) | 5.06 ± 1.43 (5.84) | 2.33 ± 1.01 (2.70) |
| back | p | 0.788 | 50/50 | 0 | 47 | 2.63 ± 0.34 (2.60) | 12.03 ± 29.52 (5.34) | 2.36 ± 0.66 (2.62) | 5.11 ± 1.55 (5.88) | 2.41 ± 1.00 (2.80) |
| right | p | 0.877 | 50/50 | 0 | 49 | 1.86 ± 0.35 (1.91) | 5.09 ± 3.63 (4.58) | 2.34 ± 0.47 (2.51) | 5.06 ± 1.23 (5.67) | 2.31 ± 0.87 (2.56) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.859 | 100/100 | 0 | 97 | 1.91 ± 0.58 (1.91) | 6.49 ± 14.12 (4.11) | 2.37 ± 0.54 (2.53) | 5.17 ± 1.36 (5.87) | 2.41 ± 0.92 (2.79) |
| right | p | 0.847 | 100/100 | 0 | 97 | 1.91 ± 0.58 (1.86) | 6.84 ± 16.63 (4.26) | 2.28 ± 0.55 (2.44) | 4.94 ± 1.37 (5.60) | 2.22 ± 0.93 (2.51) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.878 | 25/25 | 0 | 25 | 1.30 ± 0.25 (1.30) | 4.19 ± 3.09 (3.08) | 2.27 ± 0.44 (2.46) | 4.99 ± 1.28 (5.69) | 2.23 ± 0.85 (2.61) |
| forward/right | p | 0.888 | 25/25 | 0 | 25 | 1.29 ± 0.24 (1.22) | 4.06 ± 3.05 (3.28) | 2.26 ± 0.48 (2.38) | 4.98 ± 1.19 (5.37) | 2.18 ± 0.80 (2.40) |
| left/left | p | 0.875 | 25/25 | 0 | 24 | 1.72 ± 0.37 (1.72) | 5.35 ± 4.28 (3.99) | 2.37 ± 0.56 (2.64) | 5.14 ± 1.42 (5.94) | 2.40 ± 0.99 (2.81) |
| left/right | p | 0.852 | 25/25 | 0 | 24 | 1.97 ± 0.34 (1.98) | 5.48 ± 4.39 (4.12) | 2.28 ± 0.58 (2.43) | 4.98 ± 1.44 (5.77) | 2.26 ± 1.02 (2.51) |
| back/left | p | 0.795 | 25/25 | 0 | 23 | 2.63 ± 0.33 (2.68) | 11.81 ± 26.85 (7.14) | 2.43 ± 0.66 (2.65) | 5.29 ± 1.55 (6.02) | 2.56 ± 0.97 (2.86) |
| back/right | p | 0.780 | 25/25 | 0 | 24 | 2.63 ± 0.35 (2.58) | 12.24 ± 31.96 (5.24) | 2.30 ± 0.65 (2.55) | 4.93 ± 1.53 (5.72) | 2.27 ± 1.00 (2.64) |
| right/left | p | 0.887 | 25/25 | 0 | 25 | 1.98 ± 0.31 (2.00) | 4.59 ± 3.17 (3.96) | 2.41 ± 0.45 (2.51) | 5.24 ± 1.15 (5.82) | 2.44 ± 0.83 (2.57) |
| right/right | p | 0.866 | 25/25 | 0 | 24 | 1.74 ± 0.34 (1.84) | 5.59 ± 3.97 (5.18) | 2.27 ± 0.48 (2.51) | 4.88 ± 1.28 (5.61) | 2.19 ± 0.89 (2.48) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.883 | 6.1 | 6.05 | 2.96 |
| p | normal | 0.823 | 7.3 | 4.06 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.785 | 0.20 | 2.11 ± 0.66 (2.05) | 3.49 | 1.25 |
| p | medium | 15 | 0.898 | 0.78 | 1.03 ± 0.31 (1.05) | 3.32 | 1.18 |
| p | strong | 125 | 0.879 | 0.80 | - | 6.01 | 2.96 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector back (0.788).
