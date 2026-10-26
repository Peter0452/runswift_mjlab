# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-21-20_t5_n7_stand01/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.841** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 195 |
| Weak kicks (< 0.3 m) | 1 |
| Time to kick [s] | 1.78 ± 0.62 (1.68) |
| Direction error [°] | 5.04 ± 3.96 (3.94) |
| Avg ball speed [m/s] | 1.86 ± 0.36 (1.79) |
| Peak ball speed [m/s] | 3.97 ± 0.86 (3.66) |
| Distance [m] | 1.50 ± 0.52 (1.33) |
| Path length [m] | 1.51 ± 0.52 (1.34) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.845 | 50/50 | 0 | 49 | 1.15 ± 0.29 (1.22) | 5.22 ± 3.96 (4.10) | 1.68 ± 0.29 (1.63) | 3.60 ± 0.69 (3.37) | 1.25 ± 0.44 (1.10) |
| left | p | 0.857 | 50/50 | 0 | 49 | 1.70 ± 0.40 (1.62) | 5.24 ± 3.49 (4.50) | 1.88 ± 0.31 (1.88) | 4.02 ± 0.78 (4.12) | 1.53 ± 0.48 (1.55) |
| back | p | 0.821 | 50/50 | 0 | 48 | 2.56 ± 0.33 (2.52) | 4.45 ± 4.57 (3.23) | 2.04 ± 0.40 (2.20) | 4.39 ± 0.95 (4.83) | 1.76 ± 0.53 (1.91) |
| right | p | 0.841 | 50/50 | 0 | 49 | 1.70 ± 0.39 (1.68) | 5.24 ± 3.67 (4.27) | 1.83 ± 0.34 (1.67) | 3.88 ± 0.81 (3.55) | 1.44 ± 0.50 (1.24) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.841 | 100/100 | 0 | 99 | 1.79 ± 0.62 (1.65) | 4.68 ± 3.30 (3.92) | 1.91 ± 0.37 (1.96) | 4.09 ± 0.88 (4.20) | 1.58 ± 0.54 (1.64) |
| right | p | 0.840 | 100/100 | 0 | 96 | 1.77 ± 0.62 (1.73) | 5.40 ± 4.49 (4.01) | 1.80 ± 0.35 (1.72) | 3.86 ± 0.83 (3.56) | 1.42 ± 0.48 (1.25) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.851 | 25/25 | 0 | 25 | 1.15 ± 0.30 (1.08) | 4.71 ± 3.14 (4.10) | 1.69 ± 0.32 (1.63) | 3.60 ± 0.76 (3.34) | 1.26 ± 0.47 (1.09) |
| forward/right | p | 0.838 | 25/25 | 0 | 24 | 1.15 ± 0.29 (1.22) | 5.73 ± 4.57 (4.26) | 1.67 ± 0.26 (1.63) | 3.60 ± 0.62 (3.49) | 1.24 ± 0.41 (1.10) |
| left/left | p | 0.859 | 25/25 | 0 | 25 | 1.60 ± 0.40 (1.50) | 5.12 ± 3.14 (4.54) | 1.89 ± 0.37 (1.97) | 4.07 ± 0.90 (4.20) | 1.57 ± 0.55 (1.69) |
| left/right | p | 0.854 | 25/25 | 0 | 24 | 1.81 ± 0.37 (1.82) | 5.36 ± 3.81 (3.85) | 1.87 ± 0.23 (1.86) | 3.98 ± 0.64 (3.89) | 1.50 ± 0.40 (1.46) |
| back/left | p | 0.824 | 25/25 | 0 | 25 | 2.56 ± 0.30 (2.50) | 3.61 ± 2.38 (3.20) | 2.08 ± 0.31 (2.23) | 4.48 ± 0.79 (4.80) | 1.82 ± 0.49 (1.98) |
| back/right | p | 0.818 | 25/25 | 0 | 23 | 2.56 ± 0.36 (2.54) | 5.28 ± 5.88 (3.38) | 1.99 ± 0.47 (2.18) | 4.30 ± 1.09 (4.89) | 1.71 ± 0.55 (1.88) |
| right/left | p | 0.831 | 25/25 | 0 | 24 | 1.84 ± 0.37 (1.74) | 5.27 ± 4.05 (4.08) | 1.98 ± 0.33 (2.06) | 4.21 ± 0.84 (4.47) | 1.66 ± 0.51 (1.90) |
| right/right | p | 0.851 | 25/25 | 0 | 25 | 1.55 ± 0.36 (1.62) | 5.21 ± 3.26 (4.33) | 1.67 ± 0.27 (1.62) | 3.55 ± 0.64 (3.31) | 1.23 ± 0.37 (1.07) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.849 | 5.1 | 4.40 | 1.74 |
| p | normal | 0.833 | 4.9 | 3.54 | 1.26 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.787 | 0.25 | 2.02 ± 0.70 (2.00) | 3.14 | 1.01 |
| p | medium | 20 | 0.928 | 0.88 | 1.05 ± 0.14 (1.07) | 3.34 | 1.12 |
| p | strong | 126 | 0.850 | 0.59 | - | 4.43 | 1.77 |

## Notes

- p: score 0.841, 200/200 kicked, 0 fell; worst sector back (0.821).
