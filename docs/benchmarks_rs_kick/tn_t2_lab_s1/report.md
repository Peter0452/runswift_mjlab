# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t2_control_s7/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.829** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.55 ± 0.55 (1.42) |
| Direction error [°] | 6.57 ± 4.02 (6.67) |
| Avg ball speed [m/s] | 1.71 ± 0.37 (1.71) |
| Peak ball speed [m/s] | 3.67 ± 0.85 (3.61) |
| Distance [m] | 1.27 ± 0.48 (1.21) |
| Path length [m] | 1.28 ± 0.48 (1.22) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.835 | 50/50 | 0 | 49 | 0.99 ± 0.25 (1.06) | 5.75 ± 3.56 (5.34) | 1.49 ± 0.36 (1.44) | 3.22 ± 0.80 (3.14) | 0.99 ± 0.43 (0.88) |
| left | p | 0.836 | 50/50 | 0 | 47 | 1.47 ± 0.35 (1.41) | 7.16 ± 4.27 (7.37) | 1.66 ± 0.39 (1.66) | 3.56 ± 0.89 (3.50) | 1.21 ± 0.48 (1.16) |
| back | p | 0.814 | 50/50 | 0 | 50 | 2.26 ± 0.31 (2.21) | 7.14 ± 2.89 (7.55) | 1.94 ± 0.24 (2.00) | 4.17 ± 0.57 (4.33) | 1.56 ± 0.35 (1.61) |
| right | p | 0.829 | 50/50 | 0 | 47 | 1.47 ± 0.34 (1.43) | 6.23 ± 4.88 (5.03) | 1.75 ± 0.34 (1.70) | 3.73 ± 0.79 (3.55) | 1.31 ± 0.47 (1.19) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.821 | 100/100 | 0 | 94 | 1.54 ± 0.55 (1.43) | 6.83 ± 4.33 (6.70) | 1.69 ± 0.39 (1.71) | 3.63 ± 0.88 (3.61) | 1.25 ± 0.49 (1.20) |
| right | p | 0.836 | 100/100 | 0 | 99 | 1.55 ± 0.56 (1.42) | 6.30 ± 3.66 (6.58) | 1.73 ± 0.36 (1.71) | 3.71 ± 0.81 (3.66) | 1.29 ± 0.46 (1.23) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.830 | 25/25 | 0 | 24 | 0.97 ± 0.25 (1.00) | 6.42 ± 4.27 (5.97) | 1.44 ± 0.31 (1.40) | 3.12 ± 0.70 (3.00) | 0.94 ± 0.36 (0.86) |
| forward/right | p | 0.841 | 25/25 | 0 | 25 | 1.00 ± 0.24 (1.08) | 5.08 ± 2.51 (4.62) | 1.54 ± 0.40 (1.49) | 3.32 ± 0.87 (3.19) | 1.04 ± 0.48 (0.89) |
| left/left | p | 0.825 | 25/25 | 0 | 22 | 1.40 ± 0.35 (1.34) | 8.07 ± 4.71 (8.48) | 1.61 ± 0.46 (1.73) | 3.46 ± 1.04 (3.73) | 1.15 ± 0.52 (1.31) |
| left/right | p | 0.847 | 25/25 | 0 | 25 | 1.54 ± 0.34 (1.56) | 6.24 ± 3.55 (6.97) | 1.71 ± 0.30 (1.64) | 3.67 ± 0.70 (3.43) | 1.28 ± 0.42 (1.12) |
| back/left | p | 0.809 | 25/25 | 0 | 25 | 2.25 ± 0.24 (2.26) | 7.21 ± 3.12 (7.92) | 1.91 ± 0.25 (1.99) | 4.10 ± 0.61 (4.31) | 1.52 ± 0.36 (1.61) |
| back/right | p | 0.818 | 25/25 | 0 | 25 | 2.26 ± 0.37 (2.18) | 7.08 ± 2.65 (7.41) | 1.98 ± 0.22 (2.01) | 4.24 ± 0.52 (4.35) | 1.61 ± 0.32 (1.62) |
| right/left | p | 0.821 | 25/25 | 0 | 23 | 1.55 ± 0.33 (1.48) | 5.63 ± 4.66 (4.45) | 1.82 ± 0.34 (1.71) | 3.86 ± 0.78 (3.61) | 1.39 ± 0.48 (1.19) |
| right/right | p | 0.838 | 25/25 | 0 | 24 | 1.38 ± 0.33 (1.38) | 6.82 ± 5.02 (6.12) | 1.69 ± 0.33 (1.63) | 3.60 ± 0.78 (3.37) | 1.22 ± 0.43 (1.04) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.833 | 6.5 | 3.88 | 1.38 |
| p | normal | 0.824 | 6.7 | 3.46 | 1.16 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.789 | 0.28 | 1.95 ± 0.62 (1.91) | 3.06 | 0.93 |
| p | medium | 20 | 0.886 | 0.84 | 1.05 ± 0.20 (1.08) | 3.37 | 1.10 |
| p | strong | 126 | 0.837 | 0.53 | - | 3.98 | 1.44 |

## Notes

- p: score 0.829, 200/200 kicked, 0 fell; worst sector back (0.814).
