# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_20950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.815** |
| Kicked / fell | 199 / 0 |
| Kicks within 15° | 179 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.97 ± 1.35 (1.76) |
| Direction error [°] | 12.16 ± 26.52 (4.92) |
| Avg ball speed [m/s] | 2.19 ± 0.62 (2.25) |
| Peak ball speed [m/s] | 5.15 ± 1.53 (5.76) |
| Distance [m] | 2.39 ± 0.95 (2.55) |
| Path length [m] | 2.40 ± 0.95 (2.56) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.829 | 50/50 | 0 | 46 | 1.68 ± 1.94 (1.33) | 8.06 ± 11.71 (4.71) | 2.17 ± 0.61 (2.24) | 5.12 ± 1.49 (5.76) | 2.35 ± 0.90 (2.53) |
| left | p | 0.844 | 50/50 | 0 | 45 | 1.72 ± 0.45 (1.68) | 10.49 ± 21.31 (3.80) | 2.19 ± 0.60 (2.29) | 5.14 ± 1.49 (5.64) | 2.37 ± 0.93 (2.48) |
| back | p | 0.775 | 50/50 | 0 | 43 | 2.75 ± 1.52 (2.57) | 20.47 ± 43.06 (5.84) | 2.22 ± 0.74 (2.38) | 5.25 ± 1.79 (5.94) | 2.51 ± 1.10 (2.80) |
| right | p | 0.810 | 49/50 | 0 | 45 | 1.71 ± 0.37 (1.76) | 9.56 ± 16.23 (4.95) | 2.20 ± 0.52 (2.17) | 5.11 ± 1.30 (5.37) | 2.34 ± 0.84 (2.21) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.816 | 99/100 | 0 | 87 | 1.81 ± 0.66 (1.64) | 11.99 ± 25.50 (4.01) | 2.17 ± 0.68 (2.29) | 5.12 ± 1.64 (5.76) | 2.38 ± 0.99 (2.65) |
| right | p | 0.813 | 100/100 | 0 | 92 | 2.12 ± 1.77 (1.78) | 12.32 ± 27.49 (5.24) | 2.22 ± 0.57 (2.25) | 5.19 ± 1.41 (5.72) | 2.40 ± 0.91 (2.45) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.847 | 25/25 | 0 | 23 | 1.29 ± 0.32 (1.30) | 7.47 ± 11.05 (2.83) | 2.15 ± 0.64 (2.17) | 5.05 ± 1.56 (5.59) | 2.31 ± 0.92 (2.56) |
| forward/right | p | 0.811 | 25/25 | 0 | 23 | 2.07 ± 2.67 (1.38) | 8.65 ± 12.30 (5.07) | 2.20 ± 0.59 (2.26) | 5.19 ± 1.42 (5.76) | 2.39 ± 0.88 (2.50) |
| left/left | p | 0.860 | 25/25 | 0 | 23 | 1.70 ± 0.44 (1.58) | 6.44 ± 8.82 (3.23) | 2.26 ± 0.61 (2.52) | 5.34 ± 1.53 (6.07) | 2.52 ± 0.93 (2.85) |
| left/right | p | 0.829 | 25/25 | 0 | 22 | 1.74 ± 0.46 (1.80) | 14.54 ± 28.24 (4.04) | 2.12 ± 0.58 (2.23) | 4.94 ± 1.43 (4.88) | 2.21 ± 0.91 (2.20) |
| back/left | p | 0.778 | 25/25 | 0 | 20 | 2.46 ± 0.79 (2.56) | 21.96 ± 42.21 (5.98) | 2.16 ± 0.83 (2.46) | 5.07 ± 1.99 (5.95) | 2.43 ± 1.18 (2.82) |
| back/right | p | 0.772 | 25/25 | 0 | 23 | 3.04 ± 1.96 (2.58) | 18.97 ± 43.84 (5.70) | 2.28 ± 0.64 (2.32) | 5.43 ± 1.55 (5.92) | 2.59 ± 1.00 (2.78) |
| right/left | p | 0.780 | 24/25 | 0 | 21 | 1.81 ± 0.38 (1.84) | 12.08 ± 21.47 (4.62) | 2.11 ± 0.58 (2.11) | 5.02 ± 1.41 (5.40) | 2.27 ± 0.87 (2.15) |
| right/right | p | 0.839 | 25/25 | 0 | 24 | 1.62 ± 0.33 (1.56) | 7.14 ± 7.87 (5.69) | 2.28 ± 0.43 (2.17) | 5.20 ± 1.17 (5.10) | 2.41 ± 0.81 (2.23) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.846 | 14.3 | 5.68 | 2.74 |
| p | normal | 0.783 | 10.0 | 4.63 | 2.04 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.732 | 0.08 | 2.67 ± 0.97 (2.57) | 4.11 | 1.68 |
| p | medium | 20 | 0.863 | 0.64 | 1.36 ± 0.15 (1.36) | 4.37 | 1.84 |
| p | strong | 126 | 0.842 | 0.76 | - | 5.72 | 2.78 |

## Notes

- p: score 0.815, 199/200 kicked, 0 fell; worst sector back (0.775).
