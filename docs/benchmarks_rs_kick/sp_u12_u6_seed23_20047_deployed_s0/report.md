# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_15-01-05_u12_u6_seed23/model_20047.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.792** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 8 |
| Time to kick [s] | 2.03 ± 1.75 (1.70) |
| Direction error [°] | 18.89 ± 38.11 (4.51) |
| Avg ball speed [m/s] | 1.89 ± 0.57 (1.99) |
| Peak ball speed [m/s] | 4.78 ± 1.50 (5.38) |
| Distance [m] | 2.09 ± 0.89 (2.17) |
| Path length [m] | 2.10 ± 0.90 (2.18) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.803 | 50/50 | 0 | 41 | 1.63 ± 1.76 (1.34) | 9.10 ± 12.29 (4.44) | 1.81 ± 0.52 (1.87) | 4.54 ± 1.45 (4.51) | 1.93 ± 0.84 (1.93) |
| left | p | 0.801 | 49/50 | 0 | 41 | 1.77 ± 1.25 (1.72) | 20.51 ± 37.53 (4.98) | 1.88 ± 0.56 (2.05) | 4.85 ± 1.47 (5.57) | 2.13 ± 0.85 (2.40) |
| back | p | 0.766 | 50/50 | 0 | 42 | 2.68 ± 1.79 (2.49) | 28.61 ± 55.10 (4.16) | 1.94 ± 0.65 (2.07) | 4.88 ± 1.67 (5.58) | 2.21 ± 1.00 (2.41) |
| right | p | 0.799 | 50/50 | 0 | 42 | 2.03 ± 1.91 (1.70) | 17.38 ± 31.91 (5.08) | 1.93 ± 0.53 (2.01) | 4.84 ± 1.38 (5.23) | 2.11 ± 0.85 (2.19) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.814 | 100/100 | 0 | 86 | 1.81 ± 1.05 (1.71) | 17.92 ± 37.65 (4.48) | 1.91 ± 0.56 (1.99) | 4.88 ± 1.42 (5.43) | 2.15 ± 0.87 (2.23) |
| right | p | 0.770 | 99/100 | 0 | 80 | 2.24 ± 2.22 (1.70) | 19.87 ± 38.54 (4.93) | 1.86 ± 0.59 (1.98) | 4.68 ± 1.57 (4.78) | 2.04 ± 0.92 (2.09) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 21 | 1.29 ± 0.29 (1.32) | 8.61 ± 13.40 (4.24) | 1.84 ± 0.55 (1.86) | 4.74 ± 1.49 (4.67) | 2.06 ± 0.85 (2.06) |
| forward/right | p | 0.774 | 25/25 | 0 | 20 | 1.96 ± 2.43 (1.34) | 9.58 ± 11.04 (6.30) | 1.77 ± 0.50 (1.87) | 4.35 ± 1.39 (4.41) | 1.80 ± 0.81 (1.91) |
| left/left | p | 0.846 | 25/25 | 0 | 23 | 1.56 ± 0.41 (1.66) | 13.03 ± 23.63 (5.81) | 1.99 ± 0.48 (2.11) | 5.09 ± 1.18 (5.60) | 2.29 ± 0.71 (2.59) |
| left/right | p | 0.756 | 24/25 | 0 | 18 | 2.00 ± 1.71 (1.76) | 28.29 ± 46.64 (3.11) | 1.75 ± 0.61 (1.99) | 4.60 ± 1.68 (5.52) | 1.96 ± 0.94 (2.27) |
| back/left | p | 0.766 | 25/25 | 0 | 21 | 2.68 ± 1.69 (2.50) | 29.05 ± 56.19 (4.16) | 1.96 ± 0.63 (1.98) | 4.98 ± 1.57 (5.57) | 2.25 ± 1.02 (2.37) |
| back/right | p | 0.766 | 25/25 | 0 | 21 | 2.68 ± 1.88 (2.48) | 28.18 ± 53.99 (4.16) | 1.91 ± 0.67 (2.19) | 4.79 ± 1.76 (5.69) | 2.16 ± 0.98 (2.49) |
| right/left | p | 0.814 | 25/25 | 0 | 21 | 1.73 ± 0.48 (1.76) | 21.00 ± 39.15 (4.42) | 1.86 ± 0.54 (1.99) | 4.72 ± 1.39 (5.18) | 1.99 ± 0.82 (2.16) |
| right/right | p | 0.784 | 25/25 | 0 | 21 | 2.32 ± 2.63 (1.64) | 13.77 ± 21.86 (6.54) | 1.99 ± 0.52 (2.03) | 4.96 ± 1.35 (5.27) | 2.22 ± 0.87 (2.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.829 | 17.1 | 5.44 | 2.49 |
| p | normal | 0.755 | 20.7 | 4.13 | 1.70 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.16 | 2.44 ± 1.00 (2.24) | 3.80 | 1.51 |
| p | medium | 16 | 0.803 | 0.58 | 1.27 ± 0.37 (1.33) | 4.12 | 1.76 |
| p | strong | 126 | 0.826 | 0.71 | - | 5.32 | 2.41 |

## Notes

- p: score 0.792, 199/200 kicked, 0 fell; worst sector back (0.766).
