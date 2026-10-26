# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s6_ctl7_30_n7_70.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.836** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.57 ± 0.53 (1.51) |
| Direction error [°] | 7.47 ± 15.89 (5.02) |
| Avg ball speed [m/s] | 2.10 ± 0.37 (2.08) |
| Peak ball speed [m/s] | 4.47 ± 0.86 (4.42) |
| Distance [m] | 1.89 ± 0.55 (1.84) |
| Path length [m] | 1.90 ± 0.55 (1.86) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.846 | 50/50 | 0 | 49 | 1.02 ± 0.22 (1.02) | 5.46 ± 3.82 (4.59) | 1.96 ± 0.32 (1.95) | 4.20 ± 0.73 (3.98) | 1.67 ± 0.51 (1.51) |
| left | p | 0.843 | 50/50 | 0 | 48 | 1.50 ± 0.32 (1.48) | 6.17 ± 4.63 (4.09) | 2.13 ± 0.29 (2.12) | 4.54 ± 0.70 (4.53) | 1.92 ± 0.48 (1.91) |
| back | p | 0.813 | 50/50 | 0 | 48 | 2.25 ± 0.32 (2.26) | 12.72 ± 30.37 (5.90) | 2.14 ± 0.48 (2.21) | 4.55 ± 1.12 (4.74) | 1.99 ± 0.64 (2.15) |
| right | p | 0.844 | 50/50 | 0 | 50 | 1.52 ± 0.32 (1.59) | 5.54 ± 3.81 (4.87) | 2.16 ± 0.33 (2.23) | 4.60 ± 0.77 (4.86) | 1.97 ± 0.52 (2.11) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.843 | 100/100 | 0 | 98 | 1.57 ± 0.52 (1.52) | 7.02 ± 16.27 (4.51) | 2.11 ± 0.36 (2.13) | 4.49 ± 0.84 (4.53) | 1.90 ± 0.55 (1.87) |
| right | p | 0.830 | 100/100 | 0 | 97 | 1.57 ± 0.54 (1.48) | 7.92 ± 15.49 (5.58) | 2.09 ± 0.38 (2.01) | 4.46 ± 0.88 (4.37) | 1.88 ± 0.56 (1.79) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.854 | 25/25 | 0 | 25 | 1.03 ± 0.21 (1.02) | 4.85 ± 3.27 (4.41) | 1.99 ± 0.31 (1.97) | 4.26 ± 0.73 (4.10) | 1.71 ± 0.54 (1.57) |
| forward/right | p | 0.837 | 25/25 | 0 | 24 | 1.01 ± 0.22 (1.06) | 6.07 ± 4.21 (4.76) | 1.93 ± 0.32 (1.82) | 4.14 ± 0.72 (3.94) | 1.63 ± 0.47 (1.48) |
| left/left | p | 0.841 | 25/25 | 0 | 24 | 1.41 ± 0.30 (1.46) | 6.58 ± 4.50 (4.14) | 2.14 ± 0.31 (2.19) | 4.55 ± 0.71 (4.58) | 1.93 ± 0.47 (2.01) |
| left/right | p | 0.846 | 25/25 | 0 | 24 | 1.59 ± 0.31 (1.56) | 5.76 ± 4.71 (4.04) | 2.12 ± 0.27 (2.05) | 4.53 ± 0.69 (4.39) | 1.91 ± 0.49 (1.84) |
| back/left | p | 0.826 | 25/25 | 0 | 24 | 2.24 ± 0.32 (2.24) | 12.17 ± 31.16 (5.59) | 2.12 ± 0.46 (2.21) | 4.53 ± 1.09 (4.69) | 1.96 ± 0.62 (2.15) |
| back/right | p | 0.799 | 25/25 | 0 | 24 | 2.27 ± 0.32 (2.32) | 13.26 ± 29.54 (5.97) | 2.16 ± 0.50 (2.26) | 4.58 ± 1.15 (4.78) | 2.01 ± 0.65 (2.14) |
| right/left | p | 0.851 | 25/25 | 0 | 25 | 1.61 ± 0.29 (1.64) | 4.49 ± 4.32 (2.52) | 2.17 ± 0.31 (2.28) | 4.61 ± 0.74 (4.92) | 1.98 ± 0.51 (2.10) |
| right/right | p | 0.837 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.36) | 6.59 ± 2.86 (6.89) | 2.16 ± 0.34 (2.17) | 4.59 ± 0.79 (4.80) | 1.95 ± 0.53 (2.11) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.874 | 6.7 | 4.94 | 2.20 |
| p | normal | 0.799 | 8.2 | 4.00 | 1.57 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.748 | 0.13 | 2.33 ± 0.72 (2.35) | 3.71 | 1.38 |
| p | medium | 18 | 0.882 | 0.79 | 1.19 ± 0.16 (1.17) | 3.79 | 1.40 |
| p | strong | 124 | 0.871 | 0.66 | - | 4.93 | 2.20 |

## Notes

- p: score 0.836, 200/200 kicked, 0 fell; worst sector back (0.813).
