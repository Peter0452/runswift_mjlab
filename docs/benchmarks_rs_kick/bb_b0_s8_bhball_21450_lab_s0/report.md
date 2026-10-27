# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_21450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.835** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.53 (1.48) |
| Direction error [°] | 7.10 ± 11.33 (5.83) |
| Avg ball speed [m/s] | 2.12 ± 0.36 (2.10) |
| Peak ball speed [m/s] | 4.52 ± 0.83 (4.55) |
| Distance [m] | 1.95 ± 0.56 (1.95) |
| Path length [m] | 1.96 ± 0.56 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.825 | 50/50 | 0 | 48 | 1.03 ± 0.23 (1.06) | 6.44 ± 4.49 (5.92) | 1.90 ± 0.33 (1.88) | 4.04 ± 0.73 (3.89) | 1.60 ± 0.49 (1.44) |
| left | p | 0.860 | 50/50 | 0 | 49 | 1.51 ± 0.35 (1.51) | 6.11 ± 4.23 (4.78) | 2.23 ± 0.32 (2.22) | 4.79 ± 0.72 (4.89) | 2.14 ± 0.51 (2.17) |
| back | p | 0.831 | 50/50 | 0 | 49 | 2.26 ± 0.26 (2.21) | 8.82 ± 21.32 (5.52) | 2.23 ± 0.40 (2.28) | 4.77 ± 0.94 (5.01) | 2.14 ± 0.57 (2.29) |
| right | p | 0.825 | 50/50 | 0 | 49 | 1.50 ± 0.35 (1.45) | 7.03 ± 4.04 (7.06) | 2.12 ± 0.27 (2.09) | 4.50 ± 0.69 (4.48) | 1.92 ± 0.47 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.838 | 100/100 | 0 | 99 | 1.58 ± 0.54 (1.49) | 6.11 ± 4.02 (5.24) | 2.12 ± 0.30 (2.09) | 4.51 ± 0.73 (4.52) | 1.94 ± 0.52 (1.93) |
| right | p | 0.832 | 100/100 | 0 | 96 | 1.57 ± 0.52 (1.46) | 8.09 ± 15.45 (6.26) | 2.13 ± 0.41 (2.10) | 4.53 ± 0.92 (4.56) | 1.97 ± 0.59 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.817 | 25/25 | 0 | 24 | 1.03 ± 0.22 (1.06) | 7.01 ± 4.03 (7.26) | 1.88 ± 0.26 (1.89) | 4.00 ± 0.59 (3.89) | 1.57 ± 0.41 (1.45) |
| forward/right | p | 0.832 | 25/25 | 0 | 24 | 1.03 ± 0.24 (1.02) | 5.86 ± 4.84 (4.67) | 1.91 ± 0.38 (1.88) | 4.07 ± 0.85 (3.89) | 1.63 ± 0.55 (1.43) |
| left/left | p | 0.861 | 25/25 | 0 | 25 | 1.41 ± 0.35 (1.46) | 5.62 ± 4.49 (3.65) | 2.16 ± 0.26 (2.22) | 4.64 ± 0.67 (4.80) | 2.02 ± 0.46 (2.12) |
| left/right | p | 0.859 | 25/25 | 0 | 24 | 1.62 ± 0.31 (1.60) | 6.60 ± 3.88 (6.27) | 2.31 ± 0.34 (2.28) | 4.93 ± 0.74 (4.96) | 2.26 ± 0.54 (2.28) |
| back/left | p | 0.841 | 25/25 | 0 | 25 | 2.29 ± 0.27 (2.22) | 5.03 ± 3.34 (3.99) | 2.28 ± 0.25 (2.30) | 4.87 ± 0.66 (5.06) | 2.19 ± 0.51 (2.32) |
| back/right | p | 0.820 | 25/25 | 0 | 24 | 2.22 ± 0.24 (2.16) | 12.61 ± 29.49 (6.80) | 2.19 ± 0.51 (2.18) | 4.66 ± 1.14 (4.72) | 2.08 ± 0.63 (2.17) |
| right/left | p | 0.833 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.60) | 6.77 ± 3.78 (6.25) | 2.15 ± 0.29 (2.16) | 4.54 ± 0.72 (4.58) | 1.95 ± 0.49 (1.82) |
| right/right | p | 0.817 | 25/25 | 0 | 24 | 1.40 ± 0.34 (1.42) | 7.29 ± 4.26 (8.51) | 2.10 ± 0.25 (2.06) | 4.46 ± 0.66 (4.41) | 1.89 ± 0.46 (1.92) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.868 | 5.9 | 4.95 | 2.24 |
| p | normal | 0.802 | 8.3 | 4.09 | 1.66 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.745 | 0.12 | 2.33 ± 0.77 (2.24) | 3.69 | 1.39 |
| p | medium | 16 | 0.874 | 0.82 | 1.16 ± 0.15 (1.15) | 3.78 | 1.46 |
| p | strong | 126 | 0.872 | 0.67 | - | 5.00 | 2.27 |

## Notes

- p: score 0.835, 200/200 kicked, 0 fell; worst sector forward (0.825).
