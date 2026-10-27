# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-08-39_u2_aim_sigma02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.827** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.61 ± 0.54 (1.52) |
| Direction error [°] | 6.74 ± 11.56 (4.91) |
| Avg ball speed [m/s] | 1.91 ± 0.40 (2.01) |
| Peak ball speed [m/s] | 4.05 ± 0.87 (4.24) |
| Distance [m] | 1.54 ± 0.52 (1.60) |
| Path length [m] | 1.55 ± 0.52 (1.61) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.823 | 50/50 | 0 | 48 | 1.05 ± 0.24 (1.10) | 5.52 ± 4.22 (4.22) | 1.55 ± 0.42 (1.46) | 3.24 ± 0.87 (3.02) | 1.06 ± 0.49 (0.88) |
| left | p | 0.850 | 50/50 | 0 | 48 | 1.55 ± 0.35 (1.57) | 5.73 ± 4.21 (4.34) | 2.02 ± 0.29 (2.08) | 4.32 ± 0.66 (4.51) | 1.69 ± 0.41 (1.76) |
| back | p | 0.811 | 50/50 | 0 | 47 | 2.29 ± 0.26 (2.26) | 9.59 ± 21.71 (6.25) | 2.10 ± 0.31 (2.13) | 4.50 ± 0.67 (4.58) | 1.82 ± 0.39 (1.85) |
| right | p | 0.824 | 50/50 | 0 | 50 | 1.54 ± 0.35 (1.49) | 6.13 ± 4.06 (5.12) | 1.97 ± 0.30 (1.95) | 4.15 ± 0.68 (4.20) | 1.59 ± 0.41 (1.54) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.831 | 100/100 | 0 | 98 | 1.62 ± 0.55 (1.51) | 5.85 ± 3.87 (4.79) | 1.93 ± 0.41 (2.06) | 4.09 ± 0.91 (4.29) | 1.57 ± 0.54 (1.66) |
| right | p | 0.823 | 100/100 | 0 | 95 | 1.60 ± 0.53 (1.53) | 7.64 ± 15.83 (5.32) | 1.89 ± 0.38 (1.95) | 4.01 ± 0.83 (4.18) | 1.51 ± 0.50 (1.54) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.823 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.10) | 5.49 ± 3.64 (4.89) | 1.48 ± 0.44 (1.33) | 3.09 ± 0.87 (2.80) | 0.98 ± 0.49 (0.77) |
| forward/right | p | 0.824 | 25/25 | 0 | 23 | 1.05 ± 0.26 (1.12) | 5.55 ± 4.72 (3.35) | 1.61 ± 0.39 (1.68) | 3.39 ± 0.84 (3.58) | 1.13 ± 0.48 (1.20) |
| left/left | p | 0.848 | 25/25 | 0 | 24 | 1.45 ± 0.36 (1.50) | 5.50 ± 4.12 (4.25) | 1.98 ± 0.31 (2.08) | 4.22 ± 0.72 (4.44) | 1.63 ± 0.41 (1.79) |
| left/right | p | 0.852 | 25/25 | 0 | 24 | 1.66 ± 0.31 (1.64) | 5.95 ± 4.29 (6.68) | 2.05 ± 0.26 (2.10) | 4.42 ± 0.57 (4.52) | 1.75 ± 0.41 (1.75) |
| back/left | p | 0.816 | 25/25 | 0 | 24 | 2.33 ± 0.26 (2.26) | 6.39 ± 3.65 (6.21) | 2.15 ± 0.16 (2.15) | 4.60 ± 0.44 (4.59) | 1.88 ± 0.32 (1.88) |
| back/right | p | 0.807 | 25/25 | 0 | 23 | 2.25 ± 0.26 (2.24) | 12.80 ± 30.15 (6.29) | 2.05 ± 0.40 (2.12) | 4.40 ± 0.83 (4.57) | 1.77 ± 0.45 (1.85) |
| right/left | p | 0.836 | 25/25 | 0 | 25 | 1.64 ± 0.32 (1.58) | 6.00 ± 3.98 (4.54) | 2.10 ± 0.28 (2.12) | 4.46 ± 0.65 (4.52) | 1.78 ± 0.39 (1.79) |
| right/right | p | 0.812 | 25/25 | 0 | 25 | 1.44 ± 0.35 (1.48) | 6.27 ± 4.13 (5.30) | 1.84 ± 0.26 (1.90) | 3.84 ± 0.56 (4.02) | 1.41 ± 0.35 (1.45) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.848 | 5.9 | 4.25 | 1.63 |
| p | normal | 0.806 | 7.6 | 3.86 | 1.45 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.769 | 0.16 | 2.29 ± 0.81 (2.14) | 3.64 | 1.33 |
| p | medium | 16 | 0.863 | 0.73 | 1.09 ± 0.31 (1.13) | 3.54 | 1.29 |
| p | strong | 126 | 0.849 | 0.57 | - | 4.31 | 1.67 |

## Notes

- p: score 0.827, 200/200 kicked, 0 fell; worst sector back (0.811).
