# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_12-23-01_u8_timecost1_anchor02/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.786** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.01 ± 1.61 (1.74) |
| Direction error [°] | 20.69 ± 40.50 (4.97) |
| Avg ball speed [m/s] | 2.09 ± 0.69 (2.31) |
| Peak ball speed [m/s] | 4.49 ± 1.59 (5.00) |
| Distance [m] | 1.88 ± 0.87 (1.94) |
| Path length [m] | 1.89 ± 0.88 (1.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.793 | 50/50 | 0 | 41 | 1.82 ± 2.17 (1.34) | 9.64 ± 14.40 (4.37) | 2.05 ± 0.64 (2.15) | 4.38 ± 1.51 (4.32) | 1.80 ± 0.84 (1.81) |
| left | p | 0.798 | 49/50 | 0 | 40 | 1.80 ± 1.12 (1.74) | 20.72 ± 37.25 (4.97) | 2.15 ± 0.68 (2.38) | 4.65 ± 1.57 (5.44) | 1.95 ± 0.89 (2.17) |
| back | p | 0.763 | 50/50 | 0 | 41 | 2.35 ± 0.66 (2.46) | 31.36 ± 56.86 (5.45) | 2.10 ± 0.76 (2.33) | 4.49 ± 1.69 (5.11) | 1.93 ± 0.94 (1.96) |
| right | p | 0.791 | 50/50 | 0 | 41 | 2.07 ± 1.93 (1.74) | 21.03 ± 38.61 (4.93) | 2.07 ± 0.67 (2.28) | 4.46 ± 1.56 (4.96) | 1.83 ± 0.82 (1.96) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.814 | 100/100 | 0 | 86 | 1.85 ± 1.09 (1.74) | 17.64 ± 38.66 (4.85) | 2.20 ± 0.58 (2.34) | 4.73 ± 1.34 (5.24) | 2.00 ± 0.78 (2.06) |
| right | p | 0.758 | 99/100 | 0 | 77 | 2.17 ± 1.99 (1.74) | 23.76 ± 42.04 (5.19) | 1.98 ± 0.77 (2.22) | 4.26 ± 1.77 (4.43) | 1.76 ± 0.95 (1.88) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.834 | 25/25 | 0 | 22 | 1.64 ± 1.86 (1.30) | 6.48 ± 10.56 (2.98) | 2.25 ± 0.50 (2.33) | 4.81 ± 1.19 (5.24) | 2.04 ± 0.71 (2.27) |
| forward/right | p | 0.751 | 25/25 | 0 | 19 | 2.00 ± 2.42 (1.36) | 12.80 ± 16.82 (7.26) | 1.86 ± 0.70 (2.04) | 3.96 ± 1.67 (4.18) | 1.57 ± 0.89 (1.45) |
| left/left | p | 0.850 | 25/25 | 0 | 22 | 1.59 ± 0.41 (1.64) | 12.57 ± 23.17 (4.19) | 2.30 ± 0.54 (2.38) | 4.95 ± 1.25 (5.44) | 2.14 ± 0.76 (2.33) |
| left/right | p | 0.746 | 24/25 | 0 | 18 | 2.01 ± 1.51 (1.90) | 29.21 ± 46.18 (5.44) | 1.99 ± 0.77 (2.28) | 4.33 ± 1.79 (5.20) | 1.76 ± 0.97 (2.02) |
| back/left | p | 0.764 | 25/25 | 0 | 21 | 2.38 ± 0.67 (2.46) | 30.85 ± 58.89 (6.63) | 2.18 ± 0.62 (2.32) | 4.65 ± 1.38 (5.04) | 1.97 ± 0.82 (1.94) |
| back/right | p | 0.761 | 25/25 | 0 | 20 | 2.31 ± 0.64 (2.46) | 31.88 ± 54.75 (5.14) | 2.03 ± 0.87 (2.36) | 4.33 ± 1.94 (5.52) | 1.89 ± 1.04 (2.19) |
| right/left | p | 0.808 | 25/25 | 0 | 21 | 1.78 ± 0.48 (1.80) | 20.67 ± 39.11 (5.00) | 2.09 ± 0.62 (2.30) | 4.50 ± 1.48 (5.12) | 1.86 ± 0.80 (2.02) |
| right/right | p | 0.775 | 25/25 | 0 | 20 | 2.37 ± 2.66 (1.74) | 21.38 ± 38.10 (3.21) | 2.05 ± 0.71 (2.23) | 4.42 ± 1.63 (4.81) | 1.81 ± 0.84 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.810 | 20.3 | 5.09 | 2.21 |
| p | normal | 0.762 | 21.1 | 3.91 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.731 | 0.16 | 2.27 ± 1.04 (2.18) | 3.57 | 1.36 |
| p | medium | 16 | 0.819 | 0.65 | 1.20 ± 0.35 (1.24) | 3.87 | 1.54 |
| p | strong | 126 | 0.807 | 0.67 | - | 5.00 | 2.17 |

## Notes

- p: score 0.786, 199/200 kicked, 0 fell; worst sector back (0.763).
