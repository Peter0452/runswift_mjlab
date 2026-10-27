# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.841** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.58 ± 0.53 (1.49) |
| Direction error [°] | 6.95 ± 12.12 (5.98) |
| Avg ball speed [m/s] | 2.25 ± 0.40 (2.28) |
| Peak ball speed [m/s] | 4.71 ± 0.91 (4.91) |
| Distance [m] | 2.13 ± 0.64 (2.23) |
| Path length [m] | 2.14 ± 0.65 (2.24) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.831 | 50/50 | 0 | 49 | 1.04 ± 0.23 (1.10) | 5.96 ± 3.86 (4.72) | 2.03 ± 0.31 (1.93) | 4.22 ± 0.71 (4.01) | 1.75 ± 0.49 (1.59) |
| left | p | 0.865 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.51) | 5.99 ± 3.87 (5.77) | 2.36 ± 0.36 (2.52) | 4.94 ± 0.82 (5.31) | 2.30 ± 0.59 (2.44) |
| back | p | 0.840 | 50/50 | 0 | 49 | 2.25 ± 0.27 (2.20) | 8.86 ± 23.16 (5.95) | 2.39 ± 0.46 (2.55) | 5.01 ± 1.02 (5.45) | 2.38 ± 0.69 (2.62) |
| right | p | 0.829 | 50/50 | 0 | 48 | 1.52 ± 0.35 (1.48) | 7.01 ± 3.97 (7.13) | 2.24 ± 0.36 (2.26) | 4.66 ± 0.85 (4.74) | 2.09 ± 0.60 (2.15) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 100 | 1.59 ± 0.54 (1.49) | 6.08 ± 3.54 (5.95) | 2.26 ± 0.38 (2.27) | 4.73 ± 0.87 (4.95) | 2.15 ± 0.64 (2.25) |
| right | p | 0.838 | 100/100 | 0 | 96 | 1.58 ± 0.52 (1.49) | 7.83 ± 16.72 (6.06) | 2.24 ± 0.42 (2.30) | 4.69 ± 0.95 (4.87) | 2.12 ± 0.65 (2.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 6.09 ± 3.87 (4.61) | 2.01 ± 0.27 (1.94) | 4.19 ± 0.63 (4.01) | 1.73 ± 0.46 (1.58) |
| forward/right | p | 0.829 | 25/25 | 0 | 24 | 1.04 ± 0.24 (1.10) | 5.84 ± 3.85 (4.73) | 2.04 ± 0.35 (1.90) | 4.26 ± 0.77 (4.02) | 1.78 ± 0.52 (1.68) |
| left/left | p | 0.859 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.44) | 6.06 ± 4.19 (6.41) | 2.29 ± 0.37 (2.49) | 4.80 ± 0.85 (5.24) | 2.19 ± 0.60 (2.44) |
| left/right | p | 0.871 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.60) | 5.92 ± 3.51 (5.65) | 2.42 ± 0.34 (2.52) | 5.09 ± 0.76 (5.48) | 2.40 ± 0.56 (2.57) |
| back/left | p | 0.842 | 25/25 | 0 | 25 | 2.29 ± 0.27 (2.20) | 5.94 ± 2.86 (5.91) | 2.45 ± 0.39 (2.61) | 5.13 ± 0.87 (5.49) | 2.46 ± 0.68 (2.76) |
| back/right | p | 0.838 | 25/25 | 0 | 24 | 2.22 ± 0.26 (2.18) | 11.78 ± 32.37 (6.13) | 2.33 ± 0.51 (2.47) | 4.89 ± 1.13 (5.37) | 2.30 ± 0.69 (2.56) |
| right/left | p | 0.842 | 25/25 | 0 | 25 | 1.62 ± 0.33 (1.58) | 6.24 ± 3.09 (6.19) | 2.31 ± 0.35 (2.33) | 4.81 ± 0.81 (5.02) | 2.20 ± 0.58 (2.26) |
| right/right | p | 0.816 | 25/25 | 0 | 23 | 1.43 ± 0.34 (1.44) | 7.77 ± 4.57 (8.45) | 2.17 ± 0.35 (2.10) | 4.50 ± 0.86 (4.12) | 1.98 ± 0.60 (1.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.873 | 6.1 | 5.23 | 2.49 |
| p | normal | 0.809 | 7.8 | 4.18 | 1.77 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.754 | 0.11 | 2.34 ± 0.76 (2.20) | 3.72 | 1.44 |
| p | medium | 16 | 0.877 | 0.80 | 1.16 ± 0.17 (1.17) | 3.77 | 1.48 |
| p | strong | 126 | 0.877 | 0.70 | - | 5.28 | 2.53 |

## Notes

- p: score 0.841, 200/200 kicked, 0 fell; worst sector right (0.829).
