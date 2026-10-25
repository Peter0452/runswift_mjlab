# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n4_cont/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.875** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 2.09 ± 1.52 (1.80) |
| Direction error [°] | 13.67 ± 29.15 (4.33) |
| Avg ball speed [m/s] | 2.04 ± 0.60 (2.20) |
| Peak ball speed [m/s] | 4.57 ± 1.44 (5.00) |
| Distance [m] | 1.82 ± 0.74 (1.91) |
| Path length [m] | 1.83 ± 0.74 (1.92) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.888 | 50/50 | 0 | 42 | 1.85 ± 2.18 (1.38) | 10.37 ± 18.23 (3.78) | 2.01 ± 0.62 (2.17) | 4.57 ± 1.51 (5.03) | 1.81 ± 0.80 (1.95) |
| left | p | 0.892 | 50/50 | 0 | 43 | 1.95 ± 1.41 (1.80) | 14.20 ± 26.50 (5.37) | 2.03 ± 0.60 (2.17) | 4.49 ± 1.44 (4.85) | 1.79 ± 0.74 (1.83) |
| back | p | 0.805 | 48/50 | 0 | 43 | 2.76 ± 1.29 (2.64) | 18.48 ± 40.75 (4.91) | 2.08 ± 0.59 (2.28) | 4.68 ± 1.39 (5.22) | 1.86 ± 0.71 (1.99) |
| right | p | 0.916 | 50/50 | 0 | 45 | 1.83 ± 0.47 (1.82) | 11.84 ± 26.47 (3.47) | 2.06 ± 0.57 (2.16) | 4.54 ± 1.39 (4.67) | 1.81 ± 0.70 (1.81) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.872 | 100/100 | 0 | 85 | 2.14 ± 1.65 (1.74) | 16.34 ± 33.05 (4.61) | 1.98 ± 0.64 (2.17) | 4.46 ± 1.54 (5.00) | 1.76 ± 0.76 (1.93) |
| right | p | 0.878 | 98/100 | 0 | 88 | 2.05 ± 1.37 (1.87) | 10.96 ± 24.25 (3.86) | 2.11 ± 0.53 (2.24) | 4.68 ± 1.32 (5.00) | 1.88 ± 0.71 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.902 | 25/25 | 0 | 21 | 1.63 ± 1.81 (1.32) | 11.05 ± 21.65 (3.70) | 1.98 ± 0.56 (2.14) | 4.51 ± 1.37 (4.99) | 1.75 ± 0.74 (1.95) |
| forward/right | p | 0.874 | 25/25 | 0 | 21 | 2.08 ± 2.48 (1.48) | 9.68 ± 13.97 (4.46) | 2.05 ± 0.68 (2.23) | 4.63 ± 1.64 (5.06) | 1.87 ± 0.84 (1.99) |
| left/left | p | 0.895 | 25/25 | 0 | 22 | 2.11 ± 1.91 (1.66) | 9.87 ± 16.24 (5.15) | 2.07 ± 0.59 (2.23) | 4.66 ± 1.41 (5.03) | 1.87 ± 0.64 (1.94) |
| left/right | p | 0.890 | 25/25 | 0 | 21 | 1.80 ± 0.52 (1.96) | 18.52 ± 33.22 (5.85) | 1.99 ± 0.62 (2.14) | 4.32 ± 1.45 (4.36) | 1.72 ± 0.82 (1.73) |
| back/left | p | 0.805 | 25/25 | 0 | 21 | 2.85 ± 1.70 (2.62) | 25.86 ± 46.84 (5.96) | 1.95 ± 0.73 (2.24) | 4.38 ± 1.71 (5.11) | 1.74 ± 0.86 (1.95) |
| back/right | p | 0.806 | 23/25 | 0 | 22 | 2.67 ± 0.57 (2.66) | 10.45 ± 30.93 (4.12) | 2.23 ± 0.30 (2.30) | 5.01 ± 0.80 (5.24) | 1.98 ± 0.47 (2.00) |
| right/left | p | 0.888 | 25/25 | 0 | 21 | 1.97 ± 0.53 (2.06) | 18.55 ± 35.74 (3.64) | 1.93 ± 0.68 (2.14) | 4.28 ± 1.61 (4.39) | 1.68 ± 0.76 (1.79) |
| right/right | p | 0.943 | 25/25 | 0 | 24 | 1.70 ± 0.35 (1.78) | 5.13 ± 5.77 (2.90) | 2.18 ± 0.40 (2.23) | 4.80 ± 1.08 (5.15) | 1.95 ± 0.61 (1.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.863 | 13.7 | 4.97 | 2.02 |
| p | normal | 0.888 | 13.6 | 4.17 | 1.62 |

## Notes

- p: score 0.875, 198/200 kicked, 0 fell; worst sector back (0.805).
