# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t1_stand03/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.798** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 190 |
| Weak kicks (< 0.3 m) | 4 |
| Time to kick [s] | 1.93 ± 0.70 (1.78) |
| Direction error [°] | 7.55 ± 4.41 (7.28) |
| Avg ball speed [m/s] | 1.53 ± 0.34 (1.53) |
| Peak ball speed [m/s] | 3.22 ± 0.73 (3.23) |
| Distance [m] | 0.99 ± 0.39 (0.94) |
| Path length [m] | 0.99 ± 0.39 (0.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.840 | 50/50 | 0 | 49 | 1.23 ± 0.30 (1.28) | 5.40 ± 3.65 (4.93) | 1.27 ± 0.30 (1.33) | 2.72 ± 0.61 (2.78) | 0.70 ± 0.29 (0.70) |
| left | p | 0.823 | 50/50 | 0 | 47 | 1.82 ± 0.43 (1.81) | 7.65 ± 4.99 (7.94) | 1.58 ± 0.29 (1.57) | 3.33 ± 0.64 (3.40) | 1.04 ± 0.33 (1.04) |
| back | p | 0.720 | 50/50 | 0 | 49 | 2.85 ± 0.40 (2.81) | 9.24 ± 3.31 (9.66) | 1.74 ± 0.28 (1.70) | 3.63 ± 0.65 (3.63) | 1.25 ± 0.38 (1.20) |
| right | p | 0.812 | 50/50 | 0 | 45 | 1.80 ± 0.41 (1.74) | 7.90 ± 4.58 (7.32) | 1.52 ± 0.32 (1.49) | 3.18 ± 0.69 (3.22) | 0.97 ± 0.35 (0.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.792 | 100/100 | 0 | 93 | 1.93 ± 0.72 (1.80) | 7.83 ± 4.65 (8.24) | 1.53 ± 0.35 (1.52) | 3.21 ± 0.74 (3.23) | 0.99 ± 0.40 (0.94) |
| right | p | 0.805 | 100/100 | 0 | 97 | 1.92 ± 0.68 (1.77) | 7.26 ± 4.14 (7.10) | 1.53 ± 0.34 (1.55) | 3.22 ± 0.72 (3.23) | 0.98 ± 0.38 (0.95) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 24 | 1.23 ± 0.30 (1.32) | 5.89 ± 4.32 (5.21) | 1.26 ± 0.30 (1.36) | 2.69 ± 0.62 (2.79) | 0.70 ± 0.28 (0.73) |
| forward/right | p | 0.846 | 25/25 | 0 | 25 | 1.23 ± 0.30 (1.28) | 4.90 ± 2.74 (4.23) | 1.28 ± 0.30 (1.27) | 2.74 ± 0.61 (2.77) | 0.71 ± 0.31 (0.59) |
| left/left | p | 0.813 | 25/25 | 0 | 23 | 1.71 ± 0.43 (1.80) | 8.32 ± 5.17 (8.24) | 1.54 ± 0.30 (1.48) | 3.22 ± 0.64 (3.17) | 0.99 ± 0.33 (0.90) |
| left/right | p | 0.833 | 25/25 | 0 | 24 | 1.94 ± 0.40 (1.98) | 6.99 ± 4.72 (5.79) | 1.62 ± 0.27 (1.63) | 3.45 ± 0.62 (3.59) | 1.08 ± 0.32 (1.05) |
| back/left | p | 0.710 | 25/25 | 0 | 24 | 2.88 ± 0.47 (2.80) | 9.36 ± 3.13 (9.80) | 1.73 ± 0.31 (1.69) | 3.64 ± 0.70 (3.65) | 1.25 ± 0.42 (1.25) |
| back/right | p | 0.729 | 25/25 | 0 | 25 | 2.82 ± 0.32 (2.82) | 9.13 ± 3.49 (9.51) | 1.74 ± 0.25 (1.73) | 3.63 ± 0.60 (3.61) | 1.24 ± 0.35 (1.19) |
| right/left | p | 0.812 | 25/25 | 0 | 22 | 1.91 ± 0.38 (1.86) | 7.78 ± 4.99 (8.25) | 1.58 ± 0.31 (1.57) | 3.29 ± 0.66 (3.40) | 1.03 ± 0.34 (0.96) |
| right/right | p | 0.811 | 25/25 | 0 | 23 | 1.69 ± 0.42 (1.70) | 8.02 ± 4.12 (7.30) | 1.46 ± 0.33 (1.48) | 3.08 ± 0.70 (3.05) | 0.90 ± 0.33 (0.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 6.6 | 3.54 | 1.14 |
| p | normal | 0.793 | 8.5 | 2.89 | 0.83 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.779 | 0.45 | 1.62 ± 0.57 (1.54) | 2.57 | 0.67 |
| p | medium | 16 | 0.833 | 0.81 | 0.83 ± 0.14 (0.81) | 2.69 | 0.75 |
| p | strong | 126 | 0.803 | 0.48 | - | 3.58 | 1.16 |

## Notes

- p: score 0.798, 200/200 kicked, 0 fell; worst sector back (0.720).
