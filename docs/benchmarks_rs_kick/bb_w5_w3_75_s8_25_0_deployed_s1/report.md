# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w5_w3_75_s8_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.87 ± 0.58 (1.76) |
| Direction error [°] | 5.14 ± 3.29 (4.30) |
| Avg ball speed [m/s] | 2.25 ± 0.37 (2.36) |
| Peak ball speed [m/s] | 4.97 ± 1.03 (5.48) |
| Distance [m] | 2.06 ± 0.65 (2.19) |
| Path length [m] | 2.07 ± 0.65 (2.19) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.878 | 50/50 | 0 | 49 | 1.28 ± 0.26 (1.31) | 4.67 ± 3.43 (3.60) | 2.24 ± 0.42 (2.40) | 5.00 ± 1.17 (5.61) | 2.05 ± 0.71 (2.22) |
| left | p | 0.860 | 50/50 | 0 | 50 | 1.80 ± 0.37 (1.71) | 5.87 ± 3.28 (5.27) | 2.25 ± 0.34 (2.29) | 4.91 ± 0.92 (5.30) | 2.03 ± 0.58 (2.03) |
| back | p | 0.815 | 50/50 | 0 | 50 | 2.59 ± 0.34 (2.50) | 5.86 ± 3.26 (6.38) | 2.33 ± 0.36 (2.46) | 5.14 ± 0.99 (5.64) | 2.19 ± 0.64 (2.40) |
| right | p | 0.863 | 50/50 | 0 | 50 | 1.80 ± 0.36 (1.76) | 4.16 ± 2.83 (3.48) | 2.19 ± 0.35 (2.24) | 4.82 ± 1.00 (5.33) | 1.95 ± 0.62 (2.02) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 99 | 1.85 ± 0.57 (1.74) | 5.66 ± 3.67 (5.54) | 2.26 ± 0.39 (2.36) | 5.00 ± 1.06 (5.49) | 2.09 ± 0.68 (2.20) |
| right | p | 0.862 | 100/100 | 0 | 100 | 1.88 ± 0.58 (1.85) | 4.62 ± 2.77 (4.19) | 2.24 ± 0.34 (2.36) | 4.94 ± 1.00 (5.48) | 2.03 ± 0.61 (2.13) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.866 | 25/25 | 0 | 24 | 1.26 ± 0.26 (1.30) | 5.56 ± 3.82 (5.61) | 2.18 ± 0.43 (2.36) | 4.90 ± 1.18 (5.50) | 1.99 ± 0.73 (2.15) |
| forward/right | p | 0.889 | 25/25 | 0 | 25 | 1.31 ± 0.27 (1.32) | 3.79 ± 2.70 (2.46) | 2.29 ± 0.39 (2.44) | 5.11 ± 1.14 (5.71) | 2.11 ± 0.68 (2.30) |
| left/left | p | 0.850 | 25/25 | 0 | 25 | 1.68 ± 0.34 (1.60) | 7.16 ± 3.20 (7.90) | 2.30 ± 0.32 (2.30) | 5.01 ± 0.92 (5.36) | 2.12 ± 0.59 (2.19) |
| left/right | p | 0.871 | 25/25 | 0 | 25 | 1.91 ± 0.36 (1.98) | 4.58 ± 2.81 (4.13) | 2.21 ± 0.34 (2.17) | 4.82 ± 0.92 (5.21) | 1.95 ± 0.57 (1.96) |
| back/left | p | 0.814 | 25/25 | 0 | 25 | 2.57 ± 0.29 (2.48) | 5.96 ± 3.70 (7.14) | 2.35 ± 0.42 (2.48) | 5.17 ± 1.07 (5.68) | 2.22 ± 0.69 (2.48) |
| back/right | p | 0.816 | 25/25 | 0 | 25 | 2.61 ± 0.38 (2.56) | 5.77 ± 2.74 (6.04) | 2.32 ± 0.30 (2.44) | 5.11 ± 0.91 (5.55) | 2.16 ± 0.59 (2.39) |
| right/left | p | 0.853 | 25/25 | 0 | 25 | 1.90 ± 0.36 (1.78) | 3.97 ± 3.16 (3.22) | 2.22 ± 0.38 (2.34) | 4.91 ± 1.04 (5.47) | 2.01 ± 0.67 (2.02) |
| right/right | p | 0.872 | 25/25 | 0 | 25 | 1.69 ± 0.34 (1.68) | 4.35 ± 2.44 (3.73) | 2.15 ± 0.31 (2.20) | 4.73 ± 0.96 (5.12) | 1.88 ± 0.56 (1.98) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.885 | 5.2 | 5.73 | 2.49 |
| p | normal | 0.823 | 5.0 | 4.21 | 1.62 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.768 | 0.14 | 2.35 ± 0.73 (2.25) | 3.66 | 1.29 |
| p | medium | 20 | 0.896 | 0.82 | 1.17 ± 0.11 (1.19) | 3.76 | 1.37 |
| p | strong | 126 | 0.884 | 0.76 | - | 5.72 | 2.49 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.815).
