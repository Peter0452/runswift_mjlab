# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_20-02-31_e0002/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.748** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 154 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.91 ± 0.83 (1.80) |
| Direction error [°] | 20.94 ± 37.43 (7.50) |
| Avg ball speed [m/s] | 1.93 ± 0.60 (2.12) |
| Peak ball speed [m/s] | 4.25 ± 1.42 (4.88) |
| Distance [m] | 1.60 ± 0.71 (1.70) |
| Path length [m] | 1.61 ± 0.72 (1.72) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.778 | 48/50 | 0 | 41 | 1.42 ± 0.34 (1.42) | 10.37 ± 14.64 (5.20) | 1.84 ± 0.59 (1.95) | 4.01 ± 1.41 (4.09) | 1.43 ± 0.67 (1.45) |
| left | p | 0.775 | 48/50 | 0 | 38 | 1.78 ± 0.50 (1.83) | 19.48 ± 31.96 (6.31) | 2.01 ± 0.55 (2.17) | 4.47 ± 1.35 (5.08) | 1.72 ± 0.72 (1.81) |
| back | p | 0.669 | 48/50 | 0 | 36 | 2.67 ± 1.11 (2.65) | 34.76 ± 55.16 (11.83) | 1.95 ± 0.64 (2.20) | 4.28 ± 1.51 (5.01) | 1.68 ± 0.73 (1.98) |
| right | p | 0.768 | 49/50 | 0 | 39 | 1.76 ± 0.52 (1.78) | 19.20 ± 32.03 (7.51) | 1.93 ± 0.59 (2.13) | 4.25 ± 1.38 (4.62) | 1.59 ± 0.69 (1.70) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.773 | 99/100 | 0 | 80 | 1.86 ± 0.69 (1.76) | 20.69 ± 37.38 (7.97) | 1.98 ± 0.56 (2.17) | 4.35 ± 1.33 (4.98) | 1.64 ± 0.68 (1.75) |
| right | p | 0.722 | 94/100 | 0 | 74 | 1.96 ± 0.95 (1.82) | 21.20 ± 37.48 (7.38) | 1.88 ± 0.63 (2.08) | 4.15 ± 1.51 (4.50) | 1.56 ± 0.75 (1.68) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.824 | 25/25 | 0 | 22 | 1.43 ± 0.35 (1.46) | 9.92 ± 15.54 (4.84) | 1.92 ± 0.58 (2.11) | 4.23 ± 1.38 (4.15) | 1.52 ± 0.65 (1.50) |
| forward/right | p | 0.732 | 23/25 | 0 | 19 | 1.41 ± 0.34 (1.42) | 10.85 ± 13.58 (5.78) | 1.75 ± 0.59 (1.87) | 3.77 ± 1.40 (3.75) | 1.33 ± 0.68 (1.30) |
| left/left | p | 0.833 | 25/25 | 0 | 20 | 1.71 ± 0.45 (1.74) | 13.71 ± 22.18 (6.18) | 2.10 ± 0.45 (2.19) | 4.67 ± 1.06 (5.11) | 1.83 ± 0.61 (1.84) |
| left/right | p | 0.717 | 23/25 | 0 | 18 | 1.85 ± 0.54 (2.02) | 25.75 ± 39.00 (6.43) | 1.92 ± 0.63 (2.13) | 4.25 ± 1.57 (4.94) | 1.59 ± 0.81 (1.71) |
| back/left | p | 0.670 | 24/25 | 0 | 18 | 2.50 ± 0.80 (2.64) | 35.38 ± 54.82 (12.39) | 1.99 ± 0.57 (2.20) | 4.32 ± 1.34 (5.01) | 1.70 ± 0.71 (1.94) |
| back/right | p | 0.668 | 24/25 | 0 | 18 | 2.84 ± 1.33 (2.65) | 34.13 ± 55.49 (11.29) | 1.91 ± 0.71 (2.21) | 4.24 ± 1.66 (5.00) | 1.67 ± 0.75 (1.98) |
| right/left | p | 0.765 | 25/25 | 0 | 20 | 1.82 ± 0.56 (1.80) | 24.35 ± 39.11 (7.97) | 1.90 ± 0.60 (2.16) | 4.17 ± 1.43 (4.36) | 1.52 ± 0.70 (1.70) |
| right/right | p | 0.771 | 24/25 | 0 | 19 | 1.70 ± 0.48 (1.74) | 13.83 ± 21.08 (7.05) | 1.96 ± 0.58 (2.10) | 4.34 ± 1.31 (4.79) | 1.65 ± 0.68 (1.69) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.778 | 17.7 | 4.81 | 1.87 |
| p | normal | 0.717 | 24.1 | 3.70 | 1.34 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.685 | 0.20 | 2.14 ± 0.96 (2.05) | 3.39 | 1.17 |
| p | medium | 16 | 0.772 | 0.74 | 1.21 ± 0.22 (1.27) | 3.90 | 1.46 |
| p | strong | 126 | 0.773 | 0.63 | - | 4.69 | 1.82 |

## Notes

- p: score 0.748, 193/200 kicked, 0 fell; worst sector back (0.669).
