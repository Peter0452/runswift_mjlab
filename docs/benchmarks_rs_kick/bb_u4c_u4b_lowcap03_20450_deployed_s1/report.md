# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_05-06-31_u4c_u4b_lowcap03/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.854** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 196 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.82 ± 0.58 (1.68) |
| Direction error [°] | 5.85 ± 12.00 (4.09) |
| Avg ball speed [m/s] | 2.25 ± 0.41 (2.24) |
| Peak ball speed [m/s] | 4.93 ± 1.09 (5.31) |
| Distance [m] | 2.05 ± 0.69 (2.12) |
| Path length [m] | 2.06 ± 0.70 (2.12) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.880 | 50/50 | 0 | 50 | 1.26 ± 0.25 (1.28) | 4.22 ± 3.10 (3.40) | 2.20 ± 0.40 (2.26) | 4.86 ± 1.10 (5.35) | 1.98 ± 0.67 (2.06) |
| left | p | 0.873 | 50/50 | 0 | 50 | 1.75 ± 0.37 (1.69) | 4.88 ± 3.31 (3.74) | 2.25 ± 0.37 (2.19) | 4.93 ± 1.05 (5.29) | 2.04 ± 0.67 (2.09) |
| back | p | 0.808 | 50/50 | 0 | 48 | 2.55 ± 0.40 (2.53) | 9.38 ± 22.81 (5.85) | 2.38 ± 0.44 (2.44) | 5.17 ± 1.10 (5.66) | 2.24 ± 0.72 (2.38) |
| right | p | 0.857 | 50/50 | 0 | 48 | 1.72 ± 0.37 (1.61) | 4.92 ± 4.25 (3.47) | 2.18 ± 0.40 (2.19) | 4.77 ± 1.07 (5.08) | 1.93 ± 0.68 (2.01) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.846 | 100/100 | 0 | 98 | 1.81 ± 0.57 (1.63) | 6.89 ± 16.50 (4.50) | 2.24 ± 0.41 (2.22) | 4.93 ± 1.09 (5.31) | 2.04 ± 0.68 (2.10) |
| right | p | 0.862 | 100/100 | 0 | 98 | 1.83 ± 0.59 (1.72) | 4.81 ± 3.68 (3.70) | 2.26 ± 0.41 (2.26) | 4.94 ± 1.09 (5.33) | 2.06 ± 0.70 (2.13) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.869 | 25/25 | 0 | 25 | 1.24 ± 0.24 (1.28) | 4.96 ± 3.43 (3.80) | 2.16 ± 0.40 (2.14) | 4.76 ± 1.13 (5.31) | 1.93 ± 0.70 (2.03) |
| forward/right | p | 0.890 | 25/25 | 0 | 25 | 1.27 ± 0.25 (1.24) | 3.48 ± 2.52 (2.96) | 2.24 ± 0.38 (2.26) | 4.97 ± 1.06 (5.44) | 2.03 ± 0.65 (2.20) |
| left/left | p | 0.870 | 25/25 | 0 | 25 | 1.66 ± 0.33 (1.60) | 5.41 ± 3.45 (5.60) | 2.28 ± 0.34 (2.21) | 5.04 ± 0.98 (5.28) | 2.09 ± 0.60 (2.10) |
| left/right | p | 0.875 | 25/25 | 0 | 25 | 1.83 ± 0.39 (1.82) | 4.35 ± 3.09 (3.00) | 2.21 ± 0.39 (2.14) | 4.82 ± 1.11 (5.34) | 1.99 ± 0.72 (1.83) |
| back/left | p | 0.794 | 25/25 | 0 | 24 | 2.51 ± 0.42 (2.48) | 13.05 ± 31.63 (7.45) | 2.35 ± 0.46 (2.37) | 5.12 ± 1.14 (5.71) | 2.20 ± 0.70 (2.37) |
| back/right | p | 0.822 | 25/25 | 0 | 24 | 2.60 ± 0.38 (2.56) | 5.71 ± 3.59 (4.93) | 2.41 ± 0.42 (2.47) | 5.21 ± 1.07 (5.61) | 2.28 ± 0.73 (2.40) |
| right/left | p | 0.852 | 25/25 | 0 | 24 | 1.82 ± 0.39 (1.78) | 4.12 ± 3.60 (3.26) | 2.17 ± 0.40 (2.19) | 4.80 ± 1.08 (5.28) | 1.94 ± 0.70 (2.04) |
| right/right | p | 0.861 | 25/25 | 0 | 24 | 1.63 ± 0.32 (1.58) | 5.72 ± 4.67 (3.77) | 2.18 ± 0.39 (2.17) | 4.74 ± 1.07 (5.07) | 1.93 ± 0.67 (1.99) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.880 | 6.9 | 5.64 | 2.44 |
| p | normal | 0.829 | 4.8 | 4.23 | 1.66 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.766 | 0.15 | 2.32 ± 0.71 (2.19) | 3.62 | 1.27 |
| p | medium | 20 | 0.913 | 0.82 | 1.16 ± 0.15 (1.12) | 3.72 | 1.34 |
| p | strong | 126 | 0.883 | 0.76 | - | 5.69 | 2.49 |

## Notes

- p: score 0.854, 200/200 kicked, 0 fell; worst sector back (0.808).
