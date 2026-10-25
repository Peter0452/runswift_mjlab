# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 2.11 ± 1.62 (1.76) |
| Direction error [°] | 14.83 ± 30.92 (5.40) |
| Avg ball speed [m/s] | 1.92 ± 0.56 (2.04) |
| Peak ball speed [m/s] | 4.20 ± 1.36 (4.74) |
| Distance [m] | 1.61 ± 0.68 (1.65) |
| Path length [m] | 1.61 ± 0.68 (1.66) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.849 | 47/50 | 0 | 40 | 1.73 ± 2.06 (1.36) | 8.02 ± 11.91 (3.47) | 1.98 ± 0.50 (2.01) | 4.36 ± 1.22 (4.66) | 1.66 ± 0.63 (1.61) |
| left | h022 | 0.882 | 50/50 | 0 | 42 | 1.98 ± 1.44 (1.76) | 15.58 ± 27.82 (6.52) | 1.90 ± 0.58 (2.01) | 4.14 ± 1.38 (4.57) | 1.59 ± 0.73 (1.62) |
| back | h022 | 0.779 | 49/50 | 0 | 40 | 2.93 ± 1.78 (2.66) | 26.45 ± 48.63 (6.43) | 1.86 ± 0.67 (2.10) | 4.10 ± 1.58 (4.84) | 1.57 ± 0.75 (1.75) |
| right | h022 | 0.906 | 49/50 | 0 | 44 | 1.80 ± 0.40 (1.82) | 8.98 ± 17.31 (4.07) | 1.94 ± 0.48 (2.05) | 4.21 ± 1.20 (4.20) | 1.60 ± 0.60 (1.59) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.859 | 98/100 | 0 | 83 | 2.14 ± 1.69 (1.76) | 13.72 ± 26.82 (5.30) | 1.93 ± 0.55 (2.09) | 4.25 ± 1.35 (4.84) | 1.64 ± 0.69 (1.69) |
| right | h022 | 0.849 | 97/100 | 0 | 83 | 2.09 ± 1.55 (1.78) | 15.95 ± 34.54 (5.69) | 1.91 ± 0.57 (1.99) | 4.15 ± 1.36 (4.11) | 1.57 ± 0.67 (1.57) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.882 | 24/25 | 0 | 21 | 1.71 ± 2.10 (1.33) | 6.36 ± 8.48 (3.15) | 2.02 ± 0.37 (2.06) | 4.44 ± 1.03 (4.80) | 1.70 ± 0.58 (1.68) |
| forward/right | h022 | 0.816 | 23/25 | 0 | 19 | 1.74 ± 2.03 (1.38) | 9.75 ± 14.45 (4.47) | 1.93 ± 0.59 (2.00) | 4.28 ± 1.38 (4.58) | 1.61 ± 0.67 (1.55) |
| left/left | h022 | 0.894 | 25/25 | 0 | 22 | 2.15 ± 1.95 (1.66) | 8.85 ± 9.15 (6.65) | 2.00 ± 0.55 (2.18) | 4.41 ± 1.32 (5.01) | 1.75 ± 0.70 (1.87) |
| left/right | h022 | 0.871 | 25/25 | 0 | 20 | 1.80 ± 0.56 (2.00) | 22.31 ± 37.07 (6.16) | 1.80 ± 0.60 (1.97) | 3.86 ± 1.37 (3.90) | 1.43 ± 0.72 (1.47) |
| back/left | h022 | 0.788 | 25/25 | 0 | 19 | 2.77 ± 1.54 (2.66) | 26.71 ± 43.39 (7.55) | 1.83 ± 0.70 (2.10) | 4.06 ± 1.65 (4.84) | 1.57 ± 0.80 (1.75) |
| back/right | h022 | 0.771 | 24/25 | 0 | 21 | 3.10 ± 1.97 (2.68) | 26.19 ± 53.54 (6.25) | 1.89 ± 0.62 (2.07) | 4.15 ± 1.51 (4.86) | 1.57 ± 0.68 (1.78) |
| right/left | h022 | 0.874 | 24/25 | 0 | 21 | 1.89 ± 0.43 (1.97) | 12.64 ± 23.68 (3.73) | 1.87 ± 0.51 (2.06) | 4.09 ± 1.26 (4.47) | 1.52 ± 0.62 (1.62) |
| right/right | h022 | 0.938 | 25/25 | 0 | 23 | 1.72 ± 0.36 (1.76) | 5.46 ± 4.86 (4.71) | 2.00 ± 0.45 (1.99) | 4.33 ± 1.12 (4.01) | 1.69 ± 0.57 (1.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.843 | 15.5 | 4.62 | 1.82 |
| h022 | normal | 0.865 | 14.2 | 3.79 | 1.39 |

## Notes

- h022: score 0.854, 195/200 kicked, 0 fell; worst sector back (0.779).
