# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/w6_w3_60_s8_40.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.852** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.86 ± 0.56 (1.77) |
| Direction error [°] | 5.19 ± 3.76 (4.31) |
| Avg ball speed [m/s] | 2.34 ± 0.37 (2.44) |
| Peak ball speed [m/s] | 5.10 ± 1.02 (5.57) |
| Distance [m] | 2.20 ± 0.66 (2.39) |
| Path length [m] | 2.21 ± 0.66 (2.40) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.860 | 50/50 | 0 | 50 | 1.29 ± 0.25 (1.30) | 4.53 ± 3.21 (3.33) | 2.21 ± 0.41 (2.27) | 4.85 ± 1.12 (5.33) | 2.00 ± 0.70 (1.91) |
| left | p | 0.873 | 50/50 | 0 | 47 | 1.78 ± 0.36 (1.80) | 5.98 ± 4.62 (4.59) | 2.40 ± 0.34 (2.50) | 5.27 ± 0.94 (5.70) | 2.30 ± 0.61 (2.45) |
| back | p | 0.818 | 50/50 | 0 | 50 | 2.56 ± 0.32 (2.50) | 5.73 ± 3.35 (5.53) | 2.42 ± 0.34 (2.50) | 5.25 ± 0.95 (5.64) | 2.35 ± 0.66 (2.49) |
| right | p | 0.859 | 50/50 | 0 | 50 | 1.80 ± 0.34 (1.75) | 4.53 ± 3.46 (3.60) | 2.32 ± 0.36 (2.40) | 5.01 ± 0.98 (5.50) | 2.14 ± 0.61 (2.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 99 | 1.87 ± 0.57 (1.78) | 5.28 ± 3.82 (4.33) | 2.35 ± 0.36 (2.43) | 5.11 ± 1.01 (5.56) | 2.21 ± 0.67 (2.42) |
| right | p | 0.852 | 100/100 | 0 | 98 | 1.85 ± 0.54 (1.76) | 5.10 ± 3.71 (4.23) | 2.33 ± 0.39 (2.44) | 5.09 ± 1.02 (5.62) | 2.18 ± 0.65 (2.30) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.861 | 25/25 | 0 | 25 | 1.30 ± 0.26 (1.30) | 4.88 ± 3.11 (4.02) | 2.24 ± 0.40 (2.32) | 4.88 ± 1.10 (5.37) | 2.04 ± 0.72 (2.07) |
| forward/right | p | 0.858 | 25/25 | 0 | 25 | 1.28 ± 0.25 (1.30) | 4.17 ± 3.27 (2.77) | 2.18 ± 0.42 (2.21) | 4.81 ± 1.13 (5.29) | 1.96 ± 0.69 (1.87) |
| left/left | p | 0.872 | 25/25 | 0 | 24 | 1.67 ± 0.36 (1.74) | 5.69 ± 4.80 (3.34) | 2.36 ± 0.29 (2.42) | 5.16 ± 0.91 (5.59) | 2.24 ± 0.56 (2.42) |
| left/right | p | 0.873 | 25/25 | 0 | 23 | 1.90 ± 0.32 (1.96) | 6.27 ± 4.41 (4.61) | 2.45 ± 0.37 (2.54) | 5.38 ± 0.96 (5.72) | 2.37 ± 0.64 (2.51) |
| back/left | p | 0.817 | 25/25 | 0 | 25 | 2.59 ± 0.33 (2.48) | 5.74 ± 3.23 (6.39) | 2.47 ± 0.33 (2.51) | 5.32 ± 0.96 (5.56) | 2.42 ± 0.70 (2.47) |
| back/right | p | 0.818 | 25/25 | 0 | 25 | 2.53 ± 0.32 (2.52) | 5.72 ± 3.46 (5.19) | 2.38 ± 0.34 (2.46) | 5.19 ± 0.94 (5.65) | 2.28 ± 0.61 (2.50) |
| right/left | p | 0.861 | 25/25 | 0 | 25 | 1.92 ± 0.32 (1.82) | 4.82 ± 3.78 (3.64) | 2.33 ± 0.36 (2.53) | 5.06 ± 1.01 (5.63) | 2.14 ± 0.62 (2.38) |
| right/right | p | 0.857 | 25/25 | 0 | 25 | 1.68 ± 0.33 (1.72) | 4.25 ± 3.09 (3.56) | 2.32 ± 0.36 (2.37) | 4.96 ± 0.96 (5.48) | 2.13 ± 0.61 (2.12) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.890 | 5.2 | 5.83 | 2.63 |
| p | normal | 0.814 | 5.2 | 4.36 | 1.76 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.761 | 0.11 | 2.40 ± 0.73 (2.19) | 3.81 | 1.41 |
| p | medium | 16 | 0.893 | 0.80 | 1.20 ± 0.13 (1.20) | 3.89 | 1.50 |
| p | strong | 126 | 0.889 | 0.78 | - | 5.84 | 2.65 |

## Notes

- p: score 0.852, 200/200 kicked, 0 fell; worst sector back (0.818).
