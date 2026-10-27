# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.803** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 169 |
| Weak kicks (< 0.3 m) | 11 |
| Time to kick [s] | 1.86 ± 1.09 (1.72) |
| Direction error [°] | 18.00 ± 38.30 (5.18) |
| Avg ball speed [m/s] | 2.39 ± 0.83 (2.63) |
| Peak ball speed [m/s] | 5.01 ± 1.81 (5.81) |
| Distance [m] | 2.48 ± 1.20 (2.88) |
| Path length [m] | 2.49 ± 1.21 (2.90) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.787 | 49/50 | 0 | 41 | 1.63 ± 1.85 (1.30) | 9.75 ± 13.67 (4.58) | 2.25 ± 0.81 (2.22) | 4.70 ± 1.76 (4.27) | 2.22 ± 1.16 (1.90) |
| left | p | 0.835 | 49/50 | 0 | 45 | 1.76 ± 0.59 (1.76) | 13.27 ± 28.03 (5.63) | 2.49 ± 0.69 (2.71) | 5.28 ± 1.57 (6.00) | 2.62 ± 1.07 (3.04) |
| back | p | 0.774 | 50/50 | 0 | 40 | 2.33 ± 0.68 (2.43) | 33.49 ± 59.12 (7.00) | 2.42 ± 1.04 (2.93) | 5.03 ± 2.22 (6.34) | 2.61 ± 1.42 (3.46) |
| right | p | 0.817 | 49/50 | 0 | 43 | 1.70 ± 0.45 (1.72) | 15.18 ± 31.88 (4.42) | 2.39 ± 0.72 (2.61) | 5.05 ± 1.55 (5.77) | 2.46 ± 1.08 (2.88) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.829 | 100/100 | 0 | 89 | 1.88 ± 1.08 (1.72) | 15.95 ± 37.41 (4.03) | 2.45 ± 0.79 (2.68) | 5.14 ± 1.74 (5.94) | 2.57 ± 1.18 (3.01) |
| right | p | 0.778 | 97/100 | 0 | 80 | 1.83 ± 1.09 (1.70) | 20.12 ± 39.09 (6.24) | 2.33 ± 0.87 (2.53) | 4.88 ± 1.87 (5.59) | 2.39 ± 1.22 (2.70) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.832 | 25/25 | 0 | 22 | 1.64 ± 1.82 (1.30) | 7.97 ± 14.02 (3.51) | 2.34 ± 0.78 (2.27) | 4.91 ± 1.75 (4.52) | 2.36 ± 1.15 (2.01) |
| forward/right | p | 0.743 | 24/25 | 0 | 19 | 1.62 ± 1.87 (1.30) | 11.60 ± 13.05 (6.22) | 2.15 ± 0.82 (2.13) | 4.47 ± 1.74 (4.27) | 2.07 ± 1.15 (1.87) |
| left/left | p | 0.868 | 25/25 | 0 | 24 | 1.76 ± 0.67 (1.72) | 7.34 ± 11.63 (5.43) | 2.60 ± 0.57 (2.71) | 5.47 ± 1.35 (6.01) | 2.76 ± 0.95 (3.08) |
| left/right | p | 0.801 | 24/25 | 0 | 21 | 1.76 ± 0.50 (1.91) | 19.44 ± 37.26 (5.89) | 2.39 ± 0.79 (2.65) | 5.08 ± 1.75 (5.93) | 2.46 ± 1.17 (2.83) |
| back/left | p | 0.787 | 25/25 | 0 | 21 | 2.33 ± 0.65 (2.52) | 30.26 ± 58.10 (5.04) | 2.47 ± 0.98 (2.91) | 5.15 ± 2.10 (6.34) | 2.68 ± 1.40 (3.55) |
| back/right | p | 0.761 | 25/25 | 0 | 19 | 2.33 ± 0.70 (2.40) | 36.72 ± 59.94 (7.92) | 2.37 ± 1.09 (3.00) | 4.90 ± 2.32 (6.33) | 2.55 ± 1.44 (3.38) |
| right/left | p | 0.829 | 25/25 | 0 | 22 | 1.80 ± 0.46 (1.84) | 18.22 ± 39.29 (3.09) | 2.39 ± 0.75 (2.61) | 5.04 ± 1.63 (5.71) | 2.46 ± 1.13 (2.88) |
| right/right | p | 0.806 | 24/25 | 0 | 21 | 1.59 ± 0.42 (1.63) | 12.02 ± 21.16 (5.15) | 2.40 ± 0.68 (2.61) | 5.05 ± 1.46 (5.79) | 2.46 ± 1.03 (2.87) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.848 | 15.6 | 5.88 | 3.11 |
| p | normal | 0.759 | 20.4 | 4.13 | 1.84 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.715 | 0.14 | 2.36 ± 1.13 (2.39) | 3.64 | 1.47 |
| p | medium | 16 | 0.801 | 0.64 | 1.19 ± 0.36 (1.26) | 3.87 | 1.62 |
| p | strong | 126 | 0.844 | 0.77 | - | 5.78 | 3.04 |

## Notes

- p: score 0.803, 197/200 kicked, 0 fell; worst sector back (0.774).
