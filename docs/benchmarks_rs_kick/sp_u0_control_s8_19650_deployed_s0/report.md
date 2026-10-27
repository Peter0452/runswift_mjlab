# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_08-10-04_u0_control_s8/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.780** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 162 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.83 ± 1.20 (1.64) |
| Direction error [°] | 19.10 ± 38.15 (4.86) |
| Avg ball speed [m/s] | 2.15 ± 0.75 (2.28) |
| Peak ball speed [m/s] | 4.62 ± 1.70 (5.09) |
| Distance [m] | 1.98 ± 0.98 (1.97) |
| Path length [m] | 1.99 ± 0.98 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.784 | 49/50 | 0 | 40 | 1.60 ± 1.76 (1.30) | 10.32 ± 15.39 (5.92) | 1.99 ± 0.75 (2.14) | 4.28 ± 1.73 (4.16) | 1.76 ± 0.93 (1.60) |
| left | p | 0.792 | 48/50 | 0 | 40 | 1.61 ± 0.49 (1.67) | 19.97 ± 35.62 (5.00) | 2.20 ± 0.74 (2.28) | 4.77 ± 1.66 (5.25) | 2.07 ± 0.98 (2.19) |
| back | p | 0.757 | 49/50 | 0 | 41 | 2.44 ± 1.29 (2.42) | 29.62 ± 55.56 (5.77) | 2.26 ± 0.83 (2.50) | 4.82 ± 1.85 (5.74) | 2.18 ± 1.09 (2.47) |
| right | p | 0.788 | 48/50 | 0 | 41 | 1.65 ± 0.47 (1.71) | 16.44 ± 31.95 (4.09) | 2.13 ± 0.66 (2.21) | 4.59 ± 1.50 (4.76) | 1.91 ± 0.85 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.812 | 100/100 | 0 | 87 | 1.87 ± 1.28 (1.67) | 17.43 ± 36.61 (4.54) | 2.19 ± 0.70 (2.33) | 4.71 ± 1.62 (5.27) | 2.03 ± 0.93 (2.15) |
| right | p | 0.748 | 94/100 | 0 | 75 | 1.79 ± 1.11 (1.61) | 20.87 ± 39.64 (5.46) | 2.11 ± 0.80 (2.26) | 4.52 ± 1.79 (4.54) | 1.93 ± 1.02 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.825 | 25/25 | 0 | 23 | 1.55 ± 1.59 (1.26) | 6.65 ± 9.84 (4.19) | 2.15 ± 0.61 (2.28) | 4.61 ± 1.45 (4.34) | 1.92 ± 0.78 (1.79) |
| forward/right | p | 0.743 | 24/25 | 0 | 17 | 1.65 ± 1.92 (1.34) | 14.15 ± 18.81 (6.98) | 1.84 ± 0.84 (1.98) | 3.94 ± 1.93 (3.99) | 1.59 ± 1.03 (1.53) |
| left/left | p | 0.849 | 25/25 | 0 | 22 | 1.54 ± 0.41 (1.64) | 13.01 ± 22.48 (4.79) | 2.31 ± 0.70 (2.55) | 4.97 ± 1.61 (5.65) | 2.23 ± 0.93 (2.47) |
| left/right | p | 0.734 | 23/25 | 0 | 18 | 1.69 ± 0.55 (1.76) | 27.53 ± 44.60 (6.78) | 2.09 ± 0.76 (2.23) | 4.54 ± 1.68 (5.08) | 1.90 ± 1.00 (2.06) |
| back/left | p | 0.767 | 25/25 | 0 | 21 | 2.64 ± 1.67 (2.46) | 29.35 ± 54.77 (6.47) | 2.24 ± 0.75 (2.55) | 4.82 ± 1.70 (5.74) | 2.13 ± 1.04 (2.47) |
| back/right | p | 0.747 | 24/25 | 0 | 20 | 2.24 ± 0.63 (2.37) | 29.90 ± 56.38 (5.03) | 2.28 ± 0.90 (2.50) | 4.82 ± 2.00 (5.75) | 2.23 ± 1.13 (2.46) |
| right/left | p | 0.806 | 25/25 | 0 | 21 | 1.74 ± 0.51 (1.74) | 20.71 ± 38.35 (4.45) | 2.05 ± 0.73 (2.19) | 4.43 ± 1.65 (4.34) | 1.82 ± 0.91 (1.75) |
| right/right | p | 0.770 | 23/25 | 0 | 20 | 1.55 ± 0.41 (1.56) | 11.79 ± 22.13 (3.35) | 2.22 ± 0.57 (2.27) | 4.77 ± 1.30 (4.85) | 2.01 ± 0.77 (1.93) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.803 | 18.3 | 5.28 | 2.38 |
| p | normal | 0.757 | 19.9 | 3.97 | 1.58 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.18 | 2.22 ± 1.00 (2.11) | 3.54 | 1.32 |
| p | medium | 16 | 0.800 | 0.68 | 1.25 ± 0.26 (1.25) | 4.03 | 1.62 |
| p | strong | 126 | 0.806 | 0.69 | - | 5.19 | 2.33 |

## Notes

- p: score 0.780, 194/200 kicked, 0 fell; worst sector back (0.757).
