# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_23-01-41_q3_speed_fastmix/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.52 (1.48) |
| Direction error [°] | 6.19 ± 11.05 (4.89) |
| Avg ball speed [m/s] | 1.83 ± 0.38 (1.91) |
| Peak ball speed [m/s] | 3.96 ± 0.89 (3.95) |
| Distance [m] | 1.39 ± 0.50 (1.42) |
| Path length [m] | 1.40 ± 0.51 (1.43) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.848 | 50/50 | 0 | 50 | 1.04 ± 0.22 (1.06) | 4.33 ± 2.80 (3.43) | 1.54 ± 0.38 (1.45) | 3.28 ± 0.79 (3.04) | 1.00 ± 0.45 (0.85) |
| left | p | 0.866 | 50/50 | 0 | 49 | 1.52 ± 0.34 (1.52) | 5.20 ± 3.59 (4.48) | 1.93 ± 0.34 (2.04) | 4.22 ± 0.79 (4.49) | 1.54 ± 0.47 (1.61) |
| back | p | 0.831 | 50/50 | 0 | 49 | 2.24 ± 0.24 (2.20) | 8.91 ± 20.95 (5.94) | 2.02 ± 0.32 (2.15) | 4.39 ± 0.81 (4.74) | 1.67 ± 0.44 (1.81) |
| right | p | 0.829 | 50/50 | 0 | 48 | 1.50 ± 0.35 (1.46) | 6.31 ± 4.14 (4.95) | 1.83 ± 0.29 (1.88) | 3.93 ± 0.73 (3.85) | 1.36 ± 0.38 (1.28) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.840 | 100/100 | 0 | 99 | 1.58 ± 0.53 (1.50) | 5.68 ± 3.29 (5.22) | 1.86 ± 0.34 (1.92) | 4.01 ± 0.81 (4.05) | 1.42 ± 0.48 (1.45) |
| right | p | 0.847 | 100/100 | 0 | 97 | 1.56 ± 0.51 (1.47) | 6.70 ± 15.26 (4.63) | 1.80 ± 0.42 (1.86) | 3.90 ± 0.96 (3.91) | 1.37 ± 0.53 (1.35) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 4.88 ± 2.43 (4.06) | 1.59 ± 0.32 (1.49) | 3.36 ± 0.67 (3.08) | 1.04 ± 0.42 (0.91) |
| forward/right | p | 0.858 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.04) | 3.78 ± 3.02 (2.85) | 1.49 ± 0.42 (1.38) | 3.20 ± 0.89 (2.98) | 0.96 ± 0.47 (0.78) |
| left/left | p | 0.853 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.98 ± 3.87 (5.04) | 1.89 ± 0.34 (2.02) | 4.10 ± 0.77 (4.28) | 1.48 ± 0.47 (1.58) |
| left/right | p | 0.879 | 25/25 | 0 | 24 | 1.62 ± 0.31 (1.62) | 4.42 ± 3.10 (4.25) | 1.97 ± 0.32 (2.08) | 4.34 ± 0.79 (4.71) | 1.60 ± 0.47 (1.69) |
| back/left | p | 0.834 | 25/25 | 0 | 25 | 2.27 ± 0.25 (2.20) | 5.84 ± 2.72 (6.17) | 2.06 ± 0.22 (2.15) | 4.49 ± 0.62 (4.84) | 1.71 ± 0.40 (1.89) |
| back/right | p | 0.829 | 25/25 | 0 | 24 | 2.21 ± 0.23 (2.20) | 11.97 ± 29.19 (5.53) | 1.98 ± 0.40 (2.13) | 4.29 ± 0.95 (4.71) | 1.63 ± 0.48 (1.71) |
| right/left | p | 0.837 | 25/25 | 0 | 24 | 1.60 ± 0.34 (1.56) | 6.01 ± 3.78 (4.83) | 1.89 ± 0.28 (1.92) | 4.10 ± 0.71 (3.97) | 1.44 ± 0.37 (1.45) |
| right/right | p | 0.821 | 25/25 | 0 | 24 | 1.40 ± 0.33 (1.44) | 6.61 ± 4.45 (4.98) | 1.77 ± 0.29 (1.74) | 3.76 ± 0.71 (3.70) | 1.27 ± 0.37 (1.20) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.853 | 5.8 | 4.34 | 1.59 |
| p | normal | 0.834 | 6.6 | 3.57 | 1.19 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.799 | 0.27 | 1.99 ± 0.73 (1.74) | 3.16 | 0.97 |
| p | medium | 16 | 0.901 | 0.84 | 1.02 ± 0.19 (1.05) | 3.31 | 1.06 |
| p | strong | 126 | 0.857 | 0.59 | - | 4.40 | 1.63 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector right (0.829).
