# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.865** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 1.70 ± 0.56 (1.64) |
| Direction error [°] | 4.80 ± 3.02 (4.28) |
| Avg ball speed [m/s] | 1.77 ± 0.49 (1.96) |
| Peak ball speed [m/s] | 3.97 ± 1.18 (4.38) |
| Distance [m] | 1.40 ± 0.63 (1.56) |
| Path length [m] | 1.40 ± 0.64 (1.56) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.862 | 50/50 | 0 | 49 | 1.10 ± 0.25 (1.12) | 4.78 ± 3.50 (3.66) | 1.48 ± 0.54 (1.55) | 3.28 ± 1.18 (3.28) | 1.01 ± 0.58 (1.00) |
| left | p | 0.885 | 50/50 | 0 | 50 | 1.65 ± 0.38 (1.66) | 4.52 ± 2.88 (4.04) | 1.87 ± 0.42 (2.02) | 4.20 ± 1.02 (4.58) | 1.51 ± 0.56 (1.63) |
| back | p | 0.843 | 50/50 | 0 | 50 | 2.40 ± 0.27 (2.40) | 5.13 ± 2.59 (4.81) | 1.94 ± 0.38 (2.13) | 4.37 ± 1.00 (4.86) | 1.63 ± 0.58 (1.86) |
| right | p | 0.871 | 50/50 | 0 | 50 | 1.65 ± 0.37 (1.63) | 4.77 ± 3.00 (4.68) | 1.80 ± 0.49 (2.06) | 4.03 ± 1.20 (4.60) | 1.43 ± 0.63 (1.66) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.863 | 100/100 | 0 | 100 | 1.70 ± 0.57 (1.65) | 4.81 ± 2.95 (4.68) | 1.79 ± 0.46 (1.96) | 4.00 ± 1.14 (4.35) | 1.41 ± 0.61 (1.56) |
| right | p | 0.867 | 100/100 | 0 | 99 | 1.70 ± 0.56 (1.64) | 4.79 ± 3.09 (4.14) | 1.76 ± 0.52 (1.97) | 3.94 ± 1.21 (4.41) | 1.38 ± 0.65 (1.56) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.867 | 25/25 | 0 | 25 | 1.10 ± 0.25 (1.12) | 4.82 ± 3.46 (3.53) | 1.58 ± 0.52 (1.81) | 3.43 ± 1.16 (3.97) | 1.10 ± 0.58 (1.28) |
| forward/right | p | 0.856 | 25/25 | 0 | 24 | 1.10 ± 0.25 (1.12) | 4.74 ± 3.54 (3.94) | 1.39 ± 0.54 (1.36) | 3.13 ± 1.18 (2.89) | 0.92 ± 0.57 (0.85) |
| left/left | p | 0.874 | 25/25 | 0 | 25 | 1.52 ± 0.36 (1.64) | 4.96 ± 3.23 (4.06) | 1.77 ± 0.39 (1.89) | 3.98 ± 0.98 (4.29) | 1.37 ± 0.53 (1.46) |
| left/right | p | 0.895 | 25/25 | 0 | 25 | 1.78 ± 0.36 (1.78) | 4.08 ± 2.41 (4.01) | 1.97 ± 0.43 (2.16) | 4.43 ± 1.01 (4.89) | 1.66 ± 0.56 (1.98) |
| back/left | p | 0.836 | 25/25 | 0 | 25 | 2.42 ± 0.29 (2.38) | 5.37 ± 2.71 (5.48) | 1.95 ± 0.38 (2.14) | 4.39 ± 1.01 (4.87) | 1.65 ± 0.60 (1.91) |
| back/right | p | 0.849 | 25/25 | 0 | 25 | 2.38 ± 0.25 (2.42) | 4.89 ± 2.45 (4.41) | 1.94 ± 0.37 (2.07) | 4.34 ± 0.98 (4.85) | 1.61 ± 0.55 (1.78) |
| right/left | p | 0.876 | 25/25 | 0 | 25 | 1.77 ± 0.33 (1.66) | 4.10 ± 2.05 (4.61) | 1.87 ± 0.47 (2.12) | 4.19 ± 1.17 (4.87) | 1.52 ± 0.61 (1.81) |
| right/right | p | 0.866 | 25/25 | 0 | 25 | 1.54 ± 0.37 (1.58) | 5.44 ± 3.58 (4.82) | 1.74 ± 0.51 (1.86) | 3.87 ± 1.21 (4.28) | 1.34 ± 0.64 (1.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.870 | 4.8 | 4.76 | 1.81 |
| p | normal | 0.860 | 4.8 | 3.18 | 0.98 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.837 | 0.49 | 1.63 ± 0.68 (1.41) | 2.56 | 0.66 |
| p | medium | 16 | 0.917 | 0.81 | 0.84 ± 0.21 (0.90) | 2.72 | 0.73 |
| p | strong | 126 | 0.871 | 0.64 | - | 4.78 | 1.82 |

## Notes

- p: score 0.865, 200/200 kicked, 0 fell; worst sector back (0.843).
