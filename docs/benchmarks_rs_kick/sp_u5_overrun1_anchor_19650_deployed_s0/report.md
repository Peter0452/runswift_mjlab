# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-06-39_u5_overrun1_anchor/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.788** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.09 ± 1.75 (1.74) |
| Direction error [°] | 19.32 ± 39.77 (5.17) |
| Avg ball speed [m/s] | 2.05 ± 0.66 (2.24) |
| Peak ball speed [m/s] | 4.53 ± 1.57 (5.14) |
| Distance [m] | 1.85 ± 0.84 (1.95) |
| Path length [m] | 1.86 ± 0.84 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.795 | 50/50 | 0 | 42 | 1.89 ± 2.23 (1.33) | 8.25 ± 11.57 (3.69) | 2.01 ± 0.66 (2.13) | 4.42 ± 1.57 (4.38) | 1.76 ± 0.83 (1.72) |
| left | p | 0.805 | 49/50 | 0 | 43 | 1.83 ± 1.41 (1.74) | 18.58 ± 35.69 (6.24) | 2.09 ± 0.61 (2.28) | 4.66 ± 1.47 (5.33) | 1.92 ± 0.82 (2.10) |
| back | p | 0.755 | 50/50 | 0 | 40 | 2.55 ± 1.13 (2.50) | 31.29 ± 57.25 (4.76) | 2.07 ± 0.75 (2.34) | 4.54 ± 1.76 (5.23) | 1.90 ± 0.91 (2.05) |
| right | p | 0.796 | 50/50 | 0 | 42 | 2.07 ± 1.91 (1.74) | 19.16 ± 37.00 (5.56) | 2.03 ± 0.60 (2.22) | 4.52 ± 1.46 (5.23) | 1.81 ± 0.77 (1.92) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 100/100 | 0 | 87 | 1.90 ± 1.29 (1.70) | 18.80 ± 40.64 (4.62) | 2.14 ± 0.59 (2.30) | 4.72 ± 1.43 (5.30) | 1.95 ± 0.81 (2.13) |
| right | p | 0.763 | 99/100 | 0 | 80 | 2.28 ± 2.10 (1.76) | 19.85 ± 38.87 (5.39) | 1.96 ± 0.72 (2.16) | 4.35 ± 1.69 (4.63) | 1.74 ± 0.85 (1.80) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 23 | 1.64 ± 1.84 (1.28) | 6.17 ± 10.60 (3.41) | 2.21 ± 0.51 (2.25) | 4.84 ± 1.26 (5.08) | 2.00 ± 0.76 (1.83) |
| forward/right | p | 0.752 | 25/25 | 0 | 19 | 2.14 ± 2.54 (1.36) | 10.33 ± 12.11 (4.77) | 1.81 ± 0.74 (2.01) | 4.00 ± 1.73 (4.13) | 1.53 ± 0.83 (1.60) |
| left/left | p | 0.849 | 25/25 | 0 | 23 | 1.58 ± 0.41 (1.62) | 12.63 ± 22.77 (7.12) | 2.21 ± 0.51 (2.34) | 4.94 ± 1.26 (5.59) | 2.09 ± 0.75 (2.30) |
| left/right | p | 0.761 | 24/25 | 0 | 20 | 2.10 ± 1.94 (1.89) | 24.77 ± 44.56 (6.15) | 1.97 ± 0.68 (2.16) | 4.36 ± 1.61 (5.05) | 1.73 ± 0.85 (1.96) |
| back/left | p | 0.759 | 25/25 | 0 | 20 | 2.58 ± 1.49 (2.48) | 35.58 ± 62.97 (4.22) | 2.08 ± 0.69 (2.28) | 4.57 ± 1.64 (5.16) | 1.90 ± 0.91 (1.93) |
| back/right | p | 0.751 | 25/25 | 0 | 20 | 2.52 ± 0.59 (2.66) | 27.00 ± 50.53 (5.90) | 2.05 ± 0.81 (2.35) | 4.51 ± 1.87 (5.29) | 1.91 ± 0.90 (2.15) |
| right/left | p | 0.805 | 25/25 | 0 | 21 | 1.79 ± 0.50 (1.80) | 20.84 ± 39.07 (5.80) | 2.05 ± 0.60 (2.30) | 4.52 ± 1.47 (5.30) | 1.82 ± 0.77 (2.02) |
| right/right | p | 0.787 | 25/25 | 0 | 21 | 2.36 ± 2.63 (1.72) | 17.48 ± 34.74 (5.17) | 2.02 ± 0.59 (2.16) | 4.52 ± 1.46 (5.17) | 1.81 ± 0.78 (1.76) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.813 | 18.1 | 5.21 | 2.22 |
| p | normal | 0.762 | 20.6 | 3.87 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.721 | 0.15 | 2.23 ± 1.05 (2.11) | 3.48 | 1.27 |
| p | medium | 16 | 0.834 | 0.70 | 1.26 ± 0.20 (1.29) | 4.11 | 1.62 |
| p | strong | 126 | 0.812 | 0.68 | - | 5.08 | 2.15 |

## Notes

- p: score 0.788, 199/200 kicked, 0 fell; worst sector back (0.755).
