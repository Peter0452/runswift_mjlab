# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_22950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.768** |
| Kicked / fell | 196 / 1 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.19 ± 1.89 (1.74) |
| Direction error [°] | 18.00 ± 36.50 (4.93) |
| Avg ball speed [m/s] | 2.05 ± 0.69 (2.27) |
| Peak ball speed [m/s] | 4.47 ± 1.62 (5.03) |
| Distance [m] | 1.83 ± 0.86 (1.96) |
| Path length [m] | 1.84 ± 0.86 (1.97) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.797 | 50/50 | 0 | 43 | 1.82 ± 2.03 (1.33) | 8.07 ± 11.48 (4.37) | 1.95 ± 0.75 (2.17) | 4.23 ± 1.74 (4.39) | 1.68 ± 0.89 (1.70) |
| left | p | 0.785 | 49/50 | 1 | 39 | 1.98 ± 1.70 (1.74) | 21.56 ± 36.39 (5.14) | 2.00 ± 0.71 (2.22) | 4.46 ± 1.73 (5.11) | 1.82 ± 0.90 (2.06) |
| back | p | 0.710 | 48/50 | 0 | 39 | 2.90 ± 1.75 (2.59) | 27.35 ± 53.20 (5.46) | 2.15 ± 0.69 (2.30) | 4.64 ± 1.54 (5.22) | 1.96 ± 0.83 (2.19) |
| right | p | 0.779 | 49/50 | 0 | 42 | 2.08 ± 1.87 (1.72) | 15.42 ± 29.88 (4.55) | 2.09 ± 0.59 (2.27) | 4.57 ± 1.42 (5.11) | 1.87 ± 0.77 (1.92) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 98/100 | 0 | 84 | 1.84 ± 0.94 (1.72) | 16.12 ± 35.18 (4.91) | 2.13 ± 0.61 (2.31) | 4.66 ± 1.45 (5.14) | 1.92 ± 0.80 (2.05) |
| right | p | 0.739 | 98/100 | 1 | 79 | 2.54 ± 2.46 (1.76) | 19.88 ± 37.69 (5.04) | 1.96 ± 0.76 (2.19) | 4.29 ± 1.75 (4.78) | 1.75 ± 0.90 (1.87) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 23 | 1.55 ± 1.39 (1.30) | 5.76 ± 9.50 (2.82) | 2.08 ± 0.63 (2.30) | 4.55 ± 1.51 (4.41) | 1.82 ± 0.80 (1.80) |
| forward/right | p | 0.760 | 25/25 | 0 | 20 | 2.09 ± 2.49 (1.38) | 10.37 ± 12.76 (6.64) | 1.82 ± 0.82 (2.08) | 3.92 ± 1.89 (4.23) | 1.54 ± 0.96 (1.64) |
| left/left | p | 0.840 | 25/25 | 0 | 21 | 1.57 ± 0.43 (1.70) | 15.21 ± 25.56 (5.28) | 2.08 ± 0.60 (2.22) | 4.68 ± 1.49 (5.05) | 1.92 ± 0.80 (2.06) |
| left/right | p | 0.730 | 24/25 | 1 | 18 | 2.40 ± 2.32 (1.86) | 28.17 ± 44.01 (4.90) | 1.91 ± 0.81 (2.21) | 4.23 ± 1.93 (5.17) | 1.73 ± 0.99 (2.00) |
| back/left | p | 0.740 | 24/25 | 0 | 20 | 2.44 ± 0.73 (2.55) | 25.15 ± 51.83 (5.46) | 2.24 ± 0.51 (2.35) | 4.85 ± 1.20 (5.39) | 2.04 ± 0.73 (2.22) |
| back/right | p | 0.681 | 24/25 | 0 | 19 | 3.35 ± 2.28 (2.64) | 29.54 ± 54.45 (5.70) | 2.05 ± 0.82 (2.19) | 4.44 ± 1.80 (5.15) | 1.88 ± 0.90 (2.10) |
| right/left | p | 0.771 | 24/25 | 0 | 20 | 1.83 ± 0.55 (1.74) | 18.83 ± 37.28 (4.04) | 2.12 ± 0.67 (2.33) | 4.57 ± 1.57 (4.96) | 1.90 ± 0.85 (1.97) |
| right/right | p | 0.787 | 25/25 | 0 | 22 | 2.32 ± 2.54 (1.72) | 12.15 ± 19.85 (4.93) | 2.07 ± 0.51 (2.26) | 4.58 ± 1.26 (5.11) | 1.85 ± 0.67 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.787 | 15.9 | 5.15 | 2.22 |
| p | normal | 0.748 | 20.0 | 3.82 | 1.46 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.705 | 0.16 | 2.26 ± 1.06 (2.21) | 3.56 | 1.34 |
| p | medium | 16 | 0.807 | 0.68 | 1.19 ± 0.33 (1.25) | 3.84 | 1.49 |
| p | strong | 126 | 0.792 | 0.67 | - | 4.99 | 2.11 |

## Notes

- p: score 0.768, 196/200 kicked, 1 fell; worst sector back (0.710).
