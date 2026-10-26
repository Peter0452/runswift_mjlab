# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.755** |
| Kicked / fell | 189 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 2.03 ± 1.39 (1.84) |
| Direction error [°] | 16.96 ± 37.64 (4.34) |
| Avg ball speed [m/s] | 1.93 ± 0.59 (2.04) |
| Peak ball speed [m/s] | 4.23 ± 1.42 (4.70) |
| Distance [m] | 1.64 ± 0.74 (1.67) |
| Path length [m] | 1.65 ± 0.74 (1.68) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.783 | 47/50 | 0 | 43 | 1.44 ± 0.91 (1.34) | 10.49 ± 25.45 (4.58) | 1.99 ± 0.52 (2.06) | 4.35 ± 1.26 (4.70) | 1.70 ± 0.73 (1.66) |
| left | p | 0.811 | 49/50 | 0 | 45 | 1.77 ± 0.47 (1.84) | 12.56 ± 27.58 (4.37) | 1.89 ± 0.58 (2.03) | 4.26 ± 1.39 (4.75) | 1.63 ± 0.70 (1.73) |
| back | p | 0.693 | 47/50 | 0 | 40 | 2.90 ± 1.80 (2.72) | 25.43 ± 50.71 (4.53) | 1.95 ± 0.65 (2.12) | 4.18 ± 1.53 (4.42) | 1.66 ± 0.79 (1.67) |
| right | p | 0.732 | 46/50 | 0 | 39 | 2.01 ± 1.54 (1.90) | 19.62 ± 39.74 (3.82) | 1.89 ± 0.62 (2.05) | 4.11 ± 1.48 (4.00) | 1.57 ± 0.72 (1.50) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.788 | 98/100 | 0 | 87 | 1.93 ± 0.89 (1.84) | 17.62 ± 39.95 (4.14) | 1.89 ± 0.63 (2.03) | 4.16 ± 1.50 (4.70) | 1.62 ± 0.77 (1.67) |
| right | p | 0.722 | 91/100 | 0 | 80 | 2.14 ± 1.77 (1.80) | 16.25 ± 34.97 (4.41) | 1.97 ± 0.55 (2.06) | 4.30 ± 1.33 (4.75) | 1.67 ± 0.70 (1.69) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.797 | 24/25 | 0 | 22 | 1.57 ± 1.23 (1.34) | 11.65 ± 32.13 (3.92) | 1.95 ± 0.59 (1.97) | 4.26 ± 1.39 (4.32) | 1.69 ± 0.82 (1.63) |
| forward/right | p | 0.768 | 23/25 | 0 | 21 | 1.31 ± 0.30 (1.34) | 9.27 ± 15.61 (4.82) | 2.04 ± 0.41 (2.08) | 4.45 ± 1.09 (4.80) | 1.72 ± 0.62 (1.84) |
| left/left | p | 0.815 | 25/25 | 0 | 23 | 1.67 ± 0.43 (1.68) | 11.26 ± 19.56 (5.97) | 1.80 ± 0.62 (1.99) | 4.07 ± 1.48 (4.70) | 1.52 ± 0.71 (1.67) |
| left/right | p | 0.807 | 24/25 | 0 | 22 | 1.88 ± 0.48 (1.95) | 13.92 ± 33.92 (4.01) | 1.98 ± 0.51 (2.09) | 4.45 ± 1.27 (4.92) | 1.74 ± 0.68 (1.82) |
| back/left | p | 0.739 | 24/25 | 0 | 21 | 2.57 ± 0.62 (2.70) | 23.99 ± 50.32 (5.31) | 1.97 ± 0.66 (2.19) | 4.25 ± 1.57 (5.04) | 1.72 ± 0.80 (1.97) |
| back/right | p | 0.648 | 23/25 | 0 | 19 | 3.24 ± 2.45 (2.76) | 26.93 ± 51.06 (4.45) | 1.92 ± 0.64 (1.99) | 4.12 ± 1.47 (4.09) | 1.60 ± 0.78 (1.54) |
| right/left | p | 0.801 | 25/25 | 0 | 21 | 1.91 ± 0.73 (1.98) | 23.60 ± 47.98 (3.59) | 1.86 ± 0.63 (2.08) | 4.06 ± 1.53 (3.93) | 1.54 ± 0.74 (1.43) |
| right/right | p | 0.664 | 21/25 | 0 | 18 | 2.13 ± 2.13 (1.86) | 14.87 ± 26.02 (3.98) | 1.92 ± 0.60 (1.96) | 4.16 ± 1.43 (4.04) | 1.62 ± 0.70 (1.53) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.801 | 15.0 | 4.72 | 1.93 |
| p | normal | 0.709 | 19.0 | 3.71 | 1.34 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.700 | 0.16 | 2.21 ± 0.82 (2.06) | 3.53 | 1.25 |
| p | medium | 18 | 0.798 | 0.78 | 1.07 ± 0.28 (1.11) | 3.44 | 1.17 |
| p | strong | 124 | 0.774 | 0.62 | - | 4.67 | 1.89 |

## Notes

- p: score 0.755, 189/200 kicked, 0 fell; worst sector back (0.693).
