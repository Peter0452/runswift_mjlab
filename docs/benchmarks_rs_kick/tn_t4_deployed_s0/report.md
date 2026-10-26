# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-06-39_t4_n7_control/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.768** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 160 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 1.91 ± 1.45 (1.70) |
| Direction error [°] | 20.87 ± 40.54 (5.56) |
| Avg ball speed [m/s] | 2.09 ± 0.70 (2.33) |
| Peak ball speed [m/s] | 4.52 ± 1.58 (5.00) |
| Distance [m] | 1.89 ± 0.84 (2.10) |
| Path length [m] | 1.90 ± 0.84 (2.11) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 50/50 | 0 | 40 | 1.73 ± 1.96 (1.35) | 10.38 ± 16.07 (4.27) | 2.01 ± 0.69 (2.27) | 4.30 ± 1.60 (4.68) | 1.76 ± 0.82 (2.02) |
| left | p | 0.766 | 48/50 | 0 | 39 | 1.80 ± 1.33 (1.70) | 23.56 ± 40.56 (6.47) | 2.07 ± 0.70 (2.34) | 4.53 ± 1.58 (5.02) | 1.90 ± 0.84 (2.09) |
| back | p | 0.753 | 49/50 | 0 | 42 | 2.45 ± 1.46 (2.40) | 28.13 ± 54.27 (7.06) | 2.24 ± 0.69 (2.45) | 4.82 ± 1.55 (5.43) | 2.11 ± 0.85 (2.29) |
| right | p | 0.765 | 48/50 | 0 | 39 | 1.66 ± 0.49 (1.70) | 21.68 ± 39.72 (4.40) | 2.05 ± 0.69 (2.26) | 4.42 ± 1.55 (4.88) | 1.80 ± 0.82 (2.00) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 100/100 | 0 | 86 | 1.90 ± 1.42 (1.67) | 19.94 ± 40.59 (5.47) | 2.15 ± 0.67 (2.36) | 4.65 ± 1.51 (5.21) | 1.96 ± 0.81 (2.13) |
| right | p | 0.737 | 95/100 | 0 | 74 | 1.93 ± 1.49 (1.70) | 21.85 ± 40.45 (5.69) | 2.03 ± 0.72 (2.27) | 4.38 ± 1.65 (4.94) | 1.82 ± 0.87 (2.07) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.812 | 25/25 | 0 | 23 | 1.62 ± 1.77 (1.36) | 8.07 ± 12.35 (3.90) | 2.12 ± 0.63 (2.28) | 4.56 ± 1.43 (4.97) | 1.89 ± 0.71 (2.08) |
| forward/right | p | 0.763 | 25/25 | 0 | 17 | 1.85 ± 2.13 (1.34) | 12.70 ± 18.80 (4.71) | 1.90 ± 0.73 (2.24) | 4.04 ± 1.72 (4.41) | 1.63 ± 0.89 (1.85) |
| left/left | p | 0.834 | 25/25 | 0 | 22 | 1.57 ± 0.41 (1.64) | 13.77 ± 22.02 (6.64) | 2.22 ± 0.64 (2.37) | 4.85 ± 1.45 (5.47) | 2.10 ± 0.76 (2.22) |
| left/right | p | 0.698 | 23/25 | 0 | 17 | 2.06 ± 1.83 (1.74) | 34.19 ± 51.86 (6.04) | 1.92 ± 0.73 (2.23) | 4.19 ± 1.65 (4.97) | 1.67 ± 0.87 (2.00) |
| back/left | p | 0.766 | 25/25 | 0 | 21 | 2.62 ± 1.95 (2.36) | 30.85 ± 58.14 (6.25) | 2.28 ± 0.67 (2.48) | 4.87 ± 1.50 (5.50) | 2.14 ± 0.88 (2.37) |
| back/right | p | 0.740 | 24/25 | 0 | 21 | 2.28 ± 0.57 (2.42) | 25.30 ± 49.77 (7.42) | 2.20 ± 0.71 (2.41) | 4.76 ± 1.59 (5.33) | 2.07 ± 0.81 (2.27) |
| right/left | p | 0.783 | 25/25 | 0 | 20 | 1.78 ± 0.50 (1.80) | 27.05 ± 47.16 (5.15) | 2.00 ± 0.71 (2.26) | 4.31 ± 1.58 (4.81) | 1.73 ± 0.82 (2.00) |
| right/right | p | 0.747 | 23/25 | 0 | 19 | 1.54 ± 0.43 (1.56) | 15.83 ± 28.44 (4.15) | 2.11 ± 0.67 (2.26) | 4.52 ± 1.52 (4.94) | 1.89 ± 0.82 (1.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.800 | 18.2 | 5.00 | 2.12 |
| p | normal | 0.735 | 23.5 | 4.04 | 1.67 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.703 | 0.15 | 2.38 ± 1.22 (2.22) | 3.75 | 1.51 |
| p | medium | 16 | 0.776 | 0.54 | 1.43 ± 0.25 (1.47) | 4.60 | 2.01 |
| p | strong | 126 | 0.796 | 0.65 | - | 4.86 | 2.05 |

## Notes

- p: score 0.768, 195/200 kicked, 0 fell; worst sector back (0.753).
