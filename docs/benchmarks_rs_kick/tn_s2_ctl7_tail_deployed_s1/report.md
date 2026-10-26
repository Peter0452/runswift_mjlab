# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s2_ctl7_tail.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.791** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 22 |
| Time to kick [s] | 1.91 ± 1.18 (1.62) |
| Direction error [°] | 16.18 ± 32.03 (5.76) |
| Avg ball speed [m/s] | 2.18 ± 0.72 (2.35) |
| Peak ball speed [m/s] | 4.69 ± 1.63 (5.30) |
| Distance [m] | 2.05 ± 0.90 (2.19) |
| Path length [m] | 2.06 ± 0.90 (2.20) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.808 | 50/50 | 0 | 42 | 1.55 ± 1.46 (1.28) | 10.45 ± 16.76 (4.24) | 2.06 ± 0.79 (2.30) | 4.47 ± 1.79 (4.67) | 1.91 ± 0.94 (1.97) |
| left | p | 0.808 | 49/50 | 0 | 43 | 1.64 ± 0.45 (1.58) | 13.55 ± 25.42 (5.43) | 2.19 ± 0.63 (2.34) | 4.73 ± 1.43 (5.05) | 2.04 ± 0.84 (2.10) |
| back | p | 0.742 | 50/50 | 0 | 40 | 2.74 ± 1.46 (2.55) | 28.35 ± 49.30 (6.99) | 2.26 ± 0.82 (2.54) | 4.84 ± 1.80 (5.69) | 2.21 ± 1.01 (2.59) |
| right | p | 0.808 | 50/50 | 0 | 44 | 1.70 ± 0.43 (1.72) | 12.29 ± 23.15 (5.94) | 2.21 ± 0.62 (2.29) | 4.72 ± 1.42 (4.96) | 2.03 ± 0.75 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.790 | 99/100 | 0 | 85 | 1.85 ± 0.97 (1.58) | 16.26 ± 31.13 (6.53) | 2.20 ± 0.71 (2.36) | 4.73 ± 1.58 (5.32) | 2.06 ± 0.87 (2.26) |
| right | p | 0.793 | 100/100 | 0 | 84 | 1.97 ± 1.36 (1.72) | 16.09 ± 32.90 (5.20) | 2.17 ± 0.74 (2.34) | 4.66 ± 1.67 (4.72) | 2.03 ± 0.92 (1.99) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.827 | 25/25 | 0 | 22 | 1.26 ± 0.30 (1.26) | 11.94 ± 20.44 (5.17) | 2.07 ± 0.78 (2.30) | 4.52 ± 1.76 (5.32) | 1.94 ± 0.92 (2.19) |
| forward/right | p | 0.789 | 25/25 | 0 | 20 | 1.85 ± 1.99 (1.38) | 8.97 ± 11.83 (4.09) | 2.04 ± 0.81 (2.28) | 4.42 ± 1.82 (4.51) | 1.88 ± 0.95 (1.93) |
| left/left | p | 0.824 | 24/25 | 0 | 23 | 1.63 ± 0.37 (1.57) | 6.42 ± 5.34 (5.71) | 2.38 ± 0.44 (2.39) | 5.14 ± 1.03 (5.28) | 2.29 ± 0.69 (2.27) |
| left/right | p | 0.792 | 25/25 | 0 | 20 | 1.65 ± 0.52 (1.74) | 20.39 ± 33.82 (5.43) | 2.01 ± 0.72 (2.21) | 4.33 ± 1.63 (4.46) | 1.80 ± 0.91 (1.82) |
| back/left | p | 0.735 | 25/25 | 0 | 19 | 2.70 ± 1.47 (2.56) | 27.49 ± 46.89 (6.71) | 2.26 ± 0.76 (2.48) | 4.83 ± 1.67 (5.67) | 2.16 ± 0.96 (2.55) |
| back/right | p | 0.749 | 25/25 | 0 | 21 | 2.77 ± 1.45 (2.54) | 29.22 ± 51.58 (7.70) | 2.27 ± 0.87 (2.59) | 4.86 ± 1.93 (5.82) | 2.26 ± 1.05 (2.72) |
| right/left | p | 0.774 | 25/25 | 0 | 21 | 1.79 ± 0.49 (1.84) | 18.81 ± 30.81 (6.53) | 2.08 ± 0.75 (2.29) | 4.43 ± 1.65 (4.50) | 1.87 ± 0.82 (1.92) |
| right/right | p | 0.842 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.54) | 5.78 ± 6.11 (3.25) | 2.35 ± 0.41 (2.29) | 5.02 ± 1.05 (5.32) | 2.19 ± 0.64 (2.28) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 14.3 | 5.13 | 2.33 |
| p | normal | 0.759 | 18.0 | 4.25 | 1.77 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.711 | 0.10 | 2.51 ± 1.08 (2.44) | 3.90 | 1.55 |
| p | medium | 20 | 0.852 | 0.66 | 1.34 ± 0.16 (1.33) | 4.30 | 1.74 |
| p | strong | 126 | 0.816 | 0.68 | - | 5.09 | 2.31 |

## Notes

- p: score 0.791, 199/200 kicked, 0 fell; worst sector back (0.742).
