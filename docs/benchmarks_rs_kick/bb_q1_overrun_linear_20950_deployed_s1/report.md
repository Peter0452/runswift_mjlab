# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.795** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 176 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.97 ± 1.42 (1.67) |
| Direction error [°] | 12.65 ± 26.61 (5.73) |
| Avg ball speed [m/s] | 2.06 ± 0.59 (2.11) |
| Peak ball speed [m/s] | 4.88 ± 1.47 (5.32) |
| Distance [m] | 2.18 ± 0.87 (2.30) |
| Path length [m] | 2.19 ± 0.87 (2.31) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.790 | 48/50 | 0 | 44 | 1.65 ± 1.77 (1.35) | 6.72 ± 6.73 (4.60) | 1.96 ± 0.60 (2.08) | 4.75 ± 1.53 (5.14) | 2.04 ± 0.81 (2.05) |
| left | p | 0.835 | 50/50 | 0 | 45 | 1.89 ± 1.45 (1.65) | 11.79 ± 24.33 (4.42) | 2.06 ± 0.54 (2.08) | 4.83 ± 1.33 (5.23) | 2.14 ± 0.78 (2.28) |
| back | p | 0.754 | 49/50 | 0 | 43 | 2.62 ± 1.47 (2.44) | 22.17 ± 42.99 (6.39) | 2.15 ± 0.72 (2.30) | 5.04 ± 1.71 (5.84) | 2.38 ± 1.05 (2.70) |
| right | p | 0.800 | 49/50 | 0 | 44 | 1.73 ± 0.39 (1.80) | 9.82 ± 14.23 (6.61) | 2.08 ± 0.48 (2.06) | 4.90 ± 1.26 (5.05) | 2.16 ± 0.77 (2.21) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 98/100 | 0 | 87 | 1.89 ± 1.15 (1.63) | 13.09 ± 26.98 (5.54) | 2.06 ± 0.64 (2.16) | 4.88 ± 1.55 (5.33) | 2.20 ± 0.91 (2.34) |
| right | p | 0.794 | 98/100 | 0 | 89 | 2.06 ± 1.65 (1.74) | 12.21 ± 26.24 (5.92) | 2.07 ± 0.55 (2.09) | 4.88 ± 1.38 (5.26) | 2.17 ± 0.83 (2.11) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.804 | 24/25 | 0 | 22 | 1.27 ± 0.27 (1.34) | 7.06 ± 7.47 (4.73) | 1.97 ± 0.59 (2.09) | 4.82 ± 1.52 (5.41) | 2.07 ± 0.83 (2.22) |
| forward/right | p | 0.776 | 24/25 | 0 | 22 | 2.02 ± 2.43 (1.37) | 6.38 ± 5.87 (4.60) | 1.95 ± 0.61 (2.08) | 4.67 ± 1.54 (4.98) | 2.00 ± 0.79 (2.03) |
| left/left | p | 0.838 | 25/25 | 0 | 23 | 2.05 ± 1.98 (1.62) | 8.88 ± 18.37 (3.26) | 2.13 ± 0.53 (2.16) | 4.93 ± 1.32 (5.32) | 2.20 ± 0.75 (2.33) |
| left/right | p | 0.832 | 25/25 | 0 | 22 | 1.72 ± 0.48 (1.76) | 14.70 ± 28.80 (4.50) | 1.99 ± 0.54 (2.07) | 4.73 ± 1.33 (4.61) | 2.08 ± 0.81 (2.03) |
| back/left | p | 0.768 | 25/25 | 0 | 21 | 2.35 ± 0.66 (2.44) | 24.63 ± 44.24 (5.64) | 2.09 ± 0.81 (2.37) | 4.92 ± 1.90 (5.84) | 2.35 ± 1.15 (2.66) |
| back/right | p | 0.739 | 24/25 | 0 | 22 | 2.90 ± 1.95 (2.50) | 19.60 ± 41.48 (7.55) | 2.21 ± 0.60 (2.25) | 5.16 ± 1.47 (5.89) | 2.42 ± 0.93 (2.73) |
| right/left | p | 0.771 | 24/25 | 0 | 21 | 1.84 ± 0.41 (1.95) | 11.48 ± 18.13 (5.61) | 2.04 ± 0.56 (2.07) | 4.86 ± 1.40 (5.03) | 2.15 ± 0.82 (2.25) |
| right/right | p | 0.829 | 25/25 | 0 | 23 | 1.62 ± 0.34 (1.54) | 8.22 ± 8.73 (7.74) | 2.12 ± 0.39 (2.06) | 4.94 ± 1.11 (5.21) | 2.17 ± 0.70 (2.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.822 | 13.2 | 5.32 | 2.46 |
| p | normal | 0.767 | 12.0 | 4.43 | 1.89 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.707 | 0.09 | 2.60 ± 0.91 (2.45) | 4.00 | 1.60 |
| p | medium | 20 | 0.874 | 0.68 | 1.31 ± 0.17 (1.28) | 4.19 | 1.70 |
| p | strong | 126 | 0.819 | 0.71 | - | 5.36 | 2.50 |

## Notes

- p: score 0.795, 196/200 kicked, 0 fell; worst sector back (0.754).
