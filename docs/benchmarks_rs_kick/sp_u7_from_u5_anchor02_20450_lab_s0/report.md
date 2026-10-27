# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_11-31-02_u7_from_u5_anchor02/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.861** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 199 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.60 ± 0.55 (1.51) |
| Direction error [°] | 3.90 ± 2.82 (3.40) |
| Avg ball speed [m/s] | 1.64 ± 0.27 (1.66) |
| Peak ball speed [m/s] | 4.45 ± 0.77 (4.63) |
| Distance [m] | 1.71 ± 0.44 (1.74) |
| Path length [m] | 1.71 ± 0.44 (1.74) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.853 | 50/50 | 0 | 49 | 1.04 ± 0.22 (1.06) | 4.13 ± 3.10 (3.44) | 1.47 ± 0.30 (1.37) | 4.04 ± 0.85 (3.84) | 1.44 ± 0.47 (1.29) |
| left | p | 0.870 | 50/50 | 0 | 50 | 1.57 ± 0.45 (1.54) | 4.52 ± 3.01 (3.91) | 1.67 ± 0.24 (1.67) | 4.53 ± 0.70 (4.66) | 1.74 ± 0.39 (1.76) |
| back | p | 0.865 | 50/50 | 0 | 50 | 2.27 ± 0.26 (2.24) | 2.84 ± 1.90 (2.07) | 1.76 ± 0.22 (1.77) | 4.75 ± 0.62 (4.94) | 1.91 ± 0.36 (1.94) |
| right | p | 0.857 | 50/50 | 0 | 50 | 1.52 ± 0.35 (1.47) | 4.11 ± 2.80 (3.80) | 1.67 ± 0.24 (1.68) | 4.47 ± 0.72 (4.60) | 1.73 ± 0.41 (1.73) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.866 | 100/100 | 0 | 100 | 1.60 ± 0.53 (1.55) | 3.74 ± 2.52 (3.43) | 1.66 ± 0.25 (1.69) | 4.50 ± 0.74 (4.64) | 1.73 ± 0.43 (1.78) |
| right | p | 0.857 | 100/100 | 0 | 99 | 1.60 ± 0.56 (1.49) | 4.06 ± 3.07 (3.31) | 1.62 ± 0.29 (1.63) | 4.40 ± 0.79 (4.62) | 1.68 ± 0.45 (1.67) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.858 | 25/25 | 0 | 25 | 1.04 ± 0.22 (1.06) | 3.91 ± 2.94 (3.28) | 1.49 ± 0.25 (1.35) | 4.10 ± 0.77 (3.85) | 1.47 ± 0.46 (1.29) |
| forward/right | p | 0.847 | 25/25 | 0 | 24 | 1.04 ± 0.22 (1.04) | 4.34 ± 3.24 (4.15) | 1.45 ± 0.34 (1.40) | 3.97 ± 0.92 (3.84) | 1.41 ± 0.49 (1.29) |
| left/left | p | 0.880 | 25/25 | 0 | 25 | 1.43 ± 0.33 (1.52) | 4.02 ± 2.33 (3.56) | 1.68 ± 0.24 (1.68) | 4.55 ± 0.73 (4.67) | 1.76 ± 0.41 (1.82) |
| left/right | p | 0.860 | 25/25 | 0 | 25 | 1.71 ± 0.50 (1.60) | 5.02 ± 3.49 (4.50) | 1.66 ± 0.24 (1.66) | 4.50 ± 0.66 (4.66) | 1.72 ± 0.36 (1.72) |
| back/left | p | 0.862 | 25/25 | 0 | 25 | 2.29 ± 0.24 (2.24) | 3.05 ± 2.01 (2.03) | 1.77 ± 0.16 (1.77) | 4.77 ± 0.55 (5.00) | 1.91 ± 0.32 (1.94) |
| back/right | p | 0.869 | 25/25 | 0 | 25 | 2.25 ± 0.27 (2.20) | 2.64 ± 1.77 (2.11) | 1.74 ± 0.27 (1.71) | 4.74 ± 0.68 (4.92) | 1.91 ± 0.39 (1.93) |
| right/left | p | 0.864 | 25/25 | 0 | 25 | 1.63 ± 0.32 (1.58) | 3.99 ± 2.59 (3.91) | 1.71 ± 0.23 (1.71) | 4.57 ± 0.74 (4.73) | 1.79 ± 0.41 (1.85) |
| right/right | p | 0.849 | 25/25 | 0 | 25 | 1.42 ± 0.34 (1.46) | 4.23 ± 2.99 (3.69) | 1.62 ± 0.25 (1.66) | 4.37 ± 0.68 (4.59) | 1.67 ± 0.40 (1.57) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.884 | 4.3 | 4.90 | 1.94 |
| p | normal | 0.839 | 3.5 | 3.99 | 1.47 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.793 | 0.16 | 2.30 ± 0.75 (2.14) | 3.64 | 1.28 |
| p | medium | 16 | 0.925 | 0.83 | 1.11 ± 0.16 (1.15) | 3.60 | 1.29 |
| p | strong | 126 | 0.884 | 0.66 | - | 4.93 | 1.95 |

## Notes

- p: score 0.861, 200/200 kicked, 0 fell; worst sector forward (0.853).
