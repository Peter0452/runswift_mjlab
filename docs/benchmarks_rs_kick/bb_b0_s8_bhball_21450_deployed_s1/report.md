# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_21450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.797** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 180 |
| Weak kicks (< 0.3 m) | 12 |
| Time to kick [s] | 1.91 ± 1.18 (1.69) |
| Direction error [°] | 11.38 ± 22.34 (5.55) |
| Avg ball speed [m/s] | 2.27 ± 0.58 (2.40) |
| Peak ball speed [m/s] | 4.90 ± 1.37 (5.48) |
| Distance [m] | 2.17 ± 0.80 (2.31) |
| Path length [m] | 2.18 ± 0.80 (2.32) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.813 | 49/50 | 0 | 45 | 1.48 ± 1.40 (1.32) | 7.81 ± 10.98 (4.58) | 2.20 ± 0.69 (2.38) | 4.78 ± 1.61 (5.47) | 2.10 ± 0.89 (2.31) |
| left | p | 0.819 | 49/50 | 0 | 45 | 1.70 ± 0.44 (1.64) | 11.63 ± 22.95 (5.48) | 2.26 ± 0.55 (2.38) | 4.87 ± 1.31 (5.33) | 2.15 ± 0.79 (2.20) |
| back | p | 0.756 | 49/50 | 0 | 45 | 2.74 ± 1.54 (2.48) | 15.61 ± 31.52 (7.33) | 2.38 ± 0.54 (2.52) | 5.13 ± 1.30 (5.76) | 2.35 ± 0.77 (2.63) |
| right | p | 0.801 | 49/50 | 0 | 45 | 1.72 ± 0.38 (1.76) | 10.46 ± 17.99 (5.58) | 2.24 ± 0.50 (2.35) | 4.80 ± 1.21 (5.18) | 2.08 ± 0.72 (2.10) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.795 | 98/100 | 0 | 89 | 1.83 ± 0.76 (1.65) | 11.80 ± 22.45 (5.56) | 2.25 ± 0.61 (2.44) | 4.86 ± 1.45 (5.53) | 2.15 ± 0.82 (2.33) |
| right | p | 0.799 | 98/100 | 0 | 91 | 1.98 ± 1.49 (1.72) | 10.96 ± 22.22 (5.55) | 2.30 ± 0.54 (2.39) | 4.93 ± 1.29 (5.39) | 2.19 ± 0.78 (2.29) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.831 | 25/25 | 0 | 23 | 1.29 ± 0.37 (1.28) | 7.62 ± 9.83 (4.58) | 2.15 ± 0.72 (2.38) | 4.67 ± 1.68 (5.47) | 2.04 ± 0.90 (2.29) |
| forward/right | p | 0.795 | 24/25 | 0 | 22 | 1.68 ± 1.94 (1.34) | 8.01 ± 12.05 (4.37) | 2.25 ± 0.64 (2.39) | 4.90 ± 1.52 (5.59) | 2.16 ± 0.88 (2.31) |
| left/left | p | 0.822 | 24/25 | 0 | 23 | 1.67 ± 0.36 (1.61) | 6.47 ± 5.97 (5.25) | 2.36 ± 0.42 (2.39) | 5.12 ± 1.05 (5.43) | 2.27 ± 0.66 (2.37) |
| left/right | p | 0.816 | 25/25 | 0 | 22 | 1.73 ± 0.50 (1.80) | 16.58 ± 30.79 (5.79) | 2.17 ± 0.63 (2.38) | 4.63 ± 1.48 (4.52) | 2.04 ± 0.87 (1.90) |
| back/left | p | 0.761 | 25/25 | 0 | 22 | 2.55 ± 1.01 (2.50) | 18.65 ± 34.25 (7.36) | 2.31 ± 0.65 (2.52) | 4.99 ± 1.53 (5.77) | 2.28 ± 0.86 (2.62) |
| back/right | p | 0.751 | 24/25 | 0 | 23 | 2.93 ± 1.93 (2.45) | 12.44 ± 28.06 (6.58) | 2.46 ± 0.36 (2.54) | 5.28 ± 0.98 (5.75) | 2.42 ± 0.65 (2.66) |
| right/left | p | 0.766 | 24/25 | 0 | 21 | 1.81 ± 0.40 (1.93) | 14.34 ± 24.46 (4.22) | 2.17 ± 0.57 (2.32) | 4.67 ± 1.38 (5.00) | 2.01 ± 0.78 (2.05) |
| right/right | p | 0.835 | 25/25 | 0 | 24 | 1.63 ± 0.35 (1.58) | 6.74 ± 5.66 (5.83) | 2.31 ± 0.40 (2.35) | 4.91 ± 1.00 (5.18) | 2.15 ± 0.65 (2.13) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.830 | 10.7 | 5.42 | 2.50 |
| p | normal | 0.764 | 12.0 | 4.37 | 1.84 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.716 | 0.09 | 2.58 ± 0.99 (2.40) | 3.97 | 1.57 |
| p | medium | 20 | 0.851 | 0.67 | 1.31 ± 0.16 (1.31) | 4.22 | 1.73 |
| p | strong | 126 | 0.823 | 0.72 | - | 5.40 | 2.50 |

## Notes

- p: score 0.797, 196/200 kicked, 0 fell; worst sector back (0.756).
