# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w6_w3_60_s8_40.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.856** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.85 ± 0.57 (1.75) |
| Direction error [°] | 5.10 ± 3.43 (4.59) |
| Avg ball speed [m/s] | 2.38 ± 0.37 (2.47) |
| Peak ball speed [m/s] | 5.23 ± 1.04 (5.69) |
| Distance [m] | 2.31 ± 0.70 (2.44) |
| Path length [m] | 2.32 ± 0.71 (2.45) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.880 | 50/50 | 0 | 50 | 1.27 ± 0.25 (1.29) | 4.09 ± 3.23 (3.64) | 2.29 ± 0.37 (2.41) | 5.11 ± 1.05 (5.62) | 2.18 ± 0.66 (2.30) |
| left | p | 0.863 | 50/50 | 0 | 49 | 1.77 ± 0.37 (1.71) | 5.91 ± 3.68 (5.69) | 2.37 ± 0.36 (2.40) | 5.18 ± 1.02 (5.60) | 2.28 ± 0.71 (2.37) |
| back | p | 0.817 | 50/50 | 0 | 50 | 2.57 ± 0.33 (2.51) | 6.41 ± 3.26 (6.56) | 2.53 ± 0.39 (2.61) | 5.51 ± 1.04 (6.01) | 2.55 ± 0.72 (2.84) |
| right | p | 0.865 | 50/50 | 0 | 50 | 1.78 ± 0.35 (1.77) | 3.98 ± 2.79 (3.35) | 2.34 ± 0.32 (2.40) | 5.14 ± 0.98 (5.56) | 2.22 ± 0.66 (2.32) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.850 | 100/100 | 0 | 99 | 1.84 ± 0.57 (1.72) | 5.49 ± 3.80 (4.87) | 2.38 ± 0.39 (2.48) | 5.27 ± 1.04 (5.78) | 2.33 ± 0.72 (2.45) |
| right | p | 0.862 | 100/100 | 0 | 100 | 1.86 ± 0.57 (1.82) | 4.71 ± 2.96 (4.32) | 2.38 ± 0.36 (2.47) | 5.20 ± 1.03 (5.63) | 2.28 ± 0.69 (2.41) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.876 | 25/25 | 0 | 25 | 1.25 ± 0.25 (1.28) | 4.35 ± 3.62 (3.49) | 2.27 ± 0.37 (2.42) | 5.08 ± 1.06 (5.82) | 2.16 ± 0.67 (2.40) |
| forward/right | p | 0.885 | 25/25 | 0 | 25 | 1.30 ± 0.25 (1.30) | 3.84 ± 2.76 (4.01) | 2.31 ± 0.36 (2.40) | 5.14 ± 1.05 (5.50) | 2.20 ± 0.65 (2.25) |
| left/left | p | 0.855 | 25/25 | 0 | 24 | 1.67 ± 0.33 (1.60) | 6.88 ± 4.06 (6.69) | 2.37 ± 0.33 (2.40) | 5.23 ± 0.95 (5.55) | 2.32 ± 0.66 (2.45) |
| left/right | p | 0.870 | 25/25 | 0 | 25 | 1.87 ± 0.37 (1.84) | 4.93 ± 2.95 (5.65) | 2.37 ± 0.38 (2.41) | 5.12 ± 1.08 (5.64) | 2.24 ± 0.75 (2.36) |
| back/left | p | 0.809 | 25/25 | 0 | 25 | 2.57 ± 0.30 (2.52) | 7.02 ± 3.24 (6.91) | 2.56 ± 0.44 (2.70) | 5.57 ± 1.08 (6.11) | 2.62 ± 0.76 (2.95) |
| back/right | p | 0.824 | 25/25 | 0 | 25 | 2.58 ± 0.36 (2.50) | 5.81 ± 3.16 (5.69) | 2.51 ± 0.34 (2.56) | 5.46 ± 1.00 (5.97) | 2.49 ± 0.68 (2.57) |
| right/left | p | 0.859 | 25/25 | 0 | 25 | 1.88 ± 0.36 (1.94) | 3.69 ± 3.00 (3.07) | 2.33 ± 0.34 (2.39) | 5.19 ± 1.00 (5.49) | 2.24 ± 0.69 (2.24) |
| right/right | p | 0.871 | 25/25 | 0 | 25 | 1.69 ± 0.32 (1.64) | 4.27 ± 2.54 (4.12) | 2.35 ± 0.31 (2.47) | 5.08 ± 0.96 (5.59) | 2.20 ± 0.63 (2.43) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.892 | 5.2 | 5.97 | 2.76 |
| p | normal | 0.820 | 5.0 | 4.50 | 1.86 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.761 | 0.10 | 2.53 ± 0.77 (2.39) | 3.93 | 1.47 |
| p | medium | 20 | 0.881 | 0.75 | 1.25 ± 0.12 (1.26) | 4.01 | 1.54 |
| p | strong | 126 | 0.893 | 0.80 | - | 5.98 | 2.79 |

## Notes

- p: score 0.856, 200/200 kicked, 0 fell; worst sector back (0.817).
