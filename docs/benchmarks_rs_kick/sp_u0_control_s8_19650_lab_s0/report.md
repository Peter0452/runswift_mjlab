# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u0_control_s8/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.853** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.54 ± 0.50 (1.46) |
| Direction error [°] | 5.89 ± 12.33 (4.45) |
| Avg ball speed [m/s] | 1.85 ± 0.38 (1.93) |
| Peak ball speed [m/s] | 4.33 ± 0.89 (4.61) |
| Distance [m] | 1.62 ± 0.55 (1.72) |
| Path length [m] | 1.63 ± 0.55 (1.73) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.836 | 50/50 | 0 | 49 | 1.09 ± 0.38 (1.07) | 5.57 ± 6.06 (4.02) | 1.61 ± 0.36 (1.54) | 3.77 ± 0.79 (3.51) | 1.26 ± 0.48 (1.09) |
| left | p | 0.874 | 50/50 | 0 | 50 | 1.48 ± 0.34 (1.47) | 4.94 ± 2.89 (4.97) | 1.96 ± 0.38 (2.06) | 4.61 ± 0.85 (4.89) | 1.79 ± 0.55 (1.90) |
| back | p | 0.861 | 50/50 | 0 | 49 | 2.15 ± 0.23 (2.17) | 7.42 ± 23.41 (4.10) | 1.94 ± 0.37 (2.04) | 4.57 ± 0.88 (4.90) | 1.77 ± 0.51 (1.93) |
| right | p | 0.842 | 50/50 | 0 | 50 | 1.46 ± 0.32 (1.42) | 5.64 ± 3.44 (5.27) | 1.89 ± 0.32 (1.93) | 4.38 ± 0.78 (4.60) | 1.66 ± 0.47 (1.68) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.851 | 100/100 | 0 | 99 | 1.57 ± 0.51 (1.48) | 5.38 ± 4.79 (4.48) | 1.87 ± 0.37 (1.97) | 4.36 ± 0.85 (4.62) | 1.65 ± 0.56 (1.74) |
| right | p | 0.856 | 100/100 | 0 | 99 | 1.52 ± 0.48 (1.46) | 6.41 ± 16.76 (4.30) | 1.83 ± 0.39 (1.92) | 4.30 ± 0.93 (4.58) | 1.59 ± 0.53 (1.69) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.826 | 25/25 | 0 | 24 | 1.17 ± 0.47 (1.10) | 6.60 ± 7.77 (4.45) | 1.61 ± 0.36 (1.53) | 3.76 ± 0.77 (3.51) | 1.27 ± 0.51 (1.07) |
| forward/right | p | 0.846 | 25/25 | 0 | 25 | 1.01 ± 0.22 (1.02) | 4.54 ± 3.32 (3.54) | 1.61 ± 0.35 (1.56) | 3.78 ± 0.81 (3.51) | 1.25 ± 0.46 (1.14) |
| left/left | p | 0.863 | 25/25 | 0 | 25 | 1.38 ± 0.32 (1.46) | 5.53 ± 3.18 (5.57) | 1.94 ± 0.37 (2.06) | 4.45 ± 0.83 (4.63) | 1.72 ± 0.56 (1.77) |
| left/right | p | 0.885 | 25/25 | 0 | 25 | 1.58 ± 0.32 (1.56) | 4.35 ± 2.41 (3.61) | 1.98 ± 0.38 (2.08) | 4.77 ± 0.84 (5.03) | 1.86 ± 0.53 (2.04) |
| back/left | p | 0.866 | 25/25 | 0 | 25 | 2.20 ± 0.23 (2.18) | 3.86 ± 2.62 (3.34) | 2.00 ± 0.27 (2.04) | 4.72 ± 0.69 (5.02) | 1.85 ± 0.47 (1.95) |
| back/right | p | 0.857 | 25/25 | 0 | 24 | 2.11 ± 0.21 (2.06) | 10.98 ± 32.62 (4.45) | 1.88 ± 0.44 (2.07) | 4.42 ± 1.02 (4.86) | 1.69 ± 0.53 (1.80) |
| right/left | p | 0.850 | 25/25 | 0 | 25 | 1.54 ± 0.30 (1.50) | 5.52 ± 3.25 (5.01) | 1.95 ± 0.35 (2.11) | 4.51 ± 0.80 (4.86) | 1.75 ± 0.51 (1.84) |
| right/right | p | 0.835 | 25/25 | 0 | 25 | 1.37 ± 0.33 (1.40) | 5.76 ± 3.62 (5.41) | 1.84 ± 0.27 (1.87) | 4.24 ± 0.73 (3.99) | 1.58 ± 0.40 (1.57) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.872 | 5.4 | 4.84 | 1.92 |
| p | normal | 0.835 | 6.4 | 3.82 | 1.32 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.787 | 0.20 | 2.13 ± 0.71 (1.93) | 3.37 | 1.06 |
| p | medium | 16 | 0.929 | 0.87 | 1.07 ± 0.14 (1.10) | 3.49 | 1.13 |
| p | strong | 126 | 0.875 | 0.65 | - | 4.88 | 1.94 |

## Notes

- p: score 0.853, 200/200 kicked, 0 fell; worst sector forward (0.836).
