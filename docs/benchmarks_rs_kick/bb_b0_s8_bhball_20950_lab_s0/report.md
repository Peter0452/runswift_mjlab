# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.839** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.57 ± 0.52 (1.49) |
| Direction error [°] | 5.83 ± 3.65 (5.46) |
| Avg ball speed [m/s] | 1.88 ± 0.35 (1.94) |
| Peak ball speed [m/s] | 4.03 ± 0.81 (4.06) |
| Distance [m] | 1.44 ± 0.47 (1.45) |
| Path length [m] | 1.45 ± 0.47 (1.46) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.838 | 50/50 | 0 | 49 | 1.04 ± 0.22 (1.07) | 5.18 ± 3.66 (3.91) | 1.60 ± 0.36 (1.55) | 3.39 ± 0.79 (3.15) | 1.07 ± 0.44 (0.95) |
| left | p | 0.855 | 50/50 | 0 | 49 | 1.51 ± 0.32 (1.53) | 5.70 ± 3.88 (4.97) | 1.92 ± 0.31 (1.98) | 4.19 ± 0.73 (4.38) | 1.52 ± 0.44 (1.54) |
| back | p | 0.827 | 50/50 | 0 | 50 | 2.25 ± 0.28 (2.19) | 6.40 ± 2.93 (6.38) | 2.08 ± 0.24 (2.12) | 4.44 ± 0.61 (4.63) | 1.71 ± 0.36 (1.79) |
| right | p | 0.836 | 50/50 | 0 | 49 | 1.50 ± 0.33 (1.48) | 6.04 ± 3.93 (5.62) | 1.92 ± 0.28 (1.95) | 4.10 ± 0.71 (4.26) | 1.47 ± 0.39 (1.44) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.837 | 100/100 | 0 | 99 | 1.58 ± 0.53 (1.52) | 5.95 ± 3.50 (5.74) | 1.87 ± 0.33 (1.92) | 4.03 ± 0.77 (4.16) | 1.44 ± 0.46 (1.45) |
| right | p | 0.841 | 100/100 | 0 | 98 | 1.57 ± 0.52 (1.48) | 5.71 ± 3.79 (5.31) | 1.89 ± 0.37 (1.94) | 4.03 ± 0.85 (4.05) | 1.44 ± 0.48 (1.45) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.835 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 5.37 ± 3.45 (4.03) | 1.65 ± 0.29 (1.56) | 3.49 ± 0.64 (3.16) | 1.12 ± 0.38 (0.95) |
| forward/right | p | 0.841 | 25/25 | 0 | 24 | 1.03 ± 0.22 (1.08) | 4.99 ± 3.84 (3.74) | 1.55 ± 0.42 (1.50) | 3.29 ± 0.90 (3.11) | 1.02 ± 0.48 (0.94) |
| left/left | p | 0.843 | 25/25 | 0 | 24 | 1.42 ± 0.32 (1.44) | 6.37 ± 4.56 (5.70) | 1.84 ± 0.36 (1.88) | 4.00 ± 0.79 (4.14) | 1.41 ± 0.47 (1.45) |
| left/right | p | 0.867 | 25/25 | 0 | 25 | 1.60 ± 0.30 (1.60) | 5.03 ± 2.91 (4.90) | 2.01 ± 0.24 (2.06) | 4.38 ± 0.61 (4.66) | 1.62 ± 0.37 (1.66) |
| back/left | p | 0.822 | 25/25 | 0 | 25 | 2.27 ± 0.29 (2.16) | 6.71 ± 2.66 (6.58) | 2.05 ± 0.22 (2.10) | 4.39 ± 0.58 (4.56) | 1.69 ± 0.35 (1.84) |
| back/right | p | 0.831 | 25/25 | 0 | 25 | 2.23 ± 0.28 (2.22) | 6.10 ± 3.15 (6.36) | 2.11 ± 0.25 (2.17) | 4.49 ± 0.64 (4.68) | 1.74 ± 0.36 (1.78) |
| right/left | p | 0.848 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.58) | 5.35 ± 2.78 (5.50) | 1.96 ± 0.29 (2.02) | 4.26 ± 0.75 (4.54) | 1.54 ± 0.42 (1.55) |
| right/right | p | 0.824 | 25/25 | 0 | 24 | 1.42 ± 0.33 (1.48) | 6.73 ± 4.71 (5.75) | 1.88 ± 0.27 (1.89) | 3.94 ± 0.63 (3.85) | 1.40 ± 0.35 (1.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.855 | 5.9 | 4.41 | 1.64 |
| p | normal | 0.823 | 5.8 | 3.65 | 1.25 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.786 | 0.23 | 2.09 ± 0.69 (1.93) | 3.31 | 1.06 |
| p | medium | 16 | 0.875 | 0.82 | 0.99 ± 0.22 (1.02) | 3.21 | 1.03 |
| p | strong | 126 | 0.858 | 0.60 | - | 4.47 | 1.67 |

## Notes

- p: score 0.839, 200/200 kicked, 0 fell; worst sector back (0.827).
