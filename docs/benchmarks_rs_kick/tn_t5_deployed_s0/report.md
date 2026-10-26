# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_00-21-20_t5_n7_stand01/model_20346.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.770** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 2.04 ± 0.77 (1.98) |
| Direction error [°] | 16.05 ± 34.00 (4.45) |
| Avg ball speed [m/s] | 2.09 ± 0.69 (2.21) |
| Peak ball speed [m/s] | 4.45 ± 1.57 (5.00) |
| Distance [m] | 1.85 ± 0.88 (1.94) |
| Path length [m] | 1.86 ± 0.88 (1.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.797 | 49/50 | 0 | 40 | 1.46 ± 0.37 (1.44) | 10.15 ± 15.16 (4.47) | 1.93 ± 0.63 (2.04) | 4.08 ± 1.48 (3.93) | 1.61 ± 0.80 (1.48) |
| left | p | 0.792 | 48/50 | 0 | 41 | 1.90 ± 0.57 (2.04) | 17.41 ± 33.35 (5.12) | 2.12 ± 0.66 (2.25) | 4.59 ± 1.54 (5.16) | 1.91 ± 0.85 (2.01) |
| back | p | 0.695 | 47/50 | 0 | 42 | 2.88 ± 0.73 (3.00) | 20.07 ± 46.64 (4.42) | 2.24 ± 0.68 (2.44) | 4.71 ± 1.55 (5.54) | 2.05 ± 0.89 (2.36) |
| right | p | 0.795 | 49/50 | 0 | 42 | 1.94 ± 0.55 (1.98) | 16.74 ± 33.07 (3.74) | 2.09 ± 0.75 (2.24) | 4.44 ± 1.65 (4.99) | 1.85 ± 0.90 (1.91) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.794 | 99/100 | 0 | 85 | 1.99 ± 0.76 (1.94) | 17.67 ± 37.53 (4.38) | 2.08 ± 0.68 (2.19) | 4.45 ± 1.58 (5.03) | 1.85 ± 0.87 (2.00) |
| right | p | 0.746 | 94/100 | 0 | 80 | 2.08 ± 0.77 (2.07) | 14.33 ± 29.73 (4.53) | 2.10 ± 0.70 (2.21) | 4.46 ± 1.57 (4.99) | 1.86 ± 0.88 (1.92) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.833 | 25/25 | 0 | 21 | 1.44 ± 0.35 (1.46) | 9.91 ± 17.88 (3.57) | 2.01 ± 0.67 (2.10) | 4.29 ± 1.58 (4.02) | 1.74 ± 0.85 (1.59) |
| forward/right | p | 0.762 | 24/25 | 0 | 19 | 1.48 ± 0.39 (1.44) | 10.40 ± 11.66 (6.28) | 1.83 ± 0.58 (1.90) | 3.86 ± 1.33 (3.81) | 1.47 ± 0.73 (1.44) |
| left/left | p | 0.844 | 25/25 | 0 | 22 | 1.79 ± 0.51 (1.96) | 16.79 ± 33.32 (5.10) | 2.14 ± 0.62 (2.26) | 4.64 ± 1.46 (5.32) | 1.93 ± 0.79 (2.00) |
| left/right | p | 0.740 | 23/25 | 0 | 19 | 2.02 ± 0.61 (2.14) | 18.07 ± 33.38 (5.14) | 2.09 ± 0.69 (2.23) | 4.54 ± 1.62 (5.05) | 1.89 ± 0.91 (2.03) |
| back/left | p | 0.712 | 24/25 | 0 | 21 | 2.76 ± 0.82 (2.86) | 22.91 ± 50.59 (4.41) | 2.19 ± 0.66 (2.44) | 4.64 ± 1.57 (5.56) | 2.00 ± 0.90 (2.46) |
| back/right | p | 0.678 | 23/25 | 0 | 21 | 3.00 ± 0.60 (3.16) | 17.12 ± 41.94 (4.42) | 2.28 ± 0.69 (2.55) | 4.79 ± 1.52 (5.43) | 2.11 ± 0.88 (2.22) |
| right/left | p | 0.786 | 25/25 | 0 | 21 | 2.01 ± 0.60 (1.98) | 21.29 ± 39.90 (4.85) | 1.99 ± 0.75 (2.06) | 4.23 ± 1.67 (4.07) | 1.73 ± 0.91 (1.65) |
| right/right | p | 0.803 | 24/25 | 0 | 21 | 1.87 ± 0.49 (1.95) | 12.01 ± 23.05 (3.61) | 2.19 ± 0.73 (2.39) | 4.66 ± 1.61 (5.43) | 1.98 ± 0.88 (2.10) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.795 | 14.5 | 5.12 | 2.23 |
| p | normal | 0.745 | 17.6 | 3.79 | 1.48 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.707 | 0.20 | 2.10 ± 0.98 (2.03) | 3.34 | 1.20 |
| p | medium | 16 | 0.825 | 0.78 | 1.17 ± 0.18 (1.19) | 3.79 | 1.43 |
| p | strong | 126 | 0.792 | 0.67 | - | 5.05 | 2.21 |

## Notes

- p: score 0.770, 193/200 kicked, 0 fell; worst sector back (0.695).
