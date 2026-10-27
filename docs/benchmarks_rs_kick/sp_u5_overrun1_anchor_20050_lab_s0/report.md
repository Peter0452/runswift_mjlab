# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 5 |
| Time to kick [s] | 1.55 ± 0.51 (1.48) |
| Direction error [°] | 7.86 ± 17.41 (5.17) |
| Avg ball speed [m/s] | 2.22 ± 0.51 (2.34) |
| Peak ball speed [m/s] | 4.65 ± 1.12 (5.01) |
| Distance [m] | 2.11 ± 0.72 (2.28) |
| Path length [m] | 2.12 ± 0.72 (2.29) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.839 | 50/50 | 0 | 50 | 1.03 ± 0.23 (1.05) | 5.41 ± 3.37 (4.86) | 2.04 ± 0.35 (1.95) | 4.25 ± 0.79 (3.98) | 1.77 ± 0.53 (1.57) |
| left | p | 0.862 | 50/50 | 0 | 49 | 1.50 ± 0.34 (1.51) | 7.43 ± 13.97 (5.02) | 2.32 ± 0.47 (2.46) | 4.88 ± 1.04 (5.27) | 2.27 ± 0.66 (2.45) |
| back | p | 0.838 | 50/50 | 0 | 48 | 2.17 ± 0.28 (2.14) | 12.31 ± 31.08 (6.38) | 2.26 ± 0.71 (2.47) | 4.73 ± 1.52 (5.25) | 2.25 ± 0.90 (2.54) |
| right | p | 0.839 | 50/50 | 0 | 50 | 1.50 ± 0.33 (1.46) | 6.29 ± 3.49 (6.23) | 2.28 ± 0.39 (2.41) | 4.75 ± 0.90 (5.20) | 2.14 ± 0.64 (2.31) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 99 | 1.55 ± 0.52 (1.48) | 7.56 ± 16.67 (5.50) | 2.23 ± 0.53 (2.32) | 4.67 ± 1.16 (4.98) | 2.13 ± 0.74 (2.28) |
| right | p | 0.843 | 100/100 | 0 | 98 | 1.55 ± 0.50 (1.47) | 8.15 ± 18.12 (5.05) | 2.22 ± 0.49 (2.37) | 4.64 ± 1.09 (5.05) | 2.09 ± 0.71 (2.27) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.844 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.06) | 5.29 ± 3.01 (4.65) | 2.07 ± 0.32 (1.98) | 4.33 ± 0.75 (3.97) | 1.83 ± 0.51 (1.57) |
| forward/right | p | 0.835 | 25/25 | 0 | 25 | 1.03 ± 0.23 (1.04) | 5.53 ± 3.69 (5.07) | 2.01 ± 0.37 (1.95) | 4.17 ± 0.82 (3.98) | 1.72 ± 0.55 (1.55) |
| left/left | p | 0.865 | 25/25 | 0 | 25 | 1.40 ± 0.33 (1.48) | 5.48 ± 3.80 (5.11) | 2.28 ± 0.34 (2.34) | 4.79 ± 0.81 (5.11) | 2.18 ± 0.58 (2.34) |
| left/right | p | 0.858 | 25/25 | 0 | 24 | 1.60 ± 0.32 (1.58) | 9.37 ± 19.19 (5.02) | 2.36 ± 0.57 (2.55) | 4.97 ± 1.23 (5.44) | 2.35 ± 0.72 (2.56) |
| back/left | p | 0.828 | 25/25 | 0 | 24 | 2.19 ± 0.32 (2.14) | 13.35 ± 32.11 (7.37) | 2.22 ± 0.84 (2.50) | 4.66 ± 1.78 (5.37) | 2.25 ± 1.02 (2.68) |
| back/right | p | 0.847 | 25/25 | 0 | 24 | 2.15 ± 0.24 (2.12) | 11.26 ± 29.99 (4.55) | 2.30 ± 0.54 (2.47) | 4.81 ± 1.19 (5.18) | 2.24 ± 0.75 (2.42) |
| right/left | p | 0.847 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.56) | 6.14 ± 3.54 (5.11) | 2.33 ± 0.40 (2.53) | 4.88 ± 0.91 (5.31) | 2.26 ± 0.65 (2.44) |
| right/right | p | 0.831 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.44) | 6.45 ± 3.43 (6.68) | 2.24 ± 0.38 (2.14) | 4.61 ± 0.87 (4.17) | 2.03 ± 0.61 (1.76) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.883 | 5.5 | 5.31 | 2.54 |
| p | normal | 0.806 | 10.2 | 3.99 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.758 | 0.13 | 2.21 ± 0.87 (2.15) | 3.48 | 1.32 |
| p | medium | 16 | 0.853 | 0.75 | 1.09 ± 0.31 (1.18) | 3.53 | 1.37 |
| p | strong | 126 | 0.883 | 0.71 | - | 5.34 | 2.56 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector back (0.838).
