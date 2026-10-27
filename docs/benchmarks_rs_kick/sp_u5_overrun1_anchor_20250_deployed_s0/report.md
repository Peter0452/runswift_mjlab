# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.08 ± 1.74 (1.74) |
| Direction error [°] | 17.47 ± 36.00 (5.12) |
| Avg ball speed [m/s] | 2.01 ± 0.62 (2.18) |
| Peak ball speed [m/s] | 4.45 ± 1.51 (4.93) |
| Distance [m] | 1.72 ± 0.79 (1.77) |
| Path length [m] | 1.73 ± 0.79 (1.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.793 | 50/50 | 0 | 42 | 1.79 ± 2.03 (1.32) | 9.59 ± 13.46 (4.82) | 1.90 ± 0.73 (2.03) | 4.16 ± 1.74 (4.11) | 1.59 ± 0.88 (1.55) |
| left | p | 0.802 | 49/50 | 0 | 43 | 1.85 ± 1.41 (1.74) | 18.20 ± 33.98 (5.59) | 2.04 ± 0.59 (2.19) | 4.56 ± 1.46 (5.08) | 1.76 ± 0.78 (1.88) |
| back | p | 0.721 | 48/50 | 0 | 42 | 2.83 ± 1.89 (2.61) | 24.97 ± 51.37 (6.20) | 2.10 ± 0.51 (2.20) | 4.62 ± 1.26 (5.00) | 1.81 ± 0.66 (1.80) |
| right | p | 0.794 | 49/50 | 0 | 41 | 1.86 ± 1.30 (1.74) | 17.43 ± 33.79 (3.81) | 2.01 ± 0.61 (2.12) | 4.48 ± 1.50 (4.97) | 1.71 ± 0.79 (1.71) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.806 | 100/100 | 0 | 88 | 1.94 ± 1.42 (1.72) | 17.69 ± 38.18 (5.15) | 2.05 ± 0.56 (2.19) | 4.54 ± 1.37 (4.96) | 1.76 ± 0.74 (1.79) |
| right | p | 0.749 | 96/100 | 0 | 80 | 2.23 ± 2.01 (1.76) | 17.25 ± 33.58 (5.09) | 1.97 ± 0.67 (2.16) | 4.36 ± 1.64 (4.89) | 1.68 ± 0.83 (1.75) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.816 | 25/25 | 0 | 23 | 1.60 ± 1.65 (1.30) | 7.47 ± 10.34 (3.11) | 2.04 ± 0.62 (2.22) | 4.47 ± 1.50 (4.36) | 1.75 ± 0.77 (1.80) |
| forward/right | p | 0.771 | 25/25 | 0 | 19 | 1.99 ± 2.34 (1.34) | 11.71 ± 15.71 (5.30) | 1.77 ± 0.79 (1.77) | 3.86 ± 1.89 (3.69) | 1.44 ± 0.95 (1.22) |
| left/left | p | 0.845 | 25/25 | 0 | 23 | 1.60 ± 0.41 (1.66) | 12.34 ± 20.69 (5.83) | 2.10 ± 0.51 (2.18) | 4.69 ± 1.28 (5.08) | 1.85 ± 0.71 (1.88) |
| left/right | p | 0.759 | 24/25 | 0 | 20 | 2.12 ± 1.93 (1.87) | 24.31 ± 42.87 (5.23) | 1.97 ± 0.65 (2.19) | 4.42 ± 1.62 (5.04) | 1.67 ± 0.84 (1.82) |
| back/left | p | 0.747 | 25/25 | 0 | 21 | 2.77 ± 1.99 (2.60) | 30.86 ± 58.25 (6.10) | 2.09 ± 0.51 (2.20) | 4.57 ± 1.25 (4.78) | 1.79 ± 0.72 (1.78) |
| back/right | p | 0.695 | 23/25 | 0 | 21 | 2.90 ± 1.78 (2.66) | 18.58 ± 41.71 (6.31) | 2.11 ± 0.51 (2.21) | 4.68 ± 1.27 (5.09) | 1.83 ± 0.60 (1.92) |
| right/left | p | 0.817 | 25/25 | 0 | 21 | 1.78 ± 0.48 (1.84) | 20.08 ± 39.89 (3.81) | 1.99 ± 0.57 (2.10) | 4.42 ± 1.42 (4.97) | 1.64 ± 0.73 (1.68) |
| right/right | p | 0.771 | 24/25 | 0 | 20 | 1.94 ± 1.78 (1.61) | 14.67 ± 25.66 (3.95) | 2.04 ± 0.65 (2.13) | 4.53 ± 1.57 (4.93) | 1.78 ± 0.84 (1.72) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.794 | 15.1 | 5.14 | 2.07 |
| p | normal | 0.761 | 19.7 | 3.79 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.17 | 2.17 ± 0.98 (2.10) | 3.43 | 1.20 |
| p | medium | 16 | 0.848 | 0.74 | 1.21 ± 0.22 (1.22) | 3.94 | 1.47 |
| p | strong | 126 | 0.797 | 0.67 | - | 5.00 | 2.00 |

## Notes

- p: score 0.778, 196/200 kicked, 0 fell; worst sector back (0.721).
