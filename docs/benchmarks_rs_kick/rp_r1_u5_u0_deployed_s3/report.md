# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r1_u5_u0.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.786** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 171 |
| Weak kicks (< 0.3 m) | 14 |
| Time to kick [s] | 2.08 ± 1.55 (1.80) |
| Direction error [°] | 15.43 ± 32.70 (4.75) |
| Avg ball speed [m/s] | 2.16 ± 0.68 (2.28) |
| Peak ball speed [m/s] | 4.88 ± 1.59 (5.34) |
| Distance [m] | 2.22 ± 0.94 (2.30) |
| Path length [m] | 2.23 ± 0.95 (2.31) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.808 | 48/50 | 0 | 43 | 1.28 ± 0.29 (1.32) | 8.59 ± 14.96 (3.98) | 2.13 ± 0.64 (2.19) | 4.87 ± 1.55 (5.02) | 2.17 ± 0.92 (2.21) |
| left | p | 0.822 | 50/50 | 0 | 44 | 1.85 ± 0.75 (1.79) | 13.60 ± 28.46 (4.67) | 2.21 ± 0.70 (2.36) | 4.98 ± 1.63 (5.66) | 2.29 ± 0.94 (2.56) |
| back | p | 0.743 | 49/50 | 0 | 44 | 2.83 ± 1.64 (2.62) | 18.65 ± 39.58 (4.83) | 2.24 ± 0.67 (2.26) | 5.00 ± 1.54 (5.11) | 2.33 ± 0.97 (2.19) |
| right | p | 0.769 | 50/50 | 0 | 40 | 2.32 ± 2.23 (1.83) | 20.66 ± 39.57 (4.83) | 2.07 ± 0.70 (2.26) | 4.68 ± 1.61 (4.83) | 2.08 ± 0.91 (2.18) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.813 | 100/100 | 0 | 87 | 1.85 ± 0.69 (1.79) | 14.86 ± 32.81 (4.34) | 2.18 ± 0.68 (2.28) | 4.91 ± 1.60 (5.40) | 2.25 ± 0.96 (2.33) |
| right | p | 0.758 | 97/100 | 0 | 84 | 2.31 ± 2.08 (1.82) | 16.01 ± 32.57 (5.30) | 2.14 ± 0.68 (2.25) | 4.86 ± 1.57 (5.23) | 2.18 ± 0.91 (2.25) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.836 | 25/25 | 0 | 22 | 1.31 ± 0.32 (1.32) | 8.65 ± 14.08 (3.98) | 2.07 ± 0.70 (2.19) | 4.72 ± 1.65 (4.80) | 2.10 ± 0.94 (2.20) |
| forward/right | p | 0.779 | 23/25 | 0 | 21 | 1.25 ± 0.25 (1.30) | 8.53 ± 15.86 (3.98) | 2.18 ± 0.57 (2.20) | 5.03 ± 1.41 (5.51) | 2.25 ± 0.88 (2.34) |
| left/left | p | 0.820 | 25/25 | 0 | 22 | 1.79 ± 0.79 (1.74) | 9.52 ± 15.57 (4.81) | 2.25 ± 0.67 (2.38) | 5.02 ± 1.57 (5.68) | 2.32 ± 0.93 (2.59) |
| left/right | p | 0.824 | 25/25 | 0 | 22 | 1.92 ± 0.70 (1.98) | 17.68 ± 36.66 (4.09) | 2.17 ± 0.73 (2.32) | 4.94 ± 1.69 (5.65) | 2.26 ± 0.95 (2.52) |
| back/left | p | 0.792 | 25/25 | 0 | 23 | 2.55 ± 0.48 (2.56) | 15.81 ± 35.48 (4.36) | 2.34 ± 0.66 (2.34) | 5.19 ± 1.55 (5.85) | 2.50 ± 1.03 (2.73) |
| back/right | p | 0.694 | 24/25 | 0 | 21 | 3.12 ± 2.25 (2.66) | 21.62 ± 43.24 (5.37) | 2.13 ± 0.66 (2.19) | 4.81 ± 1.50 (4.92) | 2.15 ± 0.88 (2.15) |
| right/left | p | 0.805 | 25/25 | 0 | 20 | 1.74 ± 0.40 (1.82) | 25.48 ± 49.25 (4.20) | 2.07 ± 0.67 (2.28) | 4.70 ± 1.57 (4.77) | 2.09 ± 0.90 (2.20) |
| right/right | p | 0.734 | 25/25 | 0 | 20 | 2.90 ± 3.02 (1.84) | 15.83 ± 25.70 (5.84) | 2.06 ± 0.72 (2.25) | 4.66 ± 1.64 (4.89) | 2.07 ± 0.93 (2.08) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.834 | 11.1 | 5.48 | 2.59 |
| p | normal | 0.737 | 19.8 | 4.28 | 1.85 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.704 | 0.08 | 2.55 ± 1.04 (2.49) | 4.06 | 1.70 |
| p | medium | 18 | 0.811 | 0.60 | 1.21 ± 0.40 (1.33) | 3.91 | 1.58 |
| p | strong | 124 | 0.820 | 0.72 | - | 5.41 | 2.56 |

## Notes

- p: score 0.786, 197/200 kicked, 0 fell; worst sector back (0.743).
