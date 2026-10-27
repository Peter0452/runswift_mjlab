# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_22950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.849** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.57 (1.50) |
| Direction error [°] | 5.38 ± 9.40 (3.76) |
| Avg ball speed [m/s] | 1.81 ± 0.32 (1.84) |
| Peak ball speed [m/s] | 4.53 ± 0.80 (4.59) |
| Distance [m] | 1.84 ± 0.52 (1.78) |
| Path length [m] | 1.85 ± 0.52 (1.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.826 | 50/50 | 0 | 47 | 1.06 ± 0.43 (1.04) | 8.34 ± 17.73 (5.50) | 1.56 ± 0.31 (1.57) | 3.97 ± 0.74 (3.84) | 1.44 ± 0.44 (1.41) |
| left | p | 0.879 | 50/50 | 0 | 50 | 1.55 ± 0.40 (1.51) | 4.07 ± 2.37 (3.65) | 1.90 ± 0.34 (1.91) | 4.78 ± 0.82 (4.98) | 2.02 ± 0.55 (1.97) |
| back | p | 0.857 | 50/50 | 0 | 50 | 2.30 ± 0.26 (2.25) | 3.33 ± 2.07 (2.87) | 1.95 ± 0.21 (1.95) | 4.88 ± 0.61 (5.14) | 2.07 ± 0.40 (2.12) |
| right | p | 0.836 | 50/50 | 0 | 49 | 1.53 ± 0.34 (1.50) | 5.76 ± 3.78 (5.32) | 1.81 ± 0.25 (1.84) | 4.49 ± 0.65 (4.59) | 1.83 ± 0.42 (1.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.63 ± 0.59 (1.51) | 6.22 ± 12.71 (4.31) | 1.78 ± 0.32 (1.80) | 4.48 ± 0.76 (4.50) | 1.81 ± 0.49 (1.74) |
| right | p | 0.855 | 100/100 | 0 | 97 | 1.59 ± 0.55 (1.50) | 4.53 ± 3.72 (3.42) | 1.83 ± 0.32 (1.88) | 4.58 ± 0.83 (4.74) | 1.88 ± 0.55 (1.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 24 | 1.12 ± 0.56 (1.08) | 10.77 ± 24.37 (6.85) | 1.54 ± 0.28 (1.61) | 3.94 ± 0.73 (3.80) | 1.41 ± 0.41 (1.34) |
| forward/right | p | 0.831 | 25/25 | 0 | 23 | 1.00 ± 0.23 (1.04) | 5.92 ± 4.77 (4.23) | 1.57 ± 0.32 (1.55) | 4.00 ± 0.76 (3.88) | 1.47 ± 0.47 (1.41) |
| left/left | p | 0.866 | 25/25 | 0 | 25 | 1.48 ± 0.45 (1.50) | 4.53 ± 2.21 (4.65) | 1.80 ± 0.34 (1.81) | 4.60 ± 0.82 (4.76) | 1.89 ± 0.51 (1.82) |
| left/right | p | 0.891 | 25/25 | 0 | 25 | 1.63 ± 0.33 (1.64) | 3.62 ± 2.44 (2.89) | 2.01 ± 0.31 (2.02) | 4.96 ± 0.79 (5.08) | 2.15 ± 0.56 (2.27) |
| back/left | p | 0.857 | 25/25 | 0 | 25 | 2.30 ± 0.25 (2.30) | 3.36 ± 1.81 (2.99) | 1.99 ± 0.19 (1.99) | 4.89 ± 0.53 (5.02) | 2.09 ± 0.39 (2.10) |
| back/right | p | 0.858 | 25/25 | 0 | 25 | 2.30 ± 0.26 (2.24) | 3.29 ± 2.30 (2.27) | 1.92 ± 0.23 (1.94) | 4.87 ± 0.68 (5.20) | 2.05 ± 0.41 (2.14) |
| right/left | p | 0.833 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.58) | 6.24 ± 3.42 (6.39) | 1.80 ± 0.25 (1.86) | 4.49 ± 0.59 (4.72) | 1.84 ± 0.38 (1.75) |
| right/right | p | 0.838 | 25/25 | 0 | 24 | 1.42 ± 0.34 (1.48) | 5.28 ± 4.05 (4.77) | 1.82 ± 0.24 (1.81) | 4.48 ± 0.70 (4.46) | 1.83 ± 0.46 (1.72) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.881 | 4.5 | 4.96 | 2.07 |
| p | normal | 0.818 | 6.2 | 4.10 | 1.61 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.761 | 0.13 | 2.36 ± 0.76 (2.18) | 3.76 | 1.39 |
| p | medium | 16 | 0.892 | 0.81 | 1.12 ± 0.18 (1.14) | 3.63 | 1.36 |
| p | strong | 126 | 0.885 | 0.67 | - | 5.00 | 2.11 |

## Notes

- p: score 0.849, 200/200 kicked, 0 fell; worst sector forward (0.826).
