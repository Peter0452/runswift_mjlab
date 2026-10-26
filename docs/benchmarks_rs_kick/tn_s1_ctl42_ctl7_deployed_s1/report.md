# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s1_ctl42_ctl7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 7 |
| Time to kick [s] | 1.98 ± 1.45 (1.64) |
| Direction error [°] | 13.04 ± 28.02 (5.01) |
| Avg ball speed [m/s] | 1.87 ± 0.46 (1.97) |
| Peak ball speed [m/s] | 4.76 ± 1.20 (4.97) |
| Distance [m] | 1.99 ± 0.66 (2.04) |
| Path length [m] | 2.00 ± 0.67 (2.04) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.794 | 48/50 | 0 | 44 | 1.65 ± 1.88 (1.28) | 8.36 ± 14.64 (4.40) | 1.86 ± 0.44 (1.92) | 4.78 ± 1.22 (4.77) | 1.98 ± 0.64 (2.01) |
| left | p | 0.822 | 50/50 | 0 | 45 | 1.82 ± 1.30 (1.58) | 12.57 ± 24.98 (5.25) | 1.85 ± 0.43 (1.99) | 4.74 ± 1.14 (4.78) | 1.96 ± 0.66 (1.95) |
| back | p | 0.749 | 49/50 | 0 | 42 | 2.75 ± 1.49 (2.52) | 19.32 ± 41.22 (5.21) | 1.96 ± 0.47 (2.08) | 4.98 ± 1.16 (5.38) | 2.15 ± 0.67 (2.22) |
| right | p | 0.808 | 50/50 | 0 | 42 | 1.70 ± 0.44 (1.67) | 11.83 ± 23.18 (3.94) | 1.80 ± 0.48 (1.93) | 4.56 ± 1.24 (4.69) | 1.87 ± 0.66 (1.98) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.794 | 99/100 | 0 | 86 | 1.93 ± 1.29 (1.58) | 14.82 ± 31.05 (5.14) | 1.84 ± 0.52 (1.94) | 4.72 ± 1.34 (4.99) | 1.97 ± 0.73 (2.02) |
| right | p | 0.793 | 98/100 | 0 | 87 | 2.03 ± 1.59 (1.68) | 11.23 ± 24.46 (4.77) | 1.89 ± 0.40 (1.99) | 4.80 ± 1.04 (4.90) | 2.01 ± 0.59 (2.04) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.804 | 24/25 | 0 | 22 | 1.22 ± 0.26 (1.26) | 9.68 ± 16.83 (4.41) | 1.82 ± 0.47 (1.90) | 4.74 ± 1.31 (4.74) | 1.95 ± 0.67 (1.98) |
| forward/right | p | 0.784 | 24/25 | 0 | 22 | 2.08 ± 2.58 (1.33) | 7.04 ± 11.92 (4.40) | 1.90 ± 0.42 (1.97) | 4.82 ± 1.13 (4.80) | 2.01 ± 0.60 (2.01) |
| left/left | p | 0.841 | 25/25 | 0 | 24 | 1.96 ± 1.76 (1.56) | 6.29 ± 4.94 (5.75) | 1.96 ± 0.34 (2.05) | 5.06 ± 0.88 (5.38) | 2.11 ± 0.55 (1.95) |
| left/right | p | 0.803 | 25/25 | 0 | 21 | 1.68 ± 0.50 (1.74) | 18.86 ± 33.83 (5.14) | 1.74 ± 0.48 (1.99) | 4.42 ± 1.27 (4.69) | 1.81 ± 0.72 (1.94) |
| back/left | p | 0.742 | 25/25 | 0 | 19 | 2.69 ± 1.46 (2.52) | 26.71 ± 48.17 (5.78) | 1.91 ± 0.59 (2.09) | 4.82 ± 1.48 (5.54) | 2.08 ± 0.82 (2.39) |
| back/right | p | 0.757 | 24/25 | 0 | 23 | 2.80 ± 1.52 (2.54) | 11.63 ± 30.60 (5.10) | 2.01 ± 0.29 (2.08) | 5.14 ± 0.66 (5.36) | 2.22 ± 0.45 (2.20) |
| right/left | p | 0.789 | 25/25 | 0 | 21 | 1.81 ± 0.49 (1.78) | 16.42 ± 30.96 (3.60) | 1.69 ± 0.58 (1.89) | 4.28 ± 1.48 (4.56) | 1.73 ± 0.78 (1.92) |
| right/right | p | 0.828 | 25/25 | 0 | 21 | 1.58 ± 0.33 (1.54) | 7.25 ± 8.59 (4.29) | 1.91 ± 0.32 (1.98) | 4.84 ± 0.85 (4.76) | 2.01 ± 0.48 (2.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 12.0 | 5.13 | 2.16 |
| p | normal | 0.764 | 14.1 | 4.40 | 1.82 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.710 | 0.08 | 2.61 ± 0.97 (2.46) | 4.09 | 1.63 |
| p | medium | 20 | 0.851 | 0.63 | 1.37 ± 0.18 (1.36) | 4.38 | 1.82 |
| p | strong | 126 | 0.820 | 0.68 | - | 5.11 | 2.17 |

## Notes

- p: score 0.793, 197/200 kicked, 0 fell; worst sector back (0.749).
