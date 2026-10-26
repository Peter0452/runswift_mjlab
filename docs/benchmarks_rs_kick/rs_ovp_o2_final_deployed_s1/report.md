# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_10-42-42_ovp_o2/model_19049.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.879** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 175 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.98 ± 1.06 (1.78) |
| Direction error [°] | 12.85 ± 28.56 (4.87) |
| Avg ball speed [m/s] | 2.02 ± 0.57 (2.06) |
| Peak ball speed [m/s] | 4.84 ± 1.44 (5.26) |
| Distance [m] | 2.11 ± 0.84 (2.27) |
| Path length [m] | 2.12 ± 0.84 (2.28) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.921 | 50/50 | 0 | 46 | 1.54 ± 1.50 (1.39) | 7.04 ± 11.06 (3.88) | 1.98 ± 0.57 (2.05) | 4.76 ± 1.45 (5.28) | 2.03 ± 0.81 (2.16) |
| left | p | 0.889 | 49/50 | 0 | 44 | 1.82 ± 0.43 (1.78) | 12.19 ± 23.50 (5.45) | 2.03 ± 0.58 (1.99) | 4.79 ± 1.42 (4.81) | 2.12 ± 0.85 (1.85) |
| back | p | 0.813 | 49/50 | 0 | 43 | 2.75 ± 1.04 (2.74) | 22.35 ± 47.01 (4.84) | 2.06 ± 0.61 (2.17) | 5.01 ± 1.52 (5.74) | 2.25 ± 0.91 (2.57) |
| right | p | 0.893 | 49/50 | 0 | 42 | 1.82 ± 0.41 (1.80) | 9.95 ± 16.12 (5.00) | 2.01 ± 0.50 (2.06) | 4.79 ± 1.35 (4.94) | 2.06 ± 0.77 (2.04) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.881 | 98/100 | 0 | 90 | 1.93 ± 0.86 (1.73) | 12.70 ± 28.60 (4.73) | 2.03 ± 0.53 (2.06) | 4.91 ± 1.40 (5.39) | 2.14 ± 0.81 (2.31) |
| right | p | 0.877 | 99/100 | 0 | 85 | 2.03 ± 1.23 (1.88) | 13.01 ± 28.53 (4.99) | 2.02 ± 0.60 (2.06) | 4.77 ± 1.48 (5.08) | 2.09 ± 0.87 (2.04) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.935 | 25/25 | 0 | 23 | 1.32 ± 0.32 (1.38) | 6.18 ± 7.38 (3.87) | 2.01 ± 0.50 (2.02) | 4.83 ± 1.29 (5.15) | 2.06 ± 0.74 (2.07) |
| forward/right | p | 0.907 | 25/25 | 0 | 23 | 1.76 ± 2.07 (1.46) | 7.90 ± 13.74 (4.44) | 1.95 ± 0.64 (2.09) | 4.69 ± 1.60 (5.56) | 2.00 ± 0.88 (2.27) |
| left/left | p | 0.899 | 24/25 | 0 | 24 | 1.76 ± 0.36 (1.64) | 6.12 ± 3.73 (4.76) | 2.21 ± 0.36 (2.06) | 5.26 ± 0.96 (5.71) | 2.38 ± 0.65 (2.54) |
| left/right | p | 0.879 | 25/25 | 0 | 20 | 1.88 ± 0.49 (1.94) | 18.01 ± 31.61 (6.67) | 1.86 ± 0.69 (1.89) | 4.35 ± 1.64 (4.28) | 1.87 ± 0.94 (1.75) |
| back/left | p | 0.818 | 25/25 | 0 | 21 | 2.70 ± 1.23 (2.74) | 26.81 ± 49.22 (5.62) | 2.01 ± 0.63 (2.08) | 4.93 ± 1.65 (5.72) | 2.19 ± 0.96 (2.50) |
| back/right | p | 0.808 | 24/25 | 0 | 22 | 2.81 ± 0.78 (2.77) | 17.70 ± 44.11 (4.02) | 2.12 ± 0.58 (2.27) | 5.10 ± 1.37 (5.74) | 2.31 ± 0.84 (2.60) |
| right/left | p | 0.871 | 24/25 | 0 | 22 | 1.93 ± 0.42 (2.02) | 11.36 ± 21.18 (4.60) | 1.88 ± 0.54 (1.94) | 4.63 ± 1.50 (4.89) | 1.94 ± 0.79 (2.00) |
| right/right | p | 0.915 | 25/25 | 0 | 20 | 1.71 ± 0.37 (1.76) | 8.60 ± 8.67 (5.81) | 2.14 ± 0.42 (2.06) | 4.94 ± 1.16 (4.94) | 2.18 ± 0.72 (2.04) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.880 | 11.4 | 5.39 | 2.45 |
| p | normal | 0.878 | 14.3 | 4.29 | 1.77 |

## Notes

- p: score 0.879, 197/200 kicked, 0 fell; worst sector back (0.813).
