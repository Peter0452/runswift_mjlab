# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.798** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.04 ± 1.62 (1.70) |
| Direction error [°] | 15.22 ± 32.51 (4.74) |
| Avg ball speed [m/s] | 1.96 ± 0.59 (2.09) |
| Peak ball speed [m/s] | 4.86 ± 1.49 (5.21) |
| Distance [m] | 2.14 ± 0.87 (2.22) |
| Path length [m] | 2.15 ± 0.87 (2.22) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.810 | 50/50 | 0 | 44 | 1.52 ± 1.36 (1.30) | 9.46 ± 12.37 (4.83) | 1.84 ± 0.61 (1.93) | 4.68 ± 1.57 (5.07) | 1.98 ± 0.84 (2.06) |
| left | p | 0.843 | 50/50 | 0 | 45 | 1.87 ± 1.31 (1.69) | 10.15 ± 22.10 (3.70) | 2.06 ± 0.46 (2.10) | 5.04 ± 1.17 (5.41) | 2.23 ± 0.74 (2.25) |
| back | p | 0.739 | 49/50 | 0 | 41 | 2.89 ± 1.92 (2.58) | 28.35 ± 53.03 (5.43) | 2.00 ± 0.67 (2.25) | 4.95 ± 1.72 (5.71) | 2.28 ± 1.00 (2.59) |
| right | p | 0.801 | 50/50 | 0 | 42 | 1.92 ± 1.48 (1.73) | 13.16 ± 24.01 (5.82) | 1.92 ± 0.57 (2.03) | 4.76 ± 1.43 (4.88) | 2.06 ± 0.83 (2.06) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 100/100 | 0 | 86 | 2.11 ± 1.85 (1.65) | 16.45 ± 34.57 (4.69) | 1.94 ± 0.61 (2.12) | 4.86 ± 1.55 (5.38) | 2.15 ± 0.90 (2.26) |
| right | p | 0.797 | 99/100 | 0 | 86 | 1.98 ± 1.35 (1.76) | 13.97 ± 30.22 (4.74) | 1.97 ± 0.56 (2.06) | 4.85 ± 1.43 (5.13) | 2.13 ± 0.83 (2.12) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 22 | 1.25 ± 0.28 (1.28) | 8.32 ± 10.23 (4.61) | 1.88 ± 0.59 (1.94) | 4.78 ± 1.53 (5.12) | 2.06 ± 0.85 (2.24) |
| forward/right | p | 0.789 | 25/25 | 0 | 22 | 1.79 ± 1.87 (1.34) | 10.60 ± 14.10 (5.85) | 1.81 ± 0.62 (1.92) | 4.57 ± 1.61 (5.02) | 1.91 ± 0.83 (1.97) |
| left/left | p | 0.860 | 25/25 | 0 | 24 | 2.01 ± 1.78 (1.62) | 4.93 ± 5.26 (3.20) | 2.14 ± 0.36 (2.21) | 5.29 ± 0.92 (5.59) | 2.38 ± 0.62 (2.44) |
| left/right | p | 0.825 | 25/25 | 0 | 21 | 1.73 ± 0.48 (1.80) | 15.37 ± 29.90 (4.30) | 1.97 ± 0.52 (2.06) | 4.80 ± 1.33 (4.76) | 2.08 ± 0.82 (2.18) |
| back/left | p | 0.736 | 25/25 | 0 | 20 | 2.95 ± 2.19 (2.60) | 33.53 ± 55.99 (6.14) | 1.94 ± 0.71 (2.22) | 4.86 ± 1.78 (5.69) | 2.22 ± 1.05 (2.58) |
| back/right | p | 0.742 | 24/25 | 0 | 21 | 2.83 ± 1.58 (2.53) | 22.96 ± 49.18 (4.42) | 2.07 ± 0.63 (2.27) | 5.04 ± 1.65 (5.84) | 2.35 ± 0.93 (2.70) |
| right/left | p | 0.769 | 25/25 | 0 | 20 | 2.22 ± 2.02 (1.86) | 19.01 ± 31.90 (5.98) | 1.82 ± 0.69 (1.93) | 4.52 ± 1.71 (4.70) | 1.94 ± 0.96 (2.04) |
| right/right | p | 0.832 | 25/25 | 0 | 22 | 1.62 ± 0.35 (1.58) | 7.30 ± 8.15 (4.88) | 2.03 ± 0.38 (2.08) | 5.00 ± 1.03 (5.32) | 2.19 ± 0.64 (2.40) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.833 | 13.5 | 5.35 | 2.42 |
| p | normal | 0.763 | 16.9 | 4.37 | 1.86 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.709 | 0.11 | 2.54 ± 1.03 (2.40) | 3.95 | 1.57 |
| p | medium | 20 | 0.851 | 0.63 | 1.37 ± 0.16 (1.36) | 4.41 | 1.85 |
| p | strong | 126 | 0.828 | 0.71 | - | 5.32 | 2.43 |

## Notes

- p: score 0.798, 199/200 kicked, 0 fell; worst sector back (0.739).
