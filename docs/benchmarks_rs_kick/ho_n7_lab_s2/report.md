# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.842** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.61 ± 0.55 (1.57) |
| Direction error [°] | 5.73 ± 3.55 (5.65) |
| Avg ball speed [m/s] | 2.15 ± 0.35 (2.19) |
| Peak ball speed [m/s] | 4.60 ± 0.81 (4.74) |
| Distance [m] | 1.96 ± 0.54 (1.97) |
| Path length [m] | 1.97 ± 0.54 (1.98) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.843 | 50/50 | 0 | 49 | 1.05 ± 0.24 (1.03) | 5.81 ± 3.70 (5.53) | 2.06 ± 0.29 (2.06) | 4.44 ± 0.68 (4.56) | 1.82 ± 0.47 (1.82) |
| left | p | 0.846 | 50/50 | 0 | 50 | 1.51 ± 0.36 (1.54) | 5.90 ± 3.26 (5.86) | 2.20 ± 0.32 (2.23) | 4.66 ± 0.76 (4.75) | 2.00 ± 0.53 (2.06) |
| back | p | 0.819 | 50/50 | 0 | 49 | 2.33 ± 0.28 (2.31) | 6.16 ± 3.59 (5.80) | 2.25 ± 0.43 (2.36) | 4.79 ± 0.98 (5.14) | 2.14 ± 0.58 (2.26) |
| right | p | 0.862 | 50/50 | 0 | 49 | 1.55 ± 0.34 (1.64) | 5.04 ± 3.55 (4.59) | 2.12 ± 0.33 (2.16) | 4.49 ± 0.76 (4.62) | 1.89 ± 0.52 (1.86) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.849 | 100/100 | 0 | 100 | 1.62 ± 0.55 (1.61) | 5.55 ± 3.26 (5.64) | 2.17 ± 0.32 (2.22) | 4.64 ± 0.73 (4.79) | 1.98 ± 0.51 (2.05) |
| right | p | 0.836 | 100/100 | 0 | 97 | 1.61 ± 0.56 (1.55) | 5.91 ± 3.81 (5.67) | 2.14 ± 0.39 (2.16) | 4.55 ± 0.89 (4.70) | 1.94 ± 0.57 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.843 | 25/25 | 0 | 25 | 1.06 ± 0.24 (1.04) | 5.46 ± 2.81 (5.82) | 2.03 ± 0.29 (2.02) | 4.37 ± 0.68 (4.33) | 1.78 ± 0.48 (1.59) |
| forward/right | p | 0.844 | 25/25 | 0 | 24 | 1.04 ± 0.23 (0.98) | 6.16 ± 4.38 (4.83) | 2.08 ± 0.28 (2.08) | 4.51 ± 0.66 (4.60) | 1.85 ± 0.45 (1.90) |
| left/left | p | 0.849 | 25/25 | 0 | 25 | 1.43 ± 0.35 (1.46) | 6.43 ± 3.18 (6.56) | 2.19 ± 0.32 (2.23) | 4.66 ± 0.73 (4.74) | 1.99 ± 0.50 (2.04) |
| left/right | p | 0.843 | 25/25 | 0 | 25 | 1.60 ± 0.36 (1.56) | 5.38 ± 3.25 (5.21) | 2.20 ± 0.33 (2.14) | 4.67 ± 0.80 (4.76) | 2.02 ± 0.56 (2.15) |
| back/left | p | 0.831 | 25/25 | 0 | 25 | 2.32 ± 0.29 (2.32) | 5.98 ± 3.51 (5.79) | 2.31 ± 0.28 (2.36) | 4.96 ± 0.64 (5.17) | 2.22 ± 0.43 (2.27) |
| back/right | p | 0.807 | 25/25 | 0 | 24 | 2.34 ± 0.28 (2.26) | 6.34 ± 3.66 (5.81) | 2.18 ± 0.54 (2.26) | 4.62 ± 1.20 (5.00) | 2.05 ± 0.69 (2.18) |
| right/left | p | 0.874 | 25/25 | 0 | 25 | 1.65 ± 0.31 (1.70) | 4.32 ± 3.13 (3.82) | 2.15 ± 0.31 (2.14) | 4.57 ± 0.73 (4.66) | 1.95 ± 0.51 (1.88) |
| right/right | p | 0.850 | 25/25 | 0 | 24 | 1.45 ± 0.33 (1.52) | 5.76 ± 3.78 (5.53) | 2.08 ± 0.33 (2.17) | 4.41 ± 0.78 (4.41) | 1.83 ± 0.53 (1.70) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.873 | 5.8 | 5.11 | 2.29 |
| p | normal | 0.812 | 5.7 | 4.08 | 1.63 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.773 | 0.16 | 2.30 ± 0.73 (2.14) | 3.78 | 1.42 |
| p | medium | 15 | 0.869 | 0.74 | 1.10 ± 0.33 (1.15) | 3.55 | 1.32 |
| p | strong | 125 | 0.873 | 0.68 | - | 5.11 | 2.30 |

## Notes

- p: score 0.842, 200/200 kicked, 0 fell; worst sector back (0.819).
