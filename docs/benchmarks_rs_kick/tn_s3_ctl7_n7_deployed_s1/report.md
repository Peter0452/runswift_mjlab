# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s3_ctl7_n7.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.807** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 20 |
| Time to kick [s] | 1.86 ± 1.22 (1.62) |
| Direction error [°] | 15.17 ± 32.18 (5.14) |
| Avg ball speed [m/s] | 2.31 ± 0.79 (2.55) |
| Peak ball speed [m/s] | 4.86 ± 1.75 (5.72) |
| Distance [m] | 2.32 ± 1.08 (2.78) |
| Path length [m] | 2.33 ± 1.08 (2.78) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.827 | 50/50 | 0 | 43 | 1.41 ± 1.43 (1.26) | 9.22 ± 16.37 (3.19) | 2.23 ± 0.84 (2.44) | 4.75 ± 1.85 (5.55) | 2.23 ± 1.10 (2.48) |
| left | p | 0.831 | 50/50 | 0 | 44 | 1.85 ± 1.27 (1.66) | 11.85 ± 22.71 (4.89) | 2.32 ± 0.76 (2.52) | 4.88 ± 1.69 (5.70) | 2.32 ± 1.08 (2.73) |
| back | p | 0.763 | 50/50 | 0 | 41 | 2.47 ± 1.22 (2.42) | 29.63 ± 52.77 (8.04) | 2.32 ± 0.87 (2.64) | 4.91 ± 1.91 (5.89) | 2.40 ± 1.16 (2.90) |
| right | p | 0.807 | 49/50 | 0 | 45 | 1.70 ± 0.39 (1.74) | 9.87 ± 16.57 (5.04) | 2.36 ± 0.66 (2.50) | 4.91 ± 1.50 (5.64) | 2.32 ± 0.96 (2.57) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.804 | 99/100 | 0 | 86 | 1.80 ± 1.05 (1.60) | 14.94 ± 30.84 (4.98) | 2.33 ± 0.81 (2.65) | 4.89 ± 1.79 (5.83) | 2.35 ± 1.11 (2.91) |
| right | p | 0.811 | 100/100 | 0 | 87 | 1.91 ± 1.36 (1.66) | 15.39 ± 33.44 (5.20) | 2.29 ± 0.76 (2.50) | 4.83 ± 1.70 (5.70) | 2.29 ± 1.05 (2.66) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.850 | 25/25 | 0 | 23 | 1.21 ± 0.27 (1.26) | 6.12 ± 8.61 (3.06) | 2.28 ± 0.79 (2.40) | 4.85 ± 1.74 (5.42) | 2.28 ± 1.07 (2.47) |
| forward/right | p | 0.804 | 25/25 | 0 | 20 | 1.62 ± 1.98 (1.30) | 12.31 ± 21.04 (3.22) | 2.18 ± 0.88 (2.50) | 4.66 ± 1.95 (5.68) | 2.19 ± 1.13 (2.50) |
| left/left | p | 0.854 | 25/25 | 0 | 23 | 1.99 ± 1.72 (1.60) | 6.08 ± 7.76 (3.03) | 2.51 ± 0.71 (2.80) | 5.27 ± 1.61 (6.15) | 2.60 ± 1.05 (3.15) |
| left/right | p | 0.808 | 25/25 | 0 | 21 | 1.71 ± 0.47 (1.78) | 17.63 ± 30.08 (5.56) | 2.13 ± 0.75 (2.24) | 4.50 ± 1.69 (4.38) | 2.04 ± 1.04 (1.79) |
| back/left | p | 0.743 | 25/25 | 0 | 19 | 2.24 ± 0.74 (2.44) | 33.76 ± 51.40 (8.89) | 2.23 ± 0.92 (2.60) | 4.70 ± 1.98 (5.71) | 2.27 ± 1.22 (2.84) |
| back/right | p | 0.783 | 25/25 | 0 | 22 | 2.70 ± 1.53 (2.36) | 25.49 ± 53.79 (5.91) | 2.40 ± 0.82 (2.68) | 5.12 ± 1.80 (5.97) | 2.53 ± 1.07 (2.94) |
| right/left | p | 0.767 | 24/25 | 0 | 21 | 1.78 ± 0.42 (1.92) | 13.76 ± 22.33 (6.09) | 2.28 ± 0.79 (2.48) | 4.76 ± 1.77 (5.00) | 2.23 ± 1.06 (2.21) |
| right/right | p | 0.847 | 25/25 | 0 | 24 | 1.62 ± 0.34 (1.56) | 6.14 ± 5.56 (4.58) | 2.43 ± 0.51 (2.50) | 5.05 ± 1.18 (5.72) | 2.40 ± 0.84 (2.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.840 | 15.4 | 5.35 | 2.69 |
| p | normal | 0.775 | 14.9 | 4.37 | 1.94 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.726 | 0.10 | 2.52 ± 1.00 (2.31) | 3.88 | 1.56 |
| p | medium | 20 | 0.846 | 0.67 | 1.23 ± 0.31 (1.31) | 3.94 | 1.61 |
| p | strong | 126 | 0.836 | 0.72 | - | 5.42 | 2.75 |

## Notes

- p: score 0.807, 199/200 kicked, 0 fell; worst sector back (0.763).
