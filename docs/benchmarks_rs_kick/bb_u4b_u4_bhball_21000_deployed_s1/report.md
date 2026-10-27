# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_21000.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.833** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 188 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.88 ± 0.59 (1.75) |
| Direction error [°] | 7.48 ± 5.33 (6.91) |
| Avg ball speed [m/s] | 2.56 ± 0.52 (2.74) |
| Peak ball speed [m/s] | 5.31 ± 1.23 (5.97) |
| Distance [m] | 2.57 ± 0.89 (3.01) |
| Path length [m] | 2.58 ± 0.90 (3.03) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.880 | 50/50 | 0 | 50 | 1.31 ± 0.26 (1.32) | 4.29 ± 2.93 (3.76) | 2.49 ± 0.44 (2.63) | 5.22 ± 1.09 (5.82) | 2.44 ± 0.80 (2.77) |
| left | p | 0.841 | 50/50 | 0 | 45 | 1.76 ± 0.37 (1.67) | 8.56 ± 4.84 (8.52) | 2.57 ± 0.47 (2.70) | 5.33 ± 1.18 (5.92) | 2.58 ± 0.89 (2.96) |
| back | p | 0.759 | 50/50 | 0 | 43 | 2.64 ± 0.36 (2.61) | 11.15 ± 6.66 (9.94) | 2.67 ± 0.66 (2.92) | 5.48 ± 1.45 (6.15) | 2.79 ± 0.97 (3.24) |
| right | p | 0.851 | 50/50 | 0 | 50 | 1.79 ± 0.38 (1.78) | 5.93 ± 3.18 (6.00) | 2.53 ± 0.48 (2.73) | 5.20 ± 1.16 (5.93) | 2.48 ± 0.87 (3.01) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.834 | 100/100 | 0 | 95 | 1.87 ± 0.59 (1.75) | 7.01 ± 4.71 (6.18) | 2.60 ± 0.46 (2.75) | 5.40 ± 1.11 (5.98) | 2.63 ± 0.84 (3.04) |
| right | p | 0.832 | 100/100 | 0 | 93 | 1.88 ± 0.60 (1.76) | 7.95 ± 5.86 (7.63) | 2.53 ± 0.58 (2.72) | 5.22 ± 1.34 (5.94) | 2.51 ± 0.94 (2.88) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.885 | 25/25 | 0 | 25 | 1.31 ± 0.27 (1.34) | 3.51 ± 2.36 (3.21) | 2.49 ± 0.47 (2.64) | 5.22 ± 1.16 (5.88) | 2.45 ± 0.84 (2.81) |
| forward/right | p | 0.875 | 25/25 | 0 | 25 | 1.32 ± 0.26 (1.32) | 5.06 ± 3.23 (4.98) | 2.48 ± 0.40 (2.62) | 5.22 ± 1.02 (5.75) | 2.42 ± 0.75 (2.76) |
| left/left | p | 0.841 | 25/25 | 0 | 22 | 1.65 ± 0.33 (1.58) | 8.88 ± 5.12 (9.41) | 2.60 ± 0.42 (2.67) | 5.44 ± 1.06 (5.97) | 2.66 ± 0.80 (3.04) |
| left/right | p | 0.842 | 25/25 | 0 | 23 | 1.87 ± 0.37 (1.88) | 8.23 ± 4.52 (8.02) | 2.54 ± 0.52 (2.73) | 5.21 ± 1.27 (5.70) | 2.50 ± 0.97 (2.64) |
| back/left | p | 0.763 | 25/25 | 0 | 23 | 2.64 ± 0.30 (2.60) | 10.37 ± 4.42 (11.89) | 2.76 ± 0.44 (2.93) | 5.68 ± 1.04 (6.11) | 2.89 ± 0.82 (3.27) |
| back/right | p | 0.755 | 25/25 | 0 | 20 | 2.64 ± 0.41 (2.66) | 11.94 ± 8.25 (9.63) | 2.58 ± 0.82 (2.90) | 5.29 ± 1.74 (6.29) | 2.69 ± 1.09 (3.21) |
| right/left | p | 0.846 | 25/25 | 0 | 25 | 1.89 ± 0.37 (1.84) | 5.28 ± 2.69 (5.19) | 2.55 ± 0.46 (2.73) | 5.26 ± 1.10 (5.87) | 2.52 ± 0.83 (3.02) |
| right/right | p | 0.857 | 25/25 | 0 | 25 | 1.69 ± 0.36 (1.68) | 6.58 ± 3.49 (6.47) | 2.52 ± 0.49 (2.73) | 5.14 ± 1.22 (5.99) | 2.44 ± 0.90 (3.00) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.864 | 8.2 | 6.13 | 3.18 |
| p | normal | 0.801 | 6.8 | 4.48 | 1.96 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.743 | 0.11 | 2.49 ± 0.85 (2.34) | 3.86 | 1.49 |
| p | medium | 20 | 0.876 | 0.76 | 1.24 ± 0.16 (1.21) | 3.97 | 1.59 |
| p | strong | 126 | 0.865 | 0.82 | - | 6.14 | 3.19 |

## Notes

- p: score 0.833, 200/200 kicked, 0 fell; worst sector back (0.759).
