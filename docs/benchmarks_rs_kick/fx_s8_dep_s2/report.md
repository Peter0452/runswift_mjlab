# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s8_ctl7_n7_n5b_n4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 190 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.83 ± 0.59 (1.78) |
| Direction error [°] | 6.81 ± 13.47 (4.27) |
| Avg ball speed [m/s] | 2.00 ± 0.58 (2.12) |
| Peak ball speed [m/s] | 5.38 ± 0.96 (5.73) |
| Distance [m] | 2.91 ± 1.33 (2.64) |
| Path length [m] | 3.03 ± 1.36 (2.67) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.854 | 50/50 | 0 | 48 | 1.26 ± 0.25 (1.25) | 7.17 ± 11.81 (5.79) | 1.97 ± 0.52 (2.10) | 5.24 ± 0.90 (5.63) | 2.72 ± 1.22 (2.53) |
| left | p | 0.859 | 50/50 | 0 | 48 | 1.75 ± 0.37 (1.78) | 6.09 ± 11.45 (3.24) | 1.93 ± 0.54 (2.05) | 5.38 ± 0.93 (5.68) | 3.13 ± 1.54 (2.64) |
| back | p | 0.785 | 49/50 | 0 | 46 | 2.58 ± 0.41 (2.54) | 8.43 ± 20.67 (4.65) | 2.02 ± 0.68 (2.23) | 5.51 ± 1.09 (5.85) | 3.01 ± 1.33 (2.70) |
| right | p | 0.861 | 50/50 | 0 | 48 | 1.75 ± 0.35 (1.81) | 5.57 ± 5.31 (4.05) | 2.09 ± 0.55 (2.19) | 5.39 ± 0.88 (5.73) | 2.76 ± 1.16 (2.64) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.841 | 99/100 | 0 | 95 | 1.84 ± 0.58 (1.80) | 5.52 ± 4.99 (4.06) | 2.03 ± 0.55 (2.16) | 5.45 ± 0.85 (5.77) | 2.98 ± 1.32 (2.64) |
| right | p | 0.838 | 100/100 | 0 | 95 | 1.83 ± 0.60 (1.78) | 8.08 ± 18.25 (5.26) | 1.98 ± 0.60 (2.08) | 5.30 ± 1.05 (5.63) | 2.84 ± 1.34 (2.63) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.848 | 25/25 | 0 | 25 | 1.27 ± 0.24 (1.30) | 5.66 ± 3.69 (5.27) | 1.98 ± 0.48 (2.06) | 5.17 ± 0.84 (5.39) | 2.55 ± 1.20 (2.30) |
| forward/right | p | 0.859 | 25/25 | 0 | 23 | 1.25 ± 0.26 (1.22) | 8.68 ± 16.15 (6.16) | 1.97 ± 0.56 (2.16) | 5.31 ± 0.95 (5.75) | 2.90 ± 1.22 (2.66) |
| left/left | p | 0.870 | 25/25 | 0 | 24 | 1.66 ± 0.35 (1.66) | 5.10 ± 4.01 (3.58) | 1.97 ± 0.57 (2.16) | 5.43 ± 0.88 (5.73) | 3.27 ± 1.55 (2.71) |
| left/right | p | 0.848 | 25/25 | 0 | 24 | 1.84 ± 0.35 (1.78) | 7.08 ± 15.62 (2.80) | 1.89 ± 0.50 (2.02) | 5.32 ± 0.97 (5.36) | 3.00 ± 1.51 (2.56) |
| back/left | p | 0.774 | 24/25 | 0 | 22 | 2.58 ± 0.38 (2.60) | 6.39 ± 7.10 (4.04) | 2.06 ± 0.58 (2.26) | 5.74 ± 0.68 (5.89) | 3.15 ± 1.11 (2.74) |
| back/right | p | 0.796 | 25/25 | 0 | 24 | 2.57 ± 0.44 (2.48) | 10.40 ± 27.94 (5.52) | 1.98 ± 0.76 (2.17) | 5.28 ± 1.33 (5.80) | 2.88 ± 1.50 (2.64) |
| right/left | p | 0.874 | 25/25 | 0 | 24 | 1.86 ± 0.33 (1.96) | 4.97 ± 4.39 (3.47) | 2.11 ± 0.57 (2.26) | 5.47 ± 0.88 (5.89) | 2.95 ± 1.24 (2.88) |
| right/right | p | 0.848 | 25/25 | 0 | 24 | 1.64 ± 0.33 (1.70) | 6.16 ± 6.04 (5.76) | 2.07 ± 0.53 (2.11) | 5.30 ± 0.87 (5.43) | 2.58 ± 1.03 (2.10) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.891 | 5.2 | 5.98 | 3.53 |
| p | normal | 0.788 | 8.5 | 4.77 | 2.27 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.741 | 0.08 | 2.67 ± 0.85 (2.45) | 4.39 | 1.88 |
| p | medium | 15 | 0.878 | 0.61 | 1.27 ± 0.33 (1.33) | 4.13 | 2.15 |
| p | strong | 125 | 0.882 | 0.80 | - | 6.01 | 3.49 |

## Notes

- p: score 0.840, 199/200 kicked, 0 fell; worst sector back (0.785).
