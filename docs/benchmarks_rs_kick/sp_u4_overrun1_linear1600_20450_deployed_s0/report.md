# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.765** |
| Kicked / fell | 189 / 0 |
| Kicks within 15° | 159 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 1.91 ± 0.74 (1.82) |
| Direction error [°] | 18.14 ± 37.09 (4.67) |
| Avg ball speed [m/s] | 1.96 ± 0.62 (2.14) |
| Peak ball speed [m/s] | 4.49 ± 1.59 (5.12) |
| Distance [m] | 1.68 ± 0.83 (1.80) |
| Path length [m] | 1.69 ± 0.83 (1.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.772 | 46/50 | 0 | 38 | 1.36 ± 0.29 (1.39) | 9.56 ± 15.27 (3.55) | 1.91 ± 0.67 (1.90) | 4.29 ± 1.67 (3.87) | 1.60 ± 0.92 (1.37) |
| left | p | 0.799 | 48/50 | 0 | 40 | 1.78 ± 0.55 (1.89) | 19.90 ± 37.42 (4.24) | 1.97 ± 0.58 (2.20) | 4.58 ± 1.53 (5.31) | 1.71 ± 0.78 (1.91) |
| back | p | 0.692 | 47/50 | 0 | 39 | 2.66 ± 0.82 (2.70) | 27.59 ± 51.18 (7.79) | 1.97 ± 0.66 (2.20) | 4.53 ± 1.66 (5.29) | 1.73 ± 0.84 (1.97) |
| right | p | 0.797 | 48/50 | 0 | 42 | 1.83 ± 0.50 (1.84) | 15.33 ± 32.53 (3.74) | 2.00 ± 0.56 (2.09) | 4.53 ± 1.46 (5.04) | 1.68 ± 0.75 (1.66) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 97/100 | 0 | 85 | 1.90 ± 0.71 (1.84) | 16.18 ± 35.64 (4.29) | 2.04 ± 0.54 (2.20) | 4.66 ± 1.42 (5.26) | 1.77 ± 0.77 (1.86) |
| right | p | 0.732 | 92/100 | 0 | 74 | 1.93 ± 0.77 (1.82) | 20.20 ± 38.45 (4.92) | 1.88 ± 0.69 (2.11) | 4.30 ± 1.72 (4.83) | 1.60 ± 0.87 (1.67) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 24/25 | 0 | 22 | 1.36 ± 0.28 (1.40) | 8.00 ± 16.95 (2.47) | 2.08 ± 0.57 (2.13) | 4.69 ± 1.46 (4.75) | 1.79 ± 0.82 (1.85) |
| forward/right | p | 0.716 | 22/25 | 0 | 16 | 1.36 ± 0.30 (1.38) | 11.27 ± 12.98 (7.69) | 1.73 ± 0.73 (1.53) | 3.86 ± 1.78 (3.17) | 1.40 ± 0.99 (1.01) |
| left/left | p | 0.854 | 25/25 | 0 | 22 | 1.72 ± 0.49 (1.84) | 12.11 ± 21.87 (4.29) | 2.07 ± 0.46 (2.20) | 4.73 ± 1.29 (5.12) | 1.80 ± 0.70 (1.86) |
| left/right | p | 0.743 | 23/25 | 0 | 18 | 1.85 ± 0.60 (2.02) | 28.37 ± 47.60 (3.95) | 1.87 ± 0.67 (2.19) | 4.42 ± 1.74 (5.36) | 1.62 ± 0.84 (1.96) |
| back/left | p | 0.689 | 23/25 | 0 | 19 | 2.58 ± 0.83 (2.70) | 27.02 ± 51.39 (7.79) | 2.05 ± 0.49 (2.24) | 4.78 ± 1.34 (5.61) | 1.81 ± 0.74 (2.21) |
| back/right | p | 0.694 | 24/25 | 0 | 20 | 2.74 ± 0.80 (2.71) | 28.14 ± 50.96 (7.64) | 1.89 ± 0.78 (2.15) | 4.28 ± 1.88 (5.04) | 1.66 ± 0.91 (1.81) |
| right/left | p | 0.817 | 25/25 | 0 | 22 | 1.96 ± 0.51 (1.98) | 18.13 ± 39.38 (3.72) | 1.98 ± 0.60 (2.03) | 4.46 ± 1.55 (5.12) | 1.67 ± 0.80 (1.67) |
| right/right | p | 0.777 | 23/25 | 0 | 20 | 1.69 ± 0.45 (1.76) | 12.29 ± 22.47 (3.74) | 2.02 ± 0.51 (2.14) | 4.61 ± 1.36 (4.96) | 1.69 ± 0.69 (1.65) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.787 | 15.5 | 5.34 | 2.13 |
| p | normal | 0.743 | 20.7 | 3.66 | 1.25 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.704 | 0.27 | 2.04 ± 0.81 (1.90) | 3.25 | 1.02 |
| p | medium | 16 | 0.821 | 0.81 | 1.10 ± 0.22 (1.10) | 3.56 | 1.21 |
| p | strong | 126 | 0.786 | 0.69 | - | 5.17 | 2.05 |

## Notes

- p: score 0.765, 189/200 kicked, 0 fell; worst sector back (0.692).
