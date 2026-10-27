# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_22450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.05 ± 1.69 (1.73) |
| Direction error [°] | 19.65 ± 39.03 (5.20) |
| Avg ball speed [m/s] | 2.04 ± 0.66 (2.25) |
| Peak ball speed [m/s] | 4.50 ± 1.56 (5.07) |
| Distance [m] | 1.82 ± 0.82 (1.95) |
| Path length [m] | 1.83 ± 0.82 (1.96) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.796 | 50/50 | 0 | 43 | 1.71 ± 1.86 (1.33) | 10.19 ± 17.03 (4.32) | 1.95 ± 0.71 (2.14) | 4.23 ± 1.67 (4.31) | 1.69 ± 0.86 (1.69) |
| left | p | 0.794 | 49/50 | 0 | 40 | 1.78 ± 1.02 (1.70) | 22.19 ± 37.98 (5.23) | 2.02 ± 0.69 (2.29) | 4.53 ± 1.66 (5.38) | 1.82 ± 0.84 (2.12) |
| back | p | 0.741 | 49/50 | 0 | 41 | 2.65 ± 1.62 (2.46) | 30.07 ± 56.33 (5.89) | 2.13 ± 0.65 (2.32) | 4.65 ± 1.52 (5.38) | 1.95 ± 0.83 (2.17) |
| right | p | 0.800 | 50/50 | 0 | 43 | 2.08 ± 1.93 (1.74) | 16.39 ± 31.73 (5.50) | 2.08 ± 0.54 (2.19) | 4.57 ± 1.34 (5.04) | 1.83 ± 0.72 (1.85) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 99/100 | 0 | 85 | 1.75 ± 0.62 (1.70) | 19.57 ± 40.15 (4.46) | 2.05 ± 0.65 (2.26) | 4.52 ± 1.53 (5.08) | 1.83 ± 0.80 (2.00) |
| right | p | 0.762 | 99/100 | 0 | 82 | 2.36 ± 2.27 (1.74) | 19.72 ± 37.87 (5.58) | 2.03 ± 0.66 (2.25) | 4.47 ± 1.59 (5.06) | 1.81 ± 0.83 (1.93) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.814 | 25/25 | 0 | 22 | 1.31 ± 0.38 (1.30) | 11.92 ± 21.28 (4.38) | 1.96 ± 0.70 (2.14) | 4.28 ± 1.63 (4.39) | 1.71 ± 0.83 (1.70) |
| forward/right | p | 0.779 | 25/25 | 0 | 21 | 2.11 ± 2.54 (1.38) | 8.45 ± 11.03 (4.27) | 1.94 ± 0.72 (2.12) | 4.19 ± 1.70 (4.20) | 1.67 ± 0.90 (1.65) |
| left/left | p | 0.843 | 25/25 | 0 | 22 | 1.56 ± 0.42 (1.64) | 15.08 ± 27.42 (5.63) | 2.08 ± 0.64 (2.29) | 4.65 ± 1.52 (5.38) | 1.90 ± 0.75 (2.07) |
| left/right | p | 0.745 | 24/25 | 0 | 18 | 2.00 ± 1.36 (1.98) | 29.60 ± 45.32 (5.13) | 1.96 ± 0.74 (2.28) | 4.41 ± 1.77 (5.42) | 1.74 ± 0.91 (2.20) |
| back/left | p | 0.742 | 24/25 | 0 | 20 | 2.32 ± 0.66 (2.44) | 31.70 ± 59.46 (5.47) | 2.12 ± 0.64 (2.34) | 4.66 ± 1.48 (5.33) | 1.94 ± 0.83 (2.12) |
| back/right | p | 0.740 | 25/25 | 0 | 21 | 2.96 ± 2.12 (2.48) | 28.52 ± 53.10 (6.98) | 2.13 ± 0.66 (2.32) | 4.64 ± 1.56 (5.41) | 1.95 ± 0.83 (2.20) |
| right/left | p | 0.814 | 25/25 | 0 | 21 | 1.82 ± 0.51 (1.80) | 20.07 ± 39.58 (2.86) | 2.05 ± 0.59 (2.18) | 4.51 ± 1.46 (5.02) | 1.79 ± 0.78 (1.82) |
| right/right | p | 0.785 | 25/25 | 0 | 22 | 2.34 ± 2.66 (1.62) | 12.72 ± 20.50 (6.89) | 2.10 ± 0.49 (2.20) | 4.63 ± 1.21 (5.06) | 1.87 ± 0.65 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.816 | 16.7 | 5.15 | 2.15 |
| p | normal | 0.750 | 22.5 | 3.86 | 1.50 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.16 | 2.21 ± 1.09 (2.14) | 3.47 | 1.29 |
| p | medium | 16 | 0.812 | 0.63 | 1.23 ± 0.35 (1.27) | 3.98 | 1.59 |
| p | strong | 126 | 0.812 | 0.67 | - | 5.04 | 2.10 |

## Notes

- p: score 0.783, 198/200 kicked, 0 fell; worst sector back (0.741).
