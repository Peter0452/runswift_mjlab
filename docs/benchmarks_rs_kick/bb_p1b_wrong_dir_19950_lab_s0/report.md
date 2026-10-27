# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-23-17_p1b_wrong_dir/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.837** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.55 ± 0.51 (1.47) |
| Direction error [°] | 7.13 ± 12.43 (5.16) |
| Avg ball speed [m/s] | 2.15 ± 0.38 (2.17) |
| Peak ball speed [m/s] | 4.55 ± 0.87 (4.73) |
| Distance [m] | 1.99 ± 0.56 (2.05) |
| Path length [m] | 2.00 ± 0.57 (2.06) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.826 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.06) | 6.00 ± 3.89 (5.29) | 1.95 ± 0.30 (1.89) | 4.09 ± 0.68 (3.88) | 1.64 ± 0.45 (1.48) |
| left | p | 0.857 | 50/50 | 0 | 48 | 1.50 ± 0.33 (1.51) | 6.41 ± 4.29 (5.69) | 2.24 ± 0.30 (2.30) | 4.79 ± 0.70 (5.05) | 2.14 ± 0.49 (2.27) |
| back | p | 0.834 | 50/50 | 0 | 48 | 2.21 ± 0.25 (2.17) | 9.47 ± 23.48 (4.88) | 2.24 ± 0.52 (2.41) | 4.76 ± 1.16 (5.24) | 2.18 ± 0.67 (2.45) |
| right | p | 0.830 | 50/50 | 0 | 47 | 1.47 ± 0.34 (1.42) | 6.65 ± 5.07 (4.74) | 2.16 ± 0.28 (2.19) | 4.57 ± 0.65 (4.80) | 1.99 ± 0.45 (2.11) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.835 | 100/100 | 0 | 96 | 1.56 ± 0.53 (1.48) | 6.64 ± 5.00 (5.58) | 2.14 ± 0.37 (2.16) | 4.54 ± 0.86 (4.67) | 1.99 ± 0.56 (2.07) |
| right | p | 0.839 | 100/100 | 0 | 97 | 1.54 ± 0.49 (1.46) | 7.63 ± 16.83 (4.93) | 2.16 ± 0.39 (2.18) | 4.56 ± 0.88 (4.77) | 1.99 ± 0.56 (2.05) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.825 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 6.14 ± 4.08 (5.77) | 1.91 ± 0.25 (1.91) | 4.03 ± 0.60 (3.95) | 1.60 ± 0.42 (1.51) |
| forward/right | p | 0.827 | 25/25 | 0 | 25 | 1.04 ± 0.21 (1.06) | 5.86 ± 3.67 (5.25) | 1.98 ± 0.34 (1.89) | 4.15 ± 0.75 (3.80) | 1.68 ± 0.47 (1.46) |
| left/left | p | 0.840 | 25/25 | 0 | 23 | 1.41 ± 0.33 (1.48) | 7.79 ± 4.68 (7.55) | 2.19 ± 0.32 (2.19) | 4.68 ± 0.74 (4.83) | 2.08 ± 0.51 (2.20) |
| left/right | p | 0.874 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.60) | 5.03 ± 3.32 (4.45) | 2.29 ± 0.27 (2.39) | 4.90 ± 0.64 (5.08) | 2.21 ± 0.45 (2.33) |
| back/left | p | 0.832 | 25/25 | 0 | 24 | 2.25 ± 0.26 (2.20) | 6.63 ± 6.20 (5.17) | 2.26 ± 0.50 (2.42) | 4.82 ± 1.16 (5.29) | 2.22 ± 0.68 (2.48) |
| back/right | p | 0.837 | 25/25 | 0 | 24 | 2.16 ± 0.23 (2.12) | 12.32 ± 32.37 (4.68) | 2.22 ± 0.53 (2.41) | 4.70 ± 1.16 (5.13) | 2.14 ± 0.67 (2.38) |
| right/left | p | 0.842 | 25/25 | 0 | 24 | 1.57 ± 0.31 (1.52) | 5.99 ± 4.60 (3.97) | 2.19 ± 0.25 (2.21) | 4.65 ± 0.59 (4.87) | 2.04 ± 0.40 (2.22) |
| right/right | p | 0.818 | 25/25 | 0 | 23 | 1.38 ± 0.33 (1.40) | 7.31 ± 5.42 (6.99) | 2.14 ± 0.31 (2.18) | 4.50 ± 0.69 (4.48) | 1.93 ± 0.48 (1.97) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.874 | 5.6 | 5.00 | 2.28 |
| p | normal | 0.800 | 8.6 | 4.10 | 1.69 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.744 | 0.11 | 2.34 ± 0.85 (2.18) | 3.68 | 1.41 |
| p | medium | 16 | 0.859 | 0.79 | 1.14 ± 0.18 (1.18) | 3.68 | 1.40 |
| p | strong | 126 | 0.877 | 0.68 | - | 5.07 | 2.33 |

## Notes

- p: score 0.837, 200/200 kicked, 0 fell; worst sector forward (0.826).
