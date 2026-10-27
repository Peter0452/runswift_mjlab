# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_00-23-17_p1b_wrong_dir/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.806** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 180 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.02 ± 1.51 (1.68) |
| Direction error [°] | 12.44 ± 25.27 (5.69) |
| Avg ball speed [m/s] | 2.25 ± 0.61 (2.38) |
| Peak ball speed [m/s] | 4.90 ± 1.45 (5.52) |
| Distance [m] | 2.16 ± 0.83 (2.31) |
| Path length [m] | 2.17 ± 0.83 (2.32) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.824 | 50/50 | 0 | 46 | 1.55 ± 1.47 (1.31) | 7.85 ± 10.88 (4.55) | 2.19 ± 0.66 (2.32) | 4.83 ± 1.58 (5.33) | 2.10 ± 0.85 (2.27) |
| left | p | 0.831 | 50/50 | 0 | 46 | 1.89 ± 1.47 (1.66) | 10.58 ± 18.51 (5.90) | 2.26 ± 0.51 (2.34) | 4.98 ± 1.27 (5.65) | 2.18 ± 0.76 (2.24) |
| back | p | 0.756 | 50/50 | 0 | 42 | 2.70 ± 1.37 (2.45) | 21.87 ± 41.07 (8.01) | 2.32 ± 0.70 (2.44) | 5.00 ± 1.60 (5.72) | 2.28 ± 0.92 (2.53) |
| right | p | 0.815 | 50/50 | 0 | 46 | 1.93 ± 1.48 (1.74) | 9.48 ± 16.85 (4.87) | 2.22 ± 0.52 (2.29) | 4.80 ± 1.31 (4.87) | 2.06 ± 0.76 (2.09) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.805 | 100/100 | 0 | 91 | 2.05 ± 1.61 (1.67) | 12.46 ± 24.63 (5.83) | 2.28 ± 0.61 (2.40) | 4.95 ± 1.43 (5.55) | 2.20 ± 0.84 (2.36) |
| right | p | 0.808 | 100/100 | 0 | 89 | 1.98 ± 1.40 (1.72) | 12.43 ± 25.89 (5.21) | 2.23 ± 0.60 (2.38) | 4.85 ± 1.46 (5.43) | 2.12 ± 0.82 (2.24) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.824 | 25/25 | 0 | 23 | 1.40 ± 0.76 (1.30) | 8.20 ± 11.22 (4.73) | 2.19 ± 0.60 (2.30) | 4.84 ± 1.42 (5.24) | 2.09 ± 0.76 (2.24) |
| forward/right | p | 0.823 | 25/25 | 0 | 23 | 1.69 ± 1.93 (1.34) | 7.50 ± 10.52 (4.38) | 2.20 ± 0.72 (2.39) | 4.83 ± 1.72 (5.49) | 2.11 ± 0.94 (2.30) |
| left/left | p | 0.841 | 25/25 | 0 | 24 | 2.06 ± 2.02 (1.62) | 6.94 ± 6.56 (5.94) | 2.40 ± 0.42 (2.50) | 5.27 ± 1.05 (5.71) | 2.38 ± 0.67 (2.65) |
| left/right | p | 0.820 | 25/25 | 0 | 22 | 1.72 ± 0.47 (1.80) | 14.21 ± 24.82 (5.40) | 2.13 ± 0.56 (2.23) | 4.69 ± 1.39 (4.65) | 1.98 ± 0.79 (1.91) |
| back/left | p | 0.765 | 25/25 | 0 | 22 | 2.52 ± 1.01 (2.44) | 22.14 ± 39.98 (8.11) | 2.37 ± 0.74 (2.53) | 5.05 ± 1.66 (5.75) | 2.35 ± 0.98 (2.70) |
| back/right | p | 0.747 | 25/25 | 0 | 20 | 2.88 ± 1.63 (2.48) | 21.59 ± 42.13 (6.75) | 2.28 ± 0.66 (2.44) | 4.94 ± 1.53 (5.70) | 2.21 ± 0.85 (2.38) |
| right/left | p | 0.791 | 25/25 | 0 | 22 | 2.23 ± 2.02 (2.04) | 12.53 ± 22.75 (4.59) | 2.15 ± 0.59 (2.28) | 4.64 ± 1.46 (4.63) | 1.97 ± 0.82 (1.94) |
| right/right | p | 0.840 | 25/25 | 0 | 24 | 1.62 ± 0.33 (1.58) | 6.42 ± 5.62 (5.12) | 2.30 ± 0.42 (2.30) | 4.96 ± 1.11 (5.63) | 2.16 ± 0.67 (2.27) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.844 | 12.0 | 5.40 | 2.46 |
| p | normal | 0.769 | 12.9 | 4.41 | 1.85 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.720 | 0.09 | 2.62 ± 0.98 (2.37) | 4.06 | 1.62 |
| p | medium | 20 | 0.858 | 0.65 | 1.34 ± 0.19 (1.37) | 4.30 | 1.76 |
| p | strong | 126 | 0.835 | 0.71 | - | 5.36 | 2.45 |

## Notes

- p: score 0.806, 200/200 kicked, 0 fell; worst sector back (0.756).
