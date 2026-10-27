# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-27_09-08-39_u2_aim_sigma02/model_19650.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.778** |
| Kicked / fell | 193 / 0 |
| Kicks within 15° | 165 |
| Weak kicks (< 0.3 m) | 9 |
| Time to kick [s] | 1.84 ± 0.96 (1.72) |
| Direction error [°] | 16.89 ± 34.71 (5.14) |
| Avg ball speed [m/s] | 2.09 ± 0.60 (2.28) |
| Peak ball speed [m/s] | 4.71 ± 1.46 (5.26) |
| Distance [m] | 1.85 ± 0.76 (1.99) |
| Path length [m] | 1.85 ± 0.76 (2.00) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.773 | 48/50 | 0 | 40 | 1.58 ± 1.53 (1.36) | 8.57 ± 11.33 (3.79) | 2.05 ± 0.63 (2.22) | 4.53 ± 1.52 (4.49) | 1.77 ± 0.82 (1.82) |
| left | p | 0.798 | 48/50 | 0 | 41 | 1.64 ± 0.50 (1.75) | 18.66 ± 35.09 (4.88) | 2.07 ± 0.62 (2.31) | 4.77 ± 1.55 (5.41) | 1.86 ± 0.78 (2.10) |
| back | p | 0.750 | 49/50 | 0 | 43 | 2.44 ± 0.66 (2.52) | 23.82 ± 47.45 (7.15) | 2.14 ± 0.58 (2.33) | 4.84 ± 1.40 (5.31) | 1.92 ± 0.71 (2.04) |
| right | p | 0.793 | 48/50 | 0 | 41 | 1.67 ± 0.45 (1.71) | 16.36 ± 32.64 (4.56) | 2.10 ± 0.55 (2.26) | 4.72 ± 1.35 (5.32) | 1.83 ± 0.72 (1.89) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.808 | 99/100 | 0 | 86 | 1.85 ± 1.13 (1.74) | 16.72 ± 35.65 (4.28) | 2.15 ± 0.53 (2.30) | 4.85 ± 1.31 (5.28) | 1.91 ± 0.72 (2.08) |
| right | p | 0.749 | 94/100 | 0 | 79 | 1.82 ± 0.75 (1.70) | 17.07 ± 33.69 (5.58) | 2.03 ± 0.66 (2.28) | 4.57 ± 1.59 (5.18) | 1.78 ± 0.80 (1.96) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.822 | 25/25 | 0 | 22 | 1.68 ± 1.95 (1.38) | 7.69 ± 12.28 (2.84) | 2.19 ± 0.47 (2.32) | 4.91 ± 1.21 (5.25) | 1.93 ± 0.68 (2.08) |
| forward/right | p | 0.723 | 23/25 | 0 | 18 | 1.48 ± 0.85 (1.34) | 9.53 ± 10.12 (5.74) | 1.89 ± 0.74 (2.03) | 4.11 ± 1.70 (4.31) | 1.58 ± 0.91 (1.66) |
| left/left | p | 0.849 | 25/25 | 0 | 22 | 1.58 ± 0.45 (1.74) | 13.58 ± 24.10 (5.11) | 2.14 ± 0.55 (2.33) | 4.94 ± 1.40 (5.37) | 1.94 ± 0.74 (2.16) |
| left/right | p | 0.746 | 23/25 | 0 | 19 | 1.71 ± 0.54 (1.76) | 24.17 ± 43.36 (4.64) | 2.01 ± 0.68 (2.28) | 4.57 ± 1.67 (5.44) | 1.76 ± 0.82 (2.04) |
| back/left | p | 0.741 | 24/25 | 0 | 21 | 2.39 ± 0.68 (2.50) | 25.78 ± 51.30 (7.18) | 2.15 ± 0.48 (2.28) | 4.88 ± 1.17 (5.28) | 1.91 ± 0.71 (1.98) |
| back/right | p | 0.759 | 25/25 | 0 | 22 | 2.49 ± 0.63 (2.60) | 21.94 ± 43.36 (7.15) | 2.12 ± 0.66 (2.34) | 4.81 ± 1.59 (5.51) | 1.93 ± 0.72 (2.08) |
| right/left | p | 0.818 | 25/25 | 0 | 21 | 1.78 ± 0.47 (1.78) | 20.18 ± 39.93 (3.71) | 2.12 ± 0.59 (2.27) | 4.68 ± 1.43 (5.31) | 1.83 ± 0.74 (1.99) |
| right/right | p | 0.767 | 23/25 | 0 | 20 | 1.55 ± 0.40 (1.56) | 12.20 ± 21.38 (5.14) | 2.09 ± 0.50 (2.23) | 4.77 ± 1.27 (5.35) | 1.84 ± 0.69 (1.86) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.806 | 13.7 | 5.40 | 2.18 |
| p | normal | 0.750 | 20.0 | 4.05 | 1.52 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.711 | 0.17 | 2.38 ± 1.09 (2.32) | 3.76 | 1.38 |
| p | medium | 16 | 0.797 | 0.61 | 1.33 ± 0.24 (1.34) | 4.31 | 1.69 |
| p | strong | 126 | 0.807 | 0.70 | - | 5.22 | 2.08 |

## Notes

- p: score 0.778, 193/200 kicked, 0 fell; worst sector back (0.750).
