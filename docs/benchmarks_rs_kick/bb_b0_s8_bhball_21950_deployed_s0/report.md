# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_21950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 2.10 ± 1.95 (1.71) |
| Direction error [°] | 18.38 ± 37.44 (6.07) |
| Avg ball speed [m/s] | 2.14 ± 0.63 (2.30) |
| Peak ball speed [m/s] | 4.59 ± 1.45 (5.11) |
| Distance [m] | 1.93 ± 0.83 (2.07) |
| Path length [m] | 1.94 ± 0.84 (2.07) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.792 | 50/50 | 0 | 44 | 2.02 ± 2.60 (1.33) | 8.14 ± 10.18 (4.84) | 2.11 ± 0.55 (2.14) | 4.53 ± 1.32 (4.33) | 1.84 ± 0.79 (1.79) |
| left | p | 0.810 | 50/50 | 0 | 43 | 1.85 ± 1.51 (1.72) | 20.02 ± 37.00 (6.55) | 2.10 ± 0.67 (2.29) | 4.56 ± 1.57 (5.24) | 1.91 ± 0.84 (2.08) |
| back | p | 0.732 | 48/50 | 0 | 41 | 2.52 ± 1.49 (2.39) | 28.70 ± 54.82 (6.56) | 2.19 ± 0.68 (2.38) | 4.67 ± 1.54 (5.52) | 2.05 ± 0.89 (2.20) |
| right | p | 0.799 | 50/50 | 0 | 43 | 2.03 ± 1.90 (1.71) | 17.05 ± 31.31 (6.31) | 2.16 ± 0.59 (2.30) | 4.61 ± 1.37 (5.12) | 1.93 ± 0.80 (2.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 100/100 | 0 | 88 | 1.90 ± 1.42 (1.69) | 17.84 ± 37.50 (6.00) | 2.18 ± 0.57 (2.33) | 4.68 ± 1.33 (5.19) | 1.98 ± 0.79 (2.10) |
| right | p | 0.759 | 98/100 | 0 | 83 | 2.30 ± 2.35 (1.73) | 18.92 ± 37.36 (6.07) | 2.09 ± 0.67 (2.26) | 4.50 ± 1.56 (5.08) | 1.88 ± 0.87 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.830 | 25/25 | 0 | 23 | 1.59 ± 1.70 (1.28) | 6.67 ± 9.13 (4.16) | 2.21 ± 0.50 (2.34) | 4.75 ± 1.20 (5.11) | 1.97 ± 0.72 (2.11) |
| forward/right | p | 0.753 | 25/25 | 0 | 21 | 2.44 ± 3.20 (1.36) | 9.62 ± 10.93 (6.03) | 2.02 ± 0.59 (2.08) | 4.30 ± 1.39 (4.20) | 1.70 ± 0.83 (1.72) |
| left/left | p | 0.848 | 25/25 | 0 | 23 | 1.55 ± 0.41 (1.58) | 11.85 ± 21.34 (6.44) | 2.22 ± 0.51 (2.24) | 4.80 ± 1.23 (5.24) | 2.03 ± 0.71 (2.10) |
| left/right | p | 0.772 | 25/25 | 0 | 20 | 2.16 ± 2.05 (1.82) | 28.20 ± 46.36 (6.66) | 1.98 ± 0.78 (2.31) | 4.32 ± 1.82 (5.24) | 1.78 ± 0.93 (2.07) |
| back/left | p | 0.753 | 25/25 | 0 | 21 | 2.73 ± 1.96 (2.40) | 31.02 ± 57.02 (7.14) | 2.23 ± 0.64 (2.49) | 4.72 ± 1.45 (5.54) | 2.08 ± 0.90 (2.39) |
| back/right | p | 0.712 | 23/25 | 0 | 20 | 2.31 ± 0.59 (2.38) | 26.17 ± 52.21 (6.37) | 2.14 ± 0.73 (2.38) | 4.61 ± 1.64 (5.50) | 2.01 ± 0.87 (2.07) |
| right/left | p | 0.798 | 25/25 | 0 | 21 | 1.74 ± 0.47 (1.74) | 21.83 ± 38.55 (8.26) | 2.08 ± 0.61 (2.19) | 4.47 ± 1.42 (4.90) | 1.84 ± 0.80 (1.88) |
| right/right | p | 0.799 | 25/25 | 0 | 22 | 2.32 ± 2.61 (1.66) | 12.27 ± 20.72 (5.80) | 2.23 ± 0.55 (2.36) | 4.76 ± 1.31 (5.35) | 2.02 ± 0.78 (2.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.809 | 16.1 | 5.26 | 2.31 |
| p | normal | 0.757 | 20.6 | 3.94 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.16 | 2.34 ± 0.95 (2.25) | 3.67 | 1.38 |
| p | medium | 16 | 0.828 | 0.66 | 1.19 ± 0.35 (1.25) | 3.85 | 1.54 |
| p | strong | 126 | 0.808 | 0.68 | - | 5.12 | 2.24 |

## Notes

- p: score 0.783, 198/200 kicked, 0 fell; worst sector back (0.732).
