# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_21450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.805** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.92 ± 1.36 (1.72) |
| Direction error [°] | 17.75 ± 34.79 (6.63) |
| Avg ball speed [m/s] | 2.39 ± 0.79 (2.60) |
| Peak ball speed [m/s] | 5.01 ± 1.74 (5.82) |
| Distance [m] | 2.45 ± 1.14 (2.87) |
| Path length [m] | 2.46 ± 1.14 (2.89) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.802 | 50/50 | 0 | 41 | 1.64 ± 1.75 (1.32) | 10.20 ± 14.16 (5.43) | 2.27 ± 0.85 (2.23) | 4.72 ± 1.83 (4.44) | 2.24 ± 1.17 (1.93) |
| left | p | 0.841 | 50/50 | 0 | 45 | 1.86 ± 1.38 (1.77) | 14.43 ± 29.00 (5.61) | 2.47 ± 0.66 (2.70) | 5.22 ± 1.52 (5.88) | 2.56 ± 1.01 (2.94) |
| back | p | 0.766 | 50/50 | 0 | 40 | 2.36 ± 0.64 (2.43) | 28.00 ± 50.41 (8.23) | 2.47 ± 0.84 (2.76) | 5.13 ± 1.83 (6.07) | 2.58 ± 1.22 (3.18) |
| right | p | 0.809 | 50/50 | 0 | 43 | 1.83 ± 1.30 (1.72) | 18.37 ± 32.95 (6.66) | 2.37 ± 0.79 (2.58) | 4.98 ± 1.71 (5.81) | 2.42 ± 1.12 (2.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.824 | 100/100 | 0 | 87 | 1.75 ± 0.61 (1.70) | 15.84 ± 34.01 (5.89) | 2.47 ± 0.68 (2.63) | 5.18 ± 1.53 (5.89) | 2.54 ± 1.06 (2.97) |
| right | p | 0.785 | 100/100 | 0 | 82 | 2.09 ± 1.80 (1.74) | 19.66 ± 35.45 (7.40) | 2.32 ± 0.88 (2.58) | 4.85 ± 1.91 (5.69) | 2.36 ± 1.21 (2.66) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.845 | 25/25 | 0 | 22 | 1.30 ± 0.29 (1.28) | 7.95 ± 13.28 (2.96) | 2.36 ± 0.78 (2.32) | 4.90 ± 1.73 (4.44) | 2.34 ± 1.13 (1.89) |
| forward/right | p | 0.758 | 25/25 | 0 | 19 | 1.97 ± 2.41 (1.32) | 12.46 ± 14.65 (7.30) | 2.19 ± 0.90 (2.21) | 4.54 ± 1.92 (4.44) | 2.15 ± 1.20 (1.93) |
| left/left | p | 0.867 | 25/25 | 0 | 24 | 1.59 ± 0.38 (1.68) | 9.21 ± 15.23 (6.63) | 2.59 ± 0.53 (2.76) | 5.46 ± 1.26 (5.93) | 2.72 ± 0.86 (2.98) |
| left/right | p | 0.816 | 25/25 | 0 | 21 | 2.12 ± 1.88 (1.92) | 19.65 ± 37.35 (5.30) | 2.34 ± 0.76 (2.64) | 4.98 ± 1.71 (5.86) | 2.39 ± 1.11 (2.77) |
| back/left | p | 0.778 | 25/25 | 0 | 19 | 2.36 ± 0.68 (2.44) | 26.39 ± 50.63 (8.66) | 2.53 ± 0.66 (2.67) | 5.32 ± 1.47 (5.96) | 2.65 ± 1.13 (3.05) |
| back/right | p | 0.754 | 25/25 | 0 | 21 | 2.35 ± 0.60 (2.38) | 29.60 ± 50.14 (8.17) | 2.41 ± 0.98 (2.99) | 4.95 ± 2.12 (6.26) | 2.51 ± 1.30 (3.20) |
| right/left | p | 0.808 | 25/25 | 0 | 22 | 1.74 ± 0.46 (1.74) | 19.82 ± 37.71 (6.06) | 2.41 ± 0.72 (2.55) | 5.05 ± 1.56 (5.82) | 2.44 ± 1.05 (2.87) |
| right/right | p | 0.810 | 25/25 | 0 | 21 | 1.93 ± 1.78 (1.70) | 16.92 ± 27.29 (7.33) | 2.32 ± 0.84 (2.59) | 4.92 ± 1.83 (5.79) | 2.40 ± 1.18 (2.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.851 | 15.7 | 5.83 | 3.04 |
| p | normal | 0.759 | 19.8 | 4.20 | 1.86 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.17 | 2.39 ± 1.05 (2.30) | 3.74 | 1.51 |
| p | medium | 16 | 0.819 | 0.68 | 1.26 ± 0.25 (1.27) | 4.09 | 1.72 |
| p | strong | 126 | 0.843 | 0.76 | - | 5.72 | 2.97 |

## Notes

- p: score 0.805, 200/200 kicked, 0 fell; worst sector back (0.766).
