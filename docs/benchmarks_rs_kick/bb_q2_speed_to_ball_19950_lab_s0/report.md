# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_21-18-55_q2_speed_to_ball/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.843** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.57 ± 0.52 (1.51) |
| Direction error [°] | 5.78 ± 3.44 (5.50) |
| Avg ball speed [m/s] | 1.86 ± 0.36 (1.96) |
| Peak ball speed [m/s] | 4.01 ± 0.85 (4.15) |
| Distance [m] | 1.43 ± 0.50 (1.44) |
| Path length [m] | 1.44 ± 0.50 (1.45) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 49 | 1.03 ± 0.23 (1.07) | 5.04 ± 3.27 (4.40) | 1.62 ± 0.39 (1.62) | 3.45 ± 0.88 (3.36) | 1.09 ± 0.47 (1.01) |
| left | p | 0.856 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.54) | 5.83 ± 3.41 (5.66) | 1.93 ± 0.31 (2.01) | 4.20 ± 0.76 (4.54) | 1.53 ± 0.49 (1.55) |
| back | p | 0.834 | 50/50 | 0 | 50 | 2.23 ± 0.27 (2.21) | 5.86 ± 3.05 (5.93) | 2.05 ± 0.24 (2.13) | 4.40 ± 0.64 (4.67) | 1.68 ± 0.39 (1.83) |
| right | p | 0.836 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.48) | 6.39 ± 3.85 (5.97) | 1.85 ± 0.32 (1.97) | 4.00 ± 0.79 (4.27) | 1.41 ± 0.43 (1.30) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 100 | 1.58 ± 0.53 (1.54) | 5.77 ± 3.28 (5.78) | 1.90 ± 0.33 (1.98) | 4.10 ± 0.79 (4.21) | 1.48 ± 0.48 (1.50) |
| right | p | 0.844 | 100/100 | 0 | 99 | 1.56 ± 0.52 (1.48) | 5.79 ± 3.59 (5.02) | 1.82 ± 0.38 (1.94) | 3.93 ± 0.90 (3.97) | 1.38 ± 0.51 (1.35) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.842 | 25/25 | 0 | 25 | 1.04 ± 0.23 (1.08) | 5.37 ± 3.01 (4.70) | 1.69 ± 0.33 (1.82) | 3.57 ± 0.73 (3.65) | 1.16 ± 0.42 (1.24) |
| forward/right | p | 0.852 | 25/25 | 0 | 24 | 1.03 ± 0.24 (1.04) | 4.71 ± 3.48 (3.69) | 1.55 ± 0.44 (1.40) | 3.32 ± 0.99 (3.00) | 1.03 ± 0.50 (0.87) |
| left/left | p | 0.851 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.50) | 5.98 ± 3.68 (6.65) | 1.89 ± 0.33 (1.88) | 4.09 ± 0.78 (4.19) | 1.47 ± 0.51 (1.31) |
| left/right | p | 0.862 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.60) | 5.68 ± 3.10 (5.28) | 1.97 ± 0.29 (2.08) | 4.31 ± 0.73 (4.65) | 1.60 ± 0.45 (1.60) |
| back/left | p | 0.829 | 25/25 | 0 | 25 | 2.26 ± 0.27 (2.22) | 6.26 ± 3.12 (6.89) | 2.09 ± 0.20 (2.13) | 4.50 ± 0.59 (4.73) | 1.75 ± 0.37 (1.88) |
| back/right | p | 0.838 | 25/25 | 0 | 25 | 2.21 ± 0.27 (2.14) | 5.46 ± 2.93 (4.67) | 2.00 ± 0.27 (2.05) | 4.30 ± 0.67 (4.50) | 1.61 ± 0.41 (1.74) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.58) | 5.47 ± 3.18 (5.02) | 1.94 ± 0.29 (2.02) | 4.23 ± 0.74 (4.60) | 1.53 ± 0.40 (1.59) |
| right/right | p | 0.823 | 25/25 | 0 | 25 | 1.40 ± 0.34 (1.42) | 7.30 ± 4.23 (6.49) | 1.76 ± 0.33 (1.74) | 3.78 ± 0.78 (3.76) | 1.29 ± 0.42 (1.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.858 | 5.7 | 4.48 | 1.67 |
| p | normal | 0.829 | 5.8 | 3.55 | 1.19 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.795 | 0.27 | 1.99 ± 0.65 (1.83) | 3.16 | 0.97 |
| p | medium | 16 | 0.895 | 0.85 | 1.00 ± 0.17 (1.05) | 3.27 | 1.05 |
| p | strong | 126 | 0.859 | 0.60 | - | 4.50 | 1.69 |

## Notes

- p: score 0.843, 200/200 kicked, 0 fell; worst sector back (0.834).
