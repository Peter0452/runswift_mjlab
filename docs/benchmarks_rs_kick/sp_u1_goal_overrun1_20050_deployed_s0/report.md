# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.770** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 2.02 ± 1.48 (1.76) |
| Direction error [°] | 18.25 ± 36.10 (5.84) |
| Avg ball speed [m/s] | 1.85 ± 0.64 (2.06) |
| Peak ball speed [m/s] | 4.40 ± 1.59 (5.04) |
| Distance [m] | 1.74 ± 0.88 (1.92) |
| Path length [m] | 1.74 ± 0.89 (1.92) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.768 | 49/50 | 0 | 41 | 2.00 ± 2.40 (1.36) | 9.84 ± 9.05 (8.47) | 1.78 ± 0.66 (1.75) | 4.21 ± 1.66 (3.87) | 1.64 ± 0.91 (1.39) |
| left | p | 0.795 | 48/50 | 0 | 41 | 1.69 ± 0.49 (1.77) | 18.48 ± 32.90 (5.49) | 1.93 ± 0.59 (2.07) | 4.62 ± 1.46 (5.31) | 1.85 ± 0.85 (2.08) |
| back | p | 0.740 | 48/50 | 0 | 41 | 2.67 ± 1.34 (2.57) | 25.49 ± 51.62 (3.81) | 1.88 ± 0.65 (2.14) | 4.49 ± 1.64 (5.26) | 1.79 ± 0.89 (2.07) |
| right | p | 0.779 | 48/50 | 0 | 38 | 1.70 ± 0.46 (1.71) | 19.36 ± 35.85 (5.53) | 1.81 ± 0.63 (2.03) | 4.26 ± 1.54 (4.87) | 1.66 ± 0.86 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.793 | 98/100 | 0 | 84 | 1.97 ± 1.34 (1.74) | 17.50 ± 36.68 (5.31) | 1.91 ± 0.60 (2.07) | 4.51 ± 1.50 (5.22) | 1.80 ± 0.86 (2.07) |
| right | p | 0.748 | 95/100 | 0 | 77 | 2.06 ± 1.60 (1.76) | 19.02 ± 35.48 (5.89) | 1.80 ± 0.67 (2.06) | 4.28 ± 1.66 (4.83) | 1.67 ± 0.89 (1.74) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.780 | 24/25 | 0 | 21 | 1.66 ± 1.65 (1.36) | 8.95 ± 9.49 (6.53) | 1.90 ± 0.61 (2.02) | 4.45 ± 1.49 (4.57) | 1.78 ± 0.84 (1.81) |
| forward/right | p | 0.756 | 25/25 | 0 | 20 | 2.33 ± 2.91 (1.36) | 10.69 ± 8.53 (10.41) | 1.67 ± 0.68 (1.56) | 3.98 ± 1.77 (3.56) | 1.51 ± 0.96 (1.31) |
| left/left | p | 0.854 | 25/25 | 0 | 23 | 1.63 ± 0.44 (1.72) | 12.96 ± 23.97 (6.73) | 2.02 ± 0.51 (2.08) | 4.81 ± 1.29 (5.35) | 1.96 ± 0.80 (2.20) |
| left/right | p | 0.736 | 23/25 | 0 | 18 | 1.77 ± 0.54 (1.86) | 24.48 ± 39.56 (5.10) | 1.84 ± 0.64 (2.04) | 4.40 ± 1.61 (5.25) | 1.73 ± 0.89 (1.88) |
| back/left | p | 0.746 | 24/25 | 0 | 21 | 2.81 ± 1.81 (2.57) | 23.40 ± 51.27 (3.81) | 1.96 ± 0.52 (2.14) | 4.67 ± 1.36 (5.32) | 1.86 ± 0.84 (2.14) |
| back/right | p | 0.734 | 24/25 | 0 | 20 | 2.52 ± 0.52 (2.58) | 27.58 ± 51.89 (4.28) | 1.80 ± 0.76 (2.15) | 4.31 ± 1.86 (5.17) | 1.73 ± 0.93 (2.04) |
| right/left | p | 0.793 | 25/25 | 0 | 19 | 1.81 ± 0.47 (1.80) | 24.57 ± 43.78 (5.94) | 1.75 ± 0.70 (1.81) | 4.10 ± 1.71 (3.96) | 1.62 ± 0.93 (1.45) |
| right/right | p | 0.766 | 23/25 | 0 | 19 | 1.59 ± 0.43 (1.54) | 13.69 ± 23.16 (5.24) | 1.88 ± 0.55 (2.06) | 4.44 ± 1.30 (4.92) | 1.71 ± 0.77 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.796 | 15.9 | 5.23 | 2.24 |
| p | normal | 0.745 | 20.6 | 3.57 | 1.24 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.710 | 0.26 | 1.96 ± 0.86 (1.79) | 3.09 | 0.97 |
| p | medium | 16 | 0.833 | 0.84 | 1.09 ± 0.17 (1.10) | 3.53 | 1.19 |
| p | strong | 126 | 0.790 | 0.68 | - | 5.12 | 2.16 |

## Notes

- p: score 0.770, 193/200 kicked, 0 fell; worst sector back (0.740).
