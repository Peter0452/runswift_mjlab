# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u10_u6_seed11/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.62 ± 0.61 (1.49) |
| Direction error [°] | 5.77 ± 16.23 (2.98) |
| Avg ball speed [m/s] | 1.76 ± 0.31 (1.78) |
| Peak ball speed [m/s] | 4.55 ± 0.80 (4.61) |
| Distance [m] | 1.83 ± 0.53 (1.81) |
| Path length [m] | 1.84 ± 0.53 (1.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.832 | 50/50 | 0 | 48 | 1.14 ± 0.56 (1.07) | 7.30 ± 20.84 (2.86) | 1.56 ± 0.26 (1.55) | 4.02 ± 0.73 (3.84) | 1.46 ± 0.45 (1.36) |
| left | p | 0.871 | 50/50 | 0 | 50 | 1.56 ± 0.49 (1.51) | 4.45 ± 3.08 (3.34) | 1.85 ± 0.29 (1.83) | 4.78 ± 0.77 (4.93) | 2.00 ± 0.53 (1.96) |
| back | p | 0.867 | 50/50 | 0 | 50 | 2.20 ± 0.27 (2.16) | 3.20 ± 2.42 (2.32) | 1.92 ± 0.28 (1.91) | 4.94 ± 0.68 (5.15) | 2.11 ± 0.48 (2.08) |
| right | p | 0.837 | 50/50 | 0 | 49 | 1.57 ± 0.55 (1.44) | 8.12 ± 24.25 (3.58) | 1.73 ± 0.27 (1.72) | 4.45 ± 0.71 (4.52) | 1.77 ± 0.41 (1.73) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 99 | 1.65 ± 0.61 (1.54) | 5.49 ± 14.94 (2.75) | 1.78 ± 0.32 (1.78) | 4.60 ± 0.78 (4.73) | 1.87 ± 0.53 (1.83) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.59 ± 0.61 (1.45) | 6.05 ± 17.42 (3.13) | 1.75 ± 0.30 (1.78) | 4.49 ± 0.83 (4.59) | 1.79 ± 0.53 (1.77) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 24 | 1.29 ± 0.73 (1.10) | 10.04 ± 28.94 (2.45) | 1.53 ± 0.23 (1.47) | 4.08 ± 0.69 (3.84) | 1.48 ± 0.45 (1.35) |
| forward/right | p | 0.842 | 25/25 | 0 | 24 | 1.00 ± 0.21 (1.02) | 4.56 ± 3.95 (3.13) | 1.58 ± 0.29 (1.58) | 3.96 ± 0.77 (3.83) | 1.43 ± 0.45 (1.38) |
| left/left | p | 0.868 | 25/25 | 0 | 25 | 1.44 ± 0.42 (1.46) | 4.61 ± 3.35 (4.00) | 1.84 ± 0.29 (1.81) | 4.72 ± 0.73 (4.92) | 1.97 ± 0.48 (1.96) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.68 ± 0.52 (1.62) | 4.29 ± 2.77 (3.21) | 1.87 ± 0.30 (1.88) | 4.83 ± 0.80 (4.97) | 2.03 ± 0.58 (1.97) |
| back/left | p | 0.868 | 25/25 | 0 | 25 | 2.23 ± 0.26 (2.16) | 3.19 ± 2.68 (2.13) | 1.98 ± 0.28 (1.97) | 5.03 ± 0.65 (5.31) | 2.19 ± 0.48 (2.17) |
| back/right | p | 0.866 | 25/25 | 0 | 25 | 2.17 ± 0.27 (2.14) | 3.21 ± 2.12 (2.57) | 1.86 ± 0.28 (1.82) | 4.84 ± 0.70 (5.15) | 2.03 ± 0.46 (2.02) |
| right/left | p | 0.855 | 25/25 | 0 | 25 | 1.64 ± 0.44 (1.56) | 4.12 ± 2.81 (3.31) | 1.76 ± 0.29 (1.68) | 4.57 ± 0.72 (4.72) | 1.86 ± 0.44 (1.89) |
| right/right | p | 0.819 | 25/25 | 0 | 24 | 1.50 ± 0.64 (1.42) | 12.12 ± 33.71 (3.85) | 1.69 ± 0.25 (1.72) | 4.33 ± 0.68 (4.50) | 1.68 ± 0.36 (1.66) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.888 | 4.2 | 5.01 | 2.10 |
| p | normal | 0.815 | 7.3 | 4.08 | 1.57 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.763 | 0.12 | 2.33 ± 0.69 (2.14) | 3.73 | 1.36 |
| p | medium | 16 | 0.900 | 0.81 | 1.15 ± 0.15 (1.18) | 3.75 | 1.40 |
| p | strong | 126 | 0.886 | 0.67 | - | 5.02 | 2.11 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector forward (0.832).
