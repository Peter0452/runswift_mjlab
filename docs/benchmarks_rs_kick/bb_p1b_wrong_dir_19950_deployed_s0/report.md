# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-23-17_p1b_wrong_dir/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.785** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 2.04 ± 1.67 (1.72) |
| Direction error [°] | 17.49 ± 36.67 (5.87) |
| Avg ball speed [m/s] | 2.12 ± 0.63 (2.29) |
| Peak ball speed [m/s] | 4.61 ± 1.48 (5.17) |
| Distance [m] | 1.91 ± 0.82 (2.04) |
| Path length [m] | 1.92 ± 0.82 (2.05) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.796 | 50/50 | 0 | 44 | 1.89 ± 2.23 (1.34) | 8.16 ± 11.96 (3.98) | 2.00 ± 0.71 (2.18) | 4.34 ± 1.63 (4.38) | 1.75 ± 0.85 (1.77) |
| left | p | 0.808 | 49/50 | 0 | 42 | 1.84 ± 1.44 (1.70) | 17.98 ± 34.62 (5.85) | 2.15 ± 0.55 (2.29) | 4.73 ± 1.33 (5.27) | 1.95 ± 0.75 (2.04) |
| back | p | 0.727 | 48/50 | 0 | 41 | 2.55 ± 1.30 (2.49) | 28.55 ± 54.12 (7.24) | 2.17 ± 0.67 (2.35) | 4.71 ± 1.56 (5.34) | 2.02 ± 0.87 (2.19) |
| right | p | 0.810 | 50/50 | 0 | 44 | 1.89 ± 1.41 (1.75) | 15.72 ± 31.01 (6.90) | 2.15 ± 0.57 (2.28) | 4.66 ± 1.34 (5.20) | 1.93 ± 0.76 (2.08) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.809 | 99/100 | 0 | 89 | 1.84 ± 1.05 (1.70) | 15.34 ± 34.17 (5.87) | 2.20 ± 0.54 (2.33) | 4.76 ± 1.29 (5.27) | 1.99 ± 0.75 (2.07) |
| right | p | 0.761 | 98/100 | 0 | 82 | 2.23 ± 2.10 (1.75) | 19.66 ± 38.92 (5.99) | 2.04 ± 0.70 (2.25) | 4.46 ± 1.63 (4.96) | 1.83 ± 0.87 (1.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.830 | 25/25 | 0 | 23 | 1.65 ± 1.82 (1.34) | 6.94 ± 12.80 (2.26) | 2.11 ± 0.62 (2.23) | 4.58 ± 1.47 (4.48) | 1.87 ± 0.81 (1.82) |
| forward/right | p | 0.761 | 25/25 | 0 | 21 | 2.12 ± 2.55 (1.34) | 9.38 ± 10.93 (5.54) | 1.90 ± 0.76 (2.11) | 4.11 ± 1.75 (4.15) | 1.62 ± 0.87 (1.74) |
| left/left | p | 0.852 | 25/25 | 0 | 23 | 1.59 ± 0.39 (1.60) | 9.95 ± 16.31 (6.37) | 2.28 ± 0.36 (2.33) | 4.99 ± 0.92 (5.35) | 2.11 ± 0.57 (2.17) |
| left/right | p | 0.764 | 24/25 | 0 | 19 | 2.10 ± 1.99 (1.85) | 26.35 ± 45.09 (4.56) | 2.03 ± 0.67 (2.25) | 4.46 ± 1.60 (5.08) | 1.79 ± 0.87 (2.01) |
| back/left | p | 0.742 | 24/25 | 0 | 21 | 2.34 ± 0.65 (2.45) | 26.11 ± 51.16 (7.61) | 2.25 ± 0.52 (2.39) | 4.89 ± 1.24 (5.35) | 2.10 ± 0.79 (2.22) |
| back/right | p | 0.711 | 24/25 | 0 | 20 | 2.76 ± 1.70 (2.52) | 30.99 ± 56.82 (6.85) | 2.08 ± 0.78 (2.31) | 4.53 ± 1.80 (5.28) | 1.94 ± 0.94 (2.07) |
| right/left | p | 0.813 | 25/25 | 0 | 22 | 1.80 ± 0.45 (1.78) | 18.79 ± 38.18 (6.93) | 2.15 ± 0.59 (2.25) | 4.59 ± 1.40 (5.11) | 1.90 ± 0.76 (2.06) |
| right/right | p | 0.807 | 25/25 | 0 | 22 | 1.97 ± 1.95 (1.64) | 12.65 ± 21.14 (6.87) | 2.16 ± 0.54 (2.33) | 4.72 ± 1.28 (5.29) | 1.96 ± 0.75 (2.10) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.811 | 15.4 | 5.25 | 2.27 |
| p | normal | 0.759 | 19.5 | 3.98 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.717 | 0.15 | 2.33 ± 1.02 (2.19) | 3.66 | 1.38 |
| p | medium | 16 | 0.836 | 0.70 | 1.25 ± 0.24 (1.23) | 4.06 | 1.60 |
| p | strong | 126 | 0.810 | 0.68 | - | 5.13 | 2.20 |

## Notes

- p: score 0.785, 197/200 kicked, 0 fell; worst sector back (0.727).
