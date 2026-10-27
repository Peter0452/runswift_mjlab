# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_22450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.847** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.57 ± 0.52 (1.49) |
| Direction error [°] | 6.02 ± 11.73 (4.59) |
| Avg ball speed [m/s] | 1.90 ± 0.32 (2.02) |
| Peak ball speed [m/s] | 4.16 ± 0.80 (4.50) |
| Distance [m] | 1.49 ± 0.44 (1.58) |
| Path length [m] | 1.50 ± 0.44 (1.59) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.854 | 50/50 | 0 | 50 | 1.03 ± 0.22 (1.06) | 4.08 ± 2.72 (3.49) | 1.76 ± 0.34 (1.87) | 3.78 ± 0.78 (3.77) | 1.26 ± 0.44 (1.31) |
| left | p | 0.868 | 50/50 | 0 | 50 | 1.51 ± 0.34 (1.52) | 5.05 ± 3.63 (4.19) | 1.97 ± 0.28 (2.06) | 4.34 ± 0.73 (4.66) | 1.58 ± 0.40 (1.68) |
| back | p | 0.826 | 50/50 | 0 | 49 | 2.23 ± 0.25 (2.18) | 9.41 ± 22.42 (6.63) | 1.98 ± 0.35 (2.12) | 4.35 ± 0.87 (4.73) | 1.63 ± 0.46 (1.78) |
| right | p | 0.840 | 50/50 | 0 | 50 | 1.50 ± 0.34 (1.45) | 5.56 ± 3.33 (5.27) | 1.92 ± 0.25 (2.01) | 4.18 ± 0.66 (4.51) | 1.49 ± 0.36 (1.46) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 99 | 1.57 ± 0.52 (1.51) | 6.95 ± 16.19 (4.73) | 1.91 ± 0.33 (2.05) | 4.16 ± 0.82 (4.55) | 1.50 ± 0.44 (1.61) |
| right | p | 0.849 | 100/100 | 0 | 100 | 1.57 ± 0.52 (1.48) | 5.10 ± 3.40 (4.45) | 1.90 ± 0.31 (1.99) | 4.16 ± 0.78 (4.47) | 1.48 ± 0.43 (1.55) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.853 | 25/25 | 0 | 25 | 1.03 ± 0.22 (1.08) | 4.09 ± 2.46 (3.59) | 1.80 ± 0.32 (1.97) | 3.86 ± 0.71 (3.90) | 1.32 ± 0.42 (1.37) |
| forward/right | p | 0.855 | 25/25 | 0 | 25 | 1.02 ± 0.23 (1.04) | 4.08 ± 2.96 (3.38) | 1.72 ± 0.36 (1.63) | 3.70 ± 0.84 (3.41) | 1.21 ± 0.45 (1.09) |
| left/left | p | 0.860 | 25/25 | 0 | 25 | 1.41 ± 0.34 (1.48) | 5.61 ± 4.12 (4.33) | 1.92 ± 0.29 (2.04) | 4.21 ± 0.77 (4.64) | 1.51 ± 0.41 (1.63) |
| left/right | p | 0.876 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.60) | 4.49 ± 2.97 (4.12) | 2.01 ± 0.26 (2.11) | 4.46 ± 0.66 (4.70) | 1.65 ± 0.38 (1.70) |
| back/left | p | 0.820 | 25/25 | 0 | 24 | 2.23 ± 0.25 (2.18) | 12.64 ± 31.18 (7.28) | 1.96 ± 0.43 (2.14) | 4.30 ± 1.04 (4.80) | 1.62 ± 0.52 (1.85) |
| back/right | p | 0.831 | 25/25 | 0 | 25 | 2.24 ± 0.26 (2.24) | 6.19 ± 3.46 (6.42) | 2.00 ± 0.24 (2.11) | 4.40 ± 0.66 (4.70) | 1.63 ± 0.38 (1.74) |
| right/left | p | 0.844 | 25/25 | 0 | 25 | 1.60 ± 0.32 (1.58) | 5.46 ± 2.89 (5.40) | 1.95 ± 0.23 (2.05) | 4.29 ± 0.62 (4.58) | 1.55 ± 0.35 (1.52) |
| right/right | p | 0.836 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.44) | 5.65 ± 3.71 (5.15) | 1.88 ± 0.27 (1.96) | 4.06 ± 0.68 (4.24) | 1.43 ± 0.37 (1.43) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.865 | 5.3 | 4.62 | 1.73 |
| p | normal | 0.828 | 6.7 | 3.70 | 1.25 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.784 | 0.20 | 2.10 ± 0.74 (1.98) | 3.31 | 1.05 |
| p | medium | 16 | 0.919 | 0.90 | 1.03 ± 0.12 (1.03) | 3.35 | 1.07 |
| p | strong | 126 | 0.867 | 0.62 | - | 4.65 | 1.74 |

## Notes

- p: score 0.847, 200/200 kicked, 0 fell; worst sector back (0.826).
