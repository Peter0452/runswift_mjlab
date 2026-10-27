# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.54 (1.48) |
| Direction error [°] | 6.43 ± 10.61 (5.08) |
| Avg ball speed [m/s] | 1.89 ± 0.39 (1.97) |
| Peak ball speed [m/s] | 4.04 ± 0.86 (4.12) |
| Distance [m] | 1.52 ± 0.52 (1.52) |
| Path length [m] | 1.53 ± 0.52 (1.53) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.846 | 50/50 | 0 | 50 | 1.01 ± 0.24 (1.05) | 4.59 ± 3.19 (3.52) | 1.62 ± 0.39 (1.62) | 3.47 ± 0.83 (3.28) | 1.14 ± 0.50 (1.04) |
| left | p | 0.853 | 50/50 | 0 | 49 | 1.50 ± 0.34 (1.48) | 6.28 ± 3.97 (5.55) | 1.95 ± 0.32 (2.01) | 4.18 ± 0.78 (4.34) | 1.61 ± 0.47 (1.69) |
| back | p | 0.836 | 50/50 | 0 | 49 | 2.26 ± 0.26 (2.20) | 7.94 ± 20.05 (4.90) | 2.12 ± 0.38 (2.20) | 4.47 ± 0.86 (4.79) | 1.84 ± 0.47 (1.96) |
| right | p | 0.824 | 50/50 | 0 | 48 | 1.49 ± 0.35 (1.46) | 6.93 ± 4.06 (6.58) | 1.89 ± 0.28 (1.96) | 4.02 ± 0.65 (4.08) | 1.49 ± 0.38 (1.45) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.838 | 100/100 | 0 | 98 | 1.57 ± 0.55 (1.48) | 5.98 ± 3.66 (5.52) | 1.92 ± 0.34 (1.99) | 4.08 ± 0.79 (4.17) | 1.54 ± 0.49 (1.54) |
| right | p | 0.842 | 100/100 | 0 | 98 | 1.56 ± 0.53 (1.48) | 6.89 ± 14.54 (4.87) | 1.87 ± 0.43 (1.95) | 4.00 ± 0.93 (4.07) | 1.49 ± 0.55 (1.49) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 25 | 1.02 ± 0.24 (1.06) | 5.44 ± 3.34 (4.61) | 1.67 ± 0.33 (1.68) | 3.52 ± 0.72 (3.28) | 1.18 ± 0.45 (1.05) |
| forward/right | p | 0.855 | 25/25 | 0 | 25 | 1.01 ± 0.24 (1.04) | 3.73 ± 2.78 (3.06) | 1.57 ± 0.44 (1.59) | 3.42 ± 0.92 (3.26) | 1.09 ± 0.55 (1.00) |
| left/left | p | 0.842 | 25/25 | 0 | 24 | 1.40 ± 0.34 (1.46) | 6.93 ± 4.35 (6.57) | 1.90 ± 0.34 (2.00) | 4.07 ± 0.82 (4.28) | 1.54 ± 0.49 (1.71) |
| left/right | p | 0.864 | 25/25 | 0 | 25 | 1.61 ± 0.31 (1.60) | 5.63 ± 3.44 (5.14) | 2.01 ± 0.29 (2.07) | 4.30 ± 0.71 (4.47) | 1.67 ± 0.45 (1.67) |
| back/left | p | 0.836 | 25/25 | 0 | 25 | 2.29 ± 0.27 (2.22) | 5.33 ± 2.71 (4.99) | 2.16 ± 0.21 (2.18) | 4.56 ± 0.57 (4.78) | 1.88 ± 0.38 (2.00) |
| back/right | p | 0.837 | 25/25 | 0 | 24 | 2.22 ± 0.25 (2.18) | 10.55 ± 27.99 (4.76) | 2.07 ± 0.49 (2.22) | 4.38 ± 1.07 (4.81) | 1.79 ± 0.54 (1.94) |
| right/left | p | 0.836 | 25/25 | 0 | 24 | 1.58 ± 0.32 (1.58) | 6.23 ± 3.82 (6.08) | 1.94 ± 0.27 (1.99) | 4.17 ± 0.66 (4.22) | 1.57 ± 0.38 (1.56) |
| right/right | p | 0.811 | 25/25 | 0 | 24 | 1.40 ± 0.35 (1.44) | 7.63 ± 4.17 (6.86) | 1.84 ± 0.27 (1.85) | 3.88 ± 0.62 (3.83) | 1.41 ± 0.36 (1.43) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.861 | 5.3 | 4.46 | 1.76 |
| p | normal | 0.819 | 7.6 | 3.61 | 1.28 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.776 | 0.23 | 2.05 ± 0.73 (1.90) | 3.25 | 1.08 |
| p | medium | 16 | 0.898 | 0.87 | 1.03 ± 0.16 (1.04) | 3.35 | 1.10 |
| p | strong | 126 | 0.862 | 0.60 | - | 4.49 | 1.78 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector right (0.824).
