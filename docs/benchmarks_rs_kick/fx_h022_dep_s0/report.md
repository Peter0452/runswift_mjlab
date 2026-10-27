# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **h022** = `logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt`.

## Overall

| Metric | h022 |
|---|---|
| **Score** | **0.835** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 188 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 1.89 ± 0.58 (1.84) |
| Direction error [°] | 8.02 ± 17.51 (4.51) |
| Avg ball speed [m/s] | 2.27 ± 0.63 (2.47) |
| Peak ball speed [m/s] | 4.76 ± 1.41 (5.38) |
| Distance [m] | 2.22 ± 0.87 (2.47) |
| Path length [m] | 2.23 ± 0.87 (2.49) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | h022 | 0.844 | 50/50 | 0 | 48 | 1.30 ± 0.27 (1.31) | 6.65 ± 11.82 (3.95) | 2.19 ± 0.57 (2.30) | 4.63 ± 1.31 (5.08) | 2.09 ± 0.80 (2.23) |
| left | h022 | 0.863 | 50/50 | 0 | 47 | 1.83 ± 0.40 (1.88) | 7.00 ± 10.61 (4.63) | 2.30 ± 0.66 (2.53) | 4.85 ± 1.45 (5.49) | 2.29 ± 0.86 (2.72) |
| back | h022 | 0.790 | 50/50 | 0 | 45 | 2.62 ± 0.31 (2.62) | 12.34 ± 29.55 (6.18) | 2.37 ± 0.68 (2.59) | 4.95 ± 1.52 (5.70) | 2.43 ± 0.96 (2.90) |
| right | h022 | 0.842 | 50/50 | 0 | 48 | 1.82 ± 0.37 (1.78) | 6.10 ± 8.69 (3.83) | 2.20 ± 0.59 (2.35) | 4.62 ± 1.33 (5.16) | 2.09 ± 0.80 (2.27) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | h022 | 0.839 | 100/100 | 0 | 93 | 1.90 ± 0.58 (1.84) | 7.82 ± 16.70 (4.44) | 2.26 ± 0.67 (2.49) | 4.76 ± 1.49 (5.38) | 2.23 ± 0.91 (2.56) |
| right | h022 | 0.831 | 100/100 | 0 | 95 | 1.89 ± 0.58 (1.82) | 8.22 ± 18.28 (4.57) | 2.27 ± 0.59 (2.41) | 4.77 ± 1.33 (5.35) | 2.22 ± 0.84 (2.45) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | h022 | 0.847 | 25/25 | 0 | 23 | 1.30 ± 0.26 (1.30) | 8.14 ± 16.16 (3.93) | 2.18 ± 0.72 (2.38) | 4.56 ± 1.61 (5.11) | 2.10 ± 0.94 (2.27) |
| forward/right | h022 | 0.841 | 25/25 | 0 | 25 | 1.30 ± 0.28 (1.34) | 5.16 ± 3.75 (3.97) | 2.21 ± 0.36 (2.28) | 4.69 ± 0.92 (5.00) | 2.08 ± 0.63 (2.04) |
| left/left | h022 | 0.866 | 25/25 | 0 | 23 | 1.72 ± 0.37 (1.84) | 6.50 ± 7.33 (4.52) | 2.25 ± 0.71 (2.56) | 4.70 ± 1.57 (5.41) | 2.21 ± 0.91 (2.65) |
| left/right | h022 | 0.861 | 25/25 | 0 | 24 | 1.95 ± 0.38 (1.98) | 7.50 ± 13.08 (4.75) | 2.35 ± 0.59 (2.53) | 4.99 ± 1.31 (5.57) | 2.36 ± 0.81 (2.74) |
| back/left | h022 | 0.784 | 25/25 | 0 | 22 | 2.64 ± 0.35 (2.64) | 12.12 ± 27.57 (6.45) | 2.33 ± 0.74 (2.57) | 4.88 ± 1.66 (5.66) | 2.39 ± 1.01 (2.88) |
| back/right | h022 | 0.796 | 25/25 | 0 | 23 | 2.60 ± 0.27 (2.58) | 12.56 ± 31.40 (5.84) | 2.42 ± 0.62 (2.76) | 5.02 ± 1.36 (5.77) | 2.46 ± 0.91 (2.96) |
| right/left | h022 | 0.858 | 25/25 | 0 | 25 | 1.93 ± 0.31 (1.86) | 4.54 ± 3.13 (3.47) | 2.30 ± 0.43 (2.36) | 4.87 ± 1.02 (5.30) | 2.22 ± 0.71 (2.41) |
| right/right | h022 | 0.825 | 25/25 | 0 | 23 | 1.71 ± 0.39 (1.76) | 7.66 ± 11.67 (3.94) | 2.10 ± 0.69 (2.34) | 4.38 ± 1.53 (4.99) | 1.96 ± 0.87 (2.19) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| h022 | strong | 0.874 | 5.7 | 5.63 | 2.80 |
| h022 | normal | 0.795 | 10.3 | 3.90 | 1.65 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| h022 | small | 58 | 0.738 | 0.11 | 2.03 ± 0.98 (2.06) | 3.23 | 1.22 |
| h022 | medium | 16 | 0.877 | 0.76 | 1.11 ± 0.31 (1.15) | 3.58 | 1.41 |
| h022 | strong | 126 | 0.874 | 0.75 | - | 5.62 | 2.79 |

## Notes

- h022: score 0.835, 200/200 kicked, 0 fell; worst sector back (0.790).
