# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-18-00_e3_drill_stand/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.844** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 192 |
| Weak kicks (< 0.3 m) | 3 |
| Time to kick [s] | 1.84 ± 0.56 (1.76) |
| Direction error [°] | 7.34 ± 12.92 (5.59) |
| Avg ball speed [m/s] | 2.61 ± 0.56 (2.77) |
| Peak ball speed [m/s] | 5.42 ± 1.26 (5.98) |
| Distance [m] | 2.72 ± 0.89 (3.06) |
| Path length [m] | 2.73 ± 0.89 (3.08) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.854 | 50/50 | 0 | 49 | 1.27 ± 0.24 (1.28) | 5.11 ± 5.63 (3.80) | 2.44 ± 0.55 (2.56) | 5.11 ± 1.28 (5.61) | 2.45 ± 0.86 (2.67) |
| left | p | 0.874 | 50/50 | 0 | 48 | 1.77 ± 0.35 (1.78) | 6.32 ± 3.96 (5.11) | 2.70 ± 0.41 (2.81) | 5.61 ± 0.96 (5.95) | 2.83 ± 0.73 (3.05) |
| back | p | 0.794 | 50/50 | 0 | 47 | 2.53 ± 0.37 (2.43) | 12.21 ± 23.98 (8.45) | 2.67 ± 0.69 (2.98) | 5.53 ± 1.53 (6.33) | 2.88 ± 1.04 (3.43) |
| right | p | 0.854 | 50/50 | 0 | 48 | 1.78 ± 0.33 (1.74) | 5.73 ± 3.57 (4.96) | 2.65 ± 0.50 (2.80) | 5.44 ± 1.13 (6.01) | 2.71 ± 0.85 (3.06) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.847 | 100/100 | 0 | 97 | 1.86 ± 0.59 (1.78) | 6.47 ± 4.93 (5.67) | 2.64 ± 0.53 (2.78) | 5.48 ± 1.21 (6.01) | 2.75 ± 0.88 (3.07) |
| right | p | 0.841 | 100/100 | 0 | 95 | 1.82 ± 0.52 (1.73) | 8.21 ± 17.55 (5.02) | 2.59 ± 0.58 (2.76) | 5.36 ± 1.30 (5.97) | 2.68 ± 0.90 (2.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.860 | 25/25 | 0 | 24 | 1.28 ± 0.24 (1.30) | 5.58 ± 7.21 (3.49) | 2.45 ± 0.67 (2.67) | 5.13 ± 1.50 (5.90) | 2.49 ± 0.97 (3.00) |
| forward/right | p | 0.849 | 25/25 | 0 | 25 | 1.25 ± 0.24 (1.28) | 4.63 ± 3.32 (3.95) | 2.43 ± 0.39 (2.47) | 5.09 ± 1.01 (5.49) | 2.40 ± 0.72 (2.41) |
| left/left | p | 0.871 | 25/25 | 0 | 24 | 1.67 ± 0.36 (1.72) | 6.32 ± 4.08 (5.29) | 2.66 ± 0.43 (2.68) | 5.50 ± 0.99 (5.75) | 2.75 ± 0.75 (2.98) |
| left/right | p | 0.877 | 25/25 | 0 | 24 | 1.87 ± 0.30 (1.90) | 6.31 ± 3.84 (4.92) | 2.74 ± 0.39 (2.83) | 5.72 ± 0.91 (6.03) | 2.90 ± 0.70 (3.11) |
| back/left | p | 0.803 | 25/25 | 0 | 25 | 2.59 ± 0.44 (2.54) | 7.69 ± 3.71 (7.98) | 2.77 ± 0.45 (2.95) | 5.72 ± 1.11 (6.35) | 2.98 ± 0.90 (3.48) |
| back/right | p | 0.785 | 25/25 | 0 | 22 | 2.47 ± 0.28 (2.40) | 16.72 ± 33.10 (8.96) | 2.58 ± 0.85 (3.01) | 5.34 ± 1.84 (6.32) | 2.78 ± 1.16 (3.41) |
| right/left | p | 0.853 | 25/25 | 0 | 24 | 1.89 ± 0.31 (1.84) | 6.27 ± 3.50 (5.97) | 2.69 ± 0.46 (2.87) | 5.57 ± 1.10 (6.21) | 2.80 ± 0.82 (3.21) |
| right/right | p | 0.855 | 25/25 | 0 | 24 | 1.67 ± 0.32 (1.72) | 5.18 ± 3.55 (4.83) | 2.61 ± 0.54 (2.73) | 5.30 ± 1.15 (5.72) | 2.63 ± 0.86 (2.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.892 | 6.4 | 6.29 | 3.35 |
| p | normal | 0.796 | 8.3 | 4.55 | 2.09 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.744 | 0.07 | 2.52 ± 0.91 (2.35) | 3.97 | 1.65 |
| p | medium | 16 | 0.842 | 0.69 | 1.19 ± 0.32 (1.24) | 3.90 | 1.64 |
| p | strong | 126 | 0.890 | 0.84 | - | 6.28 | 3.35 |

## Notes

- p: score 0.844, 200/200 kicked, 0 fell; worst sector back (0.794).
