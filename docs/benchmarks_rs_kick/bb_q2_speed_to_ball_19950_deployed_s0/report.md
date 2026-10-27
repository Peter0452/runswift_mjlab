# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_21-18-55_q2_speed_to_ball/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.770** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 160 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.96 ± 1.51 (1.72) |
| Direction error [°] | 20.42 ± 40.41 (5.70) |
| Avg ball speed [m/s] | 2.05 ± 0.69 (2.25) |
| Peak ball speed [m/s] | 4.50 ± 1.60 (5.03) |
| Distance [m] | 1.84 ± 0.85 (1.90) |
| Path length [m] | 1.85 ± 0.86 (1.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.774 | 49/50 | 0 | 38 | 1.58 ± 1.40 (1.34) | 10.44 ± 15.60 (4.02) | 1.92 ± 0.74 (2.12) | 4.19 ± 1.71 (4.30) | 1.67 ± 0.86 (1.73) |
| left | p | 0.795 | 48/50 | 0 | 41 | 1.65 ± 0.48 (1.70) | 18.81 ± 34.82 (6.01) | 2.13 ± 0.61 (2.31) | 4.72 ± 1.44 (5.27) | 1.94 ± 0.81 (2.17) |
| back | p | 0.717 | 49/50 | 0 | 38 | 2.68 ± 1.97 (2.48) | 37.26 ± 61.06 (7.32) | 2.05 ± 0.80 (2.30) | 4.44 ± 1.79 (5.15) | 1.89 ± 0.98 (2.13) |
| right | p | 0.796 | 49/50 | 0 | 43 | 1.93 ± 1.52 (1.76) | 15.13 ± 30.45 (4.48) | 2.10 ± 0.56 (2.20) | 4.65 ± 1.36 (5.11) | 1.87 ± 0.72 (1.90) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 99/100 | 0 | 85 | 1.86 ± 1.18 (1.72) | 19.25 ± 40.53 (5.74) | 2.13 ± 0.65 (2.26) | 4.65 ± 1.50 (5.09) | 1.93 ± 0.82 (2.00) |
| right | p | 0.743 | 96/100 | 0 | 75 | 2.06 ± 1.79 (1.73) | 21.63 ± 40.26 (5.52) | 1.97 ± 0.72 (2.23) | 4.34 ± 1.68 (4.64) | 1.75 ± 0.88 (1.83) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.820 | 25/25 | 0 | 21 | 1.37 ± 0.48 (1.30) | 8.70 ± 13.67 (4.46) | 2.09 ± 0.62 (2.24) | 4.55 ± 1.45 (4.51) | 1.85 ± 0.78 (1.78) |
| forward/right | p | 0.729 | 24/25 | 0 | 17 | 1.79 ± 1.91 (1.35) | 12.26 ± 17.21 (3.56) | 1.74 ± 0.80 (2.01) | 3.81 ± 1.87 (4.08) | 1.48 ± 0.91 (1.60) |
| left/left | p | 0.851 | 25/25 | 0 | 23 | 1.58 ± 0.41 (1.68) | 11.75 ± 21.87 (5.74) | 2.21 ± 0.53 (2.28) | 4.90 ± 1.24 (5.16) | 2.04 ± 0.71 (2.15) |
| left/right | p | 0.739 | 23/25 | 0 | 18 | 1.72 ± 0.53 (1.86) | 26.49 ± 43.55 (6.28) | 2.05 ± 0.67 (2.35) | 4.52 ± 1.61 (5.42) | 1.84 ± 0.89 (2.24) |
| back/left | p | 0.704 | 24/25 | 0 | 19 | 2.71 ± 2.02 (2.51) | 39.27 ± 63.96 (7.27) | 2.10 ± 0.78 (2.28) | 4.51 ± 1.72 (5.11) | 1.94 ± 0.99 (2.10) |
| back/right | p | 0.730 | 25/25 | 0 | 19 | 2.66 ± 1.91 (2.48) | 35.33 ± 58.07 (8.73) | 2.00 ± 0.82 (2.32) | 4.37 ± 1.86 (5.35) | 1.85 ± 0.97 (2.13) |
| right/left | p | 0.816 | 25/25 | 0 | 22 | 1.82 ± 0.46 (1.84) | 18.07 ± 36.88 (4.20) | 2.10 ± 0.63 (2.29) | 4.65 ± 1.54 (5.24) | 1.92 ± 0.78 (2.08) |
| right/right | p | 0.775 | 24/25 | 0 | 21 | 2.04 ± 2.12 (1.72) | 12.08 ± 21.39 (5.27) | 2.10 ± 0.47 (2.13) | 4.65 ± 1.15 (5.04) | 1.83 ± 0.64 (1.76) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.789 | 20.0 | 5.07 | 2.17 |
| p | normal | 0.752 | 20.8 | 3.94 | 1.53 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.14 | 2.31 ± 1.05 (2.23) | 3.61 | 1.36 |
| p | medium | 16 | 0.784 | 0.70 | 1.25 ± 0.23 (1.27) | 4.05 | 1.60 |
| p | strong | 126 | 0.791 | 0.66 | - | 4.97 | 2.11 |

## Notes

- p: score 0.770, 195/200 kicked, 0 fell; worst sector back (0.717).
