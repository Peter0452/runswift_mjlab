# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_21-18-55_q2_speed_to_ball/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 2.01 ± 1.44 (1.73) |
| Direction error [°] | 12.38 ± 24.70 (5.23) |
| Avg ball speed [m/s] | 2.15 ± 0.61 (2.26) |
| Peak ball speed [m/s] | 4.70 ± 1.44 (5.21) |
| Distance [m] | 1.95 ± 0.77 (2.02) |
| Path length [m] | 1.96 ± 0.77 (2.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.797 | 50/50 | 0 | 42 | 1.75 ± 1.89 (1.38) | 9.39 ± 11.30 (5.11) | 2.06 ± 0.71 (2.22) | 4.57 ± 1.67 (5.21) | 1.87 ± 0.84 (1.98) |
| left | p | 0.821 | 49/50 | 0 | 44 | 1.72 ± 0.44 (1.66) | 10.88 ± 22.60 (4.65) | 2.18 ± 0.51 (2.25) | 4.75 ± 1.26 (5.19) | 1.97 ± 0.71 (2.02) |
| back | p | 0.747 | 49/50 | 0 | 42 | 2.66 ± 1.33 (2.52) | 18.40 ± 37.45 (6.33) | 2.30 ± 0.60 (2.40) | 4.96 ± 1.36 (5.47) | 2.15 ± 0.79 (2.30) |
| right | p | 0.805 | 50/50 | 0 | 45 | 1.94 ± 1.46 (1.83) | 10.93 ± 19.10 (5.19) | 2.08 ± 0.56 (2.20) | 4.55 ± 1.37 (4.66) | 1.83 ± 0.71 (1.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.782 | 99/100 | 0 | 83 | 1.96 ± 1.28 (1.68) | 14.26 ± 26.36 (5.98) | 2.12 ± 0.66 (2.26) | 4.64 ± 1.55 (5.28) | 1.93 ± 0.82 (2.05) |
| right | p | 0.803 | 99/100 | 0 | 90 | 2.07 ± 1.58 (1.78) | 10.50 ± 22.76 (4.65) | 2.19 ± 0.55 (2.26) | 4.77 ± 1.31 (5.17) | 1.98 ± 0.72 (1.98) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.803 | 25/25 | 0 | 21 | 1.45 ± 0.72 (1.32) | 9.84 ± 10.63 (6.54) | 2.06 ± 0.72 (2.21) | 4.59 ± 1.69 (5.26) | 1.89 ± 0.85 (1.93) |
| forward/right | p | 0.791 | 25/25 | 0 | 21 | 2.04 ± 2.53 (1.46) | 8.93 ± 11.91 (4.56) | 2.05 ± 0.70 (2.23) | 4.55 ± 1.66 (5.17) | 1.86 ± 0.83 (2.02) |
| left/left | p | 0.819 | 24/25 | 0 | 22 | 1.67 ± 0.37 (1.60) | 6.38 ± 5.96 (4.99) | 2.25 ± 0.43 (2.30) | 4.94 ± 1.10 (5.30) | 2.09 ± 0.63 (2.20) |
| left/right | p | 0.824 | 25/25 | 0 | 22 | 1.76 ± 0.50 (1.80) | 15.20 ± 30.48 (4.34) | 2.10 ± 0.56 (2.24) | 4.56 ± 1.37 (4.50) | 1.86 ± 0.76 (1.78) |
| back/left | p | 0.741 | 25/25 | 0 | 19 | 2.49 ± 1.06 (2.52) | 24.48 ± 42.07 (9.20) | 2.18 ± 0.73 (2.40) | 4.70 ± 1.61 (5.40) | 2.04 ± 0.90 (2.31) |
| back/right | p | 0.753 | 24/25 | 0 | 23 | 2.84 ± 1.54 (2.47) | 12.07 ± 30.67 (5.60) | 2.42 ± 0.39 (2.43) | 5.22 ± 0.98 (5.58) | 2.27 ± 0.62 (2.26) |
| right/left | p | 0.768 | 25/25 | 0 | 21 | 2.23 ± 2.00 (2.00) | 16.01 ± 25.47 (5.44) | 1.98 ± 0.67 (2.20) | 4.34 ± 1.63 (4.46) | 1.72 ± 0.79 (1.85) |
| right/right | p | 0.843 | 25/25 | 0 | 24 | 1.65 ± 0.35 (1.58) | 5.85 ± 5.43 (4.65) | 2.19 ± 0.40 (2.19) | 4.75 ± 1.01 (5.12) | 1.93 ± 0.58 (1.82) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.820 | 12.2 | 5.16 | 2.21 |
| p | normal | 0.765 | 12.6 | 4.25 | 1.70 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.711 | 0.08 | 2.50 ± 1.00 (2.40) | 3.86 | 1.48 |
| p | medium | 20 | 0.852 | 0.67 | 1.29 ± 0.22 (1.29) | 4.14 | 1.64 |
| p | strong | 126 | 0.818 | 0.69 | - | 5.16 | 2.21 |

## Notes

- p: score 0.793, 198/200 kicked, 0 fell; worst sector back (0.747).
