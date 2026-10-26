# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.760** |
| Kicked / fell | 191 / 0 |
| Kicks within 15° | 156 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 1.89 ± 1.18 (1.76) |
| Direction error [°] | 20.98 ± 40.97 (5.61) |
| Avg ball speed [m/s] | 2.07 ± 0.82 (2.39) |
| Peak ball speed [m/s] | 4.32 ± 1.77 (5.24) |
| Distance [m] | 1.97 ± 1.06 (2.35) |
| Path length [m] | 1.97 ± 1.07 (2.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.761 | 48/50 | 0 | 40 | 1.73 ± 2.05 (1.37) | 10.77 ± 16.32 (5.18) | 1.95 ± 0.81 (1.96) | 4.02 ± 1.73 (3.88) | 1.76 ± 1.01 (1.61) |
| left | p | 0.788 | 48/50 | 0 | 39 | 1.70 ± 0.54 (1.85) | 20.69 ± 36.78 (5.34) | 2.08 ± 0.77 (2.48) | 4.41 ± 1.71 (5.38) | 1.99 ± 1.04 (2.46) |
| back | p | 0.702 | 47/50 | 0 | 36 | 2.39 ± 0.70 (2.46) | 36.35 ± 60.55 (7.17) | 2.07 ± 0.98 (2.64) | 4.33 ± 2.08 (5.62) | 2.07 ± 1.23 (2.79) |
| right | p | 0.792 | 48/50 | 0 | 41 | 1.74 ± 0.50 (1.80) | 16.44 ± 33.37 (3.88) | 2.18 ± 0.67 (2.39) | 4.54 ± 1.47 (5.32) | 2.05 ± 0.93 (2.43) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 99/100 | 0 | 83 | 1.88 ± 1.18 (1.76) | 22.00 ± 43.78 (5.24) | 2.10 ± 0.81 (2.41) | 4.38 ± 1.75 (5.36) | 2.00 ± 1.05 (2.50) |
| right | p | 0.723 | 92/100 | 0 | 73 | 1.90 ± 1.18 (1.77) | 19.89 ± 37.68 (5.74) | 2.04 ± 0.83 (2.35) | 4.26 ± 1.79 (5.03) | 1.92 ± 1.07 (2.19) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.818 | 25/25 | 0 | 23 | 1.73 ± 2.04 (1.36) | 8.06 ± 13.52 (3.70) | 2.05 ± 0.78 (2.07) | 4.22 ± 1.69 (3.88) | 1.88 ± 0.99 (1.62) |
| forward/right | p | 0.703 | 23/25 | 0 | 17 | 1.73 ± 2.05 (1.38) | 13.70 ± 18.45 (6.48) | 1.84 ± 0.83 (1.93) | 3.79 ± 1.74 (3.84) | 1.62 ± 1.02 (1.55) |
| left/left | p | 0.843 | 25/25 | 0 | 21 | 1.64 ± 0.48 (1.84) | 14.33 ± 24.25 (4.39) | 2.13 ± 0.76 (2.51) | 4.50 ± 1.67 (5.47) | 2.07 ± 1.02 (2.53) |
| left/right | p | 0.733 | 23/25 | 0 | 18 | 1.77 ± 0.59 (1.94) | 27.60 ± 45.73 (5.96) | 2.02 ± 0.78 (2.38) | 4.32 ± 1.75 (5.19) | 1.91 ± 1.05 (2.40) |
| back/left | p | 0.722 | 24/25 | 0 | 18 | 2.33 ± 0.75 (2.46) | 44.94 ± 67.93 (8.42) | 2.08 ± 0.95 (2.63) | 4.37 ± 2.02 (5.54) | 2.07 ± 1.22 (2.81) |
| back/right | p | 0.681 | 23/25 | 0 | 18 | 2.45 ± 0.64 (2.54) | 27.40 ± 50.20 (7.11) | 2.07 ± 1.02 (2.68) | 4.29 ± 2.13 (5.68) | 2.06 ± 1.24 (2.76) |
| right/left | p | 0.807 | 25/25 | 0 | 21 | 1.83 ± 0.52 (1.86) | 21.57 ± 40.39 (5.24) | 2.14 ± 0.72 (2.39) | 4.45 ± 1.57 (5.30) | 2.00 ± 0.97 (2.35) |
| right/right | p | 0.776 | 23/25 | 0 | 20 | 1.65 ± 0.46 (1.76) | 10.86 ± 22.18 (2.75) | 2.22 ± 0.61 (2.43) | 4.65 ± 1.35 (5.33) | 2.11 ± 0.89 (2.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.785 | 17.7 | 5.05 | 2.47 |
| p | normal | 0.736 | 24.2 | 3.60 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.697 | 0.22 | 2.01 ± 1.00 (1.90) | 3.14 | 1.15 |
| p | medium | 16 | 0.795 | 0.73 | 1.08 ± 0.34 (1.15) | 3.47 | 1.34 |
| p | strong | 126 | 0.785 | 0.66 | - | 4.97 | 2.41 |

## Notes

- p: score 0.760, 191/200 kicked, 0 fell; worst sector back (0.702).
