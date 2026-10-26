# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t2_control_s7/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.829** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 6 |
| Time to kick [s] | 1.55 ± 0.53 (1.46) |
| Direction error [°] | 6.65 ± 4.19 (6.21) |
| Avg ball speed [m/s] | 1.61 ± 0.39 (1.65) |
| Peak ball speed [m/s] | 3.46 ± 0.87 (3.45) |
| Distance [m] | 1.12 ± 0.46 (1.11) |
| Path length [m] | 1.12 ± 0.46 (1.11) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.834 | 50/50 | 0 | 48 | 1.01 ± 0.22 (1.02) | 5.80 ± 4.24 (4.43) | 1.27 ± 0.40 (1.20) | 2.71 ± 0.88 (2.59) | 0.73 ± 0.43 (0.61) |
| left | p | 0.850 | 50/50 | 0 | 48 | 1.48 ± 0.33 (1.50) | 5.93 ± 4.44 (5.00) | 1.69 ± 0.31 (1.67) | 3.66 ± 0.71 (3.70) | 1.21 ± 0.38 (1.24) |
| back | p | 0.809 | 50/50 | 0 | 49 | 2.25 ± 0.26 (2.22) | 7.67 ± 3.33 (7.82) | 1.81 ± 0.26 (1.76) | 3.91 ± 0.63 (3.75) | 1.37 ± 0.37 (1.29) |
| right | p | 0.824 | 50/50 | 0 | 48 | 1.48 ± 0.33 (1.44) | 7.19 ± 4.36 (7.65) | 1.66 ± 0.32 (1.76) | 3.54 ± 0.75 (3.70) | 1.15 ± 0.39 (1.25) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.822 | 100/100 | 0 | 97 | 1.56 ± 0.54 (1.50) | 6.86 ± 4.17 (6.21) | 1.61 ± 0.36 (1.65) | 3.46 ± 0.81 (3.45) | 1.12 ± 0.44 (1.13) |
| right | p | 0.837 | 100/100 | 0 | 96 | 1.55 ± 0.53 (1.46) | 6.44 ± 4.21 (6.19) | 1.61 ± 0.41 (1.64) | 3.45 ± 0.93 (3.48) | 1.11 ± 0.48 (1.10) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 24 | 1.01 ± 0.22 (1.06) | 6.08 ± 4.33 (4.62) | 1.28 ± 0.37 (1.21) | 2.74 ± 0.78 (2.60) | 0.74 ± 0.40 (0.62) |
| forward/right | p | 0.848 | 25/25 | 0 | 24 | 1.00 ± 0.22 (1.02) | 5.52 ± 4.14 (3.88) | 1.26 ± 0.44 (1.17) | 2.69 ± 0.96 (2.36) | 0.73 ± 0.45 (0.54) |
| left/left | p | 0.836 | 25/25 | 0 | 24 | 1.39 ± 0.34 (1.44) | 6.43 ± 4.88 (4.93) | 1.58 ± 0.26 (1.62) | 3.42 ± 0.59 (3.43) | 1.08 ± 0.32 (1.15) |
| left/right | p | 0.865 | 25/25 | 0 | 24 | 1.57 ± 0.30 (1.58) | 5.43 ± 3.88 (5.07) | 1.80 ± 0.33 (1.88) | 3.90 ± 0.73 (4.08) | 1.34 ± 0.39 (1.40) |
| back/left | p | 0.801 | 25/25 | 0 | 24 | 2.26 ± 0.27 (2.18) | 8.37 ± 3.26 (8.49) | 1.82 ± 0.25 (1.79) | 3.92 ± 0.59 (3.92) | 1.39 ± 0.35 (1.40) |
| back/right | p | 0.818 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.24) | 6.96 ± 3.24 (7.30) | 1.80 ± 0.28 (1.74) | 3.89 ± 0.67 (3.69) | 1.35 ± 0.40 (1.28) |
| right/left | p | 0.832 | 25/25 | 0 | 25 | 1.56 ± 0.31 (1.54) | 6.54 ± 3.64 (6.07) | 1.75 ± 0.30 (1.84) | 3.77 ± 0.71 (4.08) | 1.27 ± 0.38 (1.33) |
| right/right | p | 0.816 | 25/25 | 0 | 23 | 1.39 ± 0.34 (1.40) | 7.83 ± 4.90 (7.71) | 1.57 ± 0.32 (1.59) | 3.31 ± 0.72 (3.27) | 1.04 ± 0.36 (1.03) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.831 | 6.5 | 3.75 | 1.25 |
| p | normal | 0.828 | 6.8 | 3.16 | 0.98 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.807 | 0.39 | 1.77 ± 0.67 (1.65) | 2.82 | 0.81 |
| p | medium | 16 | 0.877 | 0.85 | 0.92 ± 0.18 (0.96) | 3.00 | 0.90 |
| p | strong | 126 | 0.834 | 0.51 | - | 3.81 | 1.29 |

## Notes

- p: score 0.829, 200/200 kicked, 0 fell; worst sector back (0.809).
