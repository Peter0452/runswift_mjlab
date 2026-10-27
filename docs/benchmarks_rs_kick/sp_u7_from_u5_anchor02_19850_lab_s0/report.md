# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.57 ± 0.52 (1.50) |
| Direction error [°] | 4.71 ± 3.02 (4.06) |
| Avg ball speed [m/s] | 1.75 ± 0.34 (1.79) |
| Peak ball speed [m/s] | 4.12 ± 0.80 (4.32) |
| Distance [m] | 1.48 ± 0.47 (1.50) |
| Path length [m] | 1.48 ± 0.48 (1.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 50 | 1.03 ± 0.22 (1.05) | 4.37 ± 2.82 (3.94) | 1.48 ± 0.32 (1.45) | 3.54 ± 0.76 (3.39) | 1.15 ± 0.44 (1.08) |
| left | p | 0.864 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.52) | 5.20 ± 2.92 (4.99) | 1.82 ± 0.29 (1.87) | 4.29 ± 0.72 (4.51) | 1.58 ± 0.44 (1.66) |
| back | p | 0.849 | 50/50 | 0 | 50 | 2.24 ± 0.26 (2.21) | 4.51 ± 3.05 (3.78) | 1.92 ± 0.26 (2.00) | 4.48 ± 0.63 (4.71) | 1.70 ± 0.41 (1.84) |
| right | p | 0.849 | 50/50 | 0 | 50 | 1.52 ± 0.34 (1.48) | 4.75 ± 3.19 (3.99) | 1.76 ± 0.31 (1.72) | 4.17 ± 0.74 (4.27) | 1.47 ± 0.42 (1.47) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 100 | 1.58 ± 0.52 (1.51) | 4.61 ± 2.76 (4.08) | 1.75 ± 0.36 (1.82) | 4.12 ± 0.83 (4.32) | 1.48 ± 0.49 (1.53) |
| right | p | 0.851 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.49) | 4.80 ± 3.25 (3.86) | 1.74 ± 0.31 (1.75) | 4.12 ± 0.77 (4.33) | 1.47 ± 0.45 (1.48) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.08) | 3.84 ± 2.28 (3.26) | 1.49 ± 0.35 (1.45) | 3.54 ± 0.78 (3.30) | 1.17 ± 0.48 (1.07) |
| forward/right | p | 0.843 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.02) | 4.90 ± 3.19 (4.20) | 1.47 ± 0.29 (1.46) | 3.54 ± 0.74 (3.53) | 1.12 ± 0.39 (1.09) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.48) | 5.34 ± 2.43 (5.46) | 1.77 ± 0.31 (1.84) | 4.12 ± 0.75 (4.48) | 1.49 ± 0.44 (1.56) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.58) | 5.05 ± 3.34 (3.65) | 1.86 ± 0.26 (1.92) | 4.46 ± 0.64 (4.63) | 1.66 ± 0.41 (1.76) |
| back/left | p | 0.850 | 25/25 | 0 | 25 | 2.26 ± 0.26 (2.20) | 4.38 ± 3.00 (3.84) | 1.95 ± 0.26 (2.00) | 4.47 ± 0.61 (4.71) | 1.71 ± 0.43 (1.85) |
| back/right | p | 0.848 | 25/25 | 0 | 25 | 2.22 ± 0.26 (2.22) | 4.65 ± 3.10 (3.55) | 1.89 ± 0.26 (2.00) | 4.48 ± 0.64 (4.70) | 1.69 ± 0.40 (1.82) |
| right/left | p | 0.855 | 25/25 | 0 | 25 | 1.62 ± 0.32 (1.58) | 4.90 ± 3.03 (4.15) | 1.79 ± 0.35 (1.87) | 4.35 ± 0.82 (4.72) | 1.55 ± 0.47 (1.61) |
| right/right | p | 0.842 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.44) | 4.60 ± 3.33 (3.76) | 1.73 ± 0.25 (1.68) | 3.99 ± 0.61 (3.75) | 1.40 ± 0.35 (1.32) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.867 | 5.0 | 4.53 | 1.70 |
| p | normal | 0.838 | 4.5 | 3.71 | 1.25 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.795 | 0.21 | 2.09 ± 0.64 (1.97) | 3.34 | 1.04 |
| p | medium | 16 | 0.938 | 0.87 | 1.03 ± 0.15 (1.02) | 3.34 | 1.05 |
| p | strong | 126 | 0.868 | 0.61 | - | 4.58 | 1.73 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector forward (0.847).
