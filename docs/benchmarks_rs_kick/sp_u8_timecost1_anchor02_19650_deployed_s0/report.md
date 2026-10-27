# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_12-23-01_u8_timecost1_anchor02/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.784** |
| Kicked / fell | 196 / 0 |
| Kicks within 15° | 167 |
| Weak kicks (< 0.3 m) | 10 |
| Time to kick [s] | 2.09 ± 1.77 (1.75) |
| Direction error [°] | 15.84 ± 34.31 (4.53) |
| Avg ball speed [m/s] | 2.16 ± 0.63 (2.30) |
| Peak ball speed [m/s] | 4.66 ± 1.47 (5.27) |
| Distance [m] | 1.96 ± 0.83 (2.06) |
| Path length [m] | 1.96 ± 0.83 (2.07) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.802 | 50/50 | 0 | 42 | 1.88 ± 2.22 (1.36) | 7.55 ± 10.80 (3.86) | 2.10 ± 0.61 (2.15) | 4.51 ± 1.44 (4.33) | 1.84 ± 0.81 (1.75) |
| left | p | 0.808 | 49/50 | 0 | 41 | 1.86 ± 1.44 (1.78) | 17.69 ± 34.98 (3.74) | 2.09 ± 0.69 (2.37) | 4.54 ± 1.61 (5.35) | 1.88 ± 0.85 (2.06) |
| back | p | 0.732 | 48/50 | 0 | 42 | 2.76 ± 1.64 (2.51) | 22.57 ± 48.01 (6.02) | 2.32 ± 0.57 (2.36) | 4.96 ± 1.33 (5.40) | 2.20 ± 0.82 (2.28) |
| right | p | 0.794 | 49/50 | 0 | 42 | 1.88 ± 1.48 (1.74) | 15.86 ± 31.47 (4.63) | 2.14 ± 0.60 (2.32) | 4.62 ± 1.42 (5.24) | 1.91 ± 0.78 (2.06) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.815 | 100/100 | 0 | 87 | 1.93 ± 1.38 (1.71) | 15.74 ± 34.99 (4.19) | 2.21 ± 0.62 (2.33) | 4.76 ± 1.44 (5.35) | 2.03 ± 0.83 (2.21) |
| right | p | 0.753 | 96/100 | 0 | 80 | 2.26 ± 2.09 (1.76) | 15.95 ± 33.58 (4.70) | 2.11 ± 0.63 (2.27) | 4.55 ± 1.49 (4.88) | 1.88 ± 0.82 (1.91) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.835 | 25/25 | 0 | 22 | 1.61 ± 1.69 (1.30) | 6.56 ± 10.59 (3.15) | 2.30 ± 0.53 (2.34) | 4.93 ± 1.26 (5.20) | 2.11 ± 0.78 (2.05) |
| forward/right | p | 0.768 | 25/25 | 0 | 20 | 2.15 ± 2.62 (1.36) | 8.54 ± 10.91 (4.41) | 1.90 ± 0.62 (2.05) | 4.10 ± 1.49 (4.15) | 1.57 ± 0.75 (1.66) |
| left/left | p | 0.848 | 25/25 | 0 | 22 | 1.59 ± 0.40 (1.70) | 12.10 ± 23.49 (3.69) | 2.13 ± 0.67 (2.37) | 4.63 ± 1.56 (5.41) | 1.95 ± 0.79 (2.16) |
| left/right | p | 0.768 | 24/25 | 0 | 19 | 2.13 ± 1.98 (1.91) | 23.52 ± 43.09 (4.35) | 2.05 ± 0.71 (2.28) | 4.45 ± 1.66 (5.07) | 1.81 ± 0.90 (1.99) |
| back/left | p | 0.765 | 25/25 | 0 | 22 | 2.74 ± 1.86 (2.50) | 24.63 ± 50.63 (6.00) | 2.30 ± 0.54 (2.33) | 4.93 ± 1.25 (5.33) | 2.16 ± 0.85 (2.24) |
| back/right | p | 0.699 | 23/25 | 0 | 20 | 2.78 ± 1.37 (2.60) | 20.32 ± 44.88 (6.04) | 2.35 ± 0.61 (2.44) | 5.00 ± 1.41 (5.56) | 2.24 ± 0.79 (2.57) |
| right/left | p | 0.811 | 25/25 | 0 | 21 | 1.78 ± 0.49 (1.80) | 19.66 ± 38.46 (4.90) | 2.12 ± 0.69 (2.32) | 4.56 ± 1.60 (5.43) | 1.90 ± 0.85 (2.11) |
| right/right | p | 0.777 | 24/25 | 0 | 21 | 2.00 ± 2.06 (1.71) | 11.89 ± 21.24 (4.59) | 2.16 ± 0.49 (2.33) | 4.68 ± 1.19 (5.11) | 1.93 ± 0.68 (2.01) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.806 | 12.9 | 5.35 | 2.34 |
| p | normal | 0.762 | 18.7 | 3.99 | 1.59 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.723 | 0.15 | 2.34 ± 1.02 (2.27) | 3.67 | 1.40 |
| p | medium | 16 | 0.841 | 0.70 | 1.26 ± 0.24 (1.30) | 4.08 | 1.63 |
| p | strong | 126 | 0.805 | 0.69 | - | 5.20 | 2.26 |

## Notes

- p: score 0.784, 196/200 kicked, 0 fell; worst sector back (0.732).
