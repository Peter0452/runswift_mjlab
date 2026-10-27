# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_22950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.806** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 177 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 2.11 ± 1.80 (1.69) |
| Direction error [°] | 13.17 ± 27.13 (5.49) |
| Avg ball speed [m/s] | 2.39 ± 0.80 (2.62) |
| Peak ball speed [m/s] | 5.00 ± 1.77 (5.88) |
| Distance [m] | 2.43 ± 1.11 (2.89) |
| Path length [m] | 2.44 ± 1.11 (2.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.823 | 50/50 | 0 | 47 | 1.88 ± 2.18 (1.32) | 6.73 ± 9.54 (4.54) | 2.38 ± 0.82 (2.55) | 4.98 ± 1.81 (5.80) | 2.40 ± 1.10 (2.63) |
| left | p | 0.836 | 50/50 | 0 | 44 | 1.87 ± 1.31 (1.65) | 12.20 ± 24.51 (5.13) | 2.40 ± 0.69 (2.55) | 5.04 ± 1.58 (5.78) | 2.42 ± 1.04 (2.78) |
| back | p | 0.755 | 50/50 | 0 | 41 | 2.78 ± 1.93 (2.59) | 22.89 ± 42.54 (6.82) | 2.40 ± 0.90 (2.73) | 5.03 ± 1.98 (6.00) | 2.52 ± 1.19 (3.04) |
| right | p | 0.810 | 50/50 | 0 | 45 | 1.91 ± 1.46 (1.75) | 10.85 ± 17.32 (5.45) | 2.40 ± 0.77 (2.54) | 4.93 ± 1.71 (5.22) | 2.37 ± 1.09 (2.49) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.807 | 100/100 | 0 | 90 | 2.07 ± 1.65 (1.65) | 13.26 ± 27.59 (5.01) | 2.36 ± 0.87 (2.63) | 4.92 ± 1.91 (5.90) | 2.40 ± 1.15 (2.97) |
| right | p | 0.805 | 100/100 | 0 | 87 | 2.15 ± 1.93 (1.74) | 13.08 ± 26.66 (5.79) | 2.43 ± 0.72 (2.59) | 5.07 ± 1.63 (5.86) | 2.45 ± 1.06 (2.73) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 24 | 1.75 ± 1.76 (1.28) | 5.23 ± 6.85 (3.19) | 2.33 ± 0.88 (2.48) | 4.84 ± 1.93 (5.74) | 2.33 ± 1.15 (2.58) |
| forward/right | p | 0.813 | 25/25 | 0 | 23 | 2.01 ± 2.53 (1.34) | 8.24 ± 11.42 (4.81) | 2.43 ± 0.75 (2.61) | 5.12 ± 1.67 (5.87) | 2.47 ± 1.03 (2.69) |
| left/left | p | 0.860 | 25/25 | 0 | 24 | 2.02 ± 1.77 (1.60) | 5.54 ± 4.95 (3.73) | 2.56 ± 0.49 (2.64) | 5.44 ± 1.21 (5.89) | 2.66 ± 0.84 (2.97) |
| left/right | p | 0.812 | 25/25 | 0 | 20 | 1.73 ± 0.51 (1.78) | 18.85 ± 32.99 (5.88) | 2.24 ± 0.80 (2.26) | 4.65 ± 1.79 (4.39) | 2.18 ± 1.16 (1.84) |
| back/left | p | 0.745 | 25/25 | 0 | 20 | 2.29 ± 0.75 (2.44) | 28.81 ± 45.47 (8.03) | 2.29 ± 1.07 (2.73) | 4.77 ± 2.27 (6.03) | 2.41 ± 1.35 (3.06) |
| back/right | p | 0.766 | 25/25 | 0 | 21 | 3.27 ± 2.54 (2.62) | 16.97 ± 38.49 (5.66) | 2.52 ± 0.69 (2.74) | 5.29 ± 1.58 (5.98) | 2.62 ± 1.00 (3.03) |
| right/left | p | 0.791 | 25/25 | 0 | 22 | 2.21 ± 2.00 (1.94) | 13.45 ± 23.20 (5.02) | 2.27 ± 0.89 (2.39) | 4.64 ± 1.96 (4.53) | 2.20 ± 1.16 (1.93) |
| right/right | p | 0.830 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.56) | 8.25 ± 6.94 (5.85) | 2.53 ± 0.59 (2.70) | 5.23 ± 1.35 (6.10) | 2.55 ± 0.98 (3.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.837 | 14.8 | 5.58 | 2.88 |
| p | normal | 0.775 | 11.5 | 4.41 | 1.98 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.726 | 0.08 | 2.53 ± 1.06 (2.38) | 3.91 | 1.60 |
| p | medium | 20 | 0.849 | 0.68 | 1.29 ± 0.21 (1.32) | 4.13 | 1.71 |
| p | strong | 126 | 0.834 | 0.75 | - | 5.60 | 2.90 |

## Notes

- p: score 0.806, 200/200 kicked, 0 fell; worst sector back (0.755).
