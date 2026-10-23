# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball ours, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **pow_b** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_21-02-12_pow_b/model_19249.pt`.

## Overall

| Metric | pow_b |
|---|---|
| **Score** | **0.848** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 153 |
| Weak kicks (< 0.3 m) | 6 |
| Time to kick [s] | 2.12 ± 1.80 (1.74) |
| Direction error [°] | 18.61 ± 35.13 (6.62) |
| Avg ball speed [m/s] | 1.60 ± 0.51 (1.70) |
| Peak ball speed [m/s] | 5.70 ± 2.00 (5.97) |
| Distance [m] | 4.23 ± 1.72 (4.35) |
| Path length [m] | 4.23 ± 1.72 (4.35) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | pow_b | 0.856 | 49/50 | 0 | 37 | 1.64 ± 1.76 (1.30) | 11.87 ± 13.73 (8.46) | 1.52 ± 0.50 (1.63) | 5.39 ± 1.94 (5.67) | 3.92 ± 1.66 (4.16) |
| left | pow_b | 0.862 | 48/50 | 0 | 39 | 1.68 ± 0.49 (1.76) | 17.93 ± 32.85 (6.12) | 1.58 ± 0.53 (1.70) | 5.63 ± 2.07 (6.01) | 4.21 ± 1.74 (4.31) |
| back | pow_b | 0.823 | 50/50 | 0 | 41 | 3.08 ± 2.23 (2.71) | 21.09 ± 45.77 (4.63) | 1.77 ± 0.46 (1.81) | 6.37 ± 1.86 (6.27) | 4.82 ± 1.59 (4.81) |
| right | pow_b | 0.852 | 50/50 | 0 | 36 | 2.05 ± 1.79 (1.73) | 23.38 ± 38.38 (9.52) | 1.53 ± 0.52 (1.66) | 5.40 ± 1.99 (5.81) | 3.96 ± 1.73 (4.21) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | pow_b | 0.882 | 100/100 | 0 | 83 | 1.98 ± 1.41 (1.73) | 16.58 ± 34.59 (6.62) | 1.66 ± 0.45 (1.73) | 5.97 ± 1.82 (6.03) | 4.45 ± 1.57 (4.50) |
| right | pow_b | 0.815 | 97/100 | 0 | 70 | 2.26 ± 2.12 (1.76) | 20.69 ± 35.56 (6.84) | 1.53 ± 0.56 (1.68) | 5.42 ± 2.14 (5.88) | 4.00 ± 1.83 (4.30) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | pow_b | 0.897 | 25/25 | 0 | 21 | 1.59 ± 1.69 (1.30) | 10.16 ± 13.01 (7.97) | 1.61 ± 0.35 (1.63) | 5.73 ± 1.46 (5.72) | 4.22 ± 1.24 (4.18) |
| forward/right | pow_b | 0.814 | 24/25 | 0 | 16 | 1.69 ± 1.82 (1.31) | 13.65 ± 14.23 (9.98) | 1.42 ± 0.60 (1.62) | 5.03 ± 2.27 (5.67) | 3.60 ± 1.96 (4.09) |
| left/left | pow_b | 0.923 | 25/25 | 0 | 22 | 1.62 ± 0.42 (1.68) | 9.36 ± 14.71 (6.56) | 1.69 ± 0.49 (1.78) | 6.08 ± 2.01 (6.17) | 4.59 ± 1.64 (4.68) |
| left/right | pow_b | 0.800 | 23/25 | 0 | 17 | 1.75 ± 0.55 (1.88) | 27.25 ± 43.02 (5.60) | 1.46 ± 0.54 (1.56) | 5.14 ± 2.02 (5.25) | 3.79 ± 1.76 (4.06) |
| back/left | pow_b | 0.834 | 25/25 | 0 | 20 | 2.96 ± 1.82 (2.68) | 18.67 ± 43.90 (3.70) | 1.78 ± 0.34 (1.82) | 6.44 ± 1.50 (6.34) | 4.82 ± 1.33 (4.90) |
| back/right | pow_b | 0.812 | 25/25 | 0 | 21 | 3.20 ± 2.57 (2.74) | 23.50 ± 47.45 (5.19) | 1.76 ± 0.56 (1.80) | 6.30 ± 2.16 (6.22) | 4.82 ± 1.81 (4.74) |
| right/left | pow_b | 0.872 | 25/25 | 0 | 20 | 1.76 ± 0.51 (1.74) | 28.15 ± 47.34 (9.92) | 1.58 ± 0.56 (1.68) | 5.61 ± 2.12 (5.96) | 4.18 ± 1.89 (4.26) |
| right/right | pow_b | 0.833 | 25/25 | 0 | 16 | 2.35 ± 2.44 (1.72) | 18.60 ± 25.69 (8.90) | 1.47 ± 0.47 (1.58) | 5.19 ± 1.83 (5.57) | 3.75 ± 1.51 (4.07) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| pow_b | strong | 0.865 | 13.4 | 6.28 | 4.80 |
| pow_b | normal | 0.831 | 23.8 | 5.12 | 3.66 |

## Notes

- pow_b: score 0.848, 197/200 kicked, 0 fell; worst sector back (0.823).
