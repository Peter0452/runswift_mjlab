# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_21-18-55_q2_speed_to_ball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.815** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 182 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 1.99 ± 1.45 (1.69) |
| Direction error [°] | 11.69 ± 25.68 (5.02) |
| Avg ball speed [m/s] | 2.28 ± 0.61 (2.43) |
| Peak ball speed [m/s] | 4.88 ± 1.45 (5.49) |
| Distance [m] | 2.18 ± 0.83 (2.39) |
| Path length [m] | 2.19 ± 0.83 (2.41) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.830 | 50/50 | 0 | 45 | 1.49 ± 1.38 (1.30) | 7.73 ± 10.10 (4.69) | 2.27 ± 0.66 (2.44) | 4.90 ± 1.52 (5.52) | 2.18 ± 0.82 (2.48) |
| left | p | 0.831 | 50/50 | 0 | 46 | 1.86 ± 1.24 (1.69) | 11.32 ± 23.87 (4.04) | 2.21 ± 0.67 (2.44) | 4.77 ± 1.59 (5.56) | 2.13 ± 0.89 (2.42) |
| back | p | 0.778 | 50/50 | 0 | 44 | 2.69 ± 1.45 (2.55) | 19.40 ± 40.83 (6.19) | 2.34 ± 0.63 (2.52) | 5.01 ± 1.47 (5.62) | 2.29 ± 0.87 (2.53) |
| right | p | 0.821 | 50/50 | 0 | 47 | 1.92 ± 1.48 (1.73) | 8.31 ± 14.57 (4.56) | 2.27 ± 0.47 (2.35) | 4.83 ± 1.18 (5.25) | 2.10 ± 0.70 (2.13) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 100/100 | 0 | 92 | 2.01 ± 1.49 (1.69) | 11.43 ± 24.44 (5.55) | 2.28 ± 0.58 (2.44) | 4.91 ± 1.39 (5.52) | 2.19 ± 0.80 (2.44) |
| right | p | 0.818 | 100/100 | 0 | 90 | 1.96 ± 1.42 (1.69) | 11.95 ± 26.86 (4.69) | 2.27 ± 0.64 (2.41) | 4.85 ± 1.51 (5.47) | 2.16 ± 0.85 (2.27) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.840 | 25/25 | 0 | 24 | 1.32 ± 0.47 (1.28) | 6.44 ± 6.81 (4.31) | 2.27 ± 0.57 (2.46) | 4.93 ± 1.37 (5.44) | 2.18 ± 0.76 (2.48) |
| forward/right | p | 0.820 | 25/25 | 0 | 21 | 1.66 ± 1.87 (1.34) | 9.02 ± 12.42 (4.98) | 2.28 ± 0.74 (2.42) | 4.87 ± 1.66 (5.59) | 2.18 ± 0.88 (2.49) |
| left/left | p | 0.834 | 25/25 | 0 | 24 | 1.99 ± 1.67 (1.60) | 7.27 ± 9.58 (5.79) | 2.29 ± 0.59 (2.44) | 4.95 ± 1.43 (5.59) | 2.23 ± 0.80 (2.46) |
| left/right | p | 0.827 | 25/25 | 0 | 22 | 1.72 ± 0.50 (1.78) | 15.37 ± 31.85 (3.78) | 2.14 ± 0.73 (2.33) | 4.59 ± 1.71 (4.66) | 2.03 ± 0.97 (2.09) |
| back/left | p | 0.775 | 25/25 | 0 | 21 | 2.53 ± 0.99 (2.54) | 21.13 ± 41.68 (6.24) | 2.35 ± 0.63 (2.53) | 5.02 ± 1.46 (5.63) | 2.32 ± 0.89 (2.59) |
| back/right | p | 0.780 | 25/25 | 0 | 23 | 2.85 ± 1.78 (2.56) | 17.68 ± 39.89 (5.79) | 2.34 ± 0.63 (2.46) | 5.00 ± 1.48 (5.56) | 2.27 ± 0.84 (2.53) |
| right/left | p | 0.798 | 25/25 | 0 | 23 | 2.21 ± 2.01 (1.88) | 10.89 ± 19.43 (4.72) | 2.21 ± 0.53 (2.28) | 4.73 ± 1.29 (5.20) | 2.04 ± 0.73 (2.15) |
| right/right | p | 0.844 | 25/25 | 0 | 24 | 1.62 ± 0.36 (1.66) | 5.74 ± 5.81 (4.46) | 2.33 ± 0.39 (2.40) | 4.93 ± 1.05 (5.36) | 2.17 ± 0.67 (2.12) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.838 | 12.8 | 5.31 | 2.45 |
| p | normal | 0.792 | 10.6 | 4.44 | 1.90 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.733 | 0.10 | 2.55 ± 1.06 (2.38) | 3.94 | 1.60 |
| p | medium | 20 | 0.874 | 0.67 | 1.28 ± 0.23 (1.28) | 4.11 | 1.67 |
| p | strong | 126 | 0.841 | 0.72 | - | 5.40 | 2.51 |

## Notes

- p: score 0.815, 200/200 kicked, 0 fell; worst sector back (0.778).
