# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/u4_20250.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.857** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.92 ± 0.60 (1.88) |
| Direction error [°] | 5.24 ± 3.85 (4.41) |
| Avg ball speed [m/s] | 2.46 ± 0.54 (2.63) |
| Peak ball speed [m/s] | 5.25 ± 1.34 (5.92) |
| Distance [m] | 2.51 ± 0.98 (2.81) |
| Path length [m] | 2.52 ± 0.98 (2.83) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.884 | 50/50 | 0 | 49 | 1.31 ± 0.25 (1.28) | 4.62 ± 4.04 (3.25) | 2.37 ± 0.54 (2.60) | 5.14 ± 1.36 (5.91) | 2.39 ± 0.96 (2.75) |
| left | p | 0.874 | 50/50 | 0 | 49 | 1.86 ± 0.34 (1.86) | 5.36 ± 4.10 (4.32) | 2.51 ± 0.51 (2.68) | 5.36 ± 1.28 (5.93) | 2.59 ± 0.94 (2.85) |
| back | p | 0.799 | 50/50 | 0 | 48 | 2.69 ± 0.41 (2.62) | 6.29 ± 4.00 (5.50) | 2.48 ± 0.54 (2.64) | 5.22 ± 1.35 (5.89) | 2.53 ± 1.02 (2.86) |
| right | p | 0.872 | 50/50 | 0 | 50 | 1.85 ± 0.34 (1.94) | 4.70 ± 2.88 (4.17) | 2.46 ± 0.57 (2.64) | 5.26 ± 1.35 (5.92) | 2.52 ± 0.98 (2.94) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.858 | 100/100 | 0 | 97 | 1.92 ± 0.59 (1.88) | 5.58 ± 4.09 (4.51) | 2.47 ± 0.53 (2.66) | 5.29 ± 1.32 (5.93) | 2.55 ± 0.99 (2.84) |
| right | p | 0.857 | 100/100 | 0 | 99 | 1.93 ± 0.61 (1.89) | 4.90 ± 3.55 (4.09) | 2.44 ± 0.55 (2.62) | 5.20 ± 1.35 (5.91) | 2.47 ± 0.97 (2.77) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.887 | 25/25 | 0 | 24 | 1.31 ± 0.25 (1.28) | 4.72 ± 4.38 (3.46) | 2.38 ± 0.52 (2.55) | 5.14 ± 1.31 (5.80) | 2.41 ± 0.95 (2.63) |
| forward/right | p | 0.882 | 25/25 | 0 | 25 | 1.31 ± 0.25 (1.26) | 4.53 ± 3.67 (3.04) | 2.37 ± 0.55 (2.61) | 5.14 ± 1.40 (5.91) | 2.38 ± 0.97 (2.77) |
| left/left | p | 0.872 | 25/25 | 0 | 24 | 1.73 ± 0.30 (1.78) | 6.12 ± 4.50 (5.87) | 2.58 ± 0.47 (2.70) | 5.52 ± 1.22 (5.97) | 2.72 ± 0.94 (2.91) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.98 ± 0.32 (2.02) | 4.59 ± 3.48 (3.43) | 2.43 ± 0.53 (2.60) | 5.19 ± 1.32 (5.92) | 2.46 ± 0.93 (2.75) |
| back/left | p | 0.805 | 25/25 | 0 | 24 | 2.67 ± 0.42 (2.58) | 7.00 ± 4.01 (5.71) | 2.50 ± 0.54 (2.66) | 5.30 ± 1.34 (6.02) | 2.59 ± 1.03 (2.89) |
| back/right | p | 0.793 | 25/25 | 0 | 24 | 2.70 ± 0.41 (2.66) | 5.58 ± 3.85 (5.48) | 2.45 ± 0.53 (2.63) | 5.14 ± 1.35 (5.83) | 2.48 ± 1.01 (2.80) |
| right/left | p | 0.867 | 25/25 | 0 | 25 | 1.95 ± 0.28 (2.02) | 4.49 ± 2.69 (3.95) | 2.43 ± 0.57 (2.62) | 5.21 ± 1.36 (5.94) | 2.49 ± 1.00 (2.97) |
| right/right | p | 0.876 | 25/25 | 0 | 25 | 1.74 ± 0.35 (1.74) | 4.91 ± 3.04 (4.29) | 2.50 ± 0.57 (2.66) | 5.31 ± 1.33 (5.88) | 2.56 ± 0.96 (2.78) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.894 | 5.7 | 6.23 | 3.20 |
| p | normal | 0.820 | 4.8 | 4.26 | 1.82 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.761 | 0.15 | 2.26 ± 0.66 (2.12) | 3.56 | 1.32 |
| p | medium | 18 | 0.898 | 0.83 | 1.16 ± 0.14 (1.17) | 3.70 | 1.39 |
| p | strong | 124 | 0.896 | 0.83 | - | 6.26 | 3.23 |

## Notes

- p: score 0.857, 200/200 kicked, 0 fell; worst sector back (0.799).
