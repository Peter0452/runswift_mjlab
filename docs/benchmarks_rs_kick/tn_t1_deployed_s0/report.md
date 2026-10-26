# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_23-10-27_t1_stand03/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.738** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 172 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.41 ± 1.56 (2.10) |
| Direction error [°] | 18.86 ± 36.14 (7.78) |
| Avg ball speed [m/s] | 1.94 ± 0.62 (2.07) |
| Peak ball speed [m/s] | 4.05 ± 1.35 (4.58) |
| Distance [m] | 1.62 ± 0.73 (1.71) |
| Path length [m] | 1.63 ± 0.73 (1.72) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.780 | 49/50 | 0 | 44 | 1.94 ± 2.04 (1.58) | 9.51 ± 12.24 (6.79) | 1.86 ± 0.59 (1.95) | 3.89 ± 1.31 (3.91) | 1.48 ± 0.68 (1.48) |
| left | p | 0.758 | 48/50 | 0 | 43 | 2.05 ± 0.63 (2.09) | 17.86 ± 31.94 (7.66) | 1.93 ± 0.63 (2.08) | 4.07 ± 1.36 (4.59) | 1.60 ± 0.69 (1.73) |
| back | p | 0.648 | 50/50 | 0 | 42 | 3.29 ± 1.37 (3.22) | 29.46 ± 52.14 (9.27) | 1.99 ± 0.65 (2.22) | 4.14 ± 1.43 (4.82) | 1.74 ± 0.79 (2.09) |
| right | p | 0.764 | 50/50 | 0 | 43 | 2.32 ± 1.44 (2.13) | 18.40 ± 33.20 (7.75) | 1.98 ± 0.60 (2.12) | 4.11 ± 1.30 (4.66) | 1.67 ± 0.72 (1.72) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.768 | 100/100 | 0 | 89 | 2.17 ± 0.86 (2.04) | 17.92 ± 35.73 (7.70) | 1.99 ± 0.57 (2.11) | 4.14 ± 1.26 (4.64) | 1.66 ± 0.68 (1.73) |
| right | p | 0.707 | 97/100 | 0 | 83 | 2.65 ± 2.01 (2.16) | 19.84 ± 36.53 (7.78) | 1.89 ± 0.66 (2.04) | 3.96 ± 1.45 (4.52) | 1.59 ± 0.77 (1.64) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.823 | 25/25 | 0 | 24 | 1.53 ± 0.35 (1.58) | 8.56 ± 10.55 (7.00) | 1.88 ± 0.62 (1.99) | 3.95 ± 1.40 (3.95) | 1.51 ± 0.66 (1.55) |
| forward/right | p | 0.737 | 24/25 | 0 | 20 | 2.37 ± 2.83 (1.62) | 10.51 ± 13.71 (4.56) | 1.84 ± 0.54 (1.87) | 3.83 ± 1.21 (3.83) | 1.46 ± 0.69 (1.40) |
| left/left | p | 0.831 | 25/25 | 0 | 24 | 1.95 ± 0.52 (2.04) | 10.52 ± 16.97 (7.84) | 2.12 ± 0.39 (2.13) | 4.44 ± 0.88 (4.67) | 1.79 ± 0.53 (1.90) |
| left/right | p | 0.685 | 23/25 | 0 | 19 | 2.17 ± 0.72 (2.32) | 25.84 ± 41.15 (7.48) | 1.72 ± 0.76 (2.02) | 3.66 ± 1.65 (4.44) | 1.40 ± 0.78 (1.47) |
| back/left | p | 0.662 | 25/25 | 0 | 20 | 3.03 ± 1.01 (3.20) | 32.14 ± 55.44 (9.14) | 1.99 ± 0.59 (2.21) | 4.12 ± 1.32 (4.85) | 1.70 ± 0.77 (2.14) |
| back/right | p | 0.634 | 25/25 | 0 | 22 | 3.55 ± 1.62 (3.24) | 26.77 ± 48.46 (9.89) | 2.00 ± 0.70 (2.24) | 4.16 ± 1.53 (4.82) | 1.78 ± 0.80 (2.08) |
| right/left | p | 0.757 | 25/25 | 0 | 21 | 2.18 ± 0.61 (2.18) | 20.46 ± 35.81 (9.06) | 1.97 ± 0.60 (2.07) | 4.05 ± 1.30 (4.64) | 1.63 ± 0.71 (1.68) |
| right/right | p | 0.772 | 25/25 | 0 | 22 | 2.45 ± 1.93 (2.12) | 16.34 ± 30.22 (7.73) | 1.99 ± 0.59 (2.13) | 4.17 ± 1.29 (4.71) | 1.71 ± 0.72 (1.85) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.765 | 16.6 | 4.62 | 1.95 |
| p | normal | 0.711 | 21.2 | 3.48 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.677 | 0.23 | 2.06 ± 0.85 (1.91) | 3.26 | 1.15 |
| p | medium | 16 | 0.796 | 0.82 | 1.09 ± 0.22 (1.07) | 3.54 | 1.30 |
| p | strong | 126 | 0.758 | 0.60 | - | 4.48 | 1.88 |

## Notes

- p: score 0.738, 197/200 kicked, 0 fell; worst sector back (0.648).
