# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_01-33-49_t7_n7_lowcap03/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.771** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 1.92 ± 0.93 (1.80) |
| Direction error [°] | 17.86 ± 35.88 (5.41) |
| Avg ball speed [m/s] | 1.99 ± 0.68 (2.19) |
| Peak ball speed [m/s] | 4.39 ± 1.62 (4.97) |
| Distance [m] | 1.71 ± 0.84 (1.85) |
| Path length [m] | 1.72 ± 0.84 (1.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.781 | 49/50 | 0 | 42 | 1.70 ± 1.40 (1.48) | 9.85 ± 13.39 (5.82) | 1.87 ± 0.75 (1.99) | 4.08 ± 1.76 (4.04) | 1.54 ± 0.88 (1.57) |
| left | p | 0.792 | 48/50 | 0 | 41 | 1.73 ± 0.47 (1.82) | 18.29 ± 32.89 (5.32) | 2.07 ± 0.65 (2.29) | 4.58 ± 1.56 (5.26) | 1.81 ± 0.81 (2.05) |
| back | p | 0.742 | 49/50 | 0 | 42 | 2.48 ± 0.76 (2.58) | 26.87 ± 51.57 (7.16) | 2.02 ± 0.68 (2.21) | 4.45 ± 1.60 (5.06) | 1.78 ± 0.85 (1.85) |
| right | p | 0.767 | 47/50 | 0 | 39 | 1.76 ± 0.47 (1.80) | 16.40 ± 32.68 (4.04) | 2.01 ± 0.61 (2.18) | 4.44 ± 1.49 (4.97) | 1.73 ± 0.78 (1.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 98/100 | 0 | 88 | 1.89 ± 0.97 (1.82) | 15.95 ± 35.26 (4.80) | 2.05 ± 0.61 (2.21) | 4.54 ± 1.47 (5.03) | 1.78 ± 0.78 (1.89) |
| right | p | 0.742 | 95/100 | 0 | 76 | 1.95 ± 0.88 (1.80) | 19.84 ± 36.40 (6.22) | 1.93 ± 0.74 (2.18) | 4.23 ± 1.75 (4.62) | 1.65 ± 0.89 (1.76) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.827 | 25/25 | 0 | 23 | 1.72 ± 1.62 (1.46) | 7.58 ± 12.27 (3.35) | 2.01 ± 0.69 (2.12) | 4.47 ± 1.67 (4.34) | 1.73 ± 0.87 (1.76) |
| forward/right | p | 0.735 | 24/25 | 0 | 19 | 1.68 ± 1.14 (1.49) | 12.20 ± 14.08 (7.66) | 1.72 ± 0.77 (1.88) | 3.68 ± 1.77 (3.88) | 1.35 ± 0.85 (1.38) |
| left/left | p | 0.853 | 25/25 | 0 | 23 | 1.66 ± 0.42 (1.80) | 11.85 ± 22.90 (4.65) | 2.15 ± 0.48 (2.29) | 4.79 ± 1.18 (5.32) | 1.89 ± 0.65 (2.06) |
| left/right | p | 0.730 | 23/25 | 0 | 18 | 1.80 ± 0.52 (1.84) | 25.28 ± 39.92 (6.00) | 1.98 ± 0.79 (2.26) | 4.35 ± 1.86 (5.13) | 1.71 ± 0.95 (2.04) |
| back/left | p | 0.739 | 24/25 | 0 | 21 | 2.35 ± 0.66 (2.46) | 25.97 ± 50.44 (8.15) | 2.09 ± 0.59 (2.28) | 4.62 ± 1.40 (5.13) | 1.86 ± 0.80 (1.95) |
| back/right | p | 0.745 | 25/25 | 0 | 21 | 2.59 ± 0.82 (2.64) | 27.73 ± 52.62 (5.90) | 1.94 ± 0.74 (2.19) | 4.29 ± 1.77 (4.69) | 1.70 ± 0.88 (1.68) |
| right/left | p | 0.778 | 24/25 | 0 | 21 | 1.85 ± 0.48 (1.87) | 18.90 ± 40.38 (3.79) | 1.94 ± 0.64 (2.08) | 4.28 ± 1.54 (4.34) | 1.64 ± 0.77 (1.70) |
| right/right | p | 0.757 | 23/25 | 0 | 18 | 1.67 ± 0.44 (1.76) | 13.80 ± 21.64 (6.06) | 2.08 ± 0.58 (2.22) | 4.61 ± 1.42 (5.10) | 1.83 ± 0.78 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.786 | 16.6 | 5.03 | 2.06 |
| p | normal | 0.755 | 19.1 | 3.76 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.720 | 0.20 | 2.14 ± 0.92 (2.04) | 3.41 | 1.17 |
| p | medium | 16 | 0.826 | 0.72 | 1.22 ± 0.24 (1.25) | 3.94 | 1.45 |
| p | strong | 126 | 0.787 | 0.65 | - | 4.90 | 2.00 |

## Notes

- p: score 0.771, 193/200 kicked, 0 fell; worst sector back (0.742).
