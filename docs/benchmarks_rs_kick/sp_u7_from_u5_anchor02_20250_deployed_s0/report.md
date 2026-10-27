# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.788** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.03 ± 1.78 (1.70) |
| Direction error [°] | 20.38 ± 41.68 (5.41) |
| Avg ball speed [m/s] | 2.26 ± 0.86 (2.54) |
| Peak ball speed [m/s] | 4.72 ± 1.85 (5.51) |
| Distance [m] | 2.25 ± 1.15 (2.55) |
| Path length [m] | 2.26 ± 1.15 (2.56) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.792 | 49/50 | 0 | 41 | 1.70 ± 2.08 (1.30) | 8.83 ± 13.44 (3.77) | 2.18 ± 0.81 (2.22) | 4.51 ± 1.75 (4.35) | 2.09 ± 1.04 (1.87) |
| left | p | 0.825 | 49/50 | 0 | 43 | 1.90 ± 1.49 (1.78) | 14.06 ± 29.46 (4.89) | 2.40 ± 0.72 (2.59) | 5.05 ± 1.58 (5.76) | 2.44 ± 1.03 (2.78) |
| back | p | 0.737 | 50/50 | 0 | 37 | 2.61 ± 1.92 (2.41) | 40.85 ± 64.04 (8.61) | 2.16 ± 1.06 (2.59) | 4.50 ± 2.24 (5.59) | 2.21 ± 1.38 (2.77) |
| right | p | 0.796 | 49/50 | 0 | 42 | 1.88 ± 1.40 (1.72) | 17.37 ± 33.78 (5.01) | 2.31 ± 0.77 (2.48) | 4.81 ± 1.67 (5.26) | 2.28 ± 1.08 (2.24) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.822 | 100/100 | 0 | 87 | 1.83 ± 1.15 (1.71) | 18.70 ± 41.22 (5.13) | 2.33 ± 0.80 (2.53) | 4.86 ± 1.74 (5.56) | 2.33 ± 1.11 (2.56) |
| right | p | 0.753 | 97/100 | 0 | 76 | 2.22 ± 2.24 (1.70) | 22.11 ± 42.07 (5.74) | 2.19 ± 0.90 (2.54) | 4.57 ± 1.94 (5.42) | 2.17 ± 1.19 (2.55) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 21 | 1.29 ± 0.29 (1.30) | 8.46 ± 14.01 (3.77) | 2.20 ± 0.85 (2.37) | 4.57 ± 1.86 (4.49) | 2.14 ± 1.09 (1.92) |
| forward/right | p | 0.748 | 24/25 | 0 | 20 | 2.12 ± 2.90 (1.30) | 9.21 ± 12.82 (3.63) | 2.17 ± 0.76 (2.19) | 4.44 ± 1.62 (4.29) | 2.03 ± 0.98 (1.82) |
| left/left | p | 0.884 | 25/25 | 0 | 24 | 1.63 ± 0.37 (1.68) | 7.60 ± 15.24 (3.80) | 2.53 ± 0.53 (2.65) | 5.32 ± 1.24 (5.74) | 2.60 ± 0.87 (2.95) |
| left/right | p | 0.765 | 24/25 | 0 | 19 | 2.19 ± 2.06 (1.95) | 20.80 ± 37.97 (6.28) | 2.25 ± 0.84 (2.58) | 4.78 ± 1.84 (5.77) | 2.27 ± 1.15 (2.77) |
| back/left | p | 0.752 | 25/25 | 0 | 20 | 2.64 ± 1.95 (2.42) | 38.87 ± 64.47 (8.37) | 2.25 ± 0.98 (2.70) | 4.70 ± 2.10 (5.70) | 2.32 ± 1.35 (2.84) |
| back/right | p | 0.723 | 25/25 | 0 | 17 | 2.59 ± 1.88 (2.40) | 42.82 ± 63.54 (8.77) | 2.07 ± 1.12 (2.27) | 4.30 ± 2.36 (4.48) | 2.11 ± 1.40 (1.95) |
| right/left | p | 0.815 | 25/25 | 0 | 22 | 1.78 ± 0.47 (1.76) | 19.87 ± 39.70 (5.46) | 2.34 ± 0.73 (2.44) | 4.83 ± 1.55 (5.10) | 2.28 ± 1.01 (2.24) |
| right/right | p | 0.777 | 24/25 | 0 | 20 | 1.98 ± 1.94 (1.62) | 14.76 ± 25.97 (3.99) | 2.28 ± 0.81 (2.67) | 4.78 ± 1.78 (5.75) | 2.28 ± 1.15 (2.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.815 | 18.8 | 5.60 | 2.87 |
| p | normal | 0.760 | 21.9 | 3.86 | 1.66 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.726 | 0.16 | 2.24 ± 1.12 (2.29) | 3.48 | 1.38 |
| p | medium | 16 | 0.814 | 0.64 | 1.10 ± 0.43 (1.23) | 3.59 | 1.47 |
| p | strong | 126 | 0.812 | 0.73 | - | 5.45 | 2.77 |

## Notes

- p: score 0.788, 197/200 kicked, 0 fell; worst sector back (0.737).
