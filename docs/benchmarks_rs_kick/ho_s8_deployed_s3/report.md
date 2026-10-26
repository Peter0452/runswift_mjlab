# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.787** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 175 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.19 ± 1.96 (1.74) |
| Direction error [°] | 15.27 ± 31.79 (5.40) |
| Avg ball speed [m/s] | 2.22 ± 0.69 (2.37) |
| Peak ball speed [m/s] | 4.75 ± 1.57 (5.39) |
| Distance [m] | 2.12 ± 0.91 (2.25) |
| Path length [m] | 2.13 ± 0.92 (2.25) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.823 | 50/50 | 0 | 45 | 1.64 ± 1.89 (1.30) | 9.29 ± 16.23 (4.81) | 2.22 ± 0.66 (2.37) | 4.77 ± 1.53 (5.29) | 2.09 ± 0.89 (2.33) |
| left | p | 0.815 | 50/50 | 0 | 44 | 1.81 ± 0.77 (1.74) | 14.08 ± 28.57 (5.25) | 2.22 ± 0.67 (2.45) | 4.81 ± 1.55 (5.47) | 2.15 ± 0.89 (2.37) |
| back | p | 0.750 | 50/50 | 0 | 45 | 2.93 ± 2.04 (2.53) | 19.07 ± 38.61 (7.00) | 2.34 ± 0.66 (2.42) | 4.90 ± 1.50 (5.52) | 2.25 ± 0.92 (2.22) |
| right | p | 0.758 | 49/50 | 0 | 41 | 2.38 ± 2.46 (1.86) | 18.70 ± 37.65 (4.34) | 2.12 ± 0.74 (2.31) | 4.51 ± 1.66 (4.57) | 1.97 ± 0.93 (2.01) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 100/100 | 0 | 90 | 1.89 ± 0.94 (1.74) | 13.22 ± 29.26 (5.54) | 2.26 ± 0.65 (2.34) | 4.83 ± 1.50 (5.45) | 2.17 ± 0.90 (2.29) |
| right | p | 0.762 | 99/100 | 0 | 85 | 2.50 ± 2.57 (1.78) | 17.34 ± 34.03 (5.16) | 2.19 ± 0.73 (2.38) | 4.66 ± 1.63 (5.25) | 2.07 ± 0.93 (2.20) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.825 | 25/25 | 0 | 22 | 1.28 ± 0.30 (1.30) | 10.08 ± 15.54 (5.85) | 2.09 ± 0.74 (2.26) | 4.51 ± 1.74 (4.39) | 1.97 ± 0.97 (1.91) |
| forward/right | p | 0.822 | 25/25 | 0 | 23 | 2.01 ± 2.60 (1.30) | 8.50 ± 16.85 (2.80) | 2.34 ± 0.54 (2.46) | 5.02 ± 1.24 (5.46) | 2.21 ± 0.79 (2.36) |
| left/left | p | 0.815 | 25/25 | 0 | 22 | 1.77 ± 0.84 (1.66) | 10.13 ± 15.93 (5.41) | 2.27 ± 0.64 (2.52) | 4.90 ± 1.52 (5.66) | 2.22 ± 0.91 (2.57) |
| left/right | p | 0.816 | 25/25 | 0 | 22 | 1.84 ± 0.69 (1.78) | 18.03 ± 36.70 (4.91) | 2.17 ± 0.70 (2.45) | 4.71 ± 1.57 (5.44) | 2.09 ± 0.86 (2.33) |
| back/left | p | 0.803 | 25/25 | 0 | 24 | 2.52 ± 0.46 (2.52) | 11.49 ± 27.04 (6.76) | 2.47 ± 0.49 (2.54) | 5.21 ± 1.19 (5.69) | 2.44 ± 0.81 (2.74) |
| back/right | p | 0.697 | 25/25 | 0 | 21 | 3.34 ± 2.78 (2.64) | 26.65 ± 46.20 (7.73) | 2.20 ± 0.77 (2.37) | 4.59 ± 1.71 (4.73) | 2.07 ± 0.99 (1.93) |
| right/left | p | 0.803 | 25/25 | 0 | 22 | 1.98 ± 1.33 (1.82) | 21.17 ± 45.97 (4.34) | 2.19 ± 0.62 (2.31) | 4.70 ± 1.41 (5.22) | 2.04 ± 0.83 (2.27) |
| right/right | p | 0.713 | 24/25 | 0 | 19 | 2.79 ± 3.18 (1.88) | 16.12 ± 26.07 (3.91) | 2.04 ± 0.84 (2.23) | 4.32 ± 1.87 (4.47) | 1.90 ± 1.02 (1.92) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.831 | 12.4 | 5.30 | 2.47 |
| p | normal | 0.742 | 18.2 | 4.19 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.713 | 0.09 | 2.48 ± 1.04 (2.42) | 3.89 | 1.57 |
| p | medium | 18 | 0.813 | 0.61 | 1.16 ± 0.41 (1.33) | 3.75 | 1.49 |
| p | strong | 124 | 0.817 | 0.71 | - | 5.30 | 2.47 |

## Notes

- p: score 0.787, 199/200 kicked, 0 fell; worst sector back (0.750).
