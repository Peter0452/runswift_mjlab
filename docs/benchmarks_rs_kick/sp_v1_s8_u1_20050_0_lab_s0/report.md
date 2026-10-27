# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/sp_soups/v1_s8_u1_20050.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.855** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 197 |
| Weak kicks (< 0.3 m) | 2 |
| Time to kick [s] | 1.60 ± 0.53 (1.52) |
| Direction error [°] | 4.77 ± 3.25 (4.15) |
| Avg ball speed [m/s] | 1.64 ± 0.39 (1.72) |
| Peak ball speed [m/s] | 3.83 ± 0.91 (3.96) |
| Distance [m] | 1.32 ± 0.52 (1.36) |
| Path length [m] | 1.33 ± 0.52 (1.37) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.854 | 50/50 | 0 | 49 | 1.05 ± 0.23 (1.08) | 4.46 ± 2.98 (3.91) | 1.36 ± 0.37 (1.27) | 3.19 ± 0.86 (2.90) | 0.96 ± 0.45 (0.76) |
| left | p | 0.872 | 50/50 | 0 | 50 | 1.53 ± 0.34 (1.54) | 4.70 ± 3.01 (4.58) | 1.72 ± 0.39 (1.82) | 4.03 ± 0.86 (4.38) | 1.45 ± 0.52 (1.58) |
| back | p | 0.848 | 50/50 | 0 | 49 | 2.28 ± 0.26 (2.25) | 4.32 ± 3.47 (3.34) | 1.83 ± 0.31 (1.87) | 4.30 ± 0.74 (4.56) | 1.60 ± 0.46 (1.66) |
| right | p | 0.844 | 50/50 | 0 | 49 | 1.53 ± 0.35 (1.50) | 5.59 ± 3.36 (5.36) | 1.64 ± 0.32 (1.70) | 3.82 ± 0.76 (3.96) | 1.29 ± 0.41 (1.34) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.853 | 100/100 | 0 | 99 | 1.61 ± 0.54 (1.54) | 4.82 ± 3.06 (4.27) | 1.64 ± 0.40 (1.74) | 3.83 ± 0.91 (4.01) | 1.34 ± 0.54 (1.42) |
| right | p | 0.856 | 100/100 | 0 | 98 | 1.60 ± 0.53 (1.50) | 4.72 ± 3.42 (3.79) | 1.63 ± 0.38 (1.70) | 3.84 ± 0.91 (3.92) | 1.31 ± 0.50 (1.29) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.852 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 4.46 ± 2.60 (3.93) | 1.36 ± 0.35 (1.25) | 3.19 ± 0.79 (2.84) | 0.97 ± 0.44 (0.75) |
| forward/right | p | 0.857 | 25/25 | 0 | 24 | 1.06 ± 0.24 (1.08) | 4.47 ± 3.31 (3.21) | 1.35 ± 0.39 (1.29) | 3.19 ± 0.93 (3.01) | 0.94 ± 0.46 (0.76) |
| left/left | p | 0.865 | 25/25 | 0 | 25 | 1.44 ± 0.34 (1.52) | 5.00 ± 3.08 (4.80) | 1.67 ± 0.42 (1.80) | 3.86 ± 0.92 (4.31) | 1.37 ± 0.57 (1.57) |
| left/right | p | 0.879 | 25/25 | 0 | 25 | 1.63 ± 0.31 (1.62) | 4.39 ± 2.90 (3.96) | 1.77 ± 0.35 (1.88) | 4.20 ± 0.77 (4.59) | 1.52 ± 0.46 (1.58) |
| back/left | p | 0.851 | 25/25 | 0 | 25 | 2.30 ± 0.25 (2.24) | 3.90 ± 2.48 (3.48) | 1.86 ± 0.32 (1.87) | 4.32 ± 0.74 (4.55) | 1.64 ± 0.48 (1.79) |
| back/right | p | 0.846 | 25/25 | 0 | 24 | 2.27 ± 0.27 (2.26) | 4.75 ± 4.19 (3.25) | 1.81 ± 0.28 (1.87) | 4.27 ± 0.73 (4.62) | 1.56 ± 0.42 (1.59) |
| right/left | p | 0.843 | 25/25 | 0 | 24 | 1.64 ± 0.33 (1.60) | 5.90 ± 3.59 (5.18) | 1.68 ± 0.33 (1.75) | 3.94 ± 0.78 (4.10) | 1.36 ± 0.45 (1.41) |
| right/right | p | 0.844 | 25/25 | 0 | 25 | 1.43 ± 0.34 (1.44) | 5.28 ± 3.07 (5.82) | 1.60 ± 0.30 (1.61) | 3.69 ± 0.72 (3.71) | 1.22 ± 0.37 (1.24) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.860 | 5.0 | 4.31 | 1.58 |
| p | normal | 0.850 | 4.6 | 3.36 | 1.07 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.824 | 0.36 | 1.85 ± 0.63 (1.69) | 2.94 | 0.84 |
| p | medium | 16 | 0.911 | 0.84 | 0.91 ± 0.18 (0.92) | 2.96 | 0.86 |
| p | strong | 126 | 0.862 | 0.58 | - | 4.35 | 1.61 |

## Notes

- p: score 0.855, 200/200 kicked, 0 fell; worst sector right (0.844).
