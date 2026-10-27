# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.776** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 2.18 ± 1.98 (1.72) |
| Direction error [°] | 17.96 ± 37.73 (4.45) |
| Avg ball speed [m/s] | 1.95 ± 0.57 (2.10) |
| Peak ball speed [m/s] | 4.51 ± 1.37 (4.90) |
| Distance [m] | 1.82 ± 0.74 (1.92) |
| Path length [m] | 1.83 ± 0.74 (1.94) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.798 | 50/50 | 0 | 44 | 1.87 ± 2.16 (1.33) | 8.15 ± 11.43 (3.83) | 1.90 ± 0.58 (2.03) | 4.38 ± 1.41 (4.45) | 1.73 ± 0.76 (1.85) |
| left | p | 0.813 | 50/50 | 0 | 42 | 2.06 ± 2.00 (1.72) | 17.20 ± 32.73 (4.45) | 1.96 ± 0.56 (2.13) | 4.58 ± 1.35 (5.00) | 1.84 ± 0.73 (1.94) |
| back | p | 0.734 | 48/50 | 0 | 41 | 2.68 ± 1.65 (2.49) | 27.85 ± 56.78 (5.09) | 2.02 ± 0.58 (2.13) | 4.65 ± 1.36 (5.17) | 1.95 ± 0.73 (2.04) |
| right | p | 0.759 | 49/50 | 0 | 40 | 2.15 ± 2.00 (1.72) | 19.06 ± 33.79 (5.20) | 1.92 ± 0.56 (2.02) | 4.45 ± 1.34 (4.76) | 1.78 ± 0.73 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.800 | 99/100 | 0 | 85 | 1.92 ± 1.36 (1.68) | 16.43 ± 35.85 (4.08) | 1.97 ± 0.48 (2.10) | 4.59 ± 1.17 (5.03) | 1.85 ± 0.66 (1.96) |
| right | p | 0.752 | 98/100 | 0 | 82 | 2.44 ± 2.43 (1.74) | 19.50 ± 39.47 (5.09) | 1.93 ± 0.65 (2.10) | 4.44 ± 1.54 (4.79) | 1.80 ± 0.81 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.830 | 25/25 | 0 | 23 | 1.61 ± 1.63 (1.28) | 6.58 ± 11.44 (3.39) | 2.01 ± 0.42 (2.10) | 4.67 ± 1.11 (4.70) | 1.87 ± 0.63 (1.96) |
| forward/right | p | 0.765 | 25/25 | 0 | 21 | 2.12 ± 2.55 (1.36) | 9.71 ± 11.20 (5.85) | 1.80 ± 0.68 (1.87) | 4.08 ± 1.61 (4.10) | 1.59 ± 0.85 (1.61) |
| left/left | p | 0.843 | 25/25 | 0 | 21 | 1.55 ± 0.41 (1.62) | 13.37 ± 24.31 (5.89) | 1.93 ± 0.55 (2.02) | 4.51 ± 1.32 (4.92) | 1.81 ± 0.70 (1.86) |
| left/right | p | 0.783 | 25/25 | 0 | 21 | 2.58 ± 2.71 (1.96) | 21.02 ± 39.02 (4.24) | 1.99 ± 0.57 (2.16) | 4.65 ± 1.37 (5.16) | 1.86 ± 0.76 (1.96) |
| back/left | p | 0.765 | 25/25 | 0 | 22 | 2.74 ± 1.82 (2.54) | 23.46 ± 51.06 (5.20) | 2.09 ± 0.39 (2.21) | 4.81 ± 0.87 (5.22) | 2.01 ± 0.58 (2.09) |
| back/right | p | 0.703 | 23/25 | 0 | 19 | 2.61 ± 1.43 (2.44) | 32.61 ± 62.06 (4.67) | 1.94 ± 0.72 (2.09) | 4.49 ± 1.73 (4.97) | 1.89 ± 0.85 (1.95) |
| right/left | p | 0.761 | 24/25 | 0 | 19 | 1.80 ± 0.54 (1.75) | 22.54 ± 40.43 (4.15) | 1.86 ± 0.50 (2.01) | 4.38 ± 1.27 (4.78) | 1.70 ± 0.70 (1.91) |
| right/right | p | 0.758 | 25/25 | 0 | 21 | 2.48 ± 2.70 (1.64) | 15.72 ± 25.41 (5.44) | 1.97 ± 0.61 (2.06) | 4.53 ± 1.39 (4.74) | 1.86 ± 0.74 (1.88) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.811 | 15.9 | 5.09 | 2.11 |
| p | normal | 0.741 | 20.0 | 3.94 | 1.54 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.703 | 0.18 | 2.29 ± 1.04 (2.13) | 3.60 | 1.34 |
| p | medium | 16 | 0.823 | 0.65 | 1.35 ± 0.19 (1.35) | 4.39 | 1.80 |
| p | strong | 126 | 0.804 | 0.66 | - | 4.95 | 2.05 |

## Notes

- p: score 0.776, 197/200 kicked, 0 fell; worst sector back (0.734).
