# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **night_n2_near04_18750** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_00-33-48_night_n2_near04/model_18750.pt`.

## Overall

| Metric | night_n2_near04_18750 |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 2.02 ± 1.63 (1.76) |
| Direction error [°] | 19.38 ± 39.15 (4.41) |
| Avg ball speed [m/s] | 1.99 ± 0.63 (2.17) |
| Peak ball speed [m/s] | 4.32 ± 1.48 (4.93) |
| Distance [m] | 1.74 ± 0.77 (1.83) |
| Path length [m] | 1.75 ± 0.78 (1.84) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | night_n2_near04_18750 | 0.877 | 49/50 | 0 | 43 | 1.69 ± 1.92 (1.36) | 9.16 ± 12.96 (5.13) | 1.92 ± 0.66 (2.01) | 4.17 ± 1.57 (4.09) | 1.65 ± 0.80 (1.61) |
| left | night_n2_near04_18750 | 0.856 | 48/50 | 0 | 39 | 1.66 ± 0.54 (1.82) | 20.54 ± 37.56 (5.75) | 1.99 ± 0.61 (2.17) | 4.35 ± 1.43 (4.95) | 1.73 ± 0.77 (1.87) |
| back | night_n2_near04_18750 | 0.802 | 48/50 | 0 | 40 | 2.64 ± 1.36 (2.58) | 27.64 ± 55.33 (4.33) | 2.06 ± 0.65 (2.25) | 4.41 ± 1.47 (5.10) | 1.83 ± 0.76 (2.00) |
| right | night_n2_near04_18750 | 0.882 | 50/50 | 0 | 41 | 2.10 ± 2.03 (1.77) | 20.37 ± 36.73 (3.89) | 1.99 ± 0.59 (2.15) | 4.36 ± 1.43 (4.85) | 1.73 ± 0.76 (1.78) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | night_n2_near04_18750 | 0.884 | 99/100 | 0 | 85 | 1.88 ± 1.10 (1.76) | 17.12 ± 36.24 (4.38) | 2.07 ± 0.52 (2.22) | 4.52 ± 1.25 (5.03) | 1.83 ± 0.69 (1.96) |
| right | night_n2_near04_18750 | 0.825 | 96/100 | 0 | 78 | 2.17 ± 2.03 (1.74) | 21.71 ± 41.80 (4.75) | 1.90 ± 0.71 (2.12) | 4.12 ± 1.66 (4.55) | 1.65 ± 0.84 (1.76) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | night_n2_near04_18750 | 0.918 | 25/25 | 0 | 22 | 1.65 ± 1.80 (1.30) | 7.86 ± 12.24 (3.71) | 2.12 ± 0.47 (2.23) | 4.63 ± 1.17 (5.12) | 1.88 ± 0.65 (2.11) |
| forward/right | night_n2_near04_18750 | 0.836 | 24/25 | 0 | 21 | 1.73 ± 2.04 (1.37) | 10.52 ± 13.53 (6.08) | 1.70 ± 0.75 (1.86) | 3.69 ± 1.78 (3.91) | 1.41 ± 0.87 (1.51) |
| left/left | night_n2_near04_18750 | 0.899 | 25/25 | 0 | 21 | 1.58 ± 0.49 (1.72) | 15.03 ± 24.57 (7.18) | 2.01 ± 0.60 (2.17) | 4.40 ± 1.40 (4.93) | 1.77 ± 0.76 (1.89) |
| left/right | night_n2_near04_18750 | 0.813 | 23/25 | 0 | 18 | 1.75 ± 0.58 (1.98) | 26.53 ± 47.10 (5.38) | 1.96 ± 0.62 (2.17) | 4.29 ± 1.47 (4.96) | 1.69 ± 0.78 (1.83) |
| back/left | night_n2_near04_18750 | 0.815 | 24/25 | 0 | 21 | 2.49 ± 0.76 (2.59) | 24.60 ± 51.63 (4.33) | 2.14 ± 0.43 (2.26) | 4.63 ± 1.03 (5.20) | 1.90 ± 0.63 (2.12) |
| back/right | night_n2_near04_18750 | 0.789 | 24/25 | 0 | 19 | 2.79 ± 1.75 (2.54) | 30.67 ± 58.64 (4.33) | 1.97 ± 0.80 (2.21) | 4.19 ± 1.78 (4.98) | 1.77 ± 0.85 (1.86) |
| right/left | night_n2_near04_18750 | 0.903 | 25/25 | 0 | 21 | 1.82 ± 0.53 (1.84) | 21.30 ± 41.57 (3.96) | 2.02 ± 0.54 (2.21) | 4.43 ± 1.35 (4.91) | 1.76 ± 0.71 (1.90) |
| right/right | night_n2_near04_18750 | 0.860 | 25/25 | 0 | 20 | 2.38 ± 2.79 (1.70) | 19.44 ± 31.12 (3.82) | 1.96 ± 0.62 (2.09) | 4.29 ± 1.50 (4.79) | 1.71 ± 0.81 (1.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| night_n2_near04_18750 | strong | 0.843 | 16.5 | 4.96 | 2.08 |
| night_n2_near04_18750 | normal | 0.865 | 22.1 | 3.71 | 1.40 |

## Notes

- night_n2_near04_18750: score 0.854, 195/200 kicked, 0 fell; worst sector back (0.802).
