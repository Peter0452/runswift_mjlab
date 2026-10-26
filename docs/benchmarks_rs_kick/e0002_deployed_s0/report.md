# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_20-02-31_e0002/model_18850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.758** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 147 |
| Weak kicks (< 0.3 m) | 25 |
| Time to kick [s] | 1.95 ± 1.30 (1.80) |
| Direction error [°] | 23.16 ± 39.20 (9.48) |
| Avg ball speed [m/s] | 2.18 ± 0.87 (2.51) |
| Peak ball speed [m/s] | 4.62 ± 1.91 (5.56) |
| Distance [m] | 2.23 ± 1.18 (2.54) |
| Path length [m] | 2.24 ± 1.18 (2.57) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.786 | 50/50 | 0 | 41 | 1.73 ± 1.86 (1.39) | 11.38 ± 14.23 (6.55) | 2.09 ± 0.79 (2.21) | 4.43 ± 1.75 (4.35) | 2.01 ± 1.05 (1.85) |
| left | p | 0.770 | 48/50 | 0 | 37 | 1.74 ± 0.51 (1.88) | 20.43 ± 30.28 (9.58) | 2.27 ± 0.79 (2.53) | 4.84 ± 1.77 (5.62) | 2.37 ± 1.10 (2.76) |
| back | p | 0.701 | 50/50 | 0 | 31 | 2.60 ± 1.48 (2.55) | 40.76 ± 60.04 (12.32) | 2.07 ± 1.09 (2.70) | 4.37 ± 2.36 (5.91) | 2.23 ± 1.42 (3.05) |
| right | p | 0.774 | 49/50 | 0 | 38 | 1.72 ± 0.50 (1.78) | 19.91 ± 30.30 (8.54) | 2.31 ± 0.73 (2.60) | 4.85 ± 1.59 (5.69) | 2.31 ± 1.05 (2.74) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.785 | 100/100 | 0 | 79 | 1.78 ± 0.65 (1.80) | 23.54 ± 41.04 (8.68) | 2.21 ± 0.85 (2.53) | 4.67 ± 1.88 (5.54) | 2.25 ± 1.18 (2.53) |
| right | p | 0.731 | 97/100 | 0 | 68 | 2.12 ± 1.72 (1.80) | 22.77 ± 37.20 (10.61) | 2.16 ± 0.88 (2.50) | 4.57 ± 1.93 (5.58) | 2.20 ± 1.18 (2.54) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 23 | 1.35 ± 0.32 (1.40) | 7.75 ± 11.60 (4.73) | 2.20 ± 0.66 (2.28) | 4.65 ± 1.52 (4.40) | 2.10 ± 0.93 (1.92) |
| forward/right | p | 0.736 | 25/25 | 0 | 18 | 2.10 ± 2.56 (1.38) | 15.00 ± 15.62 (10.78) | 1.98 ± 0.88 (2.12) | 4.20 ± 1.94 (4.17) | 1.92 ± 1.15 (1.76) |
| left/left | p | 0.828 | 25/25 | 0 | 22 | 1.66 ± 0.47 (1.86) | 15.76 ± 20.96 (8.14) | 2.34 ± 0.73 (2.54) | 5.01 ± 1.63 (5.73) | 2.47 ± 1.03 (2.90) |
| left/right | p | 0.713 | 23/25 | 0 | 15 | 1.83 ± 0.54 (2.04) | 25.50 ± 37.24 (12.77) | 2.19 ± 0.84 (2.47) | 4.67 ± 1.89 (5.52) | 2.26 ± 1.17 (2.57) |
| back/left | p | 0.706 | 25/25 | 0 | 16 | 2.33 ± 0.75 (2.50) | 46.08 ± 63.60 (12.90) | 2.05 ± 1.13 (2.85) | 4.33 ± 2.45 (5.98) | 2.23 ± 1.51 (3.11) |
| back/right | p | 0.695 | 25/25 | 0 | 15 | 2.86 ± 1.91 (2.60) | 35.44 ± 55.75 (12.26) | 2.09 ± 1.05 (2.69) | 4.41 ± 2.28 (5.86) | 2.23 ± 1.33 (3.02) |
| right/left | p | 0.768 | 25/25 | 0 | 18 | 1.78 ± 0.54 (1.80) | 24.58 ± 36.04 (9.73) | 2.23 ± 0.79 (2.29) | 4.69 ± 1.73 (4.57) | 2.22 ± 1.12 (1.99) |
| right/right | p | 0.780 | 24/25 | 0 | 20 | 1.66 ± 0.45 (1.74) | 15.04 ± 21.81 (8.05) | 2.39 ± 0.65 (2.63) | 5.02 ± 1.41 (5.73) | 2.41 ± 0.97 (2.81) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.801 | 20.3 | 5.41 | 2.77 |
| p | normal | 0.714 | 26.0 | 3.83 | 1.69 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.677 | 0.19 | 2.03 ± 1.19 (2.02) | 3.23 | 1.28 |
| p | medium | 16 | 0.767 | 0.63 | 1.18 ± 0.39 (1.24) | 3.83 | 1.61 |
| p | strong | 126 | 0.794 | 0.71 | - | 5.35 | 2.73 |

## Notes

- p: score 0.758, 197/200 kicked, 0 fell; worst sector back (0.701).
