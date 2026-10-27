# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.765** |
| Kicked / fell | 192 / 0 |
| Kicks within 15° | 158 |
| Weak kicks (< 0.3 m) | 34 |
| Time to kick [s] | 1.81 ± 1.47 (1.53) |
| Direction error [°] | 22.21 ± 40.20 (6.69) |
| Avg ball speed [m/s] | 1.67 ± 0.74 (1.96) |
| Peak ball speed [m/s] | 3.58 ± 1.67 (4.29) |
| Distance [m] | 1.35 ± 0.88 (1.57) |
| Path length [m] | 1.36 ± 0.89 (1.58) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.767 | 47/50 | 0 | 40 | 1.31 ± 1.24 (1.14) | 11.05 ± 14.42 (5.80) | 1.48 ± 0.69 (1.34) | 3.20 ± 1.54 (2.81) | 1.09 ± 0.79 (0.80) |
| left | p | 0.784 | 49/50 | 0 | 41 | 1.98 ± 1.94 (1.64) | 22.17 ± 38.82 (6.49) | 1.76 ± 0.70 (2.03) | 3.77 ± 1.59 (4.48) | 1.45 ± 0.85 (1.76) |
| back | p | 0.730 | 48/50 | 0 | 38 | 2.40 ± 1.55 (2.29) | 34.49 ± 56.23 (7.08) | 1.74 ± 0.82 (2.25) | 3.74 ± 1.84 (4.91) | 1.50 ± 0.95 (2.03) |
| right | p | 0.780 | 48/50 | 0 | 39 | 1.56 ± 0.45 (1.56) | 20.88 ± 35.86 (7.96) | 1.69 ± 0.73 (1.80) | 3.59 ± 1.62 (3.87) | 1.36 ± 0.87 (1.43) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.805 | 100/100 | 0 | 85 | 1.81 ± 1.44 (1.53) | 21.28 ± 39.78 (6.28) | 1.72 ± 0.73 (2.00) | 3.70 ± 1.63 (4.37) | 1.42 ± 0.88 (1.64) |
| right | p | 0.726 | 92/100 | 0 | 73 | 1.81 ± 1.51 (1.53) | 23.21 ± 40.63 (6.79) | 1.62 ± 0.76 (1.66) | 3.46 ± 1.69 (3.51) | 1.28 ± 0.88 (1.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 23 | 1.49 ± 1.66 (1.16) | 8.17 ± 11.20 (4.96) | 1.61 ± 0.67 (1.94) | 3.50 ± 1.48 (4.25) | 1.23 ± 0.80 (1.47) |
| forward/right | p | 0.699 | 22/25 | 0 | 17 | 1.10 ± 0.26 (1.11) | 14.32 ± 16.78 (7.41) | 1.34 ± 0.67 (1.26) | 2.87 ± 1.54 (2.62) | 0.92 ± 0.75 (0.74) |
| left/left | p | 0.838 | 25/25 | 0 | 22 | 1.40 ± 0.42 (1.50) | 15.80 ± 26.13 (5.49) | 1.81 ± 0.65 (2.02) | 3.87 ± 1.49 (4.45) | 1.51 ± 0.80 (1.76) |
| left/right | p | 0.730 | 24/25 | 0 | 19 | 2.57 ± 2.62 (1.77) | 28.81 ± 47.74 (7.11) | 1.71 ± 0.74 (2.11) | 3.67 ± 1.69 (4.68) | 1.40 ± 0.89 (1.77) |
| back/left | p | 0.756 | 25/25 | 0 | 20 | 2.68 ± 2.01 (2.26) | 34.23 ± 55.98 (8.27) | 1.83 ± 0.78 (2.27) | 3.94 ± 1.78 (5.07) | 1.61 ± 0.96 (2.21) |
| back/right | p | 0.704 | 23/25 | 0 | 18 | 2.09 ± 0.63 (2.32) | 34.77 ± 56.49 (6.68) | 1.65 ± 0.85 (2.20) | 3.52 ± 1.89 (4.66) | 1.38 ± 0.93 (1.90) |
| right/left | p | 0.790 | 25/25 | 0 | 20 | 1.68 ± 0.46 (1.68) | 26.94 ± 44.55 (8.05) | 1.62 ± 0.76 (1.55) | 3.47 ± 1.72 (3.10) | 1.31 ± 0.90 (1.02) |
| right/right | p | 0.770 | 23/25 | 0 | 19 | 1.43 ± 0.39 (1.40) | 14.30 ± 21.05 (7.88) | 1.76 ± 0.67 (1.85) | 3.73 ± 1.48 (3.92) | 1.41 ± 0.84 (1.52) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.771 | 19.2 | 4.50 | 1.85 |
| p | normal | 0.759 | 25.1 | 2.68 | 0.86 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.730 | 0.51 | 1.33 ± 0.68 (1.22) | 2.07 | 0.52 |
| p | medium | 16 | 0.849 | 0.77 | 0.79 ± 0.22 (0.80) | 2.57 | 0.73 |
| p | strong | 126 | 0.771 | 0.59 | - | 4.40 | 1.82 |

## Notes

- p: score 0.765, 192/200 kicked, 0 fell; worst sector back (0.730).
