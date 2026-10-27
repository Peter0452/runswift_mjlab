# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-46-54_u4b_u4_bhball/model_21000.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.833** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 186 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.87 ± 0.57 (1.78) |
| Direction error [°] | 8.20 ± 12.15 (6.28) |
| Avg ball speed [m/s] | 2.56 ± 0.56 (2.71) |
| Peak ball speed [m/s] | 5.28 ± 1.29 (5.88) |
| Distance [m] | 2.58 ± 0.91 (2.99) |
| Path length [m] | 2.59 ± 0.91 (3.01) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.858 | 50/50 | 0 | 48 | 1.32 ± 0.26 (1.33) | 5.33 ± 8.11 (3.73) | 2.37 ± 0.57 (2.45) | 4.91 ± 1.32 (5.44) | 2.29 ± 0.87 (2.43) |
| left | p | 0.865 | 50/50 | 0 | 46 | 1.78 ± 0.36 (1.78) | 7.45 ± 4.20 (6.96) | 2.72 ± 0.45 (2.91) | 5.60 ± 1.07 (6.09) | 2.80 ± 0.81 (3.19) |
| back | p | 0.775 | 50/50 | 0 | 46 | 2.60 ± 0.33 (2.56) | 12.60 ± 21.31 (8.86) | 2.60 ± 0.67 (2.81) | 5.37 ± 1.50 (6.04) | 2.71 ± 1.01 (3.16) |
| right | p | 0.834 | 50/50 | 0 | 46 | 1.79 ± 0.38 (1.73) | 7.41 ± 4.90 (5.77) | 2.56 ± 0.47 (2.65) | 5.25 ± 1.11 (5.74) | 2.54 ± 0.84 (2.86) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.831 | 100/100 | 0 | 93 | 1.89 ± 0.59 (1.78) | 7.98 ± 8.18 (6.15) | 2.55 ± 0.59 (2.69) | 5.25 ± 1.33 (5.88) | 2.56 ± 0.92 (2.96) |
| right | p | 0.835 | 100/100 | 0 | 93 | 1.86 ± 0.55 (1.74) | 8.41 ± 15.11 (6.49) | 2.58 ± 0.53 (2.78) | 5.32 ± 1.24 (5.91) | 2.60 ± 0.89 (3.01) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.859 | 25/25 | 0 | 23 | 1.34 ± 0.24 (1.32) | 6.39 ± 11.01 (2.96) | 2.34 ± 0.65 (2.41) | 4.86 ± 1.50 (5.33) | 2.28 ± 0.96 (2.34) |
| forward/right | p | 0.857 | 25/25 | 0 | 25 | 1.31 ± 0.27 (1.34) | 4.27 ± 2.82 (4.41) | 2.41 ± 0.47 (2.52) | 4.95 ± 1.12 (5.63) | 2.29 ± 0.77 (2.58) |
| left/left | p | 0.859 | 25/25 | 0 | 23 | 1.66 ± 0.36 (1.78) | 7.60 ± 4.24 (7.08) | 2.68 ± 0.45 (2.81) | 5.45 ± 1.05 (6.05) | 2.69 ± 0.79 (3.11) |
| left/right | p | 0.870 | 25/25 | 0 | 23 | 1.90 ± 0.33 (1.98) | 7.30 ± 4.15 (6.65) | 2.76 ± 0.44 (2.93) | 5.75 ± 1.06 (6.36) | 2.91 ± 0.81 (3.26) |
| back/left | p | 0.776 | 25/25 | 0 | 24 | 2.64 ± 0.38 (2.56) | 10.00 ± 9.56 (8.81) | 2.60 ± 0.68 (2.82) | 5.39 ± 1.55 (6.01) | 2.74 ± 1.05 (3.14) |
| back/right | p | 0.775 | 25/25 | 0 | 22 | 2.56 ± 0.26 (2.56) | 15.20 ± 28.35 (9.68) | 2.60 ± 0.65 (2.79) | 5.35 ± 1.44 (6.08) | 2.69 ± 0.98 (3.18) |
| right/left | p | 0.831 | 25/25 | 0 | 23 | 1.90 ± 0.37 (1.80) | 7.92 ± 5.52 (5.87) | 2.57 ± 0.47 (2.60) | 5.29 ± 1.07 (5.65) | 2.54 ± 0.79 (2.84) |
| right/right | p | 0.837 | 25/25 | 0 | 23 | 1.69 ± 0.35 (1.72) | 6.89 ± 4.13 (5.66) | 2.55 ± 0.48 (2.68) | 5.21 ± 1.15 (5.81) | 2.53 ± 0.88 (2.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.873 | 7.7 | 6.16 | 3.21 |
| p | normal | 0.792 | 8.7 | 4.41 | 1.96 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.742 | 0.09 | 2.36 ± 0.89 (2.32) | 3.69 | 1.45 |
| p | medium | 16 | 0.875 | 0.78 | 1.22 ± 0.12 (1.22) | 3.97 | 1.59 |
| p | strong | 126 | 0.869 | 0.82 | - | 6.18 | 3.23 |

## Notes

- p: score 0.833, 200/200 kicked, 0 fell; worst sector back (0.775).
