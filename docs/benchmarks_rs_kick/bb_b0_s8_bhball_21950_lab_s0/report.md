# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_21950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.54 ± 0.52 (1.46) |
| Direction error [°] | 5.82 ± 3.78 (5.24) |
| Avg ball speed [m/s] | 1.73 ± 0.33 (1.86) |
| Peak ball speed [m/s] | 3.87 ± 0.82 (4.19) |
| Distance [m] | 1.30 ± 0.45 (1.36) |
| Path length [m] | 1.31 ± 0.45 (1.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.847 | 50/50 | 0 | 49 | 1.02 ± 0.23 (1.03) | 4.77 ± 3.43 (3.60) | 1.49 ± 0.34 (1.42) | 3.27 ± 0.78 (3.08) | 0.98 ± 0.43 (0.86) |
| left | p | 0.857 | 50/50 | 0 | 50 | 1.47 ± 0.34 (1.49) | 5.74 ± 3.80 (4.81) | 1.82 ± 0.30 (1.91) | 4.11 ± 0.70 (4.37) | 1.43 ± 0.41 (1.45) |
| back | p | 0.834 | 50/50 | 0 | 50 | 2.19 ± 0.27 (2.15) | 6.40 ± 3.10 (6.50) | 1.88 ± 0.22 (2.00) | 4.23 ± 0.64 (4.59) | 1.51 ± 0.36 (1.69) |
| right | p | 0.837 | 50/50 | 0 | 48 | 1.47 ± 0.33 (1.42) | 6.37 ± 4.43 (5.45) | 1.73 ± 0.31 (1.87) | 3.88 ± 0.80 (4.27) | 1.29 ± 0.41 (1.32) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.54 ± 0.52 (1.47) | 5.85 ± 3.71 (5.79) | 1.74 ± 0.34 (1.86) | 3.90 ± 0.82 (4.21) | 1.31 ± 0.46 (1.39) |
| right | p | 0.844 | 100/100 | 0 | 98 | 1.53 ± 0.51 (1.46) | 5.79 ± 3.84 (4.89) | 1.72 ± 0.33 (1.83) | 3.85 ± 0.82 (4.09) | 1.29 ± 0.44 (1.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 25 | 1.02 ± 0.23 (1.06) | 4.77 ± 2.84 (3.74) | 1.53 ± 0.33 (1.44) | 3.35 ± 0.74 (3.11) | 1.02 ± 0.42 (0.91) |
| forward/right | p | 0.846 | 25/25 | 0 | 24 | 1.01 ± 0.22 (1.02) | 4.78 ± 3.93 (2.99) | 1.45 ± 0.35 (1.41) | 3.19 ± 0.81 (3.06) | 0.93 ± 0.43 (0.84) |
| left/left | p | 0.849 | 25/25 | 0 | 25 | 1.37 ± 0.33 (1.44) | 6.03 ± 4.13 (4.19) | 1.74 ± 0.35 (1.87) | 3.94 ± 0.76 (4.32) | 1.32 ± 0.43 (1.41) |
| left/right | p | 0.864 | 25/25 | 0 | 25 | 1.57 ± 0.32 (1.58) | 5.46 ± 3.42 (4.88) | 1.89 ± 0.23 (1.94) | 4.27 ± 0.59 (4.48) | 1.53 ± 0.35 (1.55) |
| back/left | p | 0.831 | 25/25 | 0 | 25 | 2.21 ± 0.27 (2.16) | 6.54 ± 2.95 (6.75) | 1.89 ± 0.21 (2.00) | 4.25 ± 0.60 (4.61) | 1.53 ± 0.37 (1.75) |
| back/right | p | 0.837 | 25/25 | 0 | 25 | 2.18 ± 0.26 (2.14) | 6.26 ± 3.23 (5.99) | 1.87 ± 0.24 (2.00) | 4.20 ± 0.67 (4.54) | 1.49 ± 0.35 (1.65) |
| right/left | p | 0.847 | 25/25 | 0 | 24 | 1.56 ± 0.31 (1.56) | 6.07 ± 4.43 (5.68) | 1.78 ± 0.33 (1.92) | 4.04 ± 0.88 (4.51) | 1.39 ± 0.45 (1.49) |
| right/right | p | 0.828 | 25/25 | 0 | 24 | 1.37 ± 0.33 (1.40) | 6.67 ± 4.40 (5.07) | 1.67 ± 0.27 (1.62) | 3.71 ± 0.68 (3.53) | 1.20 ± 0.34 (1.16) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.855 | 5.7 | 4.32 | 1.53 |
| p | normal | 0.833 | 6.0 | 3.43 | 1.07 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.803 | 0.31 | 1.90 ± 0.62 (1.77) | 3.02 | 0.86 |
| p | medium | 16 | 0.894 | 0.86 | 0.96 ± 0.19 (1.02) | 3.11 | 0.91 |
| p | strong | 126 | 0.856 | 0.58 | - | 4.36 | 1.55 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector back (0.834).
