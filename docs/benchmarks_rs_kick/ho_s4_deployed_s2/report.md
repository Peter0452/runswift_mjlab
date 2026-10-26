# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s4_ctl7_n7_n5b.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.774** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 2.00 ± 1.55 (1.76) |
| Direction error [°] | 19.13 ± 36.52 (6.59) |
| Avg ball speed [m/s] | 2.24 ± 0.84 (2.42) |
| Peak ball speed [m/s] | 4.75 ± 1.85 (5.58) |
| Distance [m] | 2.22 ± 1.10 (2.48) |
| Path length [m] | 2.23 ± 1.11 (2.48) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.801 | 49/50 | 0 | 43 | 1.38 ± 1.28 (1.22) | 11.26 ± 19.74 (4.48) | 2.19 ± 0.74 (2.30) | 4.69 ± 1.67 (5.13) | 2.11 ± 0.96 (2.14) |
| left | p | 0.769 | 48/50 | 0 | 41 | 1.86 ± 0.85 (1.83) | 14.88 ± 23.53 (7.36) | 2.26 ± 0.84 (2.42) | 4.78 ± 1.85 (5.61) | 2.26 ± 1.10 (2.50) |
| back | p | 0.740 | 50/50 | 0 | 39 | 2.92 ± 2.22 (2.48) | 27.13 ± 47.17 (7.34) | 2.36 ± 0.86 (2.66) | 4.97 ± 1.90 (5.95) | 2.43 ± 1.20 (2.95) |
| right | p | 0.785 | 49/50 | 0 | 40 | 1.80 ± 0.94 (1.76) | 23.00 ± 44.43 (5.53) | 2.14 ± 0.88 (2.56) | 4.55 ± 1.96 (5.62) | 2.09 ± 1.10 (2.50) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.780 | 99/100 | 0 | 81 | 1.96 ± 1.38 (1.74) | 21.97 ± 41.07 (6.36) | 2.23 ± 0.88 (2.55) | 4.75 ± 1.93 (5.72) | 2.24 ± 1.13 (2.56) |
| right | p | 0.768 | 97/100 | 0 | 82 | 2.03 ± 1.70 (1.80) | 16.23 ± 30.94 (6.61) | 2.25 ± 0.79 (2.31) | 4.74 ± 1.77 (4.70) | 2.20 ± 1.07 (2.14) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.817 | 25/25 | 0 | 22 | 1.20 ± 0.26 (1.22) | 12.29 ± 23.14 (4.48) | 2.17 ± 0.70 (2.30) | 4.64 ± 1.60 (4.50) | 2.09 ± 0.92 (1.86) |
| forward/right | p | 0.785 | 24/25 | 0 | 21 | 1.57 ± 1.78 (1.19) | 10.18 ± 15.34 (4.42) | 2.20 ± 0.77 (2.40) | 4.73 ± 1.74 (5.28) | 2.13 ± 0.99 (2.26) |
| left/left | p | 0.761 | 24/25 | 0 | 20 | 1.92 ± 1.11 (1.74) | 14.39 ± 20.56 (7.44) | 2.23 ± 0.91 (2.60) | 4.75 ± 1.98 (5.72) | 2.26 ± 1.14 (2.59) |
| left/right | p | 0.777 | 24/25 | 0 | 21 | 1.80 ± 0.46 (1.84) | 15.38 ± 26.15 (7.04) | 2.29 ± 0.75 (2.36) | 4.81 ± 1.71 (5.14) | 2.25 ± 1.05 (2.33) |
| back/left | p | 0.762 | 25/25 | 0 | 20 | 2.68 ± 1.93 (2.48) | 26.03 ± 45.68 (7.10) | 2.43 ± 0.82 (2.71) | 5.15 ± 1.82 (5.98) | 2.54 ± 1.17 (3.00) |
| back/right | p | 0.719 | 25/25 | 0 | 19 | 3.16 ± 2.46 (2.48) | 28.23 ± 48.59 (7.97) | 2.30 ± 0.90 (2.31) | 4.78 ± 1.96 (4.55) | 2.32 ± 1.22 (1.97) |
| right/left | p | 0.779 | 25/25 | 0 | 19 | 2.03 ± 1.22 (1.80) | 34.87 ± 57.61 (5.53) | 2.08 ± 1.00 (2.63) | 4.47 ± 2.22 (5.74) | 2.09 ± 1.21 (2.56) |
| right/right | p | 0.792 | 24/25 | 0 | 21 | 1.57 ± 0.40 (1.62) | 10.64 ± 16.52 (5.44) | 2.20 ± 0.73 (2.24) | 4.63 ± 1.64 (4.31) | 2.10 ± 0.98 (1.83) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.805 | 20.2 | 5.30 | 2.60 |
| p | normal | 0.742 | 18.1 | 4.19 | 1.85 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.707 | 0.17 | 2.22 ± 0.98 (2.12) | 3.71 | 1.50 |
| p | medium | 15 | 0.802 | 0.57 | 1.09 ± 0.50 (1.24) | 3.50 | 1.40 |
| p | strong | 125 | 0.802 | 0.72 | - | 5.40 | 2.67 |

## Notes

- p: score 0.774, 196/200 kicked, 0 fell; worst sector back (0.740).
