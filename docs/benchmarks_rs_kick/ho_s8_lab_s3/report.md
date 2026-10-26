# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.53 (1.52) |
| Direction error [°] | 6.57 ± 14.56 (4.70) |
| Avg ball speed [m/s] | 2.04 ± 0.39 (2.03) |
| Peak ball speed [m/s] | 4.36 ± 0.89 (4.39) |
| Distance [m] | 1.77 ± 0.56 (1.74) |
| Path length [m] | 1.78 ± 0.56 (1.74) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.856 | 50/50 | 0 | 49 | 1.02 ± 0.21 (1.04) | 4.71 ± 3.58 (3.83) | 1.87 ± 0.33 (1.87) | 4.02 ± 0.76 (3.85) | 1.52 ± 0.50 (1.44) |
| left | p | 0.854 | 50/50 | 0 | 50 | 1.51 ± 0.32 (1.50) | 5.43 ± 3.41 (5.11) | 2.13 ± 0.32 (2.17) | 4.55 ± 0.75 (4.83) | 1.90 ± 0.50 (2.00) |
| back | p | 0.831 | 50/50 | 0 | 48 | 2.24 ± 0.31 (2.22) | 10.65 ± 28.13 (4.80) | 2.11 ± 0.50 (2.21) | 4.46 ± 1.14 (4.87) | 1.90 ± 0.65 (2.02) |
| right | p | 0.841 | 50/50 | 0 | 50 | 1.51 ± 0.30 (1.54) | 5.47 ± 3.13 (5.10) | 2.04 ± 0.31 (2.03) | 4.39 ± 0.75 (4.46) | 1.78 ± 0.48 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.848 | 100/100 | 0 | 99 | 1.57 ± 0.52 (1.56) | 6.42 ± 14.91 (4.11) | 2.04 ± 0.38 (2.05) | 4.36 ± 0.89 (4.40) | 1.78 ± 0.57 (1.71) |
| right | p | 0.843 | 100/100 | 0 | 98 | 1.57 ± 0.53 (1.50) | 6.72 ± 14.20 (4.85) | 2.03 ± 0.39 (2.03) | 4.35 ± 0.89 (4.39) | 1.77 ± 0.55 (1.76) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.865 | 25/25 | 0 | 25 | 1.03 ± 0.21 (1.04) | 3.97 ± 2.68 (3.58) | 1.85 ± 0.34 (1.86) | 3.98 ± 0.79 (3.83) | 1.49 ± 0.53 (1.36) |
| forward/right | p | 0.847 | 25/25 | 0 | 24 | 1.01 ± 0.22 (1.06) | 5.45 ± 4.16 (4.75) | 1.88 ± 0.32 (1.88) | 4.07 ± 0.74 (3.92) | 1.55 ± 0.46 (1.47) |
| left/left | p | 0.858 | 25/25 | 0 | 25 | 1.41 ± 0.31 (1.44) | 4.98 ± 3.63 (3.76) | 2.12 ± 0.32 (2.19) | 4.51 ± 0.74 (4.77) | 1.87 ± 0.48 (1.99) |
| left/right | p | 0.850 | 25/25 | 0 | 25 | 1.60 ± 0.31 (1.60) | 5.88 ± 3.11 (5.79) | 2.14 ± 0.32 (2.16) | 4.59 ± 0.77 (4.88) | 1.94 ± 0.52 (2.01) |
| back/left | p | 0.838 | 25/25 | 0 | 24 | 2.25 ± 0.31 (2.22) | 10.77 ± 28.83 (4.71) | 2.14 ± 0.49 (2.30) | 4.53 ± 1.14 (4.85) | 1.95 ± 0.67 (2.06) |
| back/right | p | 0.823 | 25/25 | 0 | 24 | 2.24 ± 0.31 (2.28) | 10.54 ± 27.40 (4.82) | 2.08 ± 0.51 (2.21) | 4.40 ± 1.14 (4.88) | 1.85 ± 0.63 (1.98) |
| right/left | p | 0.831 | 25/25 | 0 | 25 | 1.61 ± 0.27 (1.60) | 5.95 ± 3.16 (5.53) | 2.06 ± 0.28 (2.04) | 4.44 ± 0.72 (4.46) | 1.82 ± 0.48 (1.87) |
| right/right | p | 0.850 | 25/25 | 0 | 25 | 1.42 ± 0.30 (1.46) | 4.99 ± 3.01 (4.66) | 2.03 ± 0.33 (2.02) | 4.33 ± 0.78 (4.34) | 1.73 ± 0.48 (1.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.875 | 6.2 | 4.85 | 2.08 |
| p | normal | 0.816 | 6.9 | 3.87 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.768 | 0.16 | 2.24 ± 0.74 (2.20) | 3.54 | 1.26 |
| p | medium | 18 | 0.898 | 0.81 | 1.16 ± 0.16 (1.18) | 3.71 | 1.34 |
| p | strong | 124 | 0.874 | 0.64 | - | 4.83 | 2.08 |

## Notes

- p: score 0.845, 200/200 kicked, 0 fell; worst sector back (0.831).
