# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-27-29_u4_overrun1_linear1600/model_19850.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.775** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.10 ± 1.83 (1.74) |
| Direction error [°] | 19.18 ± 37.80 (5.90) |
| Avg ball speed [m/s] | 2.02 ± 0.66 (2.18) |
| Peak ball speed [m/s] | 4.44 ± 1.57 (4.98) |
| Distance [m] | 1.74 ± 0.83 (1.74) |
| Path length [m] | 1.74 ± 0.83 (1.76) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.788 | 50/50 | 0 | 45 | 2.10 ± 2.69 (1.37) | 8.64 ± 10.03 (6.24) | 2.06 ± 0.57 (2.12) | 4.47 ± 1.39 (4.39) | 1.71 ± 0.74 (1.71) |
| left | p | 0.797 | 49/50 | 0 | 41 | 1.89 ± 1.51 (1.78) | 18.97 ± 33.67 (5.90) | 2.06 ± 0.60 (2.25) | 4.56 ± 1.46 (5.14) | 1.79 ± 0.78 (1.94) |
| back | p | 0.738 | 48/50 | 0 | 40 | 2.59 ± 1.46 (2.46) | 28.55 ± 54.58 (5.69) | 2.05 ± 0.75 (2.29) | 4.50 ± 1.75 (5.29) | 1.83 ± 0.92 (1.97) |
| right | p | 0.778 | 49/50 | 0 | 40 | 1.81 ± 1.10 (1.74) | 20.95 ± 36.86 (5.10) | 1.92 ± 0.68 (2.14) | 4.22 ± 1.63 (4.56) | 1.61 ± 0.83 (1.69) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.798 | 99/100 | 0 | 87 | 1.88 ± 1.09 (1.72) | 18.51 ± 38.38 (6.00) | 2.10 ± 0.59 (2.26) | 4.61 ± 1.42 (5.09) | 1.83 ± 0.78 (1.94) |
| right | p | 0.752 | 97/100 | 0 | 79 | 2.32 ± 2.33 (1.76) | 19.86 ± 37.19 (5.58) | 1.94 ± 0.71 (2.14) | 4.26 ± 1.68 (4.47) | 1.64 ± 0.86 (1.71) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.819 | 25/25 | 0 | 24 | 1.68 ± 1.82 (1.34) | 7.91 ± 9.68 (6.33) | 2.16 ± 0.49 (2.21) | 4.72 ± 1.25 (5.05) | 1.85 ± 0.65 (1.93) |
| forward/right | p | 0.757 | 25/25 | 0 | 21 | 2.51 ± 3.29 (1.38) | 9.38 ± 10.32 (6.07) | 1.96 ± 0.62 (2.08) | 4.21 ± 1.47 (4.03) | 1.57 ± 0.80 (1.59) |
| left/left | p | 0.842 | 25/25 | 0 | 22 | 1.62 ± 0.41 (1.72) | 12.84 ± 22.54 (5.46) | 2.18 ± 0.50 (2.29) | 4.77 ± 1.21 (5.22) | 1.94 ± 0.69 (2.01) |
| left/right | p | 0.752 | 24/25 | 0 | 19 | 2.18 ± 2.08 (1.91) | 25.37 ± 41.30 (6.29) | 1.94 ± 0.67 (2.19) | 4.35 ± 1.66 (5.07) | 1.64 ± 0.84 (1.80) |
| back/left | p | 0.738 | 24/25 | 0 | 20 | 2.45 ± 0.77 (2.48) | 30.59 ± 56.93 (6.00) | 2.13 ± 0.66 (2.31) | 4.67 ± 1.56 (5.38) | 1.91 ± 0.89 (2.08) |
| back/right | p | 0.738 | 24/25 | 0 | 20 | 2.73 ± 1.91 (2.39) | 26.51 ± 52.04 (4.43) | 1.98 ± 0.82 (2.20) | 4.33 ± 1.90 (5.01) | 1.76 ± 0.95 (1.76) |
| right/left | p | 0.794 | 25/25 | 0 | 21 | 1.77 ± 0.46 (1.78) | 23.17 ± 42.59 (5.97) | 1.95 ± 0.67 (2.12) | 4.27 ± 1.59 (4.56) | 1.64 ± 0.81 (1.69) |
| right/right | p | 0.762 | 24/25 | 0 | 19 | 1.86 ± 1.50 (1.66) | 18.63 ± 29.58 (4.29) | 1.88 ± 0.70 (2.14) | 4.17 ± 1.67 (4.66) | 1.57 ± 0.84 (1.69) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.799 | 16.4 | 5.15 | 2.11 |
| p | normal | 0.752 | 21.9 | 3.76 | 1.38 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.21 | 2.18 ± 0.98 (2.06) | 3.43 | 1.20 |
| p | medium | 16 | 0.842 | 0.71 | 1.24 ± 0.23 (1.25) | 4.02 | 1.53 |
| p | strong | 126 | 0.796 | 0.66 | - | 4.97 | 2.02 |

## Notes

- p: score 0.775, 196/200 kicked, 0 fell; worst sector back (0.738).
