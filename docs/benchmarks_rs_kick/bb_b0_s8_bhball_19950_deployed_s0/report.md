# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.776** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.09 ± 1.79 (1.74) |
| Direction error [°] | 18.83 ± 37.62 (5.49) |
| Avg ball speed [m/s] | 2.04 ± 0.66 (2.26) |
| Peak ball speed [m/s] | 4.44 ± 1.55 (5.00) |
| Distance [m] | 1.75 ± 0.81 (1.89) |
| Path length [m] | 1.76 ± 0.81 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.802 | 50/50 | 0 | 43 | 1.85 ± 2.26 (1.31) | 7.94 ± 9.81 (5.07) | 1.99 ± 0.66 (2.14) | 4.30 ± 1.56 (4.24) | 1.65 ± 0.83 (1.61) |
| left | p | 0.789 | 49/50 | 0 | 39 | 1.84 ± 1.47 (1.74) | 20.81 ± 35.25 (6.24) | 1.99 ± 0.72 (2.24) | 4.43 ± 1.72 (5.13) | 1.74 ± 0.85 (1.91) |
| back | p | 0.722 | 49/50 | 0 | 41 | 2.80 ± 1.56 (2.62) | 29.91 ± 54.97 (6.94) | 2.12 ± 0.69 (2.33) | 4.56 ± 1.57 (5.20) | 1.86 ± 0.80 (1.94) |
| right | p | 0.793 | 49/50 | 0 | 40 | 1.88 ± 1.52 (1.72) | 16.91 ± 32.83 (4.41) | 2.07 ± 0.56 (2.27) | 4.49 ± 1.33 (4.96) | 1.75 ± 0.73 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.801 | 99/100 | 0 | 85 | 1.84 ± 1.04 (1.70) | 17.74 ± 38.41 (4.78) | 2.08 ± 0.62 (2.26) | 4.53 ± 1.44 (5.00) | 1.78 ± 0.75 (1.91) |
| right | p | 0.751 | 98/100 | 0 | 78 | 2.34 ± 2.28 (1.75) | 19.95 ± 36.78 (6.10) | 2.01 ± 0.70 (2.25) | 4.36 ± 1.65 (4.72) | 1.72 ± 0.86 (1.85) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.824 | 25/25 | 0 | 23 | 1.63 ± 1.73 (1.28) | 6.47 ± 9.14 (4.29) | 2.07 ± 0.58 (2.20) | 4.55 ± 1.41 (4.35) | 1.77 ± 0.76 (1.81) |
| forward/right | p | 0.779 | 25/25 | 0 | 20 | 2.06 ± 2.68 (1.34) | 9.41 ± 10.23 (5.87) | 1.90 ± 0.72 (1.93) | 4.05 ± 1.67 (4.05) | 1.53 ± 0.89 (1.51) |
| left/left | p | 0.843 | 25/25 | 0 | 22 | 1.57 ± 0.42 (1.68) | 12.20 ± 20.55 (6.03) | 2.08 ± 0.65 (2.27) | 4.61 ± 1.52 (5.23) | 1.85 ± 0.75 (2.07) |
| left/right | p | 0.735 | 24/25 | 0 | 17 | 2.12 ± 2.02 (1.85) | 29.77 ± 44.03 (6.36) | 1.90 ± 0.78 (2.20) | 4.24 ± 1.88 (4.83) | 1.63 ± 0.93 (1.74) |
| back/left | p | 0.726 | 24/25 | 0 | 20 | 2.40 ± 0.68 (2.60) | 31.66 ± 58.98 (6.26) | 2.14 ± 0.63 (2.32) | 4.59 ± 1.40 (5.00) | 1.85 ± 0.73 (1.88) |
| back/right | p | 0.717 | 25/25 | 0 | 21 | 3.17 ± 2.01 (2.68) | 28.22 ± 50.76 (7.23) | 2.09 ± 0.74 (2.33) | 4.54 ± 1.71 (5.27) | 1.86 ± 0.87 (1.96) |
| right/left | p | 0.813 | 25/25 | 0 | 20 | 1.76 ± 0.47 (1.88) | 21.17 ± 40.52 (4.02) | 2.00 ± 0.60 (2.19) | 4.36 ± 1.42 (4.77) | 1.67 ± 0.74 (1.79) |
| right/right | p | 0.772 | 24/25 | 0 | 20 | 2.00 ± 2.12 (1.62) | 12.47 ± 21.26 (5.03) | 2.13 ± 0.51 (2.32) | 4.63 ± 1.21 (5.26) | 1.84 ± 0.70 (1.95) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 14.6 | 5.16 | 2.12 |
| p | normal | 0.748 | 22.9 | 3.75 | 1.39 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.709 | 0.18 | 2.14 ± 1.03 (2.06) | 3.36 | 1.17 |
| p | medium | 16 | 0.818 | 0.67 | 1.20 ± 0.36 (1.24) | 3.88 | 1.51 |
| p | strong | 126 | 0.802 | 0.67 | - | 5.03 | 2.05 |

## Notes

- p: score 0.776, 197/200 kicked, 0 fell; worst sector back (0.722).
