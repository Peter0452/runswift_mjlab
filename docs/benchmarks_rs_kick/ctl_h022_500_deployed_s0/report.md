# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_21-10-41_control_h022_500/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.770** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.14 ± 1.96 (1.72) |
| Direction error [°] | 18.11 ± 35.65 (6.19) |
| Avg ball speed [m/s] | 1.97 ± 0.60 (2.17) |
| Peak ball speed [m/s] | 4.38 ± 1.43 (4.86) |
| Distance [m] | 1.66 ± 0.72 (1.80) |
| Path length [m] | 1.67 ± 0.72 (1.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.785 | 50/50 | 0 | 42 | 1.86 ± 2.11 (1.34) | 9.69 ± 12.35 (6.72) | 1.91 ± 0.65 (2.06) | 4.20 ± 1.53 (4.33) | 1.57 ± 0.75 (1.66) |
| left | p | 0.808 | 50/50 | 0 | 43 | 2.03 ± 2.03 (1.72) | 17.34 ± 31.54 (5.02) | 1.99 ± 0.61 (2.18) | 4.47 ± 1.49 (4.96) | 1.70 ± 0.73 (1.95) |
| back | p | 0.720 | 49/50 | 0 | 41 | 2.84 ± 2.00 (2.50) | 28.38 ± 52.48 (8.40) | 2.00 ± 0.61 (2.20) | 4.47 ± 1.45 (5.06) | 1.74 ± 0.74 (1.85) |
| right | p | 0.769 | 48/50 | 0 | 41 | 1.85 ± 1.44 (1.70) | 17.21 ± 32.06 (5.54) | 1.96 ± 0.50 (2.12) | 4.36 ± 1.23 (4.70) | 1.62 ± 0.64 (1.68) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.796 | 100/100 | 0 | 86 | 1.93 ± 1.48 (1.70) | 18.16 ± 36.12 (5.60) | 2.01 ± 0.54 (2.16) | 4.47 ± 1.31 (4.86) | 1.69 ± 0.67 (1.81) |
| right | p | 0.745 | 97/100 | 0 | 81 | 2.36 ± 2.34 (1.72) | 18.06 ± 35.17 (6.81) | 1.92 ± 0.64 (2.18) | 4.28 ± 1.54 (4.82) | 1.62 ± 0.76 (1.78) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.802 | 25/25 | 0 | 21 | 1.68 ± 1.90 (1.28) | 10.43 ± 15.77 (4.30) | 2.07 ± 0.60 (2.22) | 4.54 ± 1.41 (4.56) | 1.76 ± 0.71 (1.77) |
| forward/right | p | 0.768 | 25/25 | 0 | 21 | 2.03 ± 2.28 (1.40) | 8.95 ± 7.42 (7.87) | 1.76 ± 0.65 (1.95) | 3.86 ± 1.57 (3.93) | 1.39 ± 0.74 (1.44) |
| left/left | p | 0.840 | 25/25 | 0 | 23 | 1.57 ± 0.38 (1.64) | 11.41 ± 19.94 (4.47) | 2.07 ± 0.50 (2.16) | 4.65 ± 1.21 (4.87) | 1.78 ± 0.61 (1.93) |
| left/right | p | 0.775 | 25/25 | 0 | 20 | 2.49 ± 2.77 (1.92) | 23.28 ± 39.00 (5.80) | 1.90 ± 0.69 (2.24) | 4.30 ± 1.70 (5.01) | 1.62 ± 0.82 (1.98) |
| back/left | p | 0.735 | 25/25 | 0 | 21 | 2.74 ± 1.98 (2.48) | 29.54 ± 52.77 (8.81) | 2.00 ± 0.56 (2.17) | 4.45 ± 1.36 (4.91) | 1.71 ± 0.72 (1.81) |
| back/right | p | 0.705 | 24/25 | 0 | 20 | 2.95 ± 2.03 (2.52) | 27.17 ± 52.15 (8.08) | 2.01 ± 0.65 (2.22) | 4.49 ± 1.53 (5.10) | 1.77 ± 0.75 (1.93) |
| right/left | p | 0.805 | 25/25 | 0 | 21 | 1.74 ± 0.48 (1.78) | 21.26 ± 39.27 (5.50) | 1.90 ± 0.49 (2.09) | 4.25 ± 1.22 (4.86) | 1.53 ± 0.60 (1.62) |
| right/right | p | 0.732 | 23/25 | 0 | 20 | 1.96 ± 2.01 (1.68) | 12.80 ± 20.78 (5.57) | 2.03 ± 0.50 (2.17) | 4.49 ± 1.22 (4.54) | 1.72 ± 0.67 (1.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.795 | 17.2 | 4.88 | 1.91 |
| p | normal | 0.746 | 19.0 | 3.88 | 1.41 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.715 | 0.20 | 2.30 ± 0.95 (2.09) | 3.64 | 1.26 |
| p | medium | 16 | 0.850 | 0.72 | 1.26 ± 0.15 (1.27) | 4.12 | 1.57 |
| p | strong | 126 | 0.786 | 0.63 | - | 4.76 | 1.85 |

## Notes

- p: score 0.770, 197/200 kicked, 0 fell; worst sector back (0.720).
