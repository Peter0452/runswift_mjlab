# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t1_stand03/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.788** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 179 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.91 ± 0.70 (1.75) |
| Direction error [°] | 9.17 ± 4.55 (9.40) |
| Avg ball speed [m/s] | 1.75 ± 0.35 (1.74) |
| Peak ball speed [m/s] | 3.67 ± 0.76 (3.66) |
| Distance [m] | 1.32 ± 0.45 (1.25) |
| Path length [m] | 1.32 ± 0.46 (1.26) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.834 | 50/50 | 0 | 49 | 1.22 ± 0.31 (1.23) | 6.69 ± 3.95 (6.50) | 1.54 ± 0.32 (1.57) | 3.31 ± 0.70 (3.40) | 1.07 ± 0.38 (1.06) |
| left | p | 0.807 | 50/50 | 0 | 42 | 1.81 ± 0.42 (1.70) | 9.61 ± 4.92 (9.42) | 1.75 ± 0.30 (1.76) | 3.65 ± 0.66 (3.58) | 1.30 ± 0.39 (1.25) |
| back | p | 0.719 | 50/50 | 0 | 47 | 2.84 ± 0.36 (2.80) | 10.25 ± 3.07 (10.36) | 1.94 ± 0.28 (1.98) | 4.07 ± 0.67 (4.25) | 1.57 ± 0.42 (1.61) |
| right | p | 0.790 | 50/50 | 0 | 41 | 1.78 ± 0.42 (1.72) | 10.12 ± 5.03 (10.31) | 1.76 ± 0.35 (1.76) | 3.66 ± 0.81 (3.52) | 1.32 ± 0.47 (1.28) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.780 | 100/100 | 0 | 88 | 1.91 ± 0.70 (1.72) | 9.30 ± 4.70 (9.24) | 1.76 ± 0.36 (1.77) | 3.71 ± 0.78 (3.70) | 1.34 ± 0.47 (1.27) |
| right | p | 0.795 | 100/100 | 0 | 91 | 1.91 ± 0.70 (1.80) | 9.03 ± 4.40 (9.41) | 1.73 ± 0.34 (1.72) | 3.63 ± 0.74 (3.60) | 1.29 ± 0.44 (1.24) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.830 | 25/25 | 0 | 25 | 1.20 ± 0.32 (1.14) | 6.85 ± 3.26 (7.73) | 1.54 ± 0.33 (1.52) | 3.31 ± 0.71 (3.33) | 1.08 ± 0.39 (1.13) |
| forward/right | p | 0.838 | 25/25 | 0 | 24 | 1.23 ± 0.30 (1.24) | 6.52 ± 4.52 (5.58) | 1.54 ± 0.32 (1.60) | 3.30 ± 0.68 (3.42) | 1.07 ± 0.38 (1.05) |
| left/left | p | 0.795 | 25/25 | 0 | 19 | 1.71 ± 0.39 (1.64) | 10.58 ± 5.46 (12.24) | 1.74 ± 0.30 (1.77) | 3.64 ± 0.65 (3.50) | 1.29 ± 0.36 (1.23) |
| left/right | p | 0.819 | 25/25 | 0 | 23 | 1.91 ± 0.44 (1.86) | 8.65 ± 4.10 (9.35) | 1.75 ± 0.31 (1.76) | 3.66 ± 0.67 (3.72) | 1.31 ± 0.42 (1.26) |
| back/left | p | 0.712 | 25/25 | 0 | 23 | 2.84 ± 0.34 (2.82) | 10.41 ± 2.96 (10.20) | 1.96 ± 0.31 (1.98) | 4.11 ± 0.72 (4.27) | 1.61 ± 0.45 (1.74) |
| back/right | p | 0.727 | 25/25 | 0 | 24 | 2.83 ± 0.38 (2.78) | 10.09 ± 3.16 (10.45) | 1.93 ± 0.25 (1.99) | 4.03 ± 0.61 (4.25) | 1.54 ± 0.38 (1.58) |
| right/left | p | 0.783 | 25/25 | 0 | 21 | 1.89 ± 0.43 (1.84) | 9.37 ± 5.50 (8.76) | 1.81 ± 0.35 (1.77) | 3.77 ± 0.81 (3.80) | 1.38 ± 0.49 (1.45) |
| right/right | p | 0.798 | 25/25 | 0 | 20 | 1.67 ± 0.38 (1.70) | 10.88 ± 4.40 (10.48) | 1.71 ± 0.34 (1.75) | 3.55 ± 0.79 (3.32) | 1.26 ± 0.45 (1.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.795 | 8.5 | 4.05 | 1.53 |
| p | normal | 0.780 | 9.8 | 3.29 | 1.10 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.752 | 0.33 | 1.85 ± 0.59 (1.77) | 2.89 | 0.87 |
| p | medium | 20 | 0.850 | 0.89 | 0.97 ± 0.12 (0.96) | 3.10 | 0.98 |
| p | strong | 126 | 0.793 | 0.55 | - | 4.10 | 1.56 |

## Notes

- p: score 0.788, 200/200 kicked, 0 fell; worst sector back (0.719).
