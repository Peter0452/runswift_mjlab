# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-13-12_q6_q4_lowcap03/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 185 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.82 ± 0.59 (1.69) |
| Direction error [°] | 7.12 ± 5.42 (6.29) |
| Avg ball speed [m/s] | 2.78 ± 0.59 (3.04) |
| Peak ball speed [m/s] | 5.66 ± 1.27 (6.38) |
| Distance [m] | 2.83 ± 0.97 (3.33) |
| Path length [m] | 2.84 ± 0.97 (3.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.878 | 50/50 | 0 | 49 | 1.25 ± 0.25 (1.27) | 5.02 ± 3.51 (4.68) | 2.72 ± 0.56 (2.88) | 5.59 ± 1.22 (6.20) | 2.75 ± 0.92 (3.05) |
| left | p | 0.867 | 50/50 | 0 | 46 | 1.73 ± 0.37 (1.69) | 6.34 ± 4.61 (5.65) | 2.77 ± 0.55 (3.05) | 5.66 ± 1.23 (6.41) | 2.82 ± 0.96 (3.40) |
| back | p | 0.790 | 50/50 | 0 | 43 | 2.58 ± 0.33 (2.53) | 10.07 ± 7.21 (8.84) | 2.88 ± 0.68 (3.19) | 5.83 ± 1.41 (6.52) | 3.04 ± 1.00 (3.54) |
| right | p | 0.843 | 50/50 | 0 | 47 | 1.71 ± 0.37 (1.62) | 7.04 ± 4.30 (6.41) | 2.73 ± 0.54 (2.95) | 5.53 ± 1.21 (6.26) | 2.73 ± 0.96 (3.23) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.845 | 100/100 | 0 | 94 | 1.82 ± 0.58 (1.70) | 6.67 ± 4.43 (5.93) | 2.80 ± 0.55 (3.04) | 5.71 ± 1.20 (6.37) | 2.86 ± 0.93 (3.33) |
| right | p | 0.844 | 100/100 | 0 | 91 | 1.82 ± 0.59 (1.69) | 7.56 ± 6.23 (6.57) | 2.75 ± 0.62 (3.03) | 5.60 ± 1.34 (6.38) | 2.81 ± 1.00 (3.33) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.873 | 25/25 | 0 | 24 | 1.24 ± 0.26 (1.26) | 5.03 ± 3.70 (4.63) | 2.69 ± 0.54 (2.93) | 5.55 ± 1.20 (6.10) | 2.71 ± 0.91 (2.96) |
| forward/right | p | 0.884 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.30) | 5.02 ± 3.30 (4.80) | 2.75 ± 0.59 (2.88) | 5.64 ± 1.23 (6.30) | 2.78 ± 0.93 (3.14) |
| left/left | p | 0.877 | 25/25 | 0 | 24 | 1.67 ± 0.35 (1.58) | 5.74 ± 4.02 (5.41) | 2.83 ± 0.50 (3.07) | 5.79 ± 1.15 (6.44) | 2.91 ± 0.90 (3.42) |
| left/right | p | 0.858 | 25/25 | 0 | 22 | 1.80 ± 0.38 (1.78) | 6.94 ± 5.06 (5.86) | 2.72 ± 0.58 (3.05) | 5.53 ± 1.29 (6.37) | 2.74 ± 1.02 (3.33) |
| back/left | p | 0.792 | 25/25 | 0 | 22 | 2.58 ± 0.30 (2.58) | 9.21 ± 4.97 (8.81) | 2.95 ± 0.57 (3.19) | 5.94 ± 1.18 (6.49) | 3.10 ± 0.93 (3.52) |
| back/right | p | 0.787 | 25/25 | 0 | 21 | 2.58 ± 0.36 (2.52) | 10.93 ± 8.82 (8.99) | 2.81 ± 0.77 (3.18) | 5.73 ± 1.60 (6.54) | 2.98 ± 1.07 (3.56) |
| right/left | p | 0.839 | 25/25 | 0 | 24 | 1.80 ± 0.37 (1.76) | 6.72 ± 3.75 (6.39) | 2.73 ± 0.55 (2.98) | 5.55 ± 1.22 (6.29) | 2.72 ± 0.95 (3.24) |
| right/right | p | 0.846 | 25/25 | 0 | 23 | 1.63 ± 0.34 (1.56) | 7.36 ± 4.77 (6.61) | 2.73 ± 0.52 (2.82) | 5.52 ± 1.20 (6.13) | 2.74 ± 0.98 (3.22) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.884 | 7.5 | 6.57 | 3.53 |
| p | normal | 0.804 | 6.7 | 4.74 | 2.14 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.742 | 0.08 | 2.61 ± 0.88 (2.41) | 4.06 | 1.61 |
| p | medium | 20 | 0.874 | 0.71 | 1.29 ± 0.14 (1.30) | 4.12 | 1.64 |
| p | strong | 126 | 0.884 | 0.88 | - | 6.58 | 3.55 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector back (0.790).
