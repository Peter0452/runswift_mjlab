# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v2_s8ing_u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 194 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.93 ± 1.39 (1.74) |
| Direction error [°] | 18.66 ± 38.74 (5.40) |
| Avg ball speed [m/s] | 2.07 ± 0.64 (2.26) |
| Peak ball speed [m/s] | 4.58 ± 1.54 (5.25) |
| Distance [m] | 1.86 ± 0.83 (2.00) |
| Path length [m] | 1.87 ± 0.84 (2.01) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.794 | 49/50 | 0 | 43 | 1.76 ± 2.12 (1.32) | 7.52 ± 10.41 (4.70) | 2.02 ± 0.64 (2.04) | 4.44 ± 1.57 (4.18) | 1.77 ± 0.84 (1.60) |
| left | p | 0.796 | 48/50 | 0 | 40 | 1.66 ± 0.49 (1.73) | 19.07 ± 35.79 (5.35) | 2.10 ± 0.61 (2.32) | 4.69 ± 1.48 (5.39) | 1.91 ± 0.82 (2.18) |
| back | p | 0.740 | 49/50 | 0 | 41 | 2.59 ± 1.44 (2.50) | 30.53 ± 57.35 (6.74) | 2.07 ± 0.72 (2.27) | 4.58 ± 1.69 (5.43) | 1.92 ± 0.88 (2.21) |
| right | p | 0.781 | 48/50 | 0 | 40 | 1.71 ± 0.48 (1.74) | 17.51 ± 32.34 (5.58) | 2.09 ± 0.59 (2.23) | 4.60 ± 1.40 (5.22) | 1.85 ± 0.79 (1.87) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 98/100 | 0 | 86 | 1.77 ± 0.63 (1.70) | 15.95 ± 35.27 (5.16) | 2.16 ± 0.55 (2.28) | 4.77 ± 1.35 (5.41) | 1.95 ± 0.77 (2.11) |
| right | p | 0.748 | 96/100 | 0 | 78 | 2.10 ± 1.85 (1.75) | 21.43 ± 41.81 (5.78) | 1.98 ± 0.71 (2.17) | 4.38 ± 1.70 (5.09) | 1.77 ± 0.89 (1.86) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.821 | 24/25 | 0 | 22 | 1.29 ± 0.27 (1.31) | 6.53 ± 11.63 (3.10) | 2.13 ± 0.50 (2.19) | 4.72 ± 1.33 (4.87) | 1.89 ± 0.73 (1.89) |
| forward/right | p | 0.768 | 25/25 | 0 | 21 | 2.22 ± 2.88 (1.34) | 8.48 ± 8.98 (5.25) | 1.93 ± 0.73 (1.98) | 4.18 ± 1.73 (4.01) | 1.66 ± 0.91 (1.55) |
| left/left | p | 0.853 | 25/25 | 0 | 22 | 1.59 ± 0.41 (1.66) | 11.96 ± 22.65 (5.15) | 2.21 ± 0.51 (2.35) | 4.89 ± 1.24 (5.42) | 2.02 ± 0.69 (2.21) |
| left/right | p | 0.739 | 23/25 | 0 | 18 | 1.73 ± 0.56 (1.80) | 26.80 ± 44.73 (5.55) | 1.99 ± 0.69 (2.17) | 4.48 ± 1.68 (5.37) | 1.78 ± 0.92 (2.09) |
| back/left | p | 0.750 | 24/25 | 0 | 21 | 2.40 ± 0.69 (2.50) | 24.64 ± 51.12 (5.99) | 2.24 ± 0.49 (2.31) | 4.95 ± 1.22 (5.60) | 2.09 ± 0.77 (2.37) |
| back/right | p | 0.731 | 25/25 | 0 | 20 | 2.78 ± 1.88 (2.50) | 36.18 ± 62.23 (7.17) | 1.91 ± 0.85 (2.20) | 4.23 ± 1.98 (4.96) | 1.77 ± 0.95 (2.12) |
| right/left | p | 0.808 | 25/25 | 0 | 21 | 1.80 ± 0.50 (1.80) | 20.64 ± 39.10 (5.17) | 2.07 ± 0.65 (2.23) | 4.51 ± 1.53 (5.18) | 1.83 ± 0.84 (1.80) |
| right/right | p | 0.754 | 23/25 | 0 | 19 | 1.60 ± 0.43 (1.68) | 14.11 ± 22.32 (6.07) | 2.11 ± 0.50 (2.28) | 4.69 ± 1.23 (5.38) | 1.88 ± 0.73 (1.89) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.806 | 17.0 | 5.29 | 2.26 |
| p | normal | 0.750 | 20.3 | 3.89 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.18 | 2.23 ± 0.96 (2.10) | 3.53 | 1.26 |
| p | medium | 16 | 0.798 | 0.71 | 1.24 ± 0.22 (1.26) | 4.00 | 1.55 |
| p | strong | 126 | 0.803 | 0.69 | - | 5.14 | 2.18 |

## Notes

- p: score 0.778, 194/200 kicked, 0 fell; worst sector back (0.740).
