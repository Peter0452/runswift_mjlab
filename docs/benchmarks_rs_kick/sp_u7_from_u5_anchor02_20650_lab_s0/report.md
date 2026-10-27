# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.58 ± 0.51 (1.51) |
| Direction error [°] | 4.67 ± 2.85 (4.18) |
| Avg ball speed [m/s] | 1.97 ± 0.31 (2.02) |
| Peak ball speed [m/s] | 4.28 ± 0.77 (4.48) |
| Distance [m] | 1.64 ± 0.46 (1.61) |
| Path length [m] | 1.64 ± 0.46 (1.63) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.856 | 50/50 | 0 | 50 | 1.05 ± 0.22 (1.06) | 3.91 ± 2.94 (2.70) | 1.79 ± 0.38 (1.90) | 3.86 ± 0.89 (4.14) | 1.38 ± 0.49 (1.48) |
| left | p | 0.870 | 50/50 | 0 | 50 | 1.53 ± 0.32 (1.52) | 4.76 ± 2.44 (4.17) | 2.03 ± 0.23 (2.07) | 4.44 ± 0.62 (4.65) | 1.72 ± 0.40 (1.78) |
| back | p | 0.840 | 50/50 | 0 | 50 | 2.23 ± 0.26 (2.20) | 5.35 ± 2.78 (4.88) | 2.08 ± 0.25 (2.11) | 4.52 ± 0.65 (4.62) | 1.80 ± 0.42 (1.89) |
| right | p | 0.852 | 50/50 | 0 | 50 | 1.52 ± 0.33 (1.48) | 4.65 ± 3.03 (4.62) | 1.99 ± 0.27 (2.04) | 4.31 ± 0.71 (4.61) | 1.65 ± 0.41 (1.61) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 100 | 1.59 ± 0.52 (1.52) | 4.69 ± 2.75 (4.08) | 1.99 ± 0.27 (2.04) | 4.32 ± 0.71 (4.49) | 1.66 ± 0.44 (1.63) |
| right | p | 0.855 | 100/100 | 0 | 100 | 1.57 ± 0.50 (1.50) | 4.64 ± 2.95 (4.23) | 1.95 ± 0.34 (2.01) | 4.25 ± 0.82 (4.47) | 1.61 ± 0.48 (1.61) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.849 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.06) | 4.24 ± 3.04 (2.72) | 1.81 ± 0.29 (1.90) | 3.90 ± 0.72 (4.18) | 1.40 ± 0.42 (1.50) |
| forward/right | p | 0.863 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 3.57 ± 2.80 (2.41) | 1.77 ± 0.46 (1.91) | 3.83 ± 1.02 (4.10) | 1.36 ± 0.55 (1.46) |
| left/left | p | 0.867 | 25/25 | 0 | 25 | 1.45 ± 0.33 (1.52) | 4.70 ± 2.50 (4.04) | 2.01 ± 0.20 (2.00) | 4.36 ± 0.55 (4.63) | 1.67 ± 0.36 (1.61) |
| left/right | p | 0.873 | 25/25 | 0 | 25 | 1.61 ± 0.29 (1.60) | 4.83 ± 2.38 (4.68) | 2.05 ± 0.26 (2.10) | 4.52 ± 0.67 (4.73) | 1.77 ± 0.44 (1.80) |
| back/left | p | 0.837 | 25/25 | 0 | 25 | 2.26 ± 0.27 (2.20) | 5.47 ± 2.83 (4.92) | 2.12 ± 0.21 (2.12) | 4.60 ± 0.62 (4.75) | 1.87 ± 0.42 (1.94) |
| back/right | p | 0.843 | 25/25 | 0 | 25 | 2.21 ± 0.25 (2.20) | 5.24 ± 2.72 (4.85) | 2.03 ± 0.27 (2.05) | 4.43 ± 0.68 (4.53) | 1.73 ± 0.41 (1.72) |
| right/left | p | 0.860 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.58) | 4.35 ± 2.42 (4.85) | 2.02 ± 0.28 (2.12) | 4.42 ± 0.74 (4.68) | 1.71 ± 0.43 (1.79) |
| right/right | p | 0.843 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.46) | 4.94 ± 3.50 (4.40) | 1.95 ± 0.25 (1.95) | 4.21 ± 0.67 (4.35) | 1.59 ± 0.38 (1.53) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.872 | 5.1 | 4.73 | 1.88 |
| p | normal | 0.837 | 4.2 | 3.83 | 1.39 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.792 | 0.19 | 2.15 ± 0.68 (1.97) | 3.43 | 1.17 |
| p | medium | 16 | 0.921 | 0.84 | 1.07 ± 0.18 (1.08) | 3.47 | 1.17 |
| p | strong | 126 | 0.875 | 0.64 | - | 4.78 | 1.91 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.840).
