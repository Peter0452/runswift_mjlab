# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_01-26-16_t6_n7_control_s7/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.787** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 1.72 ± 0.88 (1.54) |
| Direction error [°] | 17.91 ± 37.08 (5.38) |
| Avg ball speed [m/s] | 2.20 ± 0.72 (2.40) |
| Peak ball speed [m/s] | 4.75 ± 1.62 (5.30) |
| Distance [m] | 2.10 ± 0.93 (2.20) |
| Path length [m] | 2.11 ± 0.94 (2.22) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.788 | 47/50 | 0 | 42 | 1.18 ± 0.28 (1.24) | 9.62 ± 17.40 (5.21) | 2.21 ± 0.68 (2.42) | 4.82 ± 1.57 (5.50) | 2.11 ± 0.90 (2.24) |
| left | p | 0.803 | 49/50 | 0 | 42 | 1.58 ± 0.42 (1.56) | 16.67 ± 33.68 (5.24) | 2.13 ± 0.68 (2.30) | 4.62 ± 1.57 (4.70) | 2.01 ± 0.90 (2.01) |
| back | p | 0.752 | 49/50 | 0 | 41 | 2.48 ± 1.33 (2.32) | 30.11 ± 54.97 (6.94) | 2.28 ± 0.80 (2.53) | 4.86 ± 1.80 (5.63) | 2.24 ± 1.03 (2.58) |
| right | p | 0.804 | 50/50 | 0 | 43 | 1.61 ± 0.41 (1.55) | 14.94 ± 27.99 (5.83) | 2.19 ± 0.69 (2.31) | 4.70 ± 1.53 (4.84) | 2.07 ± 0.88 (2.07) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.791 | 98/100 | 0 | 85 | 1.77 ± 1.08 (1.54) | 16.43 ± 33.24 (5.46) | 2.20 ± 0.67 (2.39) | 4.80 ± 1.56 (5.36) | 2.12 ± 0.91 (2.24) |
| right | p | 0.782 | 97/100 | 0 | 83 | 1.66 ± 0.61 (1.58) | 19.39 ± 40.54 (5.29) | 2.21 ± 0.76 (2.41) | 4.70 ± 1.68 (4.76) | 2.09 ± 0.96 (2.16) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.805 | 24/25 | 0 | 21 | 1.15 ± 0.26 (1.18) | 10.92 ± 21.39 (5.25) | 2.19 ± 0.71 (2.42) | 4.76 ± 1.66 (5.09) | 2.08 ± 0.96 (2.13) |
| forward/right | p | 0.771 | 23/25 | 0 | 21 | 1.21 ± 0.30 (1.26) | 8.27 ± 11.73 (4.42) | 2.24 ± 0.64 (2.42) | 4.88 ± 1.48 (5.61) | 2.13 ± 0.85 (2.54) |
| left/left | p | 0.827 | 24/25 | 0 | 23 | 1.58 ± 0.35 (1.55) | 6.31 ± 4.53 (5.98) | 2.35 ± 0.44 (2.36) | 5.17 ± 1.11 (5.39) | 2.33 ± 0.74 (2.34) |
| left/right | p | 0.780 | 25/25 | 0 | 19 | 1.58 ± 0.47 (1.64) | 26.62 ± 44.73 (5.16) | 1.93 ± 0.79 (2.30) | 4.09 ± 1.75 (4.45) | 1.69 ± 0.92 (1.85) |
| back/left | p | 0.760 | 25/25 | 0 | 21 | 2.61 ± 1.75 (2.32) | 27.60 ± 48.68 (6.27) | 2.29 ± 0.68 (2.50) | 4.92 ± 1.57 (5.62) | 2.21 ± 0.93 (2.56) |
| back/right | p | 0.743 | 24/25 | 0 | 20 | 2.34 ± 0.63 (2.31) | 32.73 ± 60.73 (7.32) | 2.27 ± 0.91 (2.58) | 4.80 ± 2.02 (5.67) | 2.26 ± 1.11 (2.59) |
| right/left | p | 0.773 | 25/25 | 0 | 20 | 1.72 ± 0.47 (1.72) | 20.29 ± 35.13 (6.34) | 1.99 ± 0.74 (2.23) | 4.36 ± 1.73 (4.46) | 1.85 ± 0.91 (1.91) |
| right/right | p | 0.834 | 25/25 | 0 | 23 | 1.50 ± 0.31 (1.48) | 9.59 ± 16.61 (5.26) | 2.39 ± 0.55 (2.41) | 5.04 ± 1.22 (5.46) | 2.29 ± 0.80 (2.42) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.819 | 18.5 | 5.18 | 2.38 |
| p | normal | 0.754 | 17.3 | 4.32 | 1.83 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.701 | 0.10 | 2.51 ± 1.08 (2.40) | 3.89 | 1.56 |
| p | medium | 20 | 0.857 | 0.63 | 1.33 ± 0.24 (1.39) | 4.26 | 1.76 |
| p | strong | 126 | 0.812 | 0.69 | - | 5.21 | 2.40 |

## Notes

- p: score 0.787, 195/200 kicked, 0 fell; worst sector back (0.752).
