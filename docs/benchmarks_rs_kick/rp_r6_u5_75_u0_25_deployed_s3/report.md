# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 3 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/r6_u5_75_u0_25.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.783** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 173 |
| Weak kicks (< 0.3 m) | 18 |
| Time to kick [s] | 2.15 ± 1.78 (1.84) |
| Direction error [°] | 15.52 ± 32.67 (5.13) |
| Avg ball speed [m/s] | 2.19 ± 0.71 (2.36) |
| Peak ball speed [m/s] | 4.69 ± 1.63 (5.18) |
| Distance [m] | 2.09 ± 0.93 (2.16) |
| Path length [m] | 2.09 ± 0.93 (2.17) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.808 | 49/50 | 0 | 44 | 1.53 ± 1.52 (1.30) | 8.77 ± 14.99 (4.53) | 2.16 ± 0.63 (2.25) | 4.65 ± 1.49 (4.96) | 2.02 ± 0.84 (1.98) |
| left | p | 0.825 | 50/50 | 0 | 44 | 1.85 ± 0.83 (1.78) | 13.37 ± 28.44 (3.54) | 2.25 ± 0.68 (2.44) | 4.86 ± 1.57 (5.45) | 2.18 ± 0.92 (2.49) |
| back | p | 0.747 | 50/50 | 0 | 44 | 2.98 ± 2.05 (2.61) | 18.35 ± 38.23 (5.70) | 2.32 ± 0.71 (2.47) | 4.87 ± 1.60 (5.50) | 2.25 ± 0.94 (2.35) |
| right | p | 0.754 | 49/50 | 0 | 41 | 2.23 ± 2.08 (1.88) | 21.58 ± 40.95 (6.25) | 2.04 ± 0.80 (2.30) | 4.35 ± 1.81 (4.57) | 1.89 ± 0.96 (1.94) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.810 | 100/100 | 0 | 89 | 1.96 ± 1.12 (1.80) | 13.83 ± 31.76 (4.69) | 2.22 ± 0.69 (2.40) | 4.75 ± 1.59 (5.31) | 2.12 ± 0.91 (2.28) |
| right | p | 0.757 | 98/100 | 0 | 84 | 2.34 ± 2.25 (1.86) | 17.25 ± 33.49 (5.88) | 2.16 ± 0.74 (2.34) | 4.62 ± 1.68 (5.04) | 2.05 ± 0.94 (2.10) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.826 | 25/25 | 0 | 23 | 1.39 ± 0.65 (1.30) | 8.77 ± 14.27 (5.93) | 2.09 ± 0.64 (2.23) | 4.52 ± 1.52 (4.96) | 1.92 ± 0.86 (1.98) |
| forward/right | p | 0.790 | 24/25 | 0 | 21 | 1.67 ± 2.06 (1.30) | 8.77 ± 15.71 (3.21) | 2.24 ± 0.62 (2.33) | 4.79 ± 1.45 (5.22) | 2.11 ± 0.81 (2.25) |
| left/left | p | 0.825 | 25/25 | 0 | 22 | 1.81 ± 0.98 (1.74) | 9.37 ± 15.91 (3.53) | 2.29 ± 0.65 (2.55) | 4.95 ± 1.56 (5.75) | 2.23 ± 0.92 (2.63) |
| left/right | p | 0.825 | 25/25 | 0 | 22 | 1.88 ± 0.65 (1.90) | 17.38 ± 36.51 (3.55) | 2.21 ± 0.70 (2.38) | 4.77 ± 1.57 (5.37) | 2.13 ± 0.92 (2.22) |
| back/left | p | 0.803 | 25/25 | 0 | 23 | 2.56 ± 0.51 (2.58) | 10.47 ± 27.94 (3.49) | 2.40 ± 0.65 (2.53) | 5.05 ± 1.47 (5.62) | 2.37 ± 0.88 (2.47) |
| back/right | p | 0.692 | 25/25 | 0 | 21 | 3.39 ± 2.79 (2.62) | 26.22 ± 44.94 (7.78) | 2.23 ± 0.76 (2.34) | 4.68 ± 1.70 (4.61) | 2.13 ± 0.98 (2.03) |
| right/left | p | 0.784 | 25/25 | 0 | 21 | 2.07 ± 1.63 (1.86) | 26.69 ± 50.76 (5.30) | 2.10 ± 0.76 (2.30) | 4.46 ± 1.70 (4.57) | 1.96 ± 0.92 (2.00) |
| right/right | p | 0.723 | 24/25 | 0 | 20 | 2.39 ± 2.45 (1.89) | 16.26 ± 26.15 (6.28) | 1.96 ± 0.83 (2.25) | 4.24 ± 1.90 (4.52) | 1.83 ± 0.99 (1.90) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.831 | 10.9 | 5.33 | 2.47 |
| p | normal | 0.736 | 20.0 | 4.06 | 1.70 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.694 | 0.08 | 2.43 ± 1.11 (2.48) | 3.79 | 1.53 |
| p | medium | 18 | 0.824 | 0.63 | 1.17 ± 0.37 (1.30) | 3.78 | 1.49 |
| p | strong | 124 | 0.819 | 0.70 | - | 5.25 | 2.44 |

## Notes

- p: score 0.783, 198/200 kicked, 0 fell; worst sector back (0.747).
