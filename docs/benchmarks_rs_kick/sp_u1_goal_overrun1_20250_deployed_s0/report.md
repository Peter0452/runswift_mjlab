# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u1_goal_overrun1/model_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.97 ± 1.11 (1.86) |
| Direction error [°] | 17.74 ± 36.60 (5.34) |
| Avg ball speed [m/s] | 2.08 ± 0.80 (2.27) |
| Peak ball speed [m/s] | 4.46 ± 1.80 (5.25) |
| Distance [m] | 1.84 ± 1.04 (1.96) |
| Path length [m] | 1.85 ± 1.04 (1.97) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.784 | 48/50 | 0 | 40 | 1.51 ± 0.87 (1.44) | 8.69 ± 10.29 (4.48) | 1.82 ± 0.75 (1.72) | 3.93 ± 1.76 (3.46) | 1.49 ± 0.94 (1.14) |
| left | p | 0.811 | 48/50 | 0 | 42 | 1.76 ± 0.52 (1.88) | 17.17 ± 35.11 (4.96) | 2.17 ± 0.71 (2.45) | 4.70 ± 1.63 (5.58) | 1.94 ± 0.93 (2.34) |
| back | p | 0.735 | 49/50 | 0 | 40 | 2.79 ± 1.63 (2.60) | 27.68 ± 53.26 (6.33) | 2.24 ± 0.82 (2.45) | 4.70 ± 1.83 (5.50) | 2.06 ± 1.09 (2.35) |
| right | p | 0.803 | 49/50 | 0 | 39 | 1.78 ± 0.50 (1.86) | 17.23 ± 31.25 (4.59) | 2.10 ± 0.83 (2.15) | 4.48 ± 1.87 (5.25) | 1.87 ± 1.09 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 100/100 | 0 | 85 | 1.94 ± 1.12 (1.87) | 17.60 ± 36.68 (5.71) | 2.12 ± 0.78 (2.34) | 4.52 ± 1.76 (5.26) | 1.89 ± 1.03 (2.05) |
| right | p | 0.753 | 94/100 | 0 | 76 | 1.99 ± 1.09 (1.86) | 17.89 ± 36.52 (4.79) | 2.05 ± 0.82 (2.18) | 4.39 ± 1.85 (5.16) | 1.80 ± 1.04 (1.84) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.835 | 25/25 | 0 | 22 | 1.40 ± 0.30 (1.44) | 8.14 ± 10.58 (3.97) | 1.95 ± 0.73 (1.87) | 4.20 ± 1.68 (3.74) | 1.64 ± 0.91 (1.34) |
| forward/right | p | 0.732 | 23/25 | 0 | 18 | 1.64 ± 1.20 (1.44) | 9.28 ± 9.93 (4.80) | 1.67 ± 0.75 (1.53) | 3.64 ± 1.81 (3.03) | 1.32 ± 0.94 (0.98) |
| left/left | p | 0.869 | 25/25 | 0 | 23 | 1.70 ± 0.42 (1.84) | 9.29 ± 15.72 (5.29) | 2.32 ± 0.55 (2.49) | 4.99 ± 1.29 (5.59) | 2.11 ± 0.80 (2.40) |
| left/right | p | 0.752 | 23/25 | 0 | 19 | 1.83 ± 0.59 (2.06) | 25.73 ± 46.51 (4.08) | 2.01 ± 0.82 (2.42) | 4.39 ± 1.88 (5.34) | 1.76 ± 1.01 (2.22) |
| back/left | p | 0.749 | 25/25 | 0 | 20 | 2.82 ± 1.83 (2.58) | 30.58 ± 56.34 (6.33) | 2.27 ± 0.84 (2.59) | 4.75 ± 1.88 (5.91) | 2.12 ± 1.18 (2.68) |
| back/right | p | 0.721 | 24/25 | 0 | 20 | 2.77 ± 1.39 (2.69) | 24.65 ± 49.67 (6.15) | 2.21 ± 0.80 (2.44) | 4.65 ± 1.78 (5.47) | 2.01 ± 0.98 (2.28) |
| right/left | p | 0.798 | 25/25 | 0 | 20 | 1.85 ± 0.55 (1.92) | 22.37 ± 38.72 (5.76) | 1.93 ± 0.87 (1.86) | 4.14 ± 1.95 (3.74) | 1.68 ± 1.10 (1.41) |
| right/right | p | 0.808 | 24/25 | 0 | 19 | 1.71 ± 0.44 (1.79) | 11.88 ± 19.40 (4.11) | 2.28 ± 0.75 (2.63) | 4.84 ± 1.71 (5.79) | 2.08 ± 1.04 (2.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.803 | 16.3 | 5.40 | 2.41 |
| p | normal | 0.763 | 19.2 | 3.53 | 1.29 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.27 | 1.93 ± 0.83 (1.76) | 3.04 | 0.98 |
| p | medium | 16 | 0.841 | 0.90 | 1.04 ± 0.12 (1.06) | 3.39 | 1.13 |
| p | strong | 126 | 0.804 | 0.70 | - | 5.25 | 2.34 |

## Notes

- p: score 0.783, 194/200 kicked, 0 fell; worst sector back (0.735).
