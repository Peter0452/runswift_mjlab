# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception camera, delay typical, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `logs/rsl_rl/k1_kick_stage3_amp/tonight_soups/s5_ctl7_t4.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.767** |
| Kicked / fell | 195 / 0 |
| Kicks within 15° | 164 |
| Weak kicks (< 0.3 m) | 15 |
| Time to kick [s] | 2.05 ± 1.68 (1.72) |
| Direction error [°] | 19.20 ± 37.80 (5.70) |
| Avg ball speed [m/s] | 2.07 ± 0.67 (2.27) |
| Peak ball speed [m/s] | 4.56 ± 1.59 (4.93) |
| Distance [m] | 1.81 ± 0.84 (1.90) |
| Path length [m] | 1.82 ± 0.84 (1.91) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.804 | 50/50 | 0 | 44 | 1.86 ± 2.17 (1.31) | 7.13 ± 8.73 (4.32) | 2.04 ± 0.69 (2.09) | 4.48 ± 1.66 (4.52) | 1.76 ± 0.88 (1.70) |
| left | p | 0.795 | 49/50 | 0 | 40 | 1.80 ± 1.28 (1.74) | 20.34 ± 35.71 (4.99) | 2.07 ± 0.65 (2.27) | 4.63 ± 1.59 (5.16) | 1.83 ± 0.84 (1.92) |
| back | p | 0.725 | 50/50 | 0 | 41 | 2.85 ± 1.90 (2.49) | 31.38 ± 53.93 (7.80) | 2.06 ± 0.73 (2.34) | 4.51 ± 1.68 (5.06) | 1.83 ± 0.85 (2.00) |
| right | p | 0.746 | 46/50 | 0 | 39 | 1.66 ± 0.49 (1.70) | 17.88 ± 33.64 (5.48) | 2.12 ± 0.58 (2.27) | 4.64 ± 1.40 (4.89) | 1.84 ± 0.76 (1.82) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.797 | 99/100 | 0 | 86 | 1.90 ± 1.32 (1.72) | 18.03 ± 38.08 (5.59) | 2.14 ± 0.59 (2.28) | 4.72 ± 1.41 (4.94) | 1.88 ± 0.77 (1.92) |
| right | p | 0.738 | 96/100 | 0 | 78 | 2.21 ± 1.97 (1.71) | 20.41 ± 37.46 (5.81) | 2.00 ± 0.73 (2.26) | 4.41 ± 1.74 (4.83) | 1.75 ± 0.90 (1.90) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.830 | 25/25 | 0 | 23 | 1.61 ± 1.73 (1.30) | 6.17 ± 9.17 (3.71) | 2.14 ± 0.64 (2.33) | 4.70 ± 1.53 (4.89) | 1.86 ± 0.80 (1.89) |
| forward/right | p | 0.778 | 25/25 | 0 | 21 | 2.10 ± 2.52 (1.34) | 8.09 ± 8.16 (4.89) | 1.94 ± 0.73 (2.03) | 4.25 ± 1.76 (4.10) | 1.66 ± 0.94 (1.59) |
| left/left | p | 0.848 | 25/25 | 0 | 22 | 1.56 ± 0.40 (1.66) | 12.44 ± 22.22 (5.06) | 2.20 ± 0.48 (2.28) | 4.97 ± 1.21 (5.37) | 1.99 ± 0.68 (2.10) |
| left/right | p | 0.742 | 24/25 | 0 | 18 | 2.05 ± 1.75 (1.78) | 28.58 ± 44.22 (4.97) | 1.92 ± 0.76 (2.24) | 4.27 ± 1.83 (4.91) | 1.66 ± 0.95 (1.90) |
| back/left | p | 0.735 | 25/25 | 0 | 21 | 2.65 ± 1.65 (2.44) | 32.13 ± 56.02 (8.18) | 2.13 ± 0.60 (2.31) | 4.66 ± 1.39 (4.94) | 1.88 ± 0.80 (1.93) |
| back/right | p | 0.714 | 25/25 | 0 | 20 | 3.04 ± 2.10 (2.56) | 30.63 ± 51.75 (7.29) | 1.99 ± 0.84 (2.38) | 4.37 ± 1.91 (5.16) | 1.78 ± 0.90 (2.03) |
| right/left | p | 0.775 | 24/25 | 0 | 20 | 1.77 ± 0.51 (1.75) | 21.53 ± 41.39 (2.93) | 2.07 ± 0.61 (2.23) | 4.52 ± 1.47 (4.81) | 1.77 ± 0.77 (1.82) |
| right/right | p | 0.717 | 22/25 | 0 | 19 | 1.55 ± 0.43 (1.51) | 13.88 ± 21.59 (5.91) | 2.17 ± 0.53 (2.27) | 4.77 ± 1.31 (5.10) | 1.91 ± 0.75 (1.96) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.804 | 17.1 | 5.19 | 2.13 |
| p | normal | 0.731 | 21.3 | 3.94 | 1.49 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.692 | 0.16 | 2.31 ± 1.05 (2.20) | 3.65 | 1.34 |
| p | medium | 16 | 0.812 | 0.63 | 1.22 ± 0.38 (1.28) | 3.93 | 1.53 |
| p | strong | 126 | 0.797 | 0.68 | - | 5.07 | 2.07 |

## Notes

- p: score 0.767, 195/200 kicked, 0 fell; worst sector back (0.725).
