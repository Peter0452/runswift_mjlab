# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 8 |
| Time to kick [s] | 1.97 ± 1.49 (1.72) |
| Direction error [°] | 17.28 ± 36.54 (5.08) |
| Avg ball speed [m/s] | 1.94 ± 0.54 (2.08) |
| Peak ball speed [m/s] | 4.53 ± 1.34 (4.81) |
| Distance [m] | 1.80 ± 0.74 (1.90) |
| Path length [m] | 1.81 ± 0.74 (1.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.794 | 50/50 | 0 | 44 | 1.81 ± 2.16 (1.33) | 8.37 ± 10.04 (5.13) | 1.89 ± 0.57 (2.02) | 4.38 ± 1.45 (4.26) | 1.71 ± 0.78 (1.69) |
| left | p | 0.812 | 48/50 | 0 | 42 | 1.71 ± 0.44 (1.79) | 14.93 ± 31.45 (4.14) | 2.06 ± 0.52 (2.15) | 4.86 ± 1.24 (5.22) | 2.01 ± 0.72 (2.10) |
| back | p | 0.733 | 48/50 | 0 | 41 | 2.52 ± 1.29 (2.48) | 26.58 ± 53.83 (5.82) | 1.94 ± 0.54 (2.14) | 4.53 ± 1.34 (4.98) | 1.79 ± 0.70 (2.01) |
| right | p | 0.776 | 49/50 | 0 | 40 | 1.83 ± 1.35 (1.74) | 19.58 ± 35.05 (5.41) | 1.86 ± 0.52 (2.02) | 4.36 ± 1.26 (4.58) | 1.69 ± 0.71 (1.77) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.806 | 99/100 | 0 | 86 | 1.83 ± 1.07 (1.72) | 16.32 ± 35.79 (4.93) | 1.96 ± 0.51 (2.12) | 4.60 ± 1.27 (4.95) | 1.83 ± 0.72 (2.00) |
| right | p | 0.751 | 96/100 | 0 | 81 | 2.11 ± 1.81 (1.73) | 18.28 ± 37.28 (5.51) | 1.91 ± 0.57 (2.04) | 4.46 ± 1.40 (4.67) | 1.76 ± 0.75 (1.82) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.811 | 25/25 | 0 | 23 | 1.62 ± 1.83 (1.30) | 8.03 ± 10.81 (4.65) | 1.90 ± 0.53 (2.08) | 4.47 ± 1.38 (4.64) | 1.75 ± 0.73 (1.78) |
| forward/right | p | 0.776 | 25/25 | 0 | 21 | 2.01 ± 2.43 (1.34) | 8.72 ± 9.18 (5.62) | 1.87 ± 0.61 (1.90) | 4.29 ± 1.51 (4.11) | 1.66 ± 0.83 (1.60) |
| left/left | p | 0.871 | 25/25 | 0 | 23 | 1.63 ± 0.37 (1.72) | 7.81 ± 16.14 (3.89) | 2.14 ± 0.44 (2.18) | 5.00 ± 1.05 (5.22) | 2.09 ± 0.62 (2.12) |
| left/right | p | 0.752 | 23/25 | 0 | 19 | 1.80 ± 0.48 (1.94) | 22.67 ± 40.81 (5.42) | 1.97 ± 0.58 (2.12) | 4.71 ± 1.40 (5.21) | 1.92 ± 0.81 (2.09) |
| back/left | p | 0.747 | 24/25 | 0 | 21 | 2.38 ± 0.68 (2.50) | 24.60 ± 51.85 (5.06) | 2.01 ± 0.40 (2.13) | 4.70 ± 0.99 (5.00) | 1.87 ± 0.64 (2.10) |
| back/right | p | 0.720 | 24/25 | 0 | 20 | 2.67 ± 1.68 (2.47) | 28.55 ± 55.67 (6.54) | 1.86 ± 0.64 (2.15) | 4.36 ± 1.59 (4.96) | 1.72 ± 0.75 (1.96) |
| right/left | p | 0.794 | 25/25 | 0 | 19 | 1.73 ± 0.49 (1.78) | 25.18 ± 42.76 (5.43) | 1.79 ± 0.59 (2.02) | 4.24 ± 1.47 (4.64) | 1.63 ± 0.81 (1.82) |
| right/right | p | 0.757 | 24/25 | 0 | 21 | 1.95 ± 1.86 (1.61) | 13.74 ± 23.16 (4.83) | 1.94 ± 0.42 (1.94) | 4.48 ± 0.98 (4.55) | 1.76 ± 0.58 (1.72) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.801 | 16.5 | 5.07 | 2.09 |
| p | normal | 0.756 | 18.0 | 4.01 | 1.52 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.716 | 0.15 | 2.34 ± 0.98 (2.25) | 3.68 | 1.33 |
| p | medium | 16 | 0.813 | 0.69 | 1.29 ± 0.22 (1.34) | 4.17 | 1.62 |
| p | strong | 126 | 0.803 | 0.66 | - | 4.98 | 2.04 |

## Notes

- p: score 0.779, 195/200 kicked, 0 fell; worst sector back (0.733).
