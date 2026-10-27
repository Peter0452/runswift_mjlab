# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_18-10-03_q1_overrun_linear/model_21450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.785** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 170 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 2.09 ± 1.73 (1.78) |
| Direction error [°] | 15.40 ± 33.39 (5.38) |
| Avg ball speed [m/s] | 1.92 ± 0.58 (2.06) |
| Peak ball speed [m/s] | 4.46 ± 1.39 (4.80) |
| Distance [m] | 1.77 ± 0.77 (1.79) |
| Path length [m] | 1.78 ± 0.77 (1.81) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 43 | 1.68 ± 1.86 (1.36) | 8.47 ± 10.81 (5.10) | 1.82 ± 0.59 (1.94) | 4.20 ± 1.46 (4.12) | 1.61 ± 0.78 (1.50) |
| left | p | 0.811 | 50/50 | 0 | 42 | 2.10 ± 2.02 (1.81) | 17.33 ± 31.95 (5.51) | 1.91 ± 0.65 (2.10) | 4.51 ± 1.54 (5.01) | 1.81 ± 0.81 (1.91) |
| back | p | 0.726 | 47/50 | 0 | 41 | 2.56 ± 1.25 (2.52) | 25.14 ± 53.54 (5.28) | 1.98 ± 0.57 (2.04) | 4.56 ± 1.37 (4.74) | 1.85 ± 0.81 (1.82) |
| right | p | 0.797 | 49/50 | 0 | 44 | 2.06 ± 1.55 (1.82) | 11.17 ± 19.70 (5.50) | 1.98 ± 0.47 (2.08) | 4.58 ± 1.11 (4.98) | 1.81 ± 0.65 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 99/100 | 0 | 87 | 1.84 ± 0.81 (1.72) | 14.02 ± 31.40 (5.11) | 1.94 ± 0.56 (2.09) | 4.52 ± 1.35 (4.94) | 1.80 ± 0.76 (1.79) |
| right | p | 0.759 | 97/100 | 0 | 83 | 2.35 ± 2.29 (1.84) | 16.81 ± 35.25 (5.94) | 1.90 ± 0.60 (2.02) | 4.41 ± 1.42 (4.73) | 1.74 ± 0.78 (1.80) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 23 | 1.31 ± 0.30 (1.34) | 7.32 ± 10.52 (4.72) | 1.90 ± 0.59 (2.09) | 4.39 ± 1.47 (4.22) | 1.73 ± 0.81 (1.71) |
| forward/right | p | 0.770 | 25/25 | 0 | 20 | 2.05 ± 2.55 (1.38) | 9.61 ± 10.98 (5.83) | 1.74 ± 0.59 (1.77) | 4.02 ± 1.42 (3.79) | 1.49 ± 0.74 (1.40) |
| left/left | p | 0.837 | 25/25 | 0 | 21 | 1.57 ± 0.41 (1.70) | 12.59 ± 20.70 (4.40) | 1.87 ± 0.61 (2.04) | 4.41 ± 1.50 (4.80) | 1.73 ± 0.74 (1.73) |
| left/right | p | 0.785 | 25/25 | 0 | 21 | 2.62 ± 2.73 (2.00) | 22.06 ± 39.60 (6.40) | 1.95 ± 0.68 (2.25) | 4.61 ± 1.57 (5.32) | 1.88 ± 0.86 (2.15) |
| back/left | p | 0.760 | 24/25 | 0 | 21 | 2.40 ± 0.69 (2.52) | 23.75 ± 52.99 (5.20) | 2.05 ± 0.52 (2.07) | 4.71 ± 1.23 (5.09) | 1.93 ± 0.81 (1.83) |
| back/right | p | 0.693 | 23/25 | 0 | 20 | 2.73 ± 1.63 (2.52) | 26.60 ± 54.07 (7.29) | 1.90 ± 0.62 (2.00) | 4.41 ± 1.48 (4.73) | 1.77 ± 0.80 (1.82) |
| right/left | p | 0.807 | 25/25 | 0 | 22 | 2.11 ± 1.08 (1.90) | 12.80 ± 23.04 (5.50) | 1.96 ± 0.48 (2.18) | 4.56 ± 1.13 (5.00) | 1.80 ± 0.65 (2.02) |
| right/right | p | 0.788 | 24/25 | 0 | 22 | 2.02 ± 1.92 (1.68) | 9.47 ± 15.29 (5.25) | 2.01 ± 0.45 (2.05) | 4.60 ± 1.09 (4.83) | 1.82 ± 0.65 (1.79) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.816 | 12.1 | 5.11 | 2.12 |
| p | normal | 0.753 | 18.7 | 3.83 | 1.42 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.706 | 0.20 | 2.13 ± 0.92 (1.99) | 3.39 | 1.15 |
| p | medium | 16 | 0.844 | 0.75 | 1.20 ± 0.17 (1.25) | 3.92 | 1.48 |
| p | strong | 126 | 0.813 | 0.67 | - | 5.03 | 2.09 |

## Notes

- p: score 0.785, 196/200 kicked, 0 fell; worst sector back (0.726).
