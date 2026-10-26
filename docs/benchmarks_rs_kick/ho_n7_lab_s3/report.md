# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.838** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 193 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.59 ± 0.53 (1.52) |
| Direction error [°] | 7.49 ± 16.04 (5.11) |
| Avg ball speed [m/s] | 2.17 ± 0.39 (2.17) |
| Peak ball speed [m/s] | 4.65 ± 0.89 (4.69) |
| Distance [m] | 2.01 ± 0.58 (2.01) |
| Path length [m] | 2.02 ± 0.58 (2.03) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.846 | 50/50 | 0 | 48 | 1.03 ± 0.22 (1.03) | 5.62 ± 3.97 (4.98) | 2.06 ± 0.29 (2.00) | 4.45 ± 0.65 (4.27) | 1.82 ± 0.44 (1.68) |
| left | p | 0.839 | 50/50 | 0 | 47 | 1.53 ± 0.33 (1.52) | 6.98 ± 4.87 (6.84) | 2.23 ± 0.32 (2.18) | 4.75 ± 0.76 (4.75) | 2.08 ± 0.54 (2.11) |
| back | p | 0.825 | 50/50 | 0 | 48 | 2.27 ± 0.32 (2.28) | 11.65 ± 30.86 (4.94) | 2.19 ± 0.50 (2.34) | 4.67 ± 1.15 (5.12) | 2.07 ± 0.68 (2.27) |
| right | p | 0.842 | 50/50 | 0 | 50 | 1.55 ± 0.32 (1.58) | 5.71 ± 3.56 (5.25) | 2.21 ± 0.38 (2.31) | 4.71 ± 0.86 (4.97) | 2.05 ± 0.61 (2.15) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.844 | 100/100 | 0 | 97 | 1.60 ± 0.53 (1.54) | 7.07 ± 15.41 (5.06) | 2.17 ± 0.39 (2.16) | 4.63 ± 0.89 (4.68) | 2.00 ± 0.59 (2.06) |
| right | p | 0.831 | 100/100 | 0 | 96 | 1.59 ± 0.54 (1.52) | 7.92 ± 16.63 (5.24) | 2.18 ± 0.39 (2.20) | 4.66 ± 0.88 (4.70) | 2.01 ± 0.57 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.857 | 25/25 | 0 | 25 | 1.04 ± 0.21 (1.02) | 4.80 ± 3.10 (4.73) | 2.06 ± 0.30 (2.03) | 4.45 ± 0.65 (4.20) | 1.83 ± 0.46 (1.76) |
| forward/right | p | 0.834 | 25/25 | 0 | 23 | 1.03 ± 0.22 (1.06) | 6.44 ± 4.53 (5.35) | 2.06 ± 0.29 (1.97) | 4.45 ± 0.66 (4.37) | 1.82 ± 0.42 (1.67) |
| left/left | p | 0.842 | 25/25 | 0 | 23 | 1.43 ± 0.29 (1.44) | 6.92 ± 4.67 (6.86) | 2.22 ± 0.32 (2.17) | 4.74 ± 0.74 (4.64) | 2.07 ± 0.51 (2.08) |
| left/right | p | 0.836 | 25/25 | 0 | 24 | 1.62 ± 0.33 (1.54) | 7.05 ± 5.06 (6.83) | 2.25 ± 0.33 (2.22) | 4.76 ± 0.79 (4.85) | 2.10 ± 0.56 (2.14) |
| back/left | p | 0.838 | 25/25 | 0 | 24 | 2.28 ± 0.30 (2.28) | 10.98 ± 29.77 (4.13) | 2.19 ± 0.51 (2.30) | 4.66 ± 1.20 (5.07) | 2.07 ± 0.71 (2.22) |
| back/right | p | 0.812 | 25/25 | 0 | 24 | 2.27 ± 0.34 (2.28) | 12.33 ± 31.90 (5.61) | 2.19 ± 0.49 (2.38) | 4.68 ± 1.11 (5.25) | 2.08 ± 0.64 (2.31) |
| right/left | p | 0.841 | 25/25 | 0 | 25 | 1.64 ± 0.29 (1.66) | 5.58 ± 2.99 (5.72) | 2.19 ± 0.38 (2.14) | 4.69 ± 0.87 (4.77) | 2.05 ± 0.61 (2.15) |
| right/right | p | 0.843 | 25/25 | 0 | 25 | 1.45 ± 0.31 (1.46) | 5.85 ± 4.04 (4.85) | 2.22 ± 0.38 (2.34) | 4.74 ± 0.86 (4.99) | 2.06 ± 0.60 (2.14) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.871 | 7.3 | 5.11 | 2.32 |
| p | normal | 0.805 | 7.7 | 4.18 | 1.69 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.750 | 0.11 | 2.41 ± 0.72 (2.43) | 3.84 | 1.46 |
| p | medium | 18 | 0.881 | 0.78 | 1.21 ± 0.15 (1.23) | 3.88 | 1.46 |
| p | strong | 124 | 0.872 | 0.68 | - | 5.13 | 2.34 |

## Notes

- p: score 0.838, 200/200 kicked, 0 fell; worst sector back (0.825).
