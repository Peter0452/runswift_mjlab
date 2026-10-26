# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_20-01-27_e0001/model_18949.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.757** |
| Kicked / fell | 191 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.84 ± 0.68 (1.76) |
| Direction error [°] | 18.09 ± 35.36 (6.35) |
| Avg ball speed [m/s] | 2.09 ± 0.64 (2.22) |
| Peak ball speed [m/s] | 4.50 ± 1.47 (4.93) |
| Distance [m] | 1.87 ± 0.83 (1.91) |
| Path length [m] | 1.88 ± 0.83 (1.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.783 | 48/50 | 0 | 43 | 1.41 ± 0.37 (1.42) | 9.13 ± 12.51 (4.92) | 2.02 ± 0.68 (2.15) | 4.29 ± 1.59 (4.26) | 1.73 ± 0.84 (1.74) |
| left | p | 0.780 | 48/50 | 0 | 39 | 1.67 ± 0.52 (1.77) | 20.20 ± 36.08 (5.35) | 2.06 ± 0.66 (2.25) | 4.47 ± 1.52 (4.99) | 1.85 ± 0.85 (2.00) |
| back | p | 0.714 | 48/50 | 0 | 41 | 2.54 ± 0.68 (2.66) | 25.41 ± 48.89 (7.42) | 2.20 ± 0.59 (2.32) | 4.74 ± 1.35 (5.28) | 2.05 ± 0.81 (2.31) |
| right | p | 0.753 | 47/50 | 0 | 40 | 1.72 ± 0.50 (1.76) | 17.61 ± 31.76 (5.87) | 2.08 ± 0.60 (2.24) | 4.48 ± 1.38 (4.91) | 1.84 ± 0.77 (1.92) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.791 | 99/100 | 0 | 86 | 1.82 ± 0.68 (1.78) | 17.10 ± 34.77 (5.54) | 2.12 ± 0.60 (2.24) | 4.57 ± 1.39 (4.93) | 1.91 ± 0.78 (1.91) |
| right | p | 0.724 | 92/100 | 0 | 77 | 1.85 ± 0.68 (1.74) | 19.16 ± 35.95 (6.84) | 2.05 ± 0.67 (2.19) | 4.41 ± 1.55 (4.85) | 1.82 ± 0.87 (1.89) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.837 | 25/25 | 0 | 24 | 1.39 ± 0.35 (1.34) | 6.87 ± 9.76 (4.07) | 2.11 ± 0.58 (2.17) | 4.53 ± 1.39 (4.27) | 1.84 ± 0.73 (1.81) |
| forward/right | p | 0.728 | 23/25 | 0 | 19 | 1.43 ± 0.39 (1.56) | 11.59 ± 14.54 (6.99) | 1.92 ± 0.75 (2.15) | 4.03 ± 1.74 (4.20) | 1.62 ± 0.93 (1.68) |
| left/left | p | 0.826 | 25/25 | 0 | 21 | 1.58 ± 0.42 (1.70) | 15.11 ± 24.52 (5.48) | 2.12 ± 0.63 (2.26) | 4.59 ± 1.41 (5.07) | 1.94 ± 0.77 (2.16) |
| left/right | p | 0.734 | 23/25 | 0 | 18 | 1.77 ± 0.59 (1.94) | 25.73 ± 44.78 (4.75) | 1.99 ± 0.69 (2.16) | 4.34 ± 1.61 (4.97) | 1.75 ± 0.92 (1.93) |
| back/left | p | 0.712 | 24/25 | 0 | 20 | 2.51 ± 0.74 (2.68) | 26.17 ± 50.32 (7.93) | 2.23 ± 0.52 (2.31) | 4.84 ± 1.19 (5.28) | 2.09 ± 0.78 (2.32) |
| back/right | p | 0.715 | 24/25 | 0 | 21 | 2.56 ± 0.62 (2.64) | 24.64 ± 47.41 (7.09) | 2.17 ± 0.66 (2.34) | 4.65 ± 1.49 (5.23) | 2.00 ± 0.84 (2.14) |
| right/left | p | 0.789 | 25/25 | 0 | 21 | 1.82 ± 0.53 (1.80) | 20.60 ± 38.23 (5.18) | 2.02 ± 0.64 (2.22) | 4.34 ± 1.49 (4.57) | 1.76 ± 0.81 (1.87) |
| right/right | p | 0.717 | 22/25 | 0 | 19 | 1.61 ± 0.44 (1.68) | 14.22 ± 21.74 (7.72) | 2.14 ± 0.53 (2.25) | 4.64 ± 1.23 (5.12) | 1.93 ± 0.72 (2.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.788 | 17.0 | 5.02 | 2.17 |
| p | normal | 0.727 | 19.2 | 3.98 | 1.56 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.699 | 0.17 | 2.36 ± 0.95 (2.17) | 3.72 | 1.40 |
| p | medium | 16 | 0.779 | 0.68 | 1.27 ± 0.22 (1.27) | 4.10 | 1.64 |
| p | strong | 126 | 0.781 | 0.65 | - | 4.91 | 2.11 |

## Notes

- p: score 0.757, 191/200 kicked, 0 fell; worst sector back (0.714).
