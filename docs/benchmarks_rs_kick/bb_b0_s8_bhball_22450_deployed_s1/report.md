# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_22450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.808** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 175 |
| Weak kicks (< 0.3 m) | 21 |
| Time to kick [s] | 1.98 ± 1.44 (1.66) |
| Direction error [°] | 13.57 ± 28.34 (4.60) |
| Avg ball speed [m/s] | 2.32 ± 0.79 (2.48) |
| Peak ball speed [m/s] | 4.88 ± 1.77 (5.65) |
| Distance [m] | 2.33 ± 1.08 (2.69) |
| Path length [m] | 2.34 ± 1.08 (2.70) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.824 | 50/50 | 0 | 46 | 1.68 ± 1.95 (1.30) | 7.33 ± 11.31 (4.14) | 2.23 ± 0.84 (2.44) | 4.74 ± 1.88 (5.11) | 2.21 ± 1.08 (2.22) |
| left | p | 0.827 | 50/50 | 0 | 43 | 1.83 ± 1.26 (1.60) | 12.16 ± 23.36 (4.29) | 2.32 ± 0.69 (2.45) | 4.88 ± 1.58 (5.46) | 2.30 ± 1.01 (2.60) |
| back | p | 0.763 | 50/50 | 0 | 41 | 2.53 ± 1.09 (2.56) | 24.45 ± 44.81 (5.76) | 2.38 ± 0.90 (2.69) | 5.00 ± 1.97 (6.03) | 2.48 ± 1.22 (3.00) |
| right | p | 0.818 | 50/50 | 0 | 45 | 1.86 ± 1.12 (1.77) | 10.35 ± 19.01 (3.68) | 2.34 ± 0.71 (2.46) | 4.91 ± 1.59 (5.13) | 2.33 ± 0.99 (2.33) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.803 | 100/100 | 0 | 86 | 1.99 ± 1.54 (1.62) | 14.95 ± 30.72 (4.56) | 2.30 ± 0.83 (2.49) | 4.85 ± 1.83 (5.61) | 2.31 ± 1.09 (2.70) |
| right | p | 0.813 | 100/100 | 0 | 89 | 1.96 ± 1.33 (1.73) | 12.20 ± 25.67 (4.64) | 2.34 ± 0.75 (2.48) | 4.92 ± 1.70 (5.66) | 2.35 ± 1.07 (2.68) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.829 | 25/25 | 0 | 23 | 1.63 ± 1.89 (1.28) | 6.13 ± 8.81 (2.53) | 2.24 ± 0.83 (2.45) | 4.78 ± 1.87 (5.58) | 2.23 ± 1.04 (2.39) |
| forward/right | p | 0.818 | 25/25 | 0 | 23 | 1.72 ± 2.02 (1.36) | 8.53 ± 13.24 (5.13) | 2.23 ± 0.86 (2.37) | 4.71 ± 1.90 (4.64) | 2.19 ± 1.11 (2.05) |
| left/left | p | 0.839 | 25/25 | 0 | 22 | 1.96 ± 1.69 (1.60) | 7.27 ± 9.15 (2.60) | 2.46 ± 0.65 (2.64) | 5.19 ± 1.46 (5.56) | 2.51 ± 0.93 (2.70) |
| left/right | p | 0.816 | 25/25 | 0 | 21 | 1.70 ± 0.51 (1.82) | 17.04 ± 30.99 (4.56) | 2.17 ± 0.70 (2.30) | 4.57 ± 1.63 (4.36) | 2.08 ± 1.04 (1.74) |
| back/left | p | 0.757 | 25/25 | 0 | 20 | 2.27 ± 0.74 (2.50) | 31.52 ± 50.66 (6.62) | 2.27 ± 0.92 (2.63) | 4.77 ± 2.01 (5.99) | 2.32 ± 1.23 (3.00) |
| back/right | p | 0.768 | 25/25 | 0 | 21 | 2.79 ± 1.30 (2.60) | 17.38 ± 36.74 (4.90) | 2.49 ± 0.86 (2.82) | 5.23 ± 1.90 (6.13) | 2.64 ± 1.18 (3.05) |
| right/left | p | 0.785 | 25/25 | 0 | 21 | 2.10 ± 1.51 (1.96) | 14.86 ± 25.22 (3.82) | 2.23 ± 0.87 (2.33) | 4.66 ± 1.89 (4.57) | 2.18 ± 1.11 (1.96) |
| right/right | p | 0.851 | 25/25 | 0 | 24 | 1.61 ± 0.33 (1.56) | 5.84 ± 6.75 (3.60) | 2.46 ± 0.47 (2.53) | 5.16 ± 1.17 (5.70) | 2.47 ± 0.84 (2.69) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.835 | 15.5 | 5.40 | 2.73 |
| p | normal | 0.781 | 11.6 | 4.37 | 1.93 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.736 | 0.08 | 2.62 ± 1.04 (2.53) | 4.04 | 1.66 |
| p | medium | 20 | 0.847 | 0.65 | 1.22 ± 0.33 (1.32) | 3.93 | 1.61 |
| p | strong | 126 | 0.833 | 0.72 | - | 5.40 | 2.73 |

## Notes

- p: score 0.808, 200/200 kicked, 0 fell; worst sector back (0.763).
