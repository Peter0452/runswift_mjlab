# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_13-42-50_u10_u6_seed11/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.00 ± 1.68 (1.69) |
| Direction error [°] | 19.22 ± 37.40 (6.00) |
| Avg ball speed [m/s] | 2.03 ± 0.69 (2.23) |
| Peak ball speed [m/s] | 4.51 ± 1.67 (5.11) |
| Distance [m] | 1.84 ± 0.86 (1.96) |
| Path length [m] | 1.85 ± 0.87 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.790 | 50/50 | 0 | 42 | 1.63 ± 1.68 (1.31) | 10.69 ± 16.10 (5.70) | 1.95 ± 0.74 (2.10) | 4.29 ± 1.78 (4.26) | 1.72 ± 0.90 (1.66) |
| left | p | 0.805 | 49/50 | 0 | 42 | 1.82 ± 1.49 (1.68) | 18.07 ± 34.83 (5.56) | 2.03 ± 0.66 (2.26) | 4.57 ± 1.63 (5.30) | 1.83 ± 0.83 (1.99) |
| back | p | 0.744 | 50/50 | 0 | 41 | 2.69 ± 1.84 (2.48) | 29.39 ± 51.81 (7.46) | 2.10 ± 0.74 (2.35) | 4.61 ± 1.71 (5.57) | 1.97 ± 0.89 (2.30) |
| right | p | 0.792 | 49/50 | 0 | 40 | 1.87 ± 1.46 (1.72) | 18.71 ± 35.43 (4.32) | 2.05 ± 0.63 (2.22) | 4.57 ± 1.55 (5.20) | 1.84 ± 0.81 (1.96) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 100/100 | 0 | 84 | 1.84 ± 1.16 (1.68) | 18.42 ± 36.98 (6.20) | 2.08 ± 0.63 (2.28) | 4.62 ± 1.53 (5.31) | 1.89 ± 0.81 (1.98) |
| right | p | 0.763 | 98/100 | 0 | 81 | 2.17 ± 2.06 (1.72) | 20.04 ± 37.81 (5.97) | 1.99 ± 0.75 (2.17) | 4.40 ± 1.80 (4.78) | 1.79 ± 0.91 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 21 | 1.32 ± 0.48 (1.30) | 9.53 ± 14.16 (4.19) | 2.08 ± 0.66 (2.19) | 4.61 ± 1.59 (4.41) | 1.88 ± 0.84 (1.79) |
| forward/right | p | 0.762 | 25/25 | 0 | 21 | 1.93 ± 2.29 (1.32) | 11.86 ± 17.75 (6.45) | 1.82 ± 0.80 (2.02) | 3.97 ± 1.90 (4.06) | 1.57 ± 0.93 (1.62) |
| left/left | p | 0.836 | 25/25 | 0 | 22 | 1.55 ± 0.39 (1.60) | 13.08 ± 22.69 (6.65) | 2.07 ± 0.63 (2.22) | 4.63 ± 1.55 (5.30) | 1.88 ± 0.78 (1.96) |
| left/right | p | 0.774 | 24/25 | 0 | 20 | 2.10 ± 2.06 (1.84) | 23.27 ± 43.45 (3.59) | 2.00 ± 0.69 (2.28) | 4.51 ± 1.71 (5.32) | 1.78 ± 0.88 (2.00) |
| back/left | p | 0.745 | 25/25 | 0 | 21 | 2.72 ± 1.90 (2.48) | 30.62 ± 54.79 (7.18) | 2.14 ± 0.61 (2.34) | 4.70 ± 1.46 (5.57) | 1.99 ± 0.80 (2.35) |
| back/right | p | 0.743 | 25/25 | 0 | 20 | 2.66 ± 1.77 (2.48) | 28.15 ± 48.61 (7.76) | 2.06 ± 0.84 (2.36) | 4.51 ± 1.92 (5.56) | 1.95 ± 0.97 (2.25) |
| right/left | p | 0.813 | 25/25 | 0 | 20 | 1.76 ± 0.48 (1.74) | 20.47 ± 38.62 (4.27) | 2.03 ± 0.61 (2.21) | 4.52 ± 1.53 (5.09) | 1.79 ± 0.81 (1.92) |
| right/right | p | 0.771 | 24/25 | 0 | 20 | 1.99 ± 2.03 (1.67) | 16.88 ± 31.66 (4.47) | 2.07 ± 0.64 (2.28) | 4.63 ± 1.56 (5.30) | 1.88 ± 0.80 (2.10) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.806 | 18.0 | 5.14 | 2.20 |
| p | normal | 0.760 | 20.5 | 3.89 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.720 | 0.16 | 2.24 ± 1.05 (2.10) | 3.53 | 1.30 |
| p | medium | 16 | 0.819 | 0.70 | 1.26 ± 0.22 (1.28) | 4.09 | 1.60 |
| p | strong | 126 | 0.807 | 0.67 | - | 5.02 | 2.12 |

## Notes

- p: score 0.783, 198/200 kicked, 0 fell; worst sector back (0.744).
