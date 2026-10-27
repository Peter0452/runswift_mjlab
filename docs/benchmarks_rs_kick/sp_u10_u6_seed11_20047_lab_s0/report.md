# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u10_u6_seed11/model_20047.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.59 ± 0.53 (1.50) |
| Direction error [°] | 5.97 ± 12.12 (4.71) |
| Avg ball speed [m/s] | 1.77 ± 0.41 (1.92) |
| Peak ball speed [m/s] | 3.84 ± 0.96 (4.17) |
| Distance [m] | 1.33 ± 0.51 (1.41) |
| Path length [m] | 1.34 ± 0.51 (1.42) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.842 | 50/50 | 0 | 48 | 1.04 ± 0.23 (1.07) | 4.46 ± 4.34 (2.78) | 1.41 ± 0.43 (1.37) | 3.02 ± 0.93 (2.87) | 0.89 ± 0.49 (0.81) |
| left | p | 0.862 | 50/50 | 0 | 50 | 1.52 ± 0.33 (1.52) | 5.38 ± 3.25 (5.20) | 1.86 ± 0.31 (1.95) | 4.07 ± 0.78 (4.29) | 1.45 ± 0.44 (1.49) |
| back | p | 0.833 | 50/50 | 0 | 49 | 2.26 ± 0.26 (2.25) | 8.84 ± 23.13 (5.52) | 1.96 ± 0.35 (2.07) | 4.26 ± 0.85 (4.54) | 1.59 ± 0.42 (1.72) |
| right | p | 0.849 | 50/50 | 0 | 50 | 1.54 ± 0.36 (1.50) | 5.19 ± 3.40 (4.56) | 1.85 ± 0.29 (1.97) | 4.00 ± 0.75 (4.35) | 1.40 ± 0.39 (1.48) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 100 | 1.60 ± 0.55 (1.51) | 5.19 ± 3.35 (5.02) | 1.80 ± 0.39 (1.91) | 3.88 ± 0.91 (4.18) | 1.35 ± 0.50 (1.45) |
| right | p | 0.848 | 100/100 | 0 | 97 | 1.58 ± 0.51 (1.50) | 6.75 ± 16.77 (4.66) | 1.75 ± 0.44 (1.92) | 3.79 ± 1.00 (4.15) | 1.31 ± 0.53 (1.38) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.841 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.08) | 4.32 ± 3.35 (3.36) | 1.47 ± 0.43 (1.41) | 3.12 ± 0.92 (2.91) | 0.96 ± 0.50 (0.90) |
| forward/right | p | 0.843 | 25/25 | 0 | 23 | 1.03 ± 0.23 (1.04) | 4.61 ± 5.14 (2.25) | 1.35 ± 0.43 (1.33) | 2.92 ± 0.93 (2.82) | 0.82 ± 0.46 (0.79) |
| left/left | p | 0.854 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.48) | 5.59 ± 3.59 (5.27) | 1.78 ± 0.31 (1.86) | 3.87 ± 0.76 (4.16) | 1.34 ± 0.42 (1.38) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.60) | 5.17 ± 2.86 (5.13) | 1.94 ± 0.29 (2.04) | 4.27 ± 0.74 (4.53) | 1.56 ± 0.44 (1.65) |
| back/left | p | 0.834 | 25/25 | 0 | 25 | 2.31 ± 0.27 (2.30) | 5.52 ± 3.01 (5.50) | 2.05 ± 0.20 (2.08) | 4.43 ± 0.57 (4.54) | 1.67 ± 0.34 (1.78) |
| back/right | p | 0.833 | 25/25 | 0 | 24 | 2.22 ± 0.23 (2.16) | 12.16 ± 32.24 (5.54) | 1.88 ± 0.44 (2.02) | 4.09 ± 1.03 (4.45) | 1.50 ± 0.48 (1.65) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.63 ± 0.33 (1.60) | 5.32 ± 3.28 (4.69) | 1.89 ± 0.31 (2.00) | 4.10 ± 0.79 (4.47) | 1.45 ± 0.41 (1.50) |
| right/right | p | 0.846 | 25/25 | 0 | 25 | 1.44 ± 0.35 (1.48) | 5.06 ± 3.50 (3.03) | 1.82 ± 0.28 (1.92) | 3.90 ± 0.68 (4.21) | 1.35 ± 0.36 (1.39) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.856 | 5.3 | 4.25 | 1.53 |
| p | normal | 0.837 | 6.7 | 3.43 | 1.13 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.808 | 0.31 | 1.91 ± 0.73 (1.69) | 3.02 | 0.92 |
| p | medium | 16 | 0.902 | 0.80 | 0.94 ± 0.23 (0.99) | 3.04 | 0.91 |
| p | strong | 126 | 0.857 | 0.58 | - | 4.32 | 1.57 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.833).
