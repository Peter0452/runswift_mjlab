# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_12-23-01_u8_timecost1_anchor02/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.56 ± 0.51 (1.48) |
| Direction error [°] | 5.91 ± 12.21 (4.49) |
| Avg ball speed [m/s] | 1.91 ± 0.32 (2.00) |
| Peak ball speed [m/s] | 4.16 ± 0.79 (4.37) |
| Distance [m] | 1.56 ± 0.47 (1.59) |
| Path length [m] | 1.56 ± 0.47 (1.60) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.843 | 50/50 | 0 | 50 | 1.02 ± 0.22 (1.05) | 4.81 ± 3.30 (3.43) | 1.71 ± 0.32 (1.71) | 3.68 ± 0.74 (3.58) | 1.26 ± 0.43 (1.22) |
| left | p | 0.869 | 50/50 | 0 | 50 | 1.51 ± 0.33 (1.51) | 4.93 ± 3.29 (4.33) | 1.99 ± 0.29 (2.13) | 4.36 ± 0.73 (4.69) | 1.68 ± 0.44 (1.82) |
| back | p | 0.838 | 50/50 | 0 | 49 | 2.21 ± 0.25 (2.18) | 8.74 ± 23.44 (5.69) | 2.02 ± 0.34 (2.15) | 4.41 ± 0.83 (4.76) | 1.74 ± 0.46 (1.93) |
| right | p | 0.842 | 50/50 | 0 | 49 | 1.48 ± 0.33 (1.47) | 5.14 ± 3.78 (4.11) | 1.92 ± 0.25 (1.99) | 4.17 ± 0.63 (4.33) | 1.54 ± 0.37 (1.54) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 99 | 1.56 ± 0.52 (1.49) | 5.19 ± 3.38 (4.40) | 1.93 ± 0.28 (2.03) | 4.20 ± 0.73 (4.38) | 1.58 ± 0.44 (1.60) |
| right | p | 0.849 | 100/100 | 0 | 99 | 1.55 ± 0.50 (1.48) | 6.63 ± 16.90 (4.52) | 1.89 ± 0.36 (1.99) | 4.11 ± 0.85 (4.37) | 1.53 ± 0.48 (1.58) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.06) | 5.11 ± 3.46 (3.63) | 1.74 ± 0.26 (1.74) | 3.70 ± 0.60 (3.64) | 1.27 ± 0.37 (1.23) |
| forward/right | p | 0.850 | 25/25 | 0 | 25 | 1.01 ± 0.22 (1.04) | 4.51 ± 3.10 (3.22) | 1.69 ± 0.36 (1.64) | 3.66 ± 0.86 (3.52) | 1.24 ± 0.47 (1.17) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.46) | 5.56 ± 3.69 (5.36) | 1.96 ± 0.29 (2.05) | 4.28 ± 0.75 (4.56) | 1.63 ± 0.43 (1.80) |
| left/right | p | 0.880 | 25/25 | 0 | 25 | 1.61 ± 0.30 (1.60) | 4.30 ± 2.70 (3.54) | 2.01 ± 0.29 (2.13) | 4.45 ± 0.70 (4.78) | 1.73 ± 0.45 (1.89) |
| back/left | p | 0.842 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.18) | 5.21 ± 2.34 (5.22) | 2.06 ± 0.22 (2.15) | 4.52 ± 0.64 (4.89) | 1.79 ± 0.42 (2.01) |
| back/right | p | 0.834 | 25/25 | 0 | 24 | 2.17 ± 0.22 (2.16) | 12.27 ± 32.68 (5.93) | 1.99 ± 0.42 (2.14) | 4.31 ± 0.98 (4.71) | 1.70 ± 0.49 (1.77) |
| right/left | p | 0.852 | 25/25 | 0 | 24 | 1.58 ± 0.30 (1.56) | 4.86 ± 3.80 (4.10) | 1.97 ± 0.24 (2.05) | 4.31 ± 0.65 (4.61) | 1.63 ± 0.38 (1.73) |
| right/right | p | 0.833 | 25/25 | 0 | 25 | 1.39 ± 0.33 (1.42) | 5.42 ± 3.74 (4.12) | 1.86 ± 0.24 (1.93) | 4.02 ± 0.57 (4.22) | 1.46 ± 0.33 (1.43) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.867 | 5.1 | 4.56 | 1.78 |
| p | normal | 0.830 | 6.7 | 3.75 | 1.33 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.782 | 0.20 | 2.11 ± 0.70 (1.94) | 3.35 | 1.11 |
| p | medium | 16 | 0.916 | 0.87 | 1.05 ± 0.14 (1.12) | 3.40 | 1.13 |
| p | strong | 126 | 0.870 | 0.62 | - | 4.62 | 1.81 |

## Notes

- p: score 0.848, 200/200 kicked, 0 fell; worst sector back (0.838).
