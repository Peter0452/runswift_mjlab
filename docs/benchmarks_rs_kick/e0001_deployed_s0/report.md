# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_20-01-27_e0001/model_18850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.755** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 160 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.08 ± 1.62 (1.74) |
| Direction error [°] | 19.12 ± 37.01 (5.71) |
| Avg ball speed [m/s] | 2.06 ± 0.69 (2.22) |
| Peak ball speed [m/s] | 4.47 ± 1.57 (4.84) |
| Distance [m] | 1.85 ± 0.89 (1.88) |
| Path length [m] | 1.86 ± 0.89 (1.88) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.767 | 49/50 | 0 | 40 | 1.81 ± 1.90 (1.36) | 11.31 ± 18.21 (5.83) | 1.94 ± 0.73 (2.05) | 4.18 ± 1.64 (4.23) | 1.67 ± 0.90 (1.63) |
| left | p | 0.788 | 49/50 | 0 | 40 | 1.84 ± 1.40 (1.70) | 19.98 ± 34.71 (6.18) | 2.06 ± 0.66 (2.20) | 4.51 ± 1.53 (5.11) | 1.86 ± 0.87 (2.07) |
| back | p | 0.706 | 48/50 | 0 | 41 | 2.95 ± 1.89 (2.69) | 27.03 ± 52.61 (6.07) | 2.17 ± 0.67 (2.34) | 4.70 ± 1.52 (5.38) | 2.02 ± 0.89 (2.13) |
| right | p | 0.760 | 47/50 | 0 | 39 | 1.70 ± 0.51 (1.74) | 18.27 ± 32.68 (4.83) | 2.06 ± 0.67 (2.19) | 4.48 ± 1.52 (4.84) | 1.84 ± 0.86 (1.83) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 100/100 | 0 | 85 | 1.97 ± 1.39 (1.74) | 17.79 ± 36.09 (5.71) | 2.09 ± 0.64 (2.23) | 4.53 ± 1.45 (4.85) | 1.87 ± 0.83 (1.83) |
| right | p | 0.716 | 93/100 | 0 | 75 | 2.19 ± 1.84 (1.74) | 20.54 ± 37.93 (5.71) | 2.02 ± 0.74 (2.20) | 4.40 ± 1.68 (4.68) | 1.83 ± 0.94 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 23 | 1.65 ± 1.52 (1.32) | 6.61 ± 9.34 (4.19) | 2.07 ± 0.61 (2.13) | 4.49 ± 1.39 (4.33) | 1.81 ± 0.75 (1.66) |
| forward/right | p | 0.712 | 24/25 | 0 | 17 | 1.98 ± 2.22 (1.39) | 16.19 ± 23.22 (8.23) | 1.80 ± 0.82 (1.80) | 3.86 ± 1.81 (3.91) | 1.53 ± 1.01 (1.41) |
| left/left | p | 0.829 | 25/25 | 0 | 21 | 1.57 ± 0.44 (1.62) | 13.72 ± 22.05 (6.76) | 2.16 ± 0.60 (2.24) | 4.68 ± 1.36 (4.91) | 1.97 ± 0.81 (2.13) |
| left/right | p | 0.748 | 24/25 | 0 | 19 | 2.13 ± 1.92 (1.93) | 26.49 ± 43.25 (4.48) | 1.95 ± 0.70 (2.19) | 4.33 ± 1.68 (5.18) | 1.74 ± 0.90 (1.99) |
| back/left | p | 0.731 | 25/25 | 0 | 21 | 2.89 ± 1.93 (2.62) | 28.68 ± 53.33 (6.42) | 2.15 ± 0.59 (2.31) | 4.70 ± 1.36 (5.33) | 1.98 ± 0.85 (2.06) |
| back/right | p | 0.680 | 23/25 | 0 | 20 | 3.02 ± 1.85 (2.72) | 25.25 ± 51.75 (5.71) | 2.18 ± 0.74 (2.39) | 4.71 ± 1.68 (5.43) | 2.07 ± 0.93 (2.15) |
| right/left | p | 0.796 | 25/25 | 0 | 20 | 1.78 ± 0.55 (1.78) | 22.16 ± 38.91 (4.00) | 1.96 ± 0.72 (2.04) | 4.26 ± 1.64 (4.68) | 1.71 ± 0.88 (1.72) |
| right/right | p | 0.723 | 22/25 | 0 | 19 | 1.61 ± 0.45 (1.62) | 13.86 ± 22.90 (5.16) | 2.17 ± 0.58 (2.25) | 4.73 ± 1.32 (5.20) | 1.99 ± 0.81 (2.08) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.778 | 17.8 | 4.99 | 2.18 |
| p | normal | 0.732 | 20.4 | 3.95 | 1.52 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.696 | 0.20 | 2.33 ± 0.93 (2.21) | 3.69 | 1.35 |
| p | medium | 16 | 0.816 | 0.68 | 1.23 ± 0.27 (1.28) | 4.00 | 1.57 |
| p | strong | 126 | 0.775 | 0.65 | - | 4.89 | 2.11 |

## Notes

- p: score 0.755, 193/200 kicked, 0 fell; worst sector back (0.706).
