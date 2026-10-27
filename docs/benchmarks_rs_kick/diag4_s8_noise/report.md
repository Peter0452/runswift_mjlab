# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.61 ± 0.55 (1.53) |
| Direction error [°] | 5.09 ± 9.12 (3.33) |
| Avg ball speed [m/s] | 1.78 ± 0.34 (1.81) |
| Peak ball speed [m/s] | 4.51 ± 0.86 (4.66) |
| Distance [m] | 1.83 ± 0.54 (1.84) |
| Path length [m] | 1.84 ± 0.54 (1.85) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.827 | 50/50 | 0 | 48 | 1.14 ± 0.53 (1.07) | 5.54 ± 4.72 (3.69) | 1.59 ± 0.35 (1.55) | 4.00 ± 0.85 (3.86) | 1.47 ± 0.49 (1.38) |
| left | p | 0.885 | 50/50 | 0 | 49 | 1.53 ± 0.33 (1.56) | 3.48 ± 2.80 (2.62) | 1.82 ± 0.29 (1.88) | 4.73 ± 0.71 (4.95) | 1.97 ± 0.47 (2.03) |
| back | p | 0.852 | 50/50 | 0 | 49 | 2.24 ± 0.24 (2.21) | 6.36 ± 16.97 (3.01) | 1.87 ± 0.36 (1.95) | 4.80 ± 0.89 (5.11) | 2.02 ± 0.56 (2.07) |
| right | p | 0.843 | 50/50 | 0 | 50 | 1.52 ± 0.33 (1.50) | 4.97 ± 3.25 (3.94) | 1.82 ± 0.29 (1.82) | 4.53 ± 0.72 (4.36) | 1.87 ± 0.45 (1.84) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.852 | 100/100 | 0 | 97 | 1.62 ± 0.56 (1.55) | 5.60 ± 12.35 (3.20) | 1.77 ± 0.35 (1.82) | 4.51 ± 0.86 (4.72) | 1.81 ± 0.53 (1.84) |
| right | p | 0.852 | 100/100 | 0 | 99 | 1.60 ± 0.53 (1.52) | 4.58 ± 3.67 (3.48) | 1.78 ± 0.34 (1.80) | 4.52 ± 0.85 (4.58) | 1.85 ± 0.54 (1.84) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 24 | 1.17 ± 0.63 (1.06) | 5.71 ± 4.61 (4.04) | 1.60 ± 0.33 (1.52) | 3.98 ± 0.79 (3.84) | 1.44 ± 0.45 (1.34) |
| forward/right | p | 0.831 | 25/25 | 0 | 24 | 1.10 ± 0.40 (1.08) | 5.37 ± 4.83 (3.34) | 1.58 ± 0.37 (1.60) | 4.02 ± 0.90 (3.88) | 1.50 ± 0.52 (1.48) |
| left/left | p | 0.877 | 25/25 | 0 | 24 | 1.44 ± 0.32 (1.50) | 3.86 ± 3.23 (2.81) | 1.75 ± 0.28 (1.74) | 4.62 ± 0.73 (4.95) | 1.88 ± 0.47 (1.88) |
| left/right | p | 0.894 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.66) | 3.11 ± 2.23 (2.59) | 1.89 ± 0.28 (1.93) | 4.84 ± 0.68 (5.07) | 2.05 ± 0.45 (2.06) |
| back/left | p | 0.861 | 25/25 | 0 | 24 | 2.24 ± 0.22 (2.20) | 7.67 ± 23.69 (2.38) | 1.87 ± 0.41 (1.95) | 4.75 ± 0.96 (5.11) | 1.98 ± 0.58 (2.06) |
| back/right | p | 0.844 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.24) | 5.06 ± 3.34 (4.41) | 1.88 ± 0.31 (1.96) | 4.85 ± 0.81 (5.12) | 2.05 ± 0.53 (2.09) |
| right/left | p | 0.848 | 25/25 | 0 | 25 | 1.62 ± 0.30 (1.60) | 5.16 ± 3.10 (4.51) | 1.88 ± 0.28 (1.90) | 4.67 ± 0.71 (4.94) | 1.94 ± 0.43 (1.96) |
| right/right | p | 0.838 | 25/25 | 0 | 25 | 1.42 ± 0.33 (1.42) | 4.78 ± 3.37 (3.67) | 1.76 ± 0.30 (1.68) | 4.39 ± 0.70 (4.06) | 1.79 ± 0.45 (1.54) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 4.4 | 5.00 | 2.11 |
| p | normal | 0.819 | 5.8 | 4.03 | 1.55 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.773 | 0.12 | 2.32 ± 0.75 (2.08) | 3.68 | 1.35 |
| p | medium | 16 | 0.896 | 0.78 | 1.13 ± 0.21 (1.16) | 3.66 | 1.35 |
| p | strong | 126 | 0.883 | 0.67 | - | 5.01 | 2.11 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector forward (0.827).
