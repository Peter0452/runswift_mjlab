# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_07-58-51_night_n3_aim025/model_19448.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.850** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 1.87 ± 1.07 (1.74) |
| Direction error [°] | 17.69 ± 35.93 (5.46) |
| Avg ball speed [m/s] | 2.08 ± 0.64 (2.26) |
| Peak ball speed [m/s] | 4.43 ± 1.47 (4.75) |
| Distance [m] | 1.76 ± 0.75 (1.89) |
| Path length [m] | 1.77 ± 0.75 (1.89) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.851 | 49/50 | 0 | 39 | 1.74 ± 1.83 (1.36) | 10.83 ± 13.04 (5.21) | 1.92 ± 0.67 (2.13) | 4.10 ± 1.57 (4.27) | 1.54 ± 0.75 (1.66) |
| left | p | 0.862 | 48/50 | 0 | 41 | 1.69 ± 0.48 (1.81) | 18.07 ± 34.79 (5.71) | 2.12 ± 0.65 (2.29) | 4.59 ± 1.49 (5.31) | 1.86 ± 0.77 (2.10) |
| back | p | 0.794 | 47/50 | 0 | 40 | 2.39 ± 0.67 (2.52) | 27.05 ± 52.66 (6.63) | 2.12 ± 0.68 (2.30) | 4.51 ± 1.50 (4.90) | 1.85 ± 0.77 (1.99) |
| right | p | 0.894 | 49/50 | 0 | 43 | 1.69 ± 0.45 (1.72) | 15.19 ± 30.50 (5.17) | 2.14 ± 0.53 (2.27) | 4.54 ± 1.23 (4.68) | 1.81 ± 0.66 (1.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.883 | 98/100 | 0 | 87 | 1.87 ± 1.03 (1.76) | 15.16 ± 34.50 (4.24) | 2.17 ± 0.56 (2.30) | 4.64 ± 1.31 (5.10) | 1.87 ± 0.69 (1.93) |
| right | p | 0.818 | 95/100 | 0 | 76 | 1.88 ± 1.11 (1.68) | 20.30 ± 37.16 (7.58) | 1.98 ± 0.70 (2.20) | 4.22 ± 1.58 (4.51) | 1.66 ± 0.79 (1.77) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.910 | 25/25 | 0 | 22 | 1.62 ± 1.72 (1.32) | 7.92 ± 12.66 (3.30) | 2.08 ± 0.58 (2.23) | 4.47 ± 1.38 (4.56) | 1.73 ± 0.67 (1.75) |
| forward/right | p | 0.791 | 24/25 | 0 | 17 | 1.87 ± 1.93 (1.41) | 13.85 ± 12.75 (8.58) | 1.75 ± 0.72 (2.07) | 3.72 ± 1.66 (4.19) | 1.35 ± 0.77 (1.60) |
| left/left | p | 0.914 | 25/25 | 0 | 23 | 1.65 ± 0.40 (1.80) | 11.17 ± 18.93 (5.34) | 2.27 ± 0.59 (2.38) | 4.90 ± 1.34 (5.43) | 2.06 ± 0.69 (2.22) |
| left/right | p | 0.809 | 23/25 | 0 | 18 | 1.74 ± 0.55 (1.98) | 25.58 ± 45.04 (6.17) | 1.96 ± 0.68 (2.20) | 4.25 ± 1.57 (4.66) | 1.64 ± 0.79 (1.89) |
| back/left | p | 0.789 | 23/25 | 0 | 20 | 2.41 ± 0.72 (2.52) | 25.42 ± 52.91 (5.29) | 2.23 ± 0.50 (2.36) | 4.72 ± 1.15 (4.90) | 1.94 ± 0.71 (1.93) |
| back/right | p | 0.800 | 24/25 | 0 | 20 | 2.37 ± 0.61 (2.47) | 28.61 ± 52.37 (7.90) | 2.03 ± 0.79 (2.29) | 4.31 ± 1.74 (4.88) | 1.78 ± 0.81 (2.02) |
| right/left | p | 0.916 | 25/25 | 0 | 22 | 1.83 ± 0.46 (1.76) | 16.95 ± 37.48 (3.37) | 2.12 ± 0.55 (2.27) | 4.48 ± 1.29 (4.55) | 1.76 ± 0.64 (1.91) |
| right/right | p | 0.872 | 24/25 | 0 | 21 | 1.55 ± 0.38 (1.57) | 13.37 ± 20.74 (6.51) | 2.17 ± 0.51 (2.22) | 4.59 ± 1.17 (4.81) | 1.86 ± 0.68 (1.79) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.840 | 15.2 | 4.96 | 2.03 |
| p | normal | 0.860 | 20.1 | 3.93 | 1.51 |

## Notes

- p: score 0.850, 193/200 kicked, 0 fell; worst sector back (0.794).
