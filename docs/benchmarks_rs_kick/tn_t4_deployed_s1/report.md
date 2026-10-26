# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-06-39_t4_n7_control/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.792** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 31 |
| Time to kick [s] | 1.79 ± 0.97 (1.62) |
| Direction error [°] | 19.98 ± 38.58 (5.93) |
| Avg ball speed [m/s] | 2.26 ± 0.92 (2.51) |
| Peak ball speed [m/s] | 4.71 ± 1.96 (5.22) |
| Distance [m] | 2.28 ± 1.16 (2.36) |
| Path length [m] | 2.29 ± 1.17 (2.36) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.823 | 50/50 | 0 | 42 | 1.29 ± 0.48 (1.29) | 10.18 ± 16.42 (4.52) | 2.23 ± 0.84 (2.42) | 4.65 ± 1.80 (4.83) | 2.17 ± 1.02 (2.29) |
| left | p | 0.799 | 49/50 | 0 | 41 | 1.66 ± 0.45 (1.60) | 16.78 ± 33.70 (6.37) | 2.27 ± 0.88 (2.55) | 4.72 ± 1.89 (5.04) | 2.28 ± 1.14 (2.32) |
| back | p | 0.753 | 50/50 | 0 | 37 | 2.40 ± 1.49 (2.32) | 37.81 ± 58.98 (8.13) | 2.21 ± 1.07 (2.64) | 4.64 ± 2.28 (5.83) | 2.33 ± 1.35 (2.89) |
| right | p | 0.792 | 50/50 | 0 | 41 | 1.79 ± 0.65 (1.75) | 15.07 ± 24.76 (7.26) | 2.34 ± 0.85 (2.52) | 4.83 ± 1.83 (4.88) | 2.35 ± 1.10 (2.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 99/100 | 0 | 83 | 1.75 ± 0.68 (1.62) | 17.39 ± 33.78 (5.56) | 2.29 ± 0.90 (2.53) | 4.79 ± 1.94 (5.44) | 2.33 ± 1.16 (2.53) |
| right | p | 0.785 | 100/100 | 0 | 78 | 1.82 ± 1.18 (1.64) | 22.54 ± 42.65 (6.77) | 2.24 ± 0.93 (2.51) | 4.63 ± 1.97 (4.82) | 2.23 ± 1.16 (2.30) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 22 | 1.20 ± 0.29 (1.22) | 10.12 ± 17.41 (4.95) | 2.21 ± 0.72 (2.36) | 4.64 ± 1.59 (4.85) | 2.12 ± 0.93 (2.24) |
| forward/right | p | 0.809 | 25/25 | 0 | 20 | 1.38 ± 0.60 (1.32) | 10.25 ± 15.36 (3.96) | 2.26 ± 0.94 (2.45) | 4.66 ± 1.98 (4.82) | 2.22 ± 1.11 (2.31) |
| left/left | p | 0.827 | 24/25 | 0 | 23 | 1.67 ± 0.36 (1.59) | 5.82 ± 5.19 (2.92) | 2.49 ± 0.74 (2.62) | 5.23 ± 1.67 (5.79) | 2.62 ± 1.01 (2.94) |
| left/right | p | 0.771 | 25/25 | 0 | 18 | 1.64 ± 0.51 (1.80) | 27.30 ± 44.44 (6.76) | 2.06 ± 0.95 (2.43) | 4.22 ± 1.96 (4.68) | 1.94 ± 1.16 (2.04) |
| back/left | p | 0.761 | 25/25 | 0 | 18 | 2.15 ± 0.69 (2.34) | 33.58 ± 52.04 (7.76) | 2.27 ± 1.07 (2.62) | 4.74 ± 2.26 (5.90) | 2.40 ± 1.39 (3.02) |
| back/right | p | 0.744 | 25/25 | 0 | 19 | 2.65 ± 1.96 (2.30) | 42.04 ± 64.92 (8.49) | 2.16 ± 1.07 (2.66) | 4.54 ± 2.30 (5.61) | 2.27 ± 1.32 (2.82) |
| right/left | p | 0.770 | 25/25 | 0 | 20 | 1.97 ± 0.80 (2.00) | 19.58 ± 32.14 (6.83) | 2.20 ± 0.98 (2.49) | 4.56 ± 2.10 (4.76) | 2.20 ± 1.20 (2.27) |
| right/right | p | 0.815 | 25/25 | 0 | 21 | 1.62 ± 0.39 (1.56) | 10.57 ± 12.38 (8.35) | 2.48 ± 0.68 (2.59) | 5.10 ± 1.46 (4.89) | 2.49 ± 0.98 (2.37) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.816 | 20.2 | 5.14 | 2.60 |
| p | normal | 0.767 | 19.8 | 4.28 | 1.97 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.718 | 0.11 | 2.49 ± 1.31 (2.50) | 3.81 | 1.64 |
| p | medium | 20 | 0.854 | 0.61 | 1.37 ± 0.18 (1.41) | 4.42 | 1.96 |
| p | strong | 126 | 0.813 | 0.69 | - | 5.14 | 2.61 |

## Notes

- p: score 0.792, 199/200 kicked, 0 fell; worst sector back (0.753).
