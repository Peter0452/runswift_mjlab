# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 2 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s6_ctl7_30_n7_70.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.779** |
| Kicked / fell | 197 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 19 |
| Time to kick [s] | 2.09 ± 1.74 (1.78) |
| Direction error [°] | 18.09 ± 36.32 (5.93) |
| Avg ball speed [m/s] | 2.22 ± 0.78 (2.42) |
| Peak ball speed [m/s] | 4.73 ± 1.75 (5.40) |
| Distance [m] | 2.18 ± 1.02 (2.42) |
| Path length [m] | 2.19 ± 1.02 (2.44) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 45 | 1.88 ± 2.49 (1.28) | 10.57 ± 20.60 (4.77) | 2.22 ± 0.72 (2.32) | 4.75 ± 1.64 (5.26) | 2.14 ± 0.92 (2.27) |
| left | p | 0.778 | 48/50 | 0 | 39 | 1.96 ± 1.43 (1.83) | 13.69 ± 23.48 (5.01) | 2.27 ± 0.76 (2.53) | 4.84 ± 1.69 (5.68) | 2.26 ± 1.02 (2.48) |
| back | p | 0.746 | 50/50 | 0 | 43 | 2.80 ± 1.61 (2.52) | 24.73 ± 48.23 (6.48) | 2.29 ± 0.80 (2.48) | 4.82 ± 1.75 (5.64) | 2.27 ± 1.02 (2.65) |
| right | p | 0.787 | 49/50 | 0 | 40 | 1.71 ± 0.71 (1.76) | 23.31 ± 42.50 (6.59) | 2.12 ± 0.84 (2.30) | 4.52 ± 1.88 (4.88) | 2.05 ± 1.09 (1.95) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.788 | 99/100 | 0 | 83 | 2.00 ± 1.54 (1.76) | 20.81 ± 39.94 (5.84) | 2.21 ± 0.82 (2.46) | 4.75 ± 1.83 (5.62) | 2.21 ± 1.05 (2.56) |
| right | p | 0.770 | 98/100 | 0 | 84 | 2.18 ± 1.92 (1.82) | 15.34 ± 32.01 (5.93) | 2.24 ± 0.74 (2.30) | 4.71 ± 1.66 (4.47) | 2.15 ± 0.98 (1.98) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.810 | 25/25 | 0 | 23 | 1.69 ± 2.06 (1.34) | 12.12 ± 25.88 (4.62) | 2.24 ± 0.70 (2.33) | 4.79 ± 1.60 (5.40) | 2.19 ± 0.89 (2.45) |
| forward/right | p | 0.798 | 25/25 | 0 | 22 | 2.06 ± 2.84 (1.24) | 9.02 ± 13.19 (4.92) | 2.21 ± 0.74 (2.30) | 4.70 ± 1.67 (5.13) | 2.09 ± 0.95 (2.21) |
| left/left | p | 0.774 | 24/25 | 0 | 20 | 2.13 ± 1.95 (1.69) | 11.92 ± 18.65 (4.38) | 2.24 ± 0.75 (2.56) | 4.86 ± 1.68 (5.72) | 2.25 ± 0.96 (2.57) |
| left/right | p | 0.781 | 24/25 | 0 | 19 | 1.80 ± 0.46 (1.88) | 15.47 ± 27.36 (5.97) | 2.30 ± 0.76 (2.41) | 4.83 ± 1.71 (4.94) | 2.27 ± 1.07 (2.20) |
| back/left | p | 0.772 | 25/25 | 0 | 21 | 2.37 ± 0.65 (2.52) | 24.65 ± 44.01 (6.29) | 2.33 ± 0.85 (2.56) | 4.94 ± 1.82 (5.77) | 2.37 ± 1.09 (2.67) |
| back/right | p | 0.720 | 25/25 | 0 | 22 | 3.23 ± 2.09 (2.52) | 24.80 ± 52.12 (6.68) | 2.25 ± 0.75 (2.42) | 4.71 ± 1.67 (4.44) | 2.17 ± 0.94 (2.01) |
| right/left | p | 0.794 | 25/25 | 0 | 19 | 1.84 ± 0.89 (1.80) | 34.21 ± 55.05 (6.05) | 2.05 ± 0.95 (2.44) | 4.43 ± 2.12 (5.38) | 2.02 ± 1.20 (2.22) |
| right/right | p | 0.780 | 24/25 | 0 | 21 | 1.58 ± 0.41 (1.63) | 11.96 ± 16.72 (6.91) | 2.19 ± 0.70 (2.21) | 4.60 ± 1.60 (4.35) | 2.09 ± 0.97 (1.91) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.807 | 18.1 | 5.31 | 2.56 |
| p | normal | 0.750 | 18.1 | 4.15 | 1.80 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 60 | 0.718 | 0.16 | 2.22 ± 0.99 (2.08) | 3.72 | 1.51 |
| p | medium | 15 | 0.812 | 0.61 | 1.16 ± 0.41 (1.27) | 3.74 | 1.49 |
| p | strong | 125 | 0.804 | 0.71 | - | 5.35 | 2.60 |

## Notes

- p: score 0.779, 197/200 kicked, 0 fell; worst sector back (0.746).
