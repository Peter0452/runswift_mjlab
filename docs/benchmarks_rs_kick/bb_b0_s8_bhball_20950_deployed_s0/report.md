# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.771** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 159 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.82 ± 1.03 (1.68) |
| Direction error [°] | 19.35 ± 38.49 (5.73) |
| Avg ball speed [m/s] | 2.08 ± 0.62 (2.23) |
| Peak ball speed [m/s] | 4.54 ± 1.49 (5.02) |
| Distance [m] | 1.79 ± 0.80 (1.88) |
| Path length [m] | 1.80 ± 0.80 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.789 | 49/50 | 0 | 42 | 1.63 ± 1.68 (1.34) | 9.18 ± 12.94 (5.23) | 2.06 ± 0.63 (2.20) | 4.47 ± 1.53 (4.37) | 1.73 ± 0.81 (1.84) |
| left | p | 0.790 | 48/50 | 0 | 38 | 1.63 ± 0.47 (1.67) | 19.46 ± 36.63 (5.45) | 2.09 ± 0.59 (2.26) | 4.62 ± 1.42 (5.13) | 1.81 ± 0.77 (1.90) |
| back | p | 0.723 | 48/50 | 0 | 39 | 2.40 ± 0.72 (2.45) | 28.56 ± 52.24 (8.10) | 2.13 ± 0.61 (2.29) | 4.60 ± 1.43 (5.16) | 1.88 ± 0.78 (1.99) |
| right | p | 0.782 | 48/50 | 0 | 40 | 1.64 ± 0.44 (1.71) | 20.41 ± 39.03 (5.12) | 2.03 ± 0.64 (2.16) | 4.47 ± 1.55 (4.93) | 1.75 ± 0.83 (1.80) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.804 | 99/100 | 0 | 85 | 1.75 ± 0.64 (1.68) | 18.38 ± 38.57 (5.52) | 2.09 ± 0.60 (2.23) | 4.57 ± 1.44 (4.98) | 1.81 ± 0.77 (1.84) |
| right | p | 0.739 | 94/100 | 0 | 74 | 1.91 ± 1.31 (1.70) | 20.38 ± 38.39 (6.28) | 2.06 ± 0.64 (2.24) | 4.50 ± 1.53 (5.05) | 1.77 ± 0.83 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.839 | 25/25 | 0 | 23 | 1.33 ± 0.35 (1.34) | 8.21 ± 14.86 (3.31) | 2.11 ± 0.66 (2.22) | 4.59 ± 1.57 (4.47) | 1.81 ± 0.80 (1.84) |
| forward/right | p | 0.740 | 24/25 | 0 | 19 | 1.95 ± 2.33 (1.32) | 10.20 ± 10.48 (6.00) | 2.00 ± 0.60 (2.10) | 4.34 ± 1.48 (4.17) | 1.64 ± 0.80 (1.58) |
| left/left | p | 0.839 | 25/25 | 0 | 21 | 1.56 ± 0.40 (1.62) | 12.94 ± 22.36 (5.59) | 2.14 ± 0.48 (2.24) | 4.71 ± 1.17 (5.12) | 1.86 ± 0.66 (1.76) |
| left/right | p | 0.742 | 23/25 | 0 | 17 | 1.69 ± 0.54 (1.82) | 26.56 ± 46.49 (4.59) | 2.04 ± 0.69 (2.27) | 4.54 ± 1.64 (5.13) | 1.76 ± 0.86 (1.95) |
| back/left | p | 0.737 | 24/25 | 0 | 21 | 2.40 ± 0.75 (2.44) | 25.61 ± 51.32 (7.68) | 2.22 ± 0.47 (2.27) | 4.81 ± 1.13 (5.21) | 1.97 ± 0.71 (2.08) |
| back/right | p | 0.708 | 24/25 | 0 | 18 | 2.40 ± 0.69 (2.46) | 31.50 ± 52.98 (8.75) | 2.04 ± 0.71 (2.31) | 4.40 ± 1.64 (5.09) | 1.78 ± 0.84 (1.95) |
| right/left | p | 0.799 | 25/25 | 0 | 20 | 1.72 ± 0.44 (1.76) | 27.04 ± 48.81 (4.21) | 1.91 ± 0.70 (2.08) | 4.20 ± 1.70 (4.51) | 1.60 ± 0.85 (1.77) |
| right/right | p | 0.765 | 23/25 | 0 | 20 | 1.56 ± 0.41 (1.60) | 13.21 ± 22.15 (5.70) | 2.16 ± 0.53 (2.32) | 4.76 ± 1.30 (5.42) | 1.92 ± 0.78 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.802 | 18.1 | 5.15 | 2.12 |
| p | normal | 0.740 | 20.6 | 3.94 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.701 | 0.18 | 2.28 ± 0.92 (2.15) | 3.60 | 1.27 |
| p | medium | 16 | 0.792 | 0.71 | 1.27 ± 0.19 (1.29) | 4.10 | 1.61 |
| p | strong | 126 | 0.801 | 0.67 | - | 5.02 | 2.05 |

## Notes

- p: score 0.771, 193/200 kicked, 0 fell; worst sector back (0.723).
