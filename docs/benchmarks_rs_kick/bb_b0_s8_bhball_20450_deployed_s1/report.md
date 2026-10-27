# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 1 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_17-58-02_b0_s8_bhball/model_20450.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.794** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 163 |
| Weak kicks (< 0.3 m) | 27 |
| Time to kick [s] | 1.94 ± 1.39 (1.63) |
| Direction error [°] | 16.16 ± 30.02 (6.51) |
| Avg ball speed [m/s] | 2.33 ± 0.94 (2.68) |
| Peak ball speed [m/s] | 4.83 ± 2.03 (5.90) |
| Distance [m] | 2.39 ± 1.27 (2.94) |
| Path length [m] | 2.40 ± 1.27 (2.95) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.814 | 50/50 | 0 | 43 | 1.58 ± 1.68 (1.30) | 9.39 ± 13.21 (4.85) | 2.32 ± 0.92 (2.51) | 4.79 ± 1.96 (5.04) | 2.31 ± 1.20 (2.23) |
| left | p | 0.815 | 50/50 | 0 | 40 | 1.84 ± 1.43 (1.61) | 14.08 ± 24.04 (4.97) | 2.33 ± 0.88 (2.59) | 4.85 ± 1.93 (5.73) | 2.38 ± 1.22 (2.87) |
| back | p | 0.738 | 50/50 | 0 | 36 | 2.58 ± 1.41 (2.48) | 28.76 ± 46.69 (9.08) | 2.29 ± 1.09 (2.80) | 4.79 ± 2.36 (6.23) | 2.48 ± 1.45 (3.37) |
| right | p | 0.811 | 50/50 | 0 | 44 | 1.75 ± 0.55 (1.79) | 12.43 ± 21.18 (6.40) | 2.37 ± 0.85 (2.52) | 4.88 ± 1.85 (5.21) | 2.40 ± 1.17 (2.37) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.799 | 100/100 | 0 | 82 | 1.83 ± 1.16 (1.56) | 17.10 ± 32.05 (6.51) | 2.35 ± 0.90 (2.68) | 4.90 ± 1.97 (5.95) | 2.43 ± 1.24 (2.98) |
| right | p | 0.790 | 100/100 | 0 | 81 | 2.05 ± 1.58 (1.73) | 15.23 ± 27.80 (6.43) | 2.31 ± 0.97 (2.63) | 4.76 ± 2.09 (5.71) | 2.35 ± 1.29 (2.60) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.838 | 25/25 | 0 | 22 | 1.21 ± 0.26 (1.26) | 7.42 ± 8.57 (4.59) | 2.37 ± 0.86 (2.64) | 4.93 ± 1.84 (5.89) | 2.39 ± 1.15 (2.95) |
| forward/right | p | 0.789 | 25/25 | 0 | 21 | 1.94 ± 2.30 (1.40) | 11.35 ± 16.36 (5.53) | 2.27 ± 0.97 (2.35) | 4.66 ± 2.06 (4.52) | 2.24 ± 1.24 (1.89) |
| left/left | p | 0.826 | 25/25 | 0 | 21 | 2.01 ± 1.94 (1.56) | 9.24 ± 10.80 (5.25) | 2.42 ± 0.86 (2.72) | 5.11 ± 1.92 (5.98) | 2.59 ± 1.21 (3.06) |
| left/right | p | 0.804 | 25/25 | 0 | 19 | 1.67 ± 0.49 (1.78) | 18.93 ± 31.51 (4.60) | 2.25 ± 0.89 (2.35) | 4.58 ± 1.90 (4.39) | 2.17 ± 1.20 (1.91) |
| back/left | p | 0.751 | 25/25 | 0 | 18 | 2.21 ± 0.73 (2.40) | 34.04 ± 51.82 (9.15) | 2.34 ± 0.94 (2.81) | 4.87 ± 2.07 (6.24) | 2.47 ± 1.34 (3.11) |
| back/right | p | 0.725 | 25/25 | 0 | 18 | 2.95 ± 1.79 (2.50) | 23.47 ± 40.24 (9.04) | 2.25 ± 1.22 (2.80) | 4.71 ± 2.62 (6.21) | 2.48 ± 1.55 (3.38) |
| right/left | p | 0.779 | 25/25 | 0 | 21 | 1.89 ± 0.67 (1.96) | 17.69 ± 28.12 (6.49) | 2.27 ± 0.94 (2.36) | 4.69 ± 2.02 (4.49) | 2.29 ± 1.23 (1.93) |
| right/right | p | 0.844 | 25/25 | 0 | 23 | 1.62 ± 0.35 (1.54) | 7.17 ± 7.16 (6.31) | 2.48 ± 0.73 (2.73) | 5.08 ± 1.64 (6.08) | 2.52 ± 1.10 (3.08) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.828 | 16.9 | 5.60 | 2.95 |
| p | normal | 0.761 | 15.4 | 4.06 | 1.84 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 54 | 0.718 | 0.09 | 2.31 ± 1.20 (2.29) | 3.52 | 1.44 |
| p | medium | 20 | 0.845 | 0.67 | 1.18 ± 0.33 (1.24) | 3.83 | 1.58 |
| p | strong | 126 | 0.819 | 0.74 | - | 5.55 | 2.93 |

## Notes

- p: score 0.794, 200/200 kicked, 0 fell; worst sector back (0.738).
