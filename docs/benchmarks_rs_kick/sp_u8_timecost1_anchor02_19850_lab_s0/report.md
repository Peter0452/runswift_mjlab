# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_12-23-01_u8_timecost1_anchor02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 194 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.62 ± 0.56 (1.53) |
| Direction error [°] | 6.29 ± 17.21 (2.93) |
| Avg ball speed [m/s] | 1.67 ± 0.29 (1.70) |
| Peak ball speed [m/s] | 4.51 ± 0.77 (4.57) |
| Distance [m] | 1.76 ± 0.46 (1.75) |
| Path length [m] | 1.76 ± 0.46 (1.76) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.817 | 50/50 | 0 | 47 | 1.21 ± 0.63 (1.10) | 8.38 ± 19.88 (3.47) | 1.48 ± 0.25 (1.44) | 3.97 ± 0.63 (3.89) | 1.42 ± 0.38 (1.35) |
| left | p | 0.872 | 50/50 | 0 | 49 | 1.50 ± 0.32 (1.50) | 4.55 ± 3.27 (3.72) | 1.75 ± 0.20 (1.77) | 4.70 ± 0.63 (4.84) | 1.88 ± 0.40 (1.85) |
| back | p | 0.871 | 50/50 | 0 | 49 | 2.21 ± 0.26 (2.16) | 5.67 ± 22.74 (1.68) | 1.80 ± 0.32 (1.88) | 4.81 ± 0.85 (5.11) | 1.96 ± 0.46 (2.12) |
| right | p | 0.841 | 50/50 | 0 | 49 | 1.56 ± 0.42 (1.50) | 6.56 ± 15.92 (3.44) | 1.67 ± 0.25 (1.69) | 4.57 ± 0.64 (4.63) | 1.77 ± 0.37 (1.75) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 97 | 1.64 ± 0.58 (1.55) | 5.68 ± 14.41 (2.64) | 1.70 ± 0.25 (1.73) | 4.53 ± 0.67 (4.59) | 1.76 ± 0.41 (1.77) |
| right | p | 0.847 | 100/100 | 0 | 97 | 1.60 ± 0.54 (1.50) | 6.90 ± 19.59 (3.29) | 1.65 ± 0.32 (1.68) | 4.49 ± 0.85 (4.54) | 1.75 ± 0.50 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.807 | 25/25 | 0 | 23 | 1.34 ± 0.78 (1.12) | 11.79 ± 27.43 (3.82) | 1.49 ± 0.21 (1.43) | 4.00 ± 0.50 (3.90) | 1.43 ± 0.34 (1.35) |
| forward/right | p | 0.826 | 25/25 | 0 | 24 | 1.09 ± 0.39 (1.06) | 4.96 ± 3.80 (3.40) | 1.46 ± 0.28 (1.45) | 3.94 ± 0.73 (3.88) | 1.40 ± 0.41 (1.39) |
| left/left | p | 0.868 | 25/25 | 0 | 24 | 1.41 ± 0.32 (1.44) | 4.73 ± 3.62 (4.11) | 1.74 ± 0.18 (1.77) | 4.59 ± 0.60 (4.72) | 1.81 ± 0.35 (1.85) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.59 ± 0.28 (1.60) | 4.37 ± 2.86 (3.23) | 1.76 ± 0.22 (1.78) | 4.81 ± 0.65 (4.87) | 1.95 ± 0.44 (1.85) |
| back/left | p | 0.878 | 25/25 | 0 | 25 | 2.23 ± 0.27 (2.16) | 2.04 ± 1.56 (1.57) | 1.81 ± 0.25 (1.89) | 4.83 ± 0.64 (5.12) | 1.96 ± 0.40 (2.16) |
| back/right | p | 0.864 | 25/25 | 0 | 24 | 2.18 ± 0.24 (2.16) | 9.30 ± 31.71 (1.74) | 1.78 ± 0.37 (1.82) | 4.78 ± 1.02 (5.04) | 1.96 ± 0.52 (2.11) |
| right/left | p | 0.859 | 25/25 | 0 | 25 | 1.59 ± 0.30 (1.56) | 4.14 ± 2.89 (3.08) | 1.74 ± 0.20 (1.75) | 4.70 ± 0.61 (4.81) | 1.85 ± 0.34 (1.88) |
| right/right | p | 0.823 | 25/25 | 0 | 24 | 1.53 ± 0.52 (1.46) | 8.99 ± 22.06 (4.00) | 1.61 ± 0.27 (1.61) | 4.43 ± 0.64 (4.32) | 1.69 ± 0.38 (1.65) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.886 | 3.9 | 4.86 | 1.93 |
| p | normal | 0.814 | 8.7 | 4.16 | 1.59 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.755 | 0.11 | 2.42 ± 0.83 (2.26) | 3.83 | 1.41 |
| p | medium | 16 | 0.909 | 0.78 | 1.18 ± 0.18 (1.20) | 3.84 | 1.42 |
| p | strong | 126 | 0.886 | 0.65 | - | 4.91 | 1.96 |

## Notes

- p: score 0.850, 200/200 kicked, 0 fell; worst sector forward (0.817).
