# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 200 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.60 ± 0.51 (1.54) |
| Direction error [°] | 4.96 ± 3.10 (4.76) |
| Avg ball speed [m/s] | 1.79 ± 0.35 (1.85) |
| Peak ball speed [m/s] | 3.90 ± 0.82 (4.08) |
| Distance [m] | 1.35 ± 0.46 (1.37) |
| Path length [m] | 1.35 ± 0.46 (1.38) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.864 | 50/50 | 0 | 50 | 1.07 ± 0.23 (1.11) | 3.69 ± 2.81 (2.41) | 1.62 ± 0.37 (1.74) | 3.47 ± 0.81 (3.60) | 1.10 ± 0.43 (1.18) |
| left | p | 0.866 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.54) | 5.15 ± 2.87 (5.35) | 1.84 ± 0.32 (1.92) | 4.05 ± 0.77 (4.29) | 1.43 ± 0.45 (1.46) |
| back | p | 0.839 | 50/50 | 0 | 50 | 2.24 ± 0.25 (2.21) | 6.04 ± 3.32 (5.00) | 1.96 ± 0.29 (2.06) | 4.27 ± 0.74 (4.61) | 1.57 ± 0.43 (1.69) |
| right | p | 0.850 | 50/50 | 0 | 50 | 1.54 ± 0.33 (1.53) | 4.97 ± 2.89 (4.98) | 1.76 ± 0.31 (1.80) | 3.81 ± 0.75 (3.80) | 1.29 ± 0.39 (1.31) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.854 | 100/100 | 0 | 100 | 1.59 ± 0.51 (1.54) | 5.05 ± 2.96 (4.90) | 1.78 ± 0.35 (1.84) | 3.88 ± 0.84 (4.07) | 1.34 ± 0.48 (1.37) |
| right | p | 0.856 | 100/100 | 0 | 100 | 1.60 ± 0.50 (1.54) | 4.88 ± 3.23 (4.34) | 1.81 ± 0.34 (1.88) | 3.92 ± 0.80 (4.08) | 1.36 ± 0.45 (1.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.864 | 25/25 | 0 | 25 | 1.06 ± 0.22 (1.10) | 3.71 ± 2.53 (2.43) | 1.61 ± 0.37 (1.74) | 3.42 ± 0.81 (3.56) | 1.09 ± 0.45 (1.16) |
| forward/right | p | 0.864 | 25/25 | 0 | 25 | 1.08 ± 0.24 (1.12) | 3.67 ± 3.07 (2.24) | 1.63 ± 0.37 (1.74) | 3.51 ± 0.81 (3.64) | 1.11 ± 0.41 (1.21) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.48) | 5.58 ± 2.99 (5.31) | 1.76 ± 0.33 (1.84) | 3.86 ± 0.79 (4.21) | 1.33 ± 0.44 (1.44) |
| left/right | p | 0.874 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.62) | 4.71 ± 2.69 (5.38) | 1.93 ± 0.29 (1.97) | 4.23 ± 0.70 (4.38) | 1.53 ± 0.42 (1.58) |
| back/left | p | 0.837 | 25/25 | 0 | 25 | 2.26 ± 0.24 (2.22) | 6.08 ± 3.20 (5.04) | 1.97 ± 0.26 (2.04) | 4.33 ± 0.70 (4.62) | 1.60 ± 0.42 (1.77) |
| back/right | p | 0.842 | 25/25 | 0 | 25 | 2.23 ± 0.25 (2.20) | 6.00 ± 3.44 (4.89) | 1.95 ± 0.31 (2.08) | 4.21 ± 0.77 (4.60) | 1.55 ± 0.44 (1.63) |
| right/left | p | 0.856 | 25/25 | 0 | 25 | 1.61 ± 0.32 (1.60) | 4.83 ± 2.50 (5.13) | 1.78 ± 0.33 (1.84) | 3.90 ± 0.80 (4.14) | 1.34 ± 0.44 (1.36) |
| right/right | p | 0.843 | 25/25 | 0 | 25 | 1.46 ± 0.32 (1.52) | 5.12 ± 3.23 (4.78) | 1.73 ± 0.29 (1.78) | 3.72 ± 0.67 (3.71) | 1.24 ± 0.33 (1.26) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.862 | 5.1 | 4.40 | 1.60 |
| p | normal | 0.848 | 4.8 | 3.40 | 1.09 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.816 | 0.34 | 1.86 ± 0.62 (1.70) | 2.95 | 0.85 |
| p | medium | 16 | 0.922 | 0.88 | 0.97 ± 0.16 (1.01) | 3.14 | 0.96 |
| p | strong | 126 | 0.864 | 0.59 | - | 4.43 | 1.63 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector back (0.839).
