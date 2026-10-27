# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.790** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 13 |
| Time to kick [s] | 2.09 ± 1.79 (1.76) |
| Direction error [°] | 17.90 ± 37.48 (5.22) |
| Avg ball speed [m/s] | 2.09 ± 0.62 (2.26) |
| Peak ball speed [m/s] | 4.54 ± 1.46 (5.04) |
| Distance [m] | 1.87 ± 0.80 (1.94) |
| Path length [m] | 1.88 ± 0.81 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 50/50 | 0 | 42 | 1.89 ± 2.17 (1.34) | 8.84 ± 11.47 (5.18) | 2.06 ± 0.57 (2.17) | 4.46 ± 1.37 (4.44) | 1.79 ± 0.73 (1.83) |
| left | p | 0.821 | 49/50 | 0 | 44 | 1.89 ± 1.39 (1.78) | 13.45 ± 28.78 (4.59) | 2.15 ± 0.52 (2.30) | 4.74 ± 1.29 (5.31) | 1.95 ± 0.72 (2.11) |
| back | p | 0.771 | 50/50 | 0 | 42 | 2.50 ± 1.44 (2.40) | 28.87 ± 56.23 (5.62) | 2.12 ± 0.70 (2.35) | 4.58 ± 1.59 (5.21) | 1.95 ± 0.90 (2.08) |
| right | p | 0.782 | 50/50 | 0 | 41 | 2.06 ± 1.95 (1.76) | 20.34 ± 35.48 (5.22) | 2.04 ± 0.65 (2.23) | 4.41 ± 1.54 (4.76) | 1.80 ± 0.83 (1.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.822 | 100/100 | 0 | 89 | 1.83 ± 0.99 (1.71) | 15.53 ± 35.30 (4.59) | 2.15 ± 0.56 (2.32) | 4.69 ± 1.34 (5.19) | 1.95 ± 0.77 (2.15) |
| right | p | 0.758 | 99/100 | 0 | 80 | 2.34 ± 2.30 (1.76) | 20.29 ± 39.42 (5.33) | 2.02 ± 0.66 (2.21) | 4.40 ± 1.56 (4.76) | 1.80 ± 0.83 (1.87) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.828 | 25/25 | 0 | 23 | 1.62 ± 1.64 (1.32) | 6.90 ± 11.16 (3.99) | 2.17 ± 0.43 (2.26) | 4.74 ± 1.10 (5.23) | 1.93 ± 0.61 (1.98) |
| forward/right | p | 0.745 | 25/25 | 0 | 19 | 2.17 ± 2.56 (1.34) | 10.78 ± 11.46 (6.18) | 1.95 ± 0.65 (2.04) | 4.18 ± 1.55 (4.19) | 1.66 ± 0.81 (1.74) |
| left/left | p | 0.870 | 25/25 | 0 | 24 | 1.63 ± 0.39 (1.68) | 7.98 ± 15.49 (4.60) | 2.21 ± 0.44 (2.37) | 4.88 ± 1.07 (5.39) | 2.01 ± 0.65 (2.29) |
| left/right | p | 0.772 | 24/25 | 0 | 20 | 2.15 ± 1.91 (1.93) | 19.15 ± 37.11 (4.52) | 2.08 ± 0.59 (2.27) | 4.60 ± 1.46 (5.27) | 1.88 ± 0.77 (2.03) |
| back/left | p | 0.795 | 25/25 | 0 | 22 | 2.36 ± 0.66 (2.52) | 23.53 ± 51.24 (4.41) | 2.24 ± 0.55 (2.37) | 4.82 ± 1.25 (5.28) | 2.09 ± 0.84 (2.32) |
| back/right | p | 0.747 | 25/25 | 0 | 20 | 2.65 ± 1.91 (2.38) | 34.20 ± 60.34 (5.91) | 2.00 ± 0.81 (2.24) | 4.33 ± 1.84 (4.72) | 1.81 ± 0.93 (1.81) |
| right/left | p | 0.795 | 25/25 | 0 | 20 | 1.73 ± 0.48 (1.82) | 23.69 ± 41.60 (5.22) | 1.99 ± 0.74 (2.27) | 4.32 ± 1.75 (4.73) | 1.76 ± 0.90 (2.03) |
| right/right | p | 0.769 | 25/25 | 0 | 21 | 2.39 ± 2.67 (1.74) | 16.99 ± 27.63 (5.23) | 2.08 ± 0.55 (2.19) | 4.49 ± 1.30 (4.79) | 1.85 ± 0.76 (1.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.822 | 17.4 | 5.11 | 2.18 |
| p | normal | 0.759 | 18.4 | 3.98 | 1.57 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.718 | 0.16 | 2.32 ± 0.98 (2.21) | 3.65 | 1.38 |
| p | medium | 16 | 0.836 | 0.68 | 1.29 ± 0.23 (1.29) | 4.18 | 1.69 |
| p | strong | 126 | 0.818 | 0.67 | - | 5.00 | 2.12 |

## Notes

- p: score 0.790, 199/200 kicked, 0 fell; worst sector back (0.771).
