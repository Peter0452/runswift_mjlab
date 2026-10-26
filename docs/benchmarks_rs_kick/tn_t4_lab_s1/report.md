# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-06-39_t4_n7_control/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.840** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 198 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.54 ± 0.51 (1.50) |
| Direction error [°] | 5.13 ± 3.45 (4.63) |
| Avg ball speed [m/s] | 1.97 ± 0.28 (1.98) |
| Peak ball speed [m/s] | 4.27 ± 0.63 (4.26) |
| Distance [m] | 1.66 ± 0.41 (1.67) |
| Path length [m] | 1.67 ± 0.41 (1.68) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.838 | 50/50 | 0 | 48 | 1.03 ± 0.27 (1.04) | 5.12 ± 3.71 (4.42) | 1.78 ± 0.26 (1.78) | 3.88 ± 0.58 (3.89) | 1.39 ± 0.37 (1.41) |
| left | p | 0.842 | 50/50 | 0 | 50 | 1.49 ± 0.35 (1.40) | 5.65 ± 3.37 (5.71) | 1.97 ± 0.22 (1.97) | 4.26 ± 0.54 (4.25) | 1.66 ± 0.32 (1.66) |
| back | p | 0.848 | 50/50 | 0 | 50 | 2.15 ± 0.26 (2.16) | 4.50 ± 3.37 (3.98) | 2.15 ± 0.21 (2.17) | 4.65 ± 0.50 (4.68) | 1.92 ± 0.36 (1.90) |
| right | p | 0.831 | 50/50 | 0 | 50 | 1.51 ± 0.36 (1.51) | 5.25 ± 3.25 (5.40) | 1.97 ± 0.28 (2.00) | 4.29 ± 0.65 (4.28) | 1.68 ± 0.38 (1.67) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.840 | 100/100 | 0 | 99 | 1.54 ± 0.51 (1.44) | 4.98 ± 3.32 (4.29) | 1.98 ± 0.26 (2.01) | 4.32 ± 0.62 (4.33) | 1.68 ± 0.40 (1.68) |
| right | p | 0.840 | 100/100 | 0 | 99 | 1.54 ± 0.51 (1.56) | 5.29 ± 3.58 (4.84) | 1.96 ± 0.29 (1.95) | 4.22 ± 0.64 (4.21) | 1.64 ± 0.41 (1.64) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 24 | 1.02 ± 0.27 (1.02) | 5.13 ± 3.38 (4.65) | 1.79 ± 0.29 (1.75) | 3.91 ± 0.65 (3.89) | 1.41 ± 0.40 (1.39) |
| forward/right | p | 0.838 | 25/25 | 0 | 24 | 1.03 ± 0.28 (1.10) | 5.11 ± 4.01 (3.84) | 1.76 ± 0.23 (1.79) | 3.84 ± 0.51 (3.89) | 1.37 ± 0.34 (1.41) |
| left/left | p | 0.850 | 25/25 | 0 | 25 | 1.39 ± 0.33 (1.34) | 5.02 ± 3.24 (3.79) | 1.99 ± 0.25 (1.99) | 4.35 ± 0.62 (4.44) | 1.69 ± 0.37 (1.73) |
| left/right | p | 0.834 | 25/25 | 0 | 25 | 1.58 ± 0.34 (1.58) | 6.28 ± 3.38 (6.46) | 1.95 ± 0.19 (1.95) | 4.18 ± 0.44 (4.12) | 1.62 ± 0.26 (1.58) |
| back/left | p | 0.844 | 25/25 | 0 | 25 | 2.15 ± 0.23 (2.16) | 4.75 ± 3.56 (3.65) | 2.13 ± 0.21 (2.13) | 4.63 ± 0.49 (4.66) | 1.91 ± 0.37 (1.90) |
| back/right | p | 0.852 | 25/25 | 0 | 25 | 2.15 ± 0.28 (2.16) | 4.25 ± 3.15 (4.34) | 2.17 ± 0.21 (2.22) | 4.67 ± 0.51 (4.71) | 1.94 ± 0.34 (1.89) |
| right/left | p | 0.826 | 25/25 | 0 | 25 | 1.61 ± 0.35 (1.52) | 5.00 ± 3.08 (4.99) | 1.99 ± 0.19 (2.03) | 4.38 ± 0.48 (4.33) | 1.71 ± 0.31 (1.68) |
| right/right | p | 0.835 | 25/25 | 0 | 25 | 1.41 ± 0.33 (1.44) | 5.51 ± 3.39 (5.45) | 1.95 ± 0.34 (1.96) | 4.19 ± 0.78 (4.24) | 1.64 ± 0.44 (1.67) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.863 | 5.2 | 4.46 | 1.77 |
| p | normal | 0.816 | 5.0 | 4.08 | 1.55 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.765 | 0.09 | 2.55 ± 0.79 (2.33) | 3.98 | 1.49 |
| p | medium | 20 | 0.901 | 0.72 | 1.25 ± 0.21 (1.29) | 3.98 | 1.52 |
| p | strong | 126 | 0.862 | 0.59 | - | 4.44 | 1.76 |

## Notes

- p: score 0.840, 200/200 kicked, 0 fell; worst sector right (0.831).
