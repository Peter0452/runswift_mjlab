# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_21950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.798** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 1.93 ± 1.39 (1.62) |
| Direction error [°] | 14.84 ± 27.67 (6.48) |
| Avg ball speed [m/s] | 2.38 ± 0.80 (2.61) |
| Peak ball speed [m/s] | 5.01 ± 1.80 (5.88) |
| Distance [m] | 2.44 ± 1.15 (2.91) |
| Path length [m] | 2.45 ± 1.15 (2.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.821 | 50/50 | 0 | 44 | 1.47 ± 1.38 (1.29) | 10.16 ± 15.94 (4.41) | 2.30 ± 0.81 (2.46) | 4.90 ± 1.83 (5.59) | 2.33 ± 1.11 (2.48) |
| left | p | 0.825 | 50/50 | 0 | 44 | 1.87 ± 1.49 (1.62) | 12.51 ± 23.05 (5.52) | 2.41 ± 0.73 (2.50) | 5.08 ± 1.63 (5.71) | 2.46 ± 1.07 (2.83) |
| back | p | 0.746 | 49/50 | 0 | 38 | 2.52 ± 1.10 (2.42) | 24.55 ± 43.37 (8.15) | 2.39 ± 0.92 (2.73) | 5.04 ± 2.05 (6.03) | 2.55 ± 1.28 (3.18) |
| right | p | 0.799 | 50/50 | 0 | 41 | 1.86 ± 1.34 (1.74) | 12.34 ± 17.06 (6.63) | 2.42 ± 0.73 (2.45) | 5.03 ± 1.66 (5.09) | 2.45 ± 1.11 (2.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 100/100 | 0 | 82 | 1.92 ± 1.48 (1.59) | 15.59 ± 28.51 (6.04) | 2.37 ± 0.83 (2.67) | 5.02 ± 1.86 (5.92) | 2.45 ± 1.17 (2.94) |
| right | p | 0.798 | 99/100 | 0 | 85 | 1.94 ± 1.29 (1.78) | 14.09 ± 26.76 (6.78) | 2.38 ± 0.78 (2.43) | 5.01 ± 1.73 (5.66) | 2.43 ± 1.12 (2.72) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 22 | 1.24 ± 0.31 (1.26) | 9.18 ± 15.59 (4.09) | 2.26 ± 0.82 (2.50) | 4.87 ± 1.85 (5.71) | 2.30 ± 1.09 (2.66) |
| forward/right | p | 0.808 | 25/25 | 0 | 22 | 1.70 ± 1.89 (1.32) | 11.14 ± 16.24 (5.64) | 2.33 ± 0.81 (2.41) | 4.94 ± 1.81 (5.46) | 2.35 ± 1.13 (2.30) |
| left/left | p | 0.833 | 25/25 | 0 | 23 | 2.02 ± 2.05 (1.58) | 8.01 ± 8.30 (5.32) | 2.50 ± 0.71 (2.71) | 5.29 ± 1.62 (6.00) | 2.62 ± 1.04 (3.06) |
| left/right | p | 0.817 | 25/25 | 0 | 21 | 1.72 ± 0.48 (1.80) | 17.01 ± 30.88 (6.05) | 2.31 ± 0.73 (2.34) | 4.87 ± 1.61 (4.53) | 2.30 ± 1.07 (1.98) |
| back/left | p | 0.763 | 25/25 | 0 | 18 | 2.29 ± 0.68 (2.42) | 28.54 ± 46.74 (8.15) | 2.40 ± 0.88 (2.73) | 5.07 ± 1.97 (6.02) | 2.55 ± 1.27 (3.18) |
| back/right | p | 0.729 | 24/25 | 0 | 20 | 2.77 ± 1.37 (2.50) | 20.39 ± 39.12 (7.93) | 2.38 ± 0.96 (2.78) | 5.01 ± 2.13 (6.09) | 2.54 ± 1.30 (3.14) |
| right/left | p | 0.764 | 25/25 | 0 | 19 | 2.14 ± 1.83 (1.86) | 16.61 ± 22.09 (6.55) | 2.32 ± 0.88 (2.36) | 4.84 ± 1.95 (4.50) | 2.34 ± 1.23 (1.90) |
| right/right | p | 0.835 | 25/25 | 0 | 22 | 1.59 ± 0.33 (1.54) | 8.07 ± 7.61 (6.72) | 2.51 ± 0.53 (2.54) | 5.22 ± 1.28 (5.69) | 2.55 ± 0.96 (2.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.828 | 13.8 | 5.69 | 2.95 |
| p | normal | 0.768 | 15.8 | 4.34 | 1.94 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.715 | 0.10 | 2.54 ± 1.05 (2.41) | 3.91 | 1.59 |
| p | medium | 20 | 0.863 | 0.69 | 1.29 ± 0.17 (1.30) | 4.15 | 1.72 |
| p | strong | 126 | 0.823 | 0.75 | - | 5.63 | 2.93 |

## Notes

- p: score 0.798, 199/200 kicked, 0 fell; worst sector back (0.746).
