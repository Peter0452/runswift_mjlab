# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r2_u5_u12.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.782** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 168 |
| Weak kicks (< 0.3 m) | 16 |
| Time to kick [s] | 1.97 ± 1.45 (1.76) |
| Direction error [°] | 17.68 ± 34.73 (5.74) |
| Avg ball speed [m/s] | 2.23 ± 0.75 (2.36) |
| Peak ball speed [m/s] | 4.75 ± 1.69 (5.37) |
| Distance [m] | 2.18 ± 1.01 (2.37) |
| Path length [m] | 2.19 ± 1.01 (2.38) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.801 | 49/50 | 0 | 44 | 1.45 ± 1.53 (1.26) | 10.75 ± 19.28 (4.38) | 2.16 ± 0.65 (2.24) | 4.66 ± 1.53 (5.06) | 2.06 ± 0.88 (2.16) |
| left | p | 0.788 | 48/50 | 0 | 42 | 1.88 ± 0.92 (1.79) | 13.61 ± 25.48 (5.43) | 2.26 ± 0.73 (2.52) | 4.82 ± 1.65 (5.46) | 2.22 ± 0.98 (2.48) |
| back | p | 0.753 | 49/50 | 0 | 43 | 2.74 ± 1.87 (2.44) | 22.30 ± 44.76 (6.26) | 2.40 ± 0.71 (2.64) | 5.10 ± 1.63 (5.86) | 2.45 ± 1.04 (2.83) |
| right | p | 0.786 | 50/50 | 0 | 39 | 1.79 ± 0.92 (1.77) | 23.87 ± 40.69 (6.74) | 2.09 ± 0.84 (2.30) | 4.42 ± 1.86 (4.57) | 2.00 ± 1.06 (1.93) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.783 | 98/100 | 0 | 83 | 1.88 ± 0.98 (1.75) | 19.96 ± 37.03 (5.84) | 2.24 ± 0.81 (2.51) | 4.81 ± 1.80 (5.68) | 2.25 ± 1.06 (2.61) |
| right | p | 0.781 | 98/100 | 0 | 85 | 2.05 ± 1.80 (1.78) | 15.40 ± 32.10 (5.73) | 2.21 ± 0.68 (2.32) | 4.69 ± 1.57 (4.63) | 2.11 ± 0.95 (1.94) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.815 | 25/25 | 0 | 22 | 1.25 ± 0.25 (1.34) | 13.19 ± 24.52 (5.27) | 2.13 ± 0.73 (2.19) | 4.55 ± 1.68 (4.38) | 2.03 ± 0.95 (1.98) |
| forward/right | p | 0.787 | 24/25 | 0 | 22 | 1.66 ± 2.16 (1.20) | 8.21 ± 10.97 (3.83) | 2.20 ± 0.55 (2.35) | 4.78 ± 1.35 (5.33) | 2.08 ± 0.80 (2.26) |
| left/left | p | 0.784 | 24/25 | 0 | 21 | 1.97 ± 1.21 (1.73) | 13.43 ± 24.27 (5.20) | 2.32 ± 0.76 (2.61) | 4.97 ± 1.69 (5.82) | 2.34 ± 1.01 (2.61) |
| left/right | p | 0.791 | 24/25 | 0 | 21 | 1.78 ± 0.45 (1.81) | 13.79 ± 26.64 (5.43) | 2.20 ± 0.70 (2.29) | 4.67 ± 1.59 (4.86) | 2.10 ± 0.92 (2.03) |
| back/left | p | 0.755 | 24/25 | 0 | 21 | 2.29 ± 0.59 (2.49) | 19.78 ± 35.57 (6.67) | 2.45 ± 0.70 (2.69) | 5.24 ± 1.60 (5.93) | 2.57 ± 1.01 (2.95) |
| back/right | p | 0.750 | 25/25 | 0 | 22 | 3.18 ± 2.47 (2.44) | 24.71 ± 51.96 (5.82) | 2.36 ± 0.71 (2.37) | 4.95 ± 1.65 (5.38) | 2.34 ± 1.05 (2.41) |
| right/left | p | 0.776 | 25/25 | 0 | 19 | 2.04 ± 1.19 (1.82) | 33.18 ± 52.29 (6.55) | 2.08 ± 0.95 (2.54) | 4.48 ± 2.09 (5.74) | 2.07 ± 1.16 (2.63) |
| right/right | p | 0.797 | 25/25 | 0 | 20 | 1.55 ± 0.41 (1.64) | 14.55 ± 20.09 (6.92) | 2.09 ± 0.72 (2.23) | 4.37 ± 1.60 (4.33) | 1.93 ± 0.94 (1.85) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.810 | 17.0 | 5.36 | 2.56 |
| p | normal | 0.754 | 18.3 | 4.15 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.719 | 0.18 | 2.23 ± 0.98 (2.08) | 3.74 | 1.51 |
| p | medium | 15 | 0.806 | 0.61 | 1.07 ± 0.46 (1.24) | 3.45 | 1.35 |
| p | strong | 125 | 0.809 | 0.72 | - | 5.41 | 2.62 |

## Notes

- p: score 0.782, 196/200 kicked, 0 fell; worst sector back (0.753).
