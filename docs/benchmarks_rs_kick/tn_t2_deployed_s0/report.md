# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t2_control_s7/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.770** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.05 ± 1.78 (1.67) |
| Direction error [°] | 21.53 ± 40.17 (6.89) |
| Avg ball speed [m/s] | 1.95 ± 0.64 (2.11) |
| Peak ball speed [m/s] | 4.26 ± 1.50 (4.77) |
| Distance [m] | 1.63 ± 0.77 (1.74) |
| Path length [m] | 1.64 ± 0.78 (1.75) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.808 | 50/50 | 0 | 44 | 1.74 ± 2.04 (1.29) | 7.43 ± 9.70 (4.25) | 1.95 ± 0.67 (2.02) | 4.21 ± 1.58 (4.06) | 1.61 ± 0.84 (1.54) |
| left | p | 0.788 | 49/50 | 0 | 39 | 1.73 ± 1.00 (1.72) | 22.50 ± 36.51 (7.32) | 1.98 ± 0.60 (2.15) | 4.41 ± 1.49 (5.01) | 1.68 ± 0.77 (1.79) |
| back | p | 0.705 | 50/50 | 0 | 39 | 2.94 ± 2.18 (2.54) | 34.02 ± 56.42 (9.19) | 1.93 ± 0.66 (2.14) | 4.20 ± 1.49 (4.73) | 1.63 ± 0.73 (1.76) |
| right | p | 0.778 | 49/50 | 0 | 40 | 1.78 ± 1.29 (1.70) | 22.20 ± 38.46 (6.32) | 1.93 ± 0.60 (2.11) | 4.22 ± 1.42 (4.92) | 1.59 ± 0.74 (1.75) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 100/100 | 0 | 85 | 1.83 ± 1.15 (1.67) | 19.55 ± 37.28 (6.77) | 1.99 ± 0.55 (2.11) | 4.37 ± 1.32 (4.86) | 1.66 ± 0.71 (1.74) |
| right | p | 0.745 | 98/100 | 0 | 77 | 2.27 ± 2.23 (1.69) | 23.55 ± 42.82 (7.08) | 1.91 ± 0.71 (2.12) | 4.15 ± 1.65 (4.41) | 1.59 ± 0.83 (1.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 24 | 1.45 ± 1.18 (1.24) | 5.90 ± 8.60 (3.96) | 2.04 ± 0.61 (2.12) | 4.42 ± 1.42 (4.29) | 1.68 ± 0.75 (1.73) |
| forward/right | p | 0.782 | 25/25 | 0 | 20 | 2.03 ± 2.59 (1.32) | 8.95 ± 10.46 (5.02) | 1.86 ± 0.72 (1.90) | 4.00 ± 1.70 (4.03) | 1.53 ± 0.91 (1.53) |
| left/left | p | 0.829 | 25/25 | 0 | 21 | 1.53 ± 0.45 (1.62) | 15.96 ± 23.85 (7.86) | 2.08 ± 0.53 (2.16) | 4.62 ± 1.30 (5.08) | 1.82 ± 0.73 (1.88) |
| left/right | p | 0.748 | 24/25 | 0 | 18 | 1.94 ± 1.32 (1.82) | 29.30 ± 45.14 (3.77) | 1.87 ± 0.66 (2.11) | 4.19 ± 1.64 (4.82) | 1.55 ± 0.80 (1.70) |
| back/left | p | 0.719 | 25/25 | 0 | 20 | 2.68 ± 1.58 (2.52) | 30.33 ± 51.17 (10.50) | 1.97 ± 0.47 (2.06) | 4.34 ± 1.11 (4.72) | 1.64 ± 0.60 (1.73) |
| back/right | p | 0.690 | 25/25 | 0 | 19 | 3.19 ± 2.63 (2.62) | 37.71 ± 61.00 (8.74) | 1.89 ± 0.80 (2.21) | 4.06 ± 1.79 (4.87) | 1.62 ± 0.84 (1.82) |
| right/left | p | 0.798 | 25/25 | 0 | 20 | 1.66 ± 0.48 (1.72) | 25.99 ± 44.05 (5.30) | 1.87 ± 0.57 (1.92) | 4.09 ± 1.39 (3.92) | 1.50 ± 0.72 (1.50) |
| right/right | p | 0.759 | 24/25 | 0 | 20 | 1.90 ± 1.76 (1.64) | 18.26 ± 31.11 (7.35) | 2.01 ± 0.63 (2.22) | 4.35 ± 1.43 (5.07) | 1.68 ± 0.75 (1.75) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.791 | 20.0 | 4.86 | 1.93 |
| p | normal | 0.749 | 23.0 | 3.67 | 1.33 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.710 | 0.21 | 2.10 ± 0.96 (2.01) | 3.32 | 1.14 |
| p | medium | 16 | 0.819 | 0.72 | 1.15 ± 0.31 (1.15) | 3.71 | 1.36 |
| p | strong | 126 | 0.791 | 0.64 | - | 4.77 | 1.89 |

## Notes

- p: score 0.770, 198/200 kicked, 0 fell; worst sector back (0.705).
