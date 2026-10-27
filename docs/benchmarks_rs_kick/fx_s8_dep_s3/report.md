# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.84 ± 0.57 (1.78) |
| Direction error [°] | 5.89 ± 12.31 (4.73) |
| Avg ball speed [m/s] | 2.35 ± 0.32 (2.38) |
| Peak ball speed [m/s] | 5.13 ± 0.88 (5.43) |
| Distance [m] | 2.21 ± 0.55 (2.22) |
| Path length [m] | 2.22 ± 0.55 (2.24) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.872 | 50/50 | 0 | 49 | 1.27 ± 0.23 (1.28) | 4.36 ± 3.06 (3.22) | 2.31 ± 0.34 (2.37) | 5.11 ± 0.92 (5.48) | 2.16 ± 0.60 (2.24) |
| left | p | 0.870 | 50/50 | 0 | 49 | 1.76 ± 0.31 (1.77) | 4.50 ± 3.28 (3.90) | 2.37 ± 0.24 (2.41) | 5.20 ± 0.78 (5.50) | 2.25 ± 0.50 (2.36) |
| back | p | 0.788 | 50/50 | 0 | 49 | 2.57 ± 0.44 (2.51) | 9.81 ± 23.57 (6.68) | 2.38 ± 0.42 (2.40) | 5.11 ± 1.03 (5.33) | 2.26 ± 0.59 (2.24) |
| right | p | 0.852 | 50/50 | 0 | 50 | 1.77 ± 0.33 (1.87) | 4.89 ± 3.08 (4.98) | 2.34 ± 0.25 (2.31) | 5.11 ± 0.76 (5.28) | 2.18 ± 0.49 (2.17) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 98 | 1.85 ± 0.57 (1.78) | 5.08 ± 3.44 (4.17) | 2.39 ± 0.29 (2.40) | 5.20 ± 0.83 (5.47) | 2.26 ± 0.55 (2.25) |
| right | p | 0.841 | 100/100 | 0 | 99 | 1.83 ± 0.57 (1.77) | 6.70 ± 17.02 (4.98) | 2.32 ± 0.35 (2.36) | 5.07 ± 0.92 (5.40) | 2.16 ± 0.54 (2.17) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.873 | 25/25 | 0 | 24 | 1.28 ± 0.24 (1.30) | 4.70 ± 3.44 (3.07) | 2.32 ± 0.36 (2.36) | 5.11 ± 0.94 (5.48) | 2.18 ± 0.62 (2.33) |
| forward/right | p | 0.871 | 25/25 | 0 | 25 | 1.27 ± 0.22 (1.26) | 4.02 ± 2.58 (3.27) | 2.30 ± 0.32 (2.37) | 5.12 ± 0.89 (5.48) | 2.14 ± 0.58 (2.16) |
| left/left | p | 0.868 | 25/25 | 0 | 24 | 1.67 ± 0.28 (1.76) | 5.15 ± 3.82 (4.11) | 2.42 ± 0.24 (2.50) | 5.30 ± 0.78 (5.62) | 2.34 ± 0.51 (2.53) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.84 ± 0.31 (1.86) | 3.85 ± 2.46 (3.75) | 2.32 ± 0.22 (2.36) | 5.10 ± 0.77 (5.45) | 2.16 ± 0.48 (2.17) |
| back/left | p | 0.806 | 25/25 | 0 | 25 | 2.60 ± 0.40 (2.50) | 6.11 ± 3.20 (6.67) | 2.48 ± 0.26 (2.42) | 5.29 ± 0.79 (5.46) | 2.37 ± 0.55 (2.33) |
| back/right | p | 0.770 | 25/25 | 0 | 24 | 2.54 ± 0.47 (2.52) | 13.51 ± 32.76 (6.70) | 2.29 ± 0.51 (2.35) | 4.93 ± 1.19 (5.19) | 2.15 ± 0.60 (2.11) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.86 ± 0.28 (1.94) | 4.35 ± 3.00 (3.67) | 2.33 ± 0.23 (2.28) | 5.09 ± 0.76 (5.10) | 2.15 ± 0.48 (2.16) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.68 ± 0.35 (1.68) | 5.43 ± 3.07 (5.52) | 2.36 ± 0.26 (2.36) | 5.14 ± 0.75 (5.39) | 2.21 ± 0.49 (2.22) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.887 | 5.3 | 5.75 | 2.56 |
| p | normal | 0.805 | 6.5 | 4.52 | 1.87 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.748 | 0.08 | 2.62 ± 0.87 (2.58) | 4.12 | 1.64 |
| p | medium | 18 | 0.874 | 0.67 | 1.33 ± 0.12 (1.33) | 4.28 | 1.73 |
| p | strong | 124 | 0.887 | 0.76 | - | 5.73 | 2.55 |

## Notes

- p: score 0.846, 200/200 kicked, 0 fell; worst sector back (0.788).
