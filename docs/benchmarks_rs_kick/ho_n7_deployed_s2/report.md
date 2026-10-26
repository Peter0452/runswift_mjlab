# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 23 |
| Time to kick [s] | 1.94 ± 1.35 (1.78) |
| Direction error [°] | 19.57 ± 37.58 (5.49) |
| Avg ball speed [m/s] | 2.22 ± 0.87 (2.50) |
| Peak ball speed [m/s] | 4.69 ± 1.92 (5.51) |
| Distance [m] | 2.26 ± 1.17 (2.50) |
| Path length [m] | 2.27 ± 1.18 (2.51) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.806 | 49/50 | 0 | 44 | 1.65 ± 2.02 (1.26) | 8.82 ± 15.20 (3.84) | 2.29 ± 0.68 (2.25) | 4.84 ± 1.53 (5.26) | 2.25 ± 0.96 (2.52) |
| left | p | 0.791 | 48/50 | 0 | 41 | 1.83 ± 0.76 (1.86) | 13.48 ± 24.39 (5.28) | 2.33 ± 0.72 (2.52) | 4.91 ± 1.62 (5.53) | 2.37 ± 1.04 (2.50) |
| back | p | 0.741 | 50/50 | 0 | 38 | 2.53 ± 1.26 (2.47) | 31.46 ± 51.72 (7.41) | 2.17 ± 1.07 (2.71) | 4.56 ± 2.31 (5.95) | 2.30 ± 1.41 (2.90) |
| right | p | 0.783 | 49/50 | 0 | 38 | 1.72 ± 0.73 (1.76) | 24.16 ± 42.28 (5.89) | 2.11 ± 0.94 (2.33) | 4.46 ± 2.06 (5.47) | 2.12 ± 1.22 (2.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.793 | 99/100 | 0 | 83 | 1.90 ± 1.27 (1.74) | 20.60 ± 38.97 (6.27) | 2.27 ± 0.85 (2.53) | 4.82 ± 1.89 (5.59) | 2.35 ± 1.19 (2.52) |
| right | p | 0.767 | 97/100 | 0 | 78 | 1.98 ± 1.43 (1.82) | 18.53 ± 36.07 (5.08) | 2.18 ± 0.89 (2.36) | 4.56 ± 1.94 (4.48) | 2.17 ± 1.15 (2.04) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.810 | 25/25 | 0 | 23 | 1.65 ± 2.00 (1.34) | 10.10 ± 18.23 (5.45) | 2.21 ± 0.67 (2.16) | 4.70 ± 1.56 (4.23) | 2.18 ± 0.98 (1.88) |
| forward/right | p | 0.801 | 24/25 | 0 | 21 | 1.66 ± 2.04 (1.23) | 7.49 ± 11.05 (3.01) | 2.38 ± 0.68 (2.56) | 4.99 ± 1.47 (5.64) | 2.33 ± 0.92 (2.73) |
| left/left | p | 0.798 | 24/25 | 0 | 21 | 1.80 ± 0.99 (1.74) | 11.17 ± 18.69 (5.93) | 2.41 ± 0.65 (2.65) | 5.11 ± 1.45 (5.71) | 2.50 ± 0.99 (2.64) |
| left/right | p | 0.784 | 24/25 | 0 | 20 | 1.86 ± 0.43 (1.87) | 15.79 ± 28.82 (5.23) | 2.25 ± 0.77 (2.42) | 4.71 ± 1.74 (4.88) | 2.24 ± 1.06 (2.15) |
| back/left | p | 0.768 | 25/25 | 0 | 20 | 2.26 ± 0.63 (2.44) | 27.47 ± 45.33 (8.15) | 2.37 ± 1.00 (2.96) | 4.98 ± 2.14 (6.19) | 2.56 ± 1.37 (3.29) |
| back/right | p | 0.713 | 25/25 | 0 | 18 | 2.79 ± 1.63 (2.48) | 35.44 ± 57.13 (5.47) | 1.96 ± 1.11 (2.20) | 4.14 ± 2.40 (4.40) | 2.04 ± 1.39 (1.95) |
| right/left | p | 0.795 | 25/25 | 0 | 19 | 1.86 ± 0.92 (1.80) | 33.26 ± 53.75 (6.27) | 2.09 ± 0.98 (2.52) | 4.51 ± 2.19 (5.54) | 2.15 ± 1.29 (2.42) |
| right/right | p | 0.772 | 24/25 | 0 | 19 | 1.57 ± 0.42 (1.63) | 14.68 ± 21.54 (5.68) | 2.13 ± 0.89 (2.17) | 4.41 ± 1.90 (4.31) | 2.09 ± 1.13 (1.92) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.811 | 18.2 | 5.35 | 2.72 |
| p | normal | 0.749 | 20.9 | 4.03 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.717 | 0.17 | 2.13 ± 0.98 (2.08) | 3.61 | 1.49 |
| p | medium | 15 | 0.792 | 0.58 | 0.96 ± 0.50 (1.16) | 3.11 | 1.23 |
| p | strong | 125 | 0.809 | 0.72 | - | 5.41 | 2.76 |

## Notes

- p: score 0.780, 196/200 kicked, 0 fell; worst sector back (0.741).
