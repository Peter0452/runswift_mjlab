# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.751** |
| Kicked / fell | 189 / 0 |
| Kicks within 15° | 161 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 2.06 ± 1.52 (1.86) |
| Direction error [°] | 18.03 ± 35.78 (5.88) |
| Avg ball speed [m/s] | 2.06 ± 0.71 (2.25) |
| Peak ball speed [m/s] | 4.35 ± 1.58 (4.98) |
| Distance [m] | 1.92 ± 0.91 (2.09) |
| Path length [m] | 1.93 ± 0.92 (2.10) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.781 | 48/50 | 0 | 43 | 1.74 ± 1.93 (1.39) | 8.52 ± 11.54 (5.33) | 2.07 ± 0.60 (2.24) | 4.40 ± 1.38 (4.89) | 1.90 ± 0.80 (2.09) |
| left | p | 0.759 | 47/50 | 0 | 41 | 2.30 ± 2.08 (1.92) | 15.40 ± 29.02 (4.94) | 2.08 ± 0.69 (2.20) | 4.38 ± 1.51 (4.96) | 1.91 ± 0.88 (2.03) |
| back | p | 0.696 | 46/50 | 0 | 38 | 2.46 ± 0.59 (2.54) | 26.77 ± 50.21 (6.79) | 2.12 ± 0.76 (2.34) | 4.48 ± 1.67 (5.17) | 2.04 ± 0.98 (2.27) |
| right | p | 0.770 | 48/50 | 0 | 39 | 1.76 ± 0.62 (1.85) | 21.75 ± 38.52 (6.09) | 1.98 ± 0.79 (2.27) | 4.15 ± 1.73 (4.76) | 1.82 ± 0.97 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.759 | 97/100 | 0 | 81 | 2.27 ± 2.01 (1.86) | 18.94 ± 35.28 (5.79) | 2.07 ± 0.76 (2.31) | 4.38 ± 1.68 (5.08) | 1.96 ± 0.96 (2.24) |
| right | p | 0.744 | 92/100 | 0 | 80 | 1.84 ± 0.63 (1.81) | 17.07 ± 36.28 (6.23) | 2.05 ± 0.65 (2.20) | 4.32 ± 1.47 (4.76) | 1.87 ± 0.86 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.778 | 25/25 | 0 | 21 | 2.13 ± 2.61 (1.44) | 10.00 ± 14.34 (5.17) | 2.01 ± 0.67 (2.06) | 4.26 ± 1.53 (4.68) | 1.86 ± 0.88 (1.99) |
| forward/right | p | 0.783 | 23/25 | 0 | 22 | 1.32 ± 0.29 (1.28) | 6.92 ± 7.03 (5.48) | 2.13 ± 0.50 (2.24) | 4.54 ± 1.18 (5.03) | 1.94 ± 0.70 (2.25) |
| left/left | p | 0.747 | 24/25 | 0 | 20 | 2.65 ± 2.82 (1.89) | 17.63 ± 29.59 (5.93) | 2.07 ± 0.80 (2.24) | 4.36 ± 1.73 (4.99) | 1.95 ± 0.97 (2.07) |
| left/right | p | 0.771 | 23/25 | 0 | 21 | 1.93 ± 0.48 (1.98) | 13.06 ± 28.22 (4.63) | 2.09 ± 0.54 (2.19) | 4.40 ± 1.24 (4.96) | 1.87 ± 0.78 (1.98) |
| back/left | p | 0.743 | 24/25 | 0 | 21 | 2.41 ± 0.61 (2.58) | 19.42 ± 36.30 (6.34) | 2.22 ± 0.65 (2.41) | 4.70 ± 1.44 (5.31) | 2.15 ± 0.90 (2.36) |
| back/right | p | 0.648 | 22/25 | 0 | 17 | 2.51 ± 0.57 (2.52) | 34.79 ± 60.91 (7.11) | 2.02 ± 0.85 (2.18) | 4.23 ± 1.85 (4.52) | 1.93 ± 1.05 (1.93) |
| right/left | p | 0.767 | 24/25 | 0 | 19 | 1.88 ± 0.72 (1.89) | 29.08 ± 49.34 (4.67) | 1.98 ± 0.89 (2.38) | 4.18 ± 1.93 (5.29) | 1.88 ± 1.06 (2.31) |
| right/right | p | 0.773 | 24/25 | 0 | 20 | 1.64 ± 0.48 (1.77) | 14.42 ± 20.61 (7.77) | 1.98 ± 0.68 (1.98) | 4.12 ± 1.51 (3.98) | 1.75 ± 0.86 (1.63) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.769 | 17.8 | 4.94 | 2.29 |
| p | normal | 0.734 | 18.2 | 3.75 | 1.54 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.684 | 0.24 | 2.00 ± 0.83 (1.97) | 3.41 | 1.29 |
| p | medium | 15 | 0.829 | 0.66 | 0.92 ± 0.44 (1.13) | 2.96 | 1.08 |
| p | strong | 125 | 0.774 | 0.66 | - | 4.96 | 2.31 |

## Notes

- p: score 0.751, 189/200 kicked, 0 fell; worst sector back (0.696).
