# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-26_08-51-51_night_n7_rest15/model_19847.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.794** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 166 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 1.97 ± 1.61 (1.69) |
| Direction error [°] | 18.48 ± 36.20 (5.70) |
| Avg ball speed [m/s] | 2.30 ± 0.87 (2.56) |
| Peak ball speed [m/s] | 4.80 ± 1.88 (5.80) |
| Distance [m] | 2.34 ± 1.20 (2.81) |
| Path length [m] | 2.35 ± 1.20 (2.82) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 44 | 1.65 ± 1.91 (1.32) | 9.85 ± 14.45 (4.68) | 2.19 ± 0.86 (2.18) | 4.53 ± 1.85 (4.25) | 2.13 ± 1.15 (1.82) |
| left | p | 0.810 | 49/50 | 0 | 42 | 1.85 ± 1.51 (1.70) | 16.88 ± 31.60 (6.65) | 2.37 ± 0.86 (2.65) | 4.98 ± 1.86 (5.86) | 2.47 ± 1.17 (3.01) |
| back | p | 0.769 | 50/50 | 0 | 40 | 2.53 ± 1.38 (2.46) | 27.11 ± 50.73 (6.31) | 2.38 ± 0.88 (2.78) | 4.97 ± 1.91 (6.03) | 2.49 ± 1.25 (3.16) |
| right | p | 0.795 | 49/50 | 0 | 40 | 1.85 ± 1.44 (1.72) | 20.09 ± 36.05 (4.63) | 2.25 ± 0.85 (2.35) | 4.74 ± 1.86 (5.33) | 2.28 ± 1.19 (2.27) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.816 | 100/100 | 0 | 86 | 1.82 ± 1.12 (1.67) | 17.87 ± 36.26 (5.32) | 2.37 ± 0.82 (2.65) | 4.95 ± 1.79 (5.97) | 2.43 ± 1.17 (2.92) |
| right | p | 0.772 | 98/100 | 0 | 80 | 2.12 ± 1.98 (1.71) | 19.10 ± 36.13 (5.86) | 2.23 ± 0.91 (2.35) | 4.65 ± 1.95 (5.36) | 2.25 ± 1.22 (2.43) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.844 | 25/25 | 0 | 23 | 1.31 ± 0.31 (1.28) | 8.23 ± 14.11 (4.64) | 2.32 ± 0.75 (2.33) | 4.82 ± 1.65 (4.39) | 2.29 ± 1.06 (1.80) |
| forward/right | p | 0.764 | 25/25 | 0 | 21 | 1.99 ± 2.64 (1.32) | 11.47 ± 14.61 (5.82) | 2.06 ± 0.94 (2.15) | 4.24 ± 1.99 (4.20) | 1.97 ± 1.22 (1.83) |
| left/left | p | 0.858 | 25/25 | 0 | 23 | 1.55 ± 0.38 (1.60) | 12.52 ± 21.78 (5.91) | 2.56 ± 0.79 (2.88) | 5.31 ± 1.74 (6.24) | 2.71 ± 1.14 (3.35) |
| left/right | p | 0.763 | 24/25 | 0 | 19 | 2.16 ± 2.08 (1.88) | 21.43 ± 38.78 (7.06) | 2.17 ± 0.88 (2.48) | 4.63 ± 1.93 (5.66) | 2.22 ± 1.16 (2.78) |
| back/left | p | 0.762 | 25/25 | 0 | 20 | 2.72 ± 1.83 (2.60) | 26.62 ± 51.61 (7.32) | 2.43 ± 0.81 (2.75) | 5.12 ± 1.80 (6.03) | 2.59 ± 1.23 (3.31) |
| back/right | p | 0.775 | 25/25 | 0 | 20 | 2.34 ± 0.60 (2.46) | 27.60 ± 49.84 (5.92) | 2.33 ± 0.94 (2.80) | 4.82 ± 2.00 (6.01) | 2.40 ± 1.25 (2.99) |
| right/left | p | 0.801 | 25/25 | 0 | 20 | 1.71 ± 0.49 (1.74) | 24.13 ± 41.04 (5.49) | 2.16 ± 0.86 (2.23) | 4.56 ± 1.88 (4.44) | 2.16 ± 1.18 (1.98) |
| right/right | p | 0.788 | 24/25 | 0 | 20 | 1.98 ± 1.98 (1.68) | 15.88 ± 29.39 (4.45) | 2.34 ± 0.83 (2.65) | 4.93 ± 1.82 (5.91) | 2.42 ± 1.18 (3.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.823 | 17.0 | 5.63 | 2.93 |
| p | normal | 0.766 | 19.9 | 4.00 | 1.77 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.725 | 0.18 | 2.28 ± 1.10 (2.23) | 3.52 | 1.41 |
| p | medium | 16 | 0.826 | 0.68 | 1.15 ± 0.35 (1.24) | 3.72 | 1.54 |
| p | strong | 126 | 0.822 | 0.74 | - | 5.54 | 2.88 |

## Notes

- p: score 0.794, 198/200 kicked, 0 fell; worst sector back (0.769).
