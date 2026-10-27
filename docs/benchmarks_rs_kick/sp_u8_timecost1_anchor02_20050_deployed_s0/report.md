# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_12-23-01_u8_timecost1_anchor02/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.781** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.05 ± 1.73 (1.72) |
| Direction error [°] | 20.06 ± 39.75 (5.76) |
| Avg ball speed [m/s] | 2.04 ± 0.68 (2.23) |
| Peak ball speed [m/s] | 4.53 ± 1.62 (5.19) |
| Distance [m] | 1.85 ± 0.86 (1.99) |
| Path length [m] | 1.86 ± 0.86 (2.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.790 | 50/50 | 0 | 41 | 1.80 ± 2.08 (1.33) | 9.99 ± 15.84 (4.14) | 1.97 ± 0.64 (2.16) | 4.35 ± 1.57 (4.33) | 1.71 ± 0.82 (1.77) |
| left | p | 0.807 | 49/50 | 0 | 41 | 1.86 ± 1.54 (1.76) | 18.84 ± 35.30 (5.81) | 2.11 ± 0.59 (2.31) | 4.73 ± 1.48 (5.43) | 1.93 ± 0.79 (2.17) |
| back | p | 0.739 | 50/50 | 0 | 40 | 2.68 ± 1.60 (2.52) | 33.25 ± 58.57 (7.41) | 2.09 ± 0.81 (2.30) | 4.56 ± 1.83 (5.19) | 1.97 ± 0.99 (2.04) |
| right | p | 0.787 | 49/50 | 0 | 41 | 1.87 ± 1.46 (1.72) | 18.10 ± 33.08 (5.02) | 2.01 ± 0.63 (2.21) | 4.50 ± 1.53 (5.33) | 1.79 ± 0.80 (1.95) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.809 | 100/100 | 0 | 86 | 1.89 ± 1.24 (1.71) | 17.75 ± 37.67 (5.76) | 2.13 ± 0.62 (2.31) | 4.72 ± 1.47 (5.40) | 1.95 ± 0.82 (2.08) |
| right | p | 0.753 | 98/100 | 0 | 77 | 2.22 ± 2.10 (1.72) | 22.42 ± 41.63 (5.73) | 1.96 ± 0.72 (2.21) | 4.34 ± 1.73 (4.53) | 1.75 ± 0.88 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.825 | 25/25 | 0 | 22 | 1.58 ± 1.60 (1.30) | 6.84 ± 10.17 (3.72) | 2.08 ± 0.60 (2.20) | 4.60 ± 1.47 (4.78) | 1.85 ± 0.77 (1.85) |
| forward/right | p | 0.755 | 25/25 | 0 | 19 | 2.01 ± 2.46 (1.34) | 13.14 ± 19.45 (5.86) | 1.86 ± 0.66 (1.96) | 4.09 ± 1.62 (4.09) | 1.56 ± 0.83 (1.56) |
| left/left | p | 0.849 | 25/25 | 0 | 22 | 1.59 ± 0.41 (1.64) | 12.27 ± 22.14 (6.01) | 2.21 ± 0.51 (2.37) | 4.96 ± 1.26 (5.54) | 2.09 ± 0.71 (2.21) |
| left/right | p | 0.764 | 24/25 | 0 | 19 | 2.14 ± 2.12 (1.89) | 25.69 ± 44.07 (4.93) | 1.99 ± 0.64 (2.22) | 4.48 ± 1.64 (5.33) | 1.77 ± 0.84 (1.95) |
| back/left | p | 0.754 | 25/25 | 0 | 21 | 2.64 ± 1.55 (2.52) | 30.63 ± 56.77 (6.57) | 2.21 ± 0.70 (2.38) | 4.79 ± 1.57 (5.46) | 2.08 ± 0.93 (2.11) |
| back/right | p | 0.724 | 25/25 | 0 | 19 | 2.72 ± 1.65 (2.54) | 35.87 ± 60.20 (7.65) | 1.98 ± 0.88 (2.26) | 4.33 ± 2.03 (5.13) | 1.85 ± 1.03 (1.99) |
| right/left | p | 0.807 | 25/25 | 0 | 21 | 1.77 ± 0.47 (1.80) | 21.28 ± 39.16 (5.72) | 2.01 ± 0.62 (2.20) | 4.50 ± 1.52 (5.38) | 1.77 ± 0.81 (1.98) |
| right/right | p | 0.767 | 24/25 | 0 | 20 | 1.98 ± 2.03 (1.68) | 14.78 ± 24.82 (4.87) | 2.01 ± 0.65 (2.23) | 4.49 ± 1.55 (4.99) | 1.81 ± 0.79 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.805 | 19.5 | 5.14 | 2.19 |
| p | normal | 0.756 | 20.6 | 3.93 | 1.51 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.715 | 0.16 | 2.29 ± 1.07 (2.23) | 3.60 | 1.33 |
| p | medium | 16 | 0.831 | 0.68 | 1.26 ± 0.24 (1.28) | 4.11 | 1.64 |
| p | strong | 126 | 0.804 | 0.67 | - | 5.02 | 2.12 |

## Notes

- p: score 0.781, 198/200 kicked, 0 fell; worst sector back (0.739).
