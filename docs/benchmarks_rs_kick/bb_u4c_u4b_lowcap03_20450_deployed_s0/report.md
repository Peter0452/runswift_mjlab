# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_05-06-31_u4c_u4b_lowcap03/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.85 ± 0.60 (1.74) |
| Direction error [°] | 5.23 ± 3.70 (4.47) |
| Avg ball speed [m/s] | 2.16 ± 0.39 (2.23) |
| Peak ball speed [m/s] | 4.76 ± 1.05 (5.24) |
| Distance [m] | 1.86 ± 0.62 (1.96) |
| Path length [m] | 1.87 ± 0.62 (1.97) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.855 | 50/50 | 0 | 48 | 1.27 ± 0.23 (1.31) | 5.25 ± 4.02 (4.27) | 2.03 ± 0.44 (1.86) | 4.49 ± 1.19 (4.17) | 1.68 ± 0.67 (1.34) |
| left | p | 0.878 | 50/50 | 0 | 49 | 1.76 ± 0.36 (1.81) | 5.01 ± 3.77 (4.66) | 2.25 ± 0.33 (2.33) | 4.97 ± 0.94 (5.42) | 1.98 ± 0.56 (2.06) |
| back | p | 0.811 | 50/50 | 0 | 50 | 2.60 ± 0.45 (2.50) | 5.66 ± 3.13 (5.20) | 2.24 ± 0.34 (2.27) | 4.92 ± 0.95 (5.40) | 1.98 ± 0.59 (2.08) |
| right | p | 0.854 | 50/50 | 0 | 49 | 1.74 ± 0.39 (1.69) | 5.02 ± 3.80 (3.81) | 2.12 ± 0.37 (2.19) | 4.65 ± 1.03 (5.17) | 1.79 ± 0.58 (1.86) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 97 | 1.86 ± 0.63 (1.78) | 5.06 ± 3.82 (4.26) | 2.17 ± 0.39 (2.23) | 4.80 ± 1.07 (5.24) | 1.88 ± 0.63 (1.96) |
| right | p | 0.847 | 100/100 | 0 | 99 | 1.83 ± 0.58 (1.72) | 5.41 ± 3.57 (4.97) | 2.14 ± 0.38 (2.23) | 4.72 ± 1.03 (5.23) | 1.83 ± 0.60 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.860 | 25/25 | 0 | 24 | 1.27 ± 0.21 (1.28) | 5.10 ± 3.69 (4.25) | 2.07 ± 0.45 (1.98) | 4.56 ± 1.20 (4.53) | 1.74 ± 0.68 (1.43) |
| forward/right | p | 0.850 | 25/25 | 0 | 24 | 1.28 ± 0.25 (1.32) | 5.40 ± 4.32 (4.29) | 1.99 ± 0.43 (1.78) | 4.42 ± 1.17 (3.84) | 1.62 ± 0.65 (1.27) |
| left/left | p | 0.879 | 25/25 | 0 | 24 | 1.67 ± 0.36 (1.80) | 4.72 ± 4.48 (3.79) | 2.20 ± 0.33 (2.22) | 4.85 ± 0.95 (5.10) | 1.90 ± 0.53 (1.96) |
| left/right | p | 0.877 | 25/25 | 0 | 25 | 1.86 ± 0.34 (1.94) | 5.29 ± 2.87 (4.90) | 2.30 ± 0.33 (2.35) | 5.10 ± 0.92 (5.48) | 2.06 ± 0.59 (2.09) |
| back/left | p | 0.810 | 25/25 | 0 | 25 | 2.64 ± 0.50 (2.52) | 5.39 ± 3.19 (4.41) | 2.29 ± 0.31 (2.28) | 5.01 ± 0.94 (5.43) | 2.06 ± 0.62 (2.10) |
| back/right | p | 0.812 | 25/25 | 0 | 25 | 2.56 ± 0.39 (2.50) | 5.93 ± 3.04 (5.93) | 2.19 ± 0.37 (2.26) | 4.83 ± 0.95 (5.37) | 1.91 ± 0.54 (2.07) |
| right/left | p | 0.859 | 25/25 | 0 | 24 | 1.86 ± 0.39 (1.76) | 5.01 ± 3.80 (4.11) | 2.14 ± 0.43 (2.23) | 4.76 ± 1.12 (5.24) | 1.84 ± 0.64 (2.01) |
| right/right | p | 0.848 | 25/25 | 0 | 25 | 1.63 ± 0.35 (1.54) | 5.03 ± 3.80 (3.52) | 2.10 ± 0.30 (2.07) | 4.55 ± 0.92 (4.74) | 1.74 ± 0.52 (1.48) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.881 | 5.3 | 5.48 | 2.23 |
| p | normal | 0.818 | 5.2 | 4.04 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.769 | 0.19 | 2.18 ± 0.66 (1.98) | 3.46 | 1.16 |
| p | medium | 16 | 0.897 | 0.85 | 1.12 ± 0.14 (1.12) | 3.63 | 1.30 |
| p | strong | 126 | 0.881 | 0.73 | - | 5.50 | 2.25 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector back (0.811).
