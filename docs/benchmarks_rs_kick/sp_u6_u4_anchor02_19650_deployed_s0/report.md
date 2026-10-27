# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_10-50-14_u6_u4_anchor02/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.793** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 8 |
| Time to kick [s] | 2.09 ± 1.81 (1.74) |
| Direction error [°] | 18.52 ± 38.05 (4.58) |
| Avg ball speed [m/s] | 1.94 ± 0.61 (2.05) |
| Peak ball speed [m/s] | 4.86 ± 1.60 (5.26) |
| Distance [m] | 2.17 ± 0.95 (2.20) |
| Path length [m] | 2.18 ± 0.96 (2.21) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 42 | 1.65 ± 1.72 (1.34) | 8.43 ± 11.72 (3.68) | 1.86 ± 0.59 (1.91) | 4.64 ± 1.56 (4.56) | 2.00 ± 0.92 (1.97) |
| left | p | 0.822 | 50/50 | 0 | 43 | 2.10 ± 2.05 (1.75) | 16.79 ± 32.40 (4.41) | 1.99 ± 0.58 (2.18) | 5.04 ± 1.55 (5.77) | 2.29 ± 0.91 (2.53) |
| back | p | 0.752 | 49/50 | 0 | 40 | 2.56 ± 1.28 (2.48) | 29.48 ± 55.07 (5.11) | 2.00 ± 0.69 (2.22) | 4.98 ± 1.72 (5.68) | 2.32 ± 1.06 (2.62) |
| right | p | 0.794 | 50/50 | 0 | 42 | 2.07 ± 1.97 (1.74) | 19.60 ± 37.13 (4.76) | 1.91 ± 0.58 (1.99) | 4.78 ± 1.52 (5.04) | 2.07 ± 0.87 (2.11) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.811 | 100/100 | 0 | 83 | 1.81 ± 1.04 (1.68) | 20.90 ± 42.62 (4.43) | 1.95 ± 0.64 (2.06) | 4.90 ± 1.67 (5.41) | 2.20 ± 1.00 (2.25) |
| right | p | 0.775 | 99/100 | 0 | 84 | 2.38 ± 2.31 (1.78) | 16.12 ± 32.61 (5.02) | 1.94 ± 0.59 (2.04) | 4.83 ± 1.52 (5.12) | 2.14 ± 0.90 (2.20) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.843 | 25/25 | 0 | 22 | 1.31 ± 0.31 (1.30) | 7.15 ± 12.64 (2.42) | 1.96 ± 0.58 (2.00) | 4.92 ± 1.56 (4.62) | 2.18 ± 0.95 (2.00) |
| forward/right | p | 0.766 | 25/25 | 0 | 20 | 1.99 ± 2.36 (1.34) | 9.72 ± 10.56 (5.78) | 1.76 ± 0.59 (1.86) | 4.37 ± 1.51 (4.47) | 1.83 ± 0.86 (1.91) |
| left/left | p | 0.848 | 25/25 | 0 | 22 | 1.54 ± 0.41 (1.62) | 13.84 ± 25.73 (5.60) | 2.00 ± 0.60 (2.18) | 5.07 ± 1.63 (5.75) | 2.33 ± 0.93 (2.52) |
| left/right | p | 0.797 | 25/25 | 0 | 21 | 2.65 ± 2.75 (2.00) | 19.74 ± 37.69 (3.87) | 1.99 ± 0.55 (2.22) | 5.01 ± 1.48 (5.87) | 2.26 ± 0.89 (2.54) |
| back/left | p | 0.754 | 25/25 | 0 | 19 | 2.63 ± 1.68 (2.40) | 36.01 ± 61.22 (5.11) | 1.97 ± 0.68 (2.15) | 4.93 ± 1.73 (5.65) | 2.26 ± 1.09 (2.51) |
| back/right | p | 0.749 | 24/25 | 0 | 21 | 2.48 ± 0.62 (2.57) | 22.67 ± 46.86 (5.14) | 2.04 ± 0.69 (2.32) | 5.03 ± 1.72 (5.84) | 2.38 ± 1.03 (2.84) |
| right/left | p | 0.800 | 25/25 | 0 | 20 | 1.75 ± 0.49 (1.80) | 26.59 ± 46.87 (4.65) | 1.86 ± 0.68 (1.96) | 4.67 ± 1.74 (4.75) | 2.03 ± 1.00 (2.02) |
| right/right | p | 0.789 | 25/25 | 0 | 22 | 2.39 ± 2.70 (1.72) | 12.60 ± 21.53 (5.08) | 1.97 ± 0.46 (2.04) | 4.90 ± 1.25 (5.12) | 2.11 ± 0.71 (2.15) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 17.6 | 5.46 | 2.53 |
| p | normal | 0.764 | 19.4 | 4.27 | 1.82 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.722 | 0.13 | 2.46 ± 1.09 (2.34) | 3.84 | 1.56 |
| p | medium | 16 | 0.828 | 0.63 | 1.35 ± 0.21 (1.38) | 4.40 | 1.90 |
| p | strong | 126 | 0.822 | 0.72 | - | 5.39 | 2.49 |

## Notes

- p: score 0.793, 199/200 kicked, 0 fell; worst sector back (0.752).
