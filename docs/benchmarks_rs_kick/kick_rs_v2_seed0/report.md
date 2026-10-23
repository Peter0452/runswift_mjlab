# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5). Trials, kick rule and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.836** |
| Kicked / fell | 190 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.90 ± 0.93 (1.80) |
| Direction error [°] | 18.26 ± 37.19 (5.75) |
| Avg ball speed [m/s] | 1.73 ± 0.51 (1.89) |
| Peak ball speed [m/s] | 4.11 ± 1.29 (4.58) |
| Distance [m] | 1.50 ± 0.64 (1.58) |
| Path length [m] | 1.50 ± 0.64 (1.59) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.846 | 48/50 | 0 | 40 | 1.60 ± 1.38 (1.39) | 13.15 ± 25.49 (5.81) | 1.65 ± 0.54 (1.80) | 3.88 ± 1.38 (3.98) | 1.39 ± 0.67 (1.39) |
| left | h022 | 0.857 | 48/50 | 0 | 40 | 1.75 ± 0.52 (1.86) | 17.67 ± 32.33 (4.98) | 1.72 ± 0.53 (1.90) | 4.15 ± 1.33 (4.62) | 1.51 ± 0.66 (1.66) |
| back | h022 | 0.777 | 46/50 | 0 | 40 | 2.50 ± 0.62 (2.69) | 25.38 ± 52.19 (6.20) | 1.77 ± 0.50 (1.94) | 4.20 ± 1.26 (4.73) | 1.56 ± 0.62 (1.75) |
| right | h022 | 0.864 | 48/50 | 0 | 41 | 1.80 ± 0.61 (1.80) | 17.14 ± 33.05 (5.53) | 1.76 ± 0.46 (1.83) | 4.22 ± 1.14 (4.60) | 1.53 ± 0.57 (1.57) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.873 | 99/100 | 0 | 85 | 1.90 ± 1.04 (1.84) | 18.60 ± 38.66 (5.66) | 1.74 ± 0.50 (1.91) | 4.15 ± 1.25 (4.61) | 1.52 ± 0.60 (1.61) |
| right | h022 | 0.798 | 91/100 | 0 | 76 | 1.91 ± 0.78 (1.80) | 17.89 ± 35.51 (5.77) | 1.70 ± 0.52 (1.85) | 4.07 ± 1.32 (4.53) | 1.48 ± 0.67 (1.57) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.899 | 25/25 | 0 | 23 | 1.69 ± 1.69 (1.32) | 8.35 ± 10.50 (4.93) | 1.76 ± 0.47 (1.83) | 4.18 ± 1.20 (4.06) | 1.53 ± 0.57 (1.61) |
| forward/right | h022 | 0.793 | 23/25 | 0 | 17 | 1.50 ± 0.91 (1.40) | 18.38 ± 34.41 (5.99) | 1.54 ± 0.59 (1.60) | 3.55 ± 1.48 (3.75) | 1.24 ± 0.74 (1.26) |
| left/left | h022 | 0.904 | 25/25 | 0 | 21 | 1.62 ± 0.44 (1.86) | 13.74 ± 23.39 (5.08) | 1.71 ± 0.51 (1.90) | 4.12 ± 1.26 (4.55) | 1.49 ± 0.61 (1.60) |
| left/right | h022 | 0.810 | 23/25 | 0 | 19 | 1.89 ± 0.56 (1.96) | 21.95 ± 39.38 (4.48) | 1.73 ± 0.55 (1.93) | 4.18 ± 1.40 (4.67) | 1.55 ± 0.72 (1.80) |
| back/left | h022 | 0.797 | 24/25 | 0 | 20 | 2.47 ± 0.71 (2.64) | 31.97 ± 59.17 (6.60) | 1.76 ± 0.51 (1.91) | 4.20 ± 1.30 (4.68) | 1.56 ± 0.64 (1.75) |
| back/right | h022 | 0.757 | 22/25 | 0 | 20 | 2.53 ± 0.51 (2.69) | 18.20 ± 42.17 (5.95) | 1.78 ± 0.49 (1.97) | 4.21 ± 1.22 (4.73) | 1.56 ± 0.60 (1.75) |
| right/left | h022 | 0.894 | 25/25 | 0 | 21 | 1.86 ± 0.54 (1.86) | 20.88 ± 39.95 (4.95) | 1.75 ± 0.51 (1.88) | 4.09 ± 1.25 (4.71) | 1.48 ± 0.59 (1.55) |
| right/right | h022 | 0.833 | 23/25 | 0 | 20 | 1.73 ± 0.68 (1.70) | 13.06 ± 22.64 (6.10) | 1.77 ± 0.39 (1.80) | 4.35 ± 0.98 (4.53) | 1.58 ± 0.53 (1.59) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.828 | 16.6 | 4.57 | 1.74 |
| h022 | normal | 0.843 | 19.9 | 3.66 | 1.27 |

## Notes

- h022: score 0.836, 190/200 kicked, 0 fell; worst sector back (0.777).
