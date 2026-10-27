# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-13-12_q6_q4_lowcap03/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.845** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.84 ± 0.57 (1.76) |
| Direction error [°] | 5.41 ± 3.67 (4.88) |
| Avg ball speed [m/s] | 2.51 ± 0.43 (2.53) |
| Peak ball speed [m/s] | 5.27 ± 1.01 (5.61) |
| Distance [m] | 2.39 ± 0.73 (2.48) |
| Path length [m] | 2.40 ± 0.73 (2.49) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.862 | 50/50 | 0 | 50 | 1.30 ± 0.25 (1.30) | 4.06 ± 2.52 (3.78) | 2.43 ± 0.45 (2.32) | 5.08 ± 1.06 (5.28) | 2.24 ± 0.74 (2.09) |
| left | p | 0.876 | 50/50 | 0 | 47 | 1.76 ± 0.37 (1.79) | 5.73 ± 4.15 (4.20) | 2.54 ± 0.38 (2.56) | 5.41 ± 0.91 (5.76) | 2.45 ± 0.65 (2.62) |
| back | p | 0.790 | 49/50 | 0 | 48 | 2.59 ± 0.36 (2.48) | 6.60 ± 3.59 (6.21) | 2.62 ± 0.42 (2.70) | 5.45 ± 1.03 (5.82) | 2.57 ± 0.77 (2.81) |
| right | p | 0.851 | 50/50 | 0 | 50 | 1.74 ± 0.34 (1.73) | 5.29 ± 3.74 (4.73) | 2.47 ± 0.44 (2.40) | 5.16 ± 1.00 (5.38) | 2.29 ± 0.70 (2.29) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.839 | 99/100 | 0 | 97 | 1.86 ± 0.57 (1.78) | 5.66 ± 3.74 (5.21) | 2.54 ± 0.41 (2.55) | 5.31 ± 0.99 (5.66) | 2.41 ± 0.71 (2.52) |
| right | p | 0.850 | 100/100 | 0 | 98 | 1.83 ± 0.58 (1.73) | 5.18 ± 3.58 (4.40) | 2.49 ± 0.44 (2.53) | 5.24 ± 1.03 (5.58) | 2.37 ± 0.75 (2.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.863 | 25/25 | 0 | 25 | 1.31 ± 0.24 (1.32) | 4.68 ± 2.79 (4.50) | 2.48 ± 0.44 (2.53) | 5.18 ± 1.07 (5.42) | 2.32 ± 0.74 (2.37) |
| forward/right | p | 0.861 | 25/25 | 0 | 25 | 1.28 ± 0.26 (1.30) | 3.44 ± 2.05 (2.69) | 2.37 ± 0.45 (2.31) | 4.98 ± 1.05 (5.09) | 2.16 ± 0.74 (1.93) |
| left/left | p | 0.877 | 25/25 | 0 | 24 | 1.67 ± 0.37 (1.78) | 5.29 ± 3.91 (3.84) | 2.56 ± 0.39 (2.55) | 5.38 ± 0.94 (5.75) | 2.44 ± 0.67 (2.52) |
| left/right | p | 0.874 | 25/25 | 0 | 23 | 1.85 ± 0.34 (1.90) | 6.18 ± 4.33 (4.22) | 2.52 ± 0.37 (2.58) | 5.45 ± 0.88 (5.77) | 2.47 ± 0.63 (2.68) |
| back/left | p | 0.768 | 24/25 | 0 | 23 | 2.62 ± 0.33 (2.57) | 6.85 ± 3.95 (6.10) | 2.63 ± 0.38 (2.70) | 5.46 ± 0.99 (5.89) | 2.58 ± 0.76 (2.81) |
| back/right | p | 0.812 | 25/25 | 0 | 25 | 2.57 ± 0.39 (2.46) | 6.36 ± 3.19 (6.21) | 2.61 ± 0.46 (2.70) | 5.43 ± 1.07 (5.82) | 2.56 ± 0.79 (2.89) |
| right/left | p | 0.849 | 25/25 | 0 | 25 | 1.84 ± 0.32 (1.78) | 5.86 ± 3.85 (6.36) | 2.48 ± 0.43 (2.45) | 5.22 ± 0.94 (5.44) | 2.31 ± 0.64 (2.48) |
| right/right | p | 0.853 | 25/25 | 0 | 25 | 1.64 ± 0.33 (1.60) | 4.73 ± 3.54 (3.91) | 2.46 ± 0.45 (2.39) | 5.10 ± 1.05 (5.32) | 2.27 ± 0.75 (2.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.882 | 5.5 | 6.00 | 2.87 |
| p | normal | 0.807 | 5.3 | 4.56 | 1.92 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.755 | 0.08 | 2.56 ± 0.79 (2.23) | 4.05 | 1.57 |
| p | medium | 16 | 0.876 | 0.76 | 1.24 ± 0.14 (1.21) | 4.04 | 1.57 |
| p | strong | 126 | 0.882 | 0.80 | - | 6.00 | 2.88 |

## Notes

- p: score 0.845, 199/200 kicked, 0 fell; worst sector back (0.790).
