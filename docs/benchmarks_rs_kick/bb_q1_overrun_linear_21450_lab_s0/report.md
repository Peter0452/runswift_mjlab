# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_21450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.58 ± 0.51 (1.51) |
| Direction error [°] | 5.92 ± 3.65 (5.85) |
| Avg ball speed [m/s] | 1.80 ± 0.41 (1.94) |
| Peak ball speed [m/s] | 3.88 ± 0.94 (4.17) |
| Distance [m] | 1.35 ± 0.52 (1.40) |
| Path length [m] | 1.36 ± 0.52 (1.41) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.853 | 50/50 | 0 | 50 | 1.06 ± 0.22 (1.08) | 5.21 ± 3.06 (4.90) | 1.52 ± 0.47 (1.57) | 3.26 ± 1.01 (3.31) | 1.00 ± 0.50 (0.94) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.55) | 5.97 ± 3.82 (6.01) | 1.89 ± 0.36 (2.04) | 4.11 ± 0.83 (4.50) | 1.47 ± 0.47 (1.58) |
| back | p | 0.834 | 50/50 | 0 | 50 | 2.24 ± 0.26 (2.20) | 6.52 ± 3.34 (6.96) | 1.97 ± 0.29 (2.12) | 4.28 ± 0.74 (4.67) | 1.60 ± 0.44 (1.78) |
| right | p | 0.843 | 50/50 | 0 | 49 | 1.51 ± 0.34 (1.45) | 5.96 ± 4.17 (5.24) | 1.81 ± 0.36 (1.92) | 3.87 ± 0.84 (4.21) | 1.35 ± 0.45 (1.35) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 100 | 1.59 ± 0.52 (1.54) | 5.96 ± 3.78 (5.99) | 1.82 ± 0.37 (1.94) | 3.92 ± 0.86 (4.20) | 1.37 ± 0.49 (1.44) |
| right | p | 0.851 | 100/100 | 0 | 99 | 1.58 ± 0.51 (1.49) | 5.87 ± 3.51 (5.85) | 1.78 ± 0.45 (1.92) | 3.84 ± 1.01 (4.16) | 1.33 ± 0.54 (1.39) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.846 | 25/25 | 0 | 25 | 1.06 ± 0.22 (1.08) | 5.47 ± 3.19 (5.13) | 1.61 ± 0.40 (1.66) | 3.42 ± 0.86 (3.48) | 1.08 ± 0.50 (1.13) |
| forward/right | p | 0.859 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.06) | 4.95 ± 2.90 (4.88) | 1.44 ± 0.51 (1.33) | 3.10 ± 1.11 (2.72) | 0.91 ± 0.49 (0.77) |
| left/left | p | 0.843 | 25/25 | 0 | 25 | 1.44 ± 0.35 (1.48) | 6.67 ± 4.20 (7.98) | 1.79 ± 0.35 (1.94) | 3.87 ± 0.81 (4.20) | 1.33 ± 0.44 (1.43) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.64) | 5.26 ± 3.24 (5.29) | 1.99 ± 0.34 (2.13) | 4.34 ± 0.78 (4.67) | 1.60 ± 0.45 (1.74) |
| back/left | p | 0.829 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.20) | 6.69 ± 3.60 (7.29) | 1.99 ± 0.26 (2.12) | 4.32 ± 0.69 (4.71) | 1.62 ± 0.43 (1.82) |
| back/right | p | 0.838 | 25/25 | 0 | 25 | 2.22 ± 0.26 (2.20) | 6.36 ± 3.04 (6.61) | 1.96 ± 0.33 (2.12) | 4.25 ± 0.78 (4.62) | 1.57 ± 0.44 (1.72) |
| right/left | p | 0.855 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.58) | 5.00 ± 3.78 (3.81) | 1.90 ± 0.34 (2.05) | 4.07 ± 0.83 (4.44) | 1.46 ± 0.44 (1.62) |
| right/right | p | 0.831 | 25/25 | 0 | 24 | 1.41 ± 0.34 (1.42) | 6.92 ± 4.31 (6.88) | 1.73 ± 0.36 (1.72) | 3.68 ± 0.80 (3.58) | 1.24 ± 0.44 (1.21) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.852 | 6.2 | 4.40 | 1.62 |
| p | normal | 0.842 | 5.7 | 3.36 | 1.08 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.816 | 0.37 | 1.80 ± 0.62 (1.66) | 2.86 | 0.80 |
| p | medium | 16 | 0.902 | 0.85 | 0.96 ± 0.18 (1.02) | 3.10 | 0.95 |
| p | strong | 126 | 0.855 | 0.59 | - | 4.45 | 1.66 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.834).
