# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.846** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.84 ± 0.56 (1.78) |
| Direction error [°] | 5.31 ± 3.52 (4.90) |
| Avg ball speed [m/s] | 2.16 ± 0.40 (2.24) |
| Peak ball speed [m/s] | 5.09 ± 0.94 (5.39) |
| Distance [m] | 2.13 ± 0.63 (2.17) |
| Path length [m] | 2.14 ± 0.63 (2.18) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.852 | 50/50 | 0 | 49 | 1.28 ± 0.25 (1.29) | 5.07 ± 3.39 (4.52) | 2.10 ± 0.46 (2.08) | 4.94 ± 1.02 (5.10) | 2.01 ± 0.68 (2.01) |
| left | p | 0.875 | 50/50 | 0 | 49 | 1.76 ± 0.36 (1.81) | 5.32 ± 3.48 (5.38) | 2.19 ± 0.36 (2.28) | 5.20 ± 0.92 (5.53) | 2.19 ± 0.60 (2.29) |
| back | p | 0.801 | 50/50 | 0 | 49 | 2.56 ± 0.33 (2.50) | 6.41 ± 3.82 (6.26) | 2.24 ± 0.35 (2.28) | 5.19 ± 0.83 (5.44) | 2.23 ± 0.58 (2.21) |
| right | p | 0.856 | 50/50 | 0 | 50 | 1.75 ± 0.34 (1.74) | 4.45 ± 3.04 (3.69) | 2.13 ± 0.40 (2.23) | 5.02 ± 0.95 (5.29) | 2.08 ± 0.62 (2.07) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 99 | 1.85 ± 0.57 (1.79) | 5.32 ± 3.51 (4.82) | 2.19 ± 0.39 (2.24) | 5.13 ± 0.93 (5.44) | 2.16 ± 0.62 (2.27) |
| right | p | 0.844 | 100/100 | 0 | 98 | 1.83 ± 0.56 (1.75) | 5.31 ± 3.52 (4.91) | 2.14 ± 0.40 (2.23) | 5.05 ± 0.95 (5.31) | 2.09 ± 0.64 (2.13) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 24 | 1.28 ± 0.24 (1.28) | 5.81 ± 3.56 (5.21) | 2.16 ± 0.45 (2.08) | 5.06 ± 0.99 (5.37) | 2.12 ± 0.66 (2.13) |
| forward/right | p | 0.857 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.30) | 4.34 ± 3.04 (2.87) | 2.05 ± 0.45 (2.04) | 4.82 ± 1.04 (4.84) | 1.90 ± 0.68 (1.83) |
| left/left | p | 0.872 | 25/25 | 0 | 25 | 1.67 ± 0.36 (1.78) | 5.29 ± 3.37 (5.02) | 2.17 ± 0.32 (2.19) | 5.15 ± 0.83 (5.40) | 2.13 ± 0.51 (2.27) |
| left/right | p | 0.877 | 25/25 | 0 | 24 | 1.86 ± 0.33 (1.90) | 5.34 ± 3.59 (5.41) | 2.21 ± 0.40 (2.34) | 5.25 ± 1.00 (5.68) | 2.26 ± 0.68 (2.31) |
| back/left | p | 0.799 | 25/25 | 0 | 25 | 2.59 ± 0.31 (2.60) | 6.55 ± 3.82 (6.79) | 2.23 ± 0.34 (2.27) | 5.14 ± 0.85 (5.46) | 2.22 ± 0.61 (2.27) |
| back/right | p | 0.804 | 25/25 | 0 | 24 | 2.54 ± 0.35 (2.48) | 6.27 ± 3.82 (5.87) | 2.24 ± 0.36 (2.29) | 5.25 ± 0.80 (5.19) | 2.24 ± 0.54 (2.18) |
| right/left | p | 0.874 | 25/25 | 0 | 25 | 1.85 ± 0.30 (1.80) | 3.63 ± 2.46 (2.38) | 2.19 ± 0.43 (2.29) | 5.16 ± 1.04 (5.53) | 2.18 ± 0.66 (2.34) |
| right/right | p | 0.838 | 25/25 | 0 | 25 | 1.65 ± 0.35 (1.72) | 5.28 ± 3.32 (4.70) | 2.07 ± 0.36 (2.10) | 4.88 ± 0.83 (5.03) | 1.97 ± 0.55 (1.94) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.894 | 4.5 | 5.76 | 2.52 |
| p | normal | 0.797 | 6.1 | 4.42 | 1.73 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.742 | 0.08 | 2.50 ± 0.76 (2.29) | 3.99 | 1.45 |
| p | medium | 16 | 0.866 | 0.74 | 1.24 ± 0.21 (1.25) | 4.02 | 1.51 |
| p | strong | 126 | 0.891 | 0.76 | - | 5.73 | 2.52 |

## Notes

- p: score 0.846, 200/200 kicked, 0 fell; worst sector back (0.801).
