# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-18-00_e3_drill_stand/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.05 ± 1.75 (1.72) |
| Direction error [°] | 20.52 ± 40.69 (4.70) |
| Avg ball speed [m/s] | 2.09 ± 0.70 (2.28) |
| Peak ball speed [m/s] | 4.48 ± 1.59 (4.98) |
| Distance [m] | 1.88 ± 0.87 (1.98) |
| Path length [m] | 1.89 ± 0.87 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.786 | 50/50 | 0 | 40 | 1.91 ± 2.37 (1.34) | 11.11 ± 16.51 (4.66) | 1.99 ± 0.75 (2.18) | 4.21 ± 1.69 (4.36) | 1.72 ± 0.91 (1.79) |
| left | p | 0.792 | 48/50 | 0 | 40 | 1.64 ± 0.50 (1.66) | 20.11 ± 38.48 (4.50) | 2.13 ± 0.62 (2.29) | 4.65 ± 1.48 (5.26) | 1.95 ± 0.82 (2.03) |
| back | p | 0.754 | 50/50 | 0 | 41 | 2.53 ± 1.31 (2.58) | 31.13 ± 57.40 (4.73) | 2.09 ± 0.75 (2.31) | 4.46 ± 1.65 (5.03) | 1.90 ± 0.89 (2.01) |
| right | p | 0.780 | 49/50 | 0 | 41 | 2.09 ± 2.03 (1.74) | 19.69 ± 36.89 (4.78) | 2.15 ± 0.65 (2.28) | 4.60 ± 1.47 (4.98) | 1.94 ± 0.83 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 100/100 | 0 | 86 | 1.94 ± 1.46 (1.68) | 17.64 ± 37.54 (4.90) | 2.18 ± 0.58 (2.29) | 4.67 ± 1.35 (5.05) | 1.97 ± 0.79 (2.00) |
| right | p | 0.748 | 97/100 | 0 | 76 | 2.16 ± 2.00 (1.74) | 23.48 ± 43.51 (4.64) | 2.00 ± 0.78 (2.26) | 4.29 ± 1.78 (4.63) | 1.78 ± 0.93 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.817 | 25/25 | 0 | 22 | 1.70 ± 2.09 (1.30) | 8.51 ± 14.53 (3.82) | 2.13 ± 0.62 (2.25) | 4.54 ± 1.44 (4.47) | 1.88 ± 0.81 (1.84) |
| forward/right | p | 0.755 | 25/25 | 0 | 18 | 2.13 ± 2.61 (1.34) | 13.72 ± 17.90 (5.63) | 1.85 ± 0.83 (2.05) | 3.88 ± 1.85 (4.10) | 1.56 ± 0.98 (1.61) |
| left/left | p | 0.846 | 25/25 | 0 | 22 | 1.57 ± 0.41 (1.60) | 12.09 ± 21.50 (6.04) | 2.23 ± 0.49 (2.28) | 4.85 ± 1.20 (5.35) | 2.07 ± 0.70 (2.22) |
| left/right | p | 0.738 | 23/25 | 0 | 18 | 1.72 ± 0.57 (1.78) | 28.82 ± 49.42 (4.09) | 2.02 ± 0.71 (2.31) | 4.44 ± 1.71 (5.22) | 1.82 ± 0.92 (1.98) |
| back/left | p | 0.761 | 25/25 | 0 | 21 | 2.71 ± 1.70 (2.58) | 28.76 ± 56.44 (5.30) | 2.23 ± 0.59 (2.32) | 4.72 ± 1.31 (5.15) | 2.03 ± 0.82 (2.20) |
| back/right | p | 0.746 | 25/25 | 0 | 20 | 2.34 ± 0.69 (2.60) | 33.49 ± 58.25 (4.64) | 1.95 ± 0.85 (2.27) | 4.20 ± 1.90 (4.98) | 1.78 ± 0.93 (1.99) |
| right/left | p | 0.808 | 25/25 | 0 | 21 | 1.77 ± 0.48 (1.76) | 21.21 ± 39.09 (6.79) | 2.12 ± 0.62 (2.28) | 4.55 ± 1.40 (4.98) | 1.89 ± 0.82 (1.98) |
| right/right | p | 0.753 | 24/25 | 0 | 20 | 2.42 ± 2.82 (1.73) | 18.11 ± 34.38 (4.49) | 2.18 ± 0.68 (2.28) | 4.65 ± 1.54 (5.01) | 1.98 ± 0.84 (2.12) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.812 | 19.5 | 5.06 | 2.22 |
| p | normal | 0.744 | 21.6 | 3.89 | 1.53 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.20 | 2.26 ± 1.04 (2.15) | 3.55 | 1.35 |
| p | medium | 16 | 0.799 | 0.66 | 1.29 ± 0.24 (1.34) | 4.17 | 1.71 |
| p | strong | 126 | 0.802 | 0.66 | - | 4.95 | 2.14 |

## Notes

- p: score 0.778, 197/200 kicked, 0 fell; worst sector back (0.754).
