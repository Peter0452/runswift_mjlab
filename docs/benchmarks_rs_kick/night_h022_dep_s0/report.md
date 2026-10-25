# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.834** |
| Kicked / fell | 191 / 0 |
| Kicks within 15° | 157 |
| Weak kicks (< 0.3 m) | 17 |
| Time to kick [s] | 1.95 ± 1.25 (1.78) |
| Direction error [°] | 18.95 ± 36.77 (5.27) |
| Avg ball speed [m/s] | 1.88 ± 0.63 (2.04) |
| Peak ball speed [m/s] | 4.09 ± 1.46 (4.63) |
| Distance [m] | 1.57 ± 0.75 (1.59) |
| Path length [m] | 1.58 ± 0.75 (1.60) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.846 | 48/50 | 0 | 38 | 1.67 ± 1.67 (1.37) | 10.36 ± 13.11 (5.60) | 1.80 ± 0.64 (1.87) | 3.88 ± 1.50 (3.85) | 1.46 ± 0.77 (1.39) |
| left | h022 | 0.850 | 48/50 | 0 | 39 | 1.69 ± 0.55 (1.87) | 20.58 ± 35.98 (4.17) | 1.83 ± 0.64 (2.04) | 4.07 ± 1.55 (4.65) | 1.53 ± 0.75 (1.59) |
| back | h022 | 0.771 | 46/50 | 0 | 40 | 2.51 ± 0.65 (2.67) | 25.42 ± 51.03 (6.30) | 2.02 ± 0.58 (2.16) | 4.38 ± 1.33 (5.04) | 1.76 ± 0.73 (2.00) |
| right | h022 | 0.870 | 49/50 | 0 | 40 | 1.95 ± 1.49 (1.76) | 19.69 ± 35.71 (3.75) | 1.87 ± 0.61 (2.04) | 4.05 ± 1.40 (4.66) | 1.54 ± 0.71 (1.59) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.876 | 99/100 | 0 | 84 | 1.91 ± 1.08 (1.82) | 18.22 ± 37.88 (4.46) | 1.94 ± 0.58 (2.09) | 4.20 ± 1.37 (4.79) | 1.63 ± 0.71 (1.78) |
| right | h022 | 0.793 | 92/100 | 0 | 73 | 1.99 ± 1.41 (1.77) | 19.73 ± 35.53 (6.06) | 1.82 ± 0.67 (1.96) | 3.97 ± 1.54 (4.18) | 1.51 ± 0.78 (1.50) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.910 | 25/25 | 0 | 22 | 1.72 ± 1.78 (1.38) | 7.49 ± 11.09 (3.52) | 1.95 ± 0.53 (2.03) | 4.20 ± 1.29 (4.02) | 1.61 ± 0.65 (1.62) |
| forward/right | h022 | 0.781 | 23/25 | 0 | 16 | 1.62 ± 1.54 (1.36) | 13.47 ± 14.36 (9.49) | 1.64 ± 0.72 (1.73) | 3.53 ± 1.63 (3.66) | 1.29 ± 0.84 (1.35) |
| left/left | h022 | 0.901 | 25/25 | 0 | 21 | 1.61 ± 0.50 (1.84) | 14.73 ± 24.59 (4.46) | 1.91 ± 0.63 (2.12) | 4.19 ± 1.50 (4.79) | 1.63 ± 0.74 (1.80) |
| left/right | h022 | 0.799 | 23/25 | 0 | 18 | 1.78 ± 0.58 (1.96) | 26.94 ± 44.35 (3.72) | 1.74 ± 0.64 (1.96) | 3.93 ± 1.59 (4.63) | 1.42 ± 0.75 (1.56) |
| back/left | h022 | 0.795 | 24/25 | 0 | 20 | 2.47 ± 0.72 (2.59) | 30.55 ± 56.25 (6.79) | 2.00 ± 0.61 (2.20) | 4.33 ± 1.40 (5.05) | 1.74 ± 0.77 (2.03) |
| back/right | h022 | 0.746 | 22/25 | 0 | 20 | 2.55 ± 0.57 (2.72) | 19.82 ± 43.97 (6.06) | 2.04 ± 0.54 (2.09) | 4.44 ± 1.26 (4.82) | 1.78 ± 0.68 (1.85) |
| right/left | h022 | 0.896 | 25/25 | 0 | 21 | 1.86 ± 0.54 (1.90) | 20.62 ± 40.46 (3.36) | 1.88 ± 0.54 (2.03) | 4.10 ± 1.29 (4.70) | 1.54 ± 0.66 (1.61) |
| right/right | h022 | 0.843 | 24/25 | 0 | 19 | 2.04 ± 2.05 (1.71) | 18.73 ± 29.94 (3.92) | 1.86 ± 0.68 (2.05) | 4.01 ± 1.50 (4.36) | 1.54 ± 0.75 (1.55) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.826 | 15.6 | 4.71 | 1.89 |
| h022 | normal | 0.842 | 22.2 | 3.50 | 1.26 |

## Notes

- h022: score 0.834, 191/200 kicked, 0 fell; worst sector back (0.771).
