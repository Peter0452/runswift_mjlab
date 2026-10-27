# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_01-18-00_e3_drill_stand/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.794** |
| Kicked / fell | 198 / 0 |
| Kicks within 15° | 174 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.03 ± 1.54 (1.66) |
| Direction error [°] | 13.35 ± 28.16 (4.97) |
| Avg ball speed [m/s] | 2.16 ± 0.56 (2.28) |
| Peak ball speed [m/s] | 4.67 ± 1.34 (5.13) |
| Distance [m] | 1.93 ± 0.74 (1.99) |
| Path length [m] | 1.94 ± 0.74 (2.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.816 | 50/50 | 0 | 44 | 1.68 ± 1.93 (1.32) | 8.81 ± 12.78 (4.71) | 2.13 ± 0.59 (2.26) | 4.66 ± 1.43 (5.00) | 1.91 ± 0.78 (1.95) |
| left | p | 0.815 | 50/50 | 0 | 42 | 1.86 ± 1.30 (1.63) | 15.67 ± 32.60 (4.34) | 2.10 ± 0.62 (2.26) | 4.54 ± 1.45 (5.09) | 1.88 ± 0.79 (1.94) |
| back | p | 0.740 | 49/50 | 0 | 44 | 2.87 ± 1.71 (2.56) | 19.25 ± 39.42 (6.10) | 2.25 ± 0.52 (2.37) | 4.88 ± 1.22 (5.41) | 2.05 ± 0.70 (2.25) |
| right | p | 0.805 | 49/50 | 0 | 44 | 1.71 ± 0.38 (1.72) | 9.72 ± 18.02 (4.16) | 2.16 ± 0.50 (2.21) | 4.63 ± 1.21 (4.60) | 1.90 ± 0.67 (1.85) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.791 | 99/100 | 0 | 86 | 1.96 ± 1.28 (1.64) | 14.19 ± 28.28 (4.93) | 2.14 ± 0.57 (2.31) | 4.65 ± 1.37 (5.16) | 1.91 ± 0.74 (2.03) |
| right | p | 0.796 | 99/100 | 0 | 88 | 2.09 ± 1.76 (1.72) | 12.51 ± 28.02 (5.08) | 2.18 ± 0.56 (2.27) | 4.70 ± 1.31 (5.11) | 1.96 ± 0.74 (1.93) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.826 | 25/25 | 0 | 22 | 1.30 ± 0.32 (1.30) | 9.76 ± 15.26 (4.69) | 2.10 ± 0.60 (2.28) | 4.57 ± 1.46 (4.94) | 1.86 ± 0.77 (1.98) |
| forward/right | p | 0.805 | 25/25 | 0 | 22 | 2.06 ± 2.65 (1.38) | 7.87 ± 9.60 (4.72) | 2.15 ± 0.58 (2.24) | 4.75 ± 1.40 (5.11) | 1.95 ± 0.79 (1.93) |
| left/left | p | 0.837 | 25/25 | 0 | 22 | 2.04 ± 1.75 (1.60) | 6.70 ± 7.55 (3.78) | 2.27 ± 0.46 (2.32) | 4.94 ± 1.09 (5.26) | 2.10 ± 0.65 (2.16) |
| left/right | p | 0.793 | 25/25 | 0 | 20 | 1.69 ± 0.50 (1.78) | 24.63 ± 43.68 (4.85) | 1.93 ± 0.71 (2.19) | 4.13 ± 1.64 (4.32) | 1.66 ± 0.85 (1.77) |
| back/left | p | 0.736 | 25/25 | 0 | 21 | 2.70 ± 1.46 (2.52) | 26.51 ± 45.60 (7.00) | 2.11 ± 0.62 (2.32) | 4.61 ± 1.46 (5.41) | 1.90 ± 0.79 (2.12) |
| back/right | p | 0.743 | 24/25 | 0 | 23 | 3.05 ± 1.92 (2.56) | 11.69 ± 29.92 (6.05) | 2.39 ± 0.34 (2.43) | 5.16 ± 0.83 (5.40) | 2.21 ± 0.54 (2.32) |
| right/left | p | 0.766 | 24/25 | 0 | 21 | 1.81 ± 0.39 (1.94) | 13.79 ± 24.37 (5.07) | 2.07 ± 0.58 (2.19) | 4.45 ± 1.38 (4.53) | 1.79 ± 0.72 (1.75) |
| right/right | p | 0.844 | 25/25 | 0 | 23 | 1.61 ± 0.35 (1.54) | 5.82 ± 5.91 (3.80) | 2.25 ± 0.40 (2.24) | 4.79 ± 0.99 (5.12) | 2.01 ± 0.60 (1.92) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.818 | 14.1 | 5.02 | 2.12 |
| p | normal | 0.769 | 12.6 | 4.33 | 1.75 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.712 | 0.09 | 2.55 ± 0.92 (2.36) | 3.95 | 1.51 |
| p | medium | 20 | 0.870 | 0.70 | 1.29 ± 0.15 (1.32) | 4.14 | 1.63 |
| p | strong | 126 | 0.816 | 0.68 | - | 5.07 | 2.16 |

## Notes

- p: score 0.794, 198/200 kicked, 0 fell; worst sector back (0.740).
