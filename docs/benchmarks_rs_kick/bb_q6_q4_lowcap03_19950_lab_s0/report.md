# Kick benchmark (runswift spec v2): results

Our kick loop on `Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1`: 200 trials, seed 0 (4 kick-direction sectors x 2 ball sides x 25), ball in front (+-30°, 0.35-1.0 m), standing start, benchmark ball, flat ground, nominal robot. Deployed action path (joint-target and torque clip, scripted head), perception perfect, delay zero, caps (2.0, 1.5, 1.5), ball bhuman, kick rule booster, ball damping on. Trials and score as `bench_bhuman_kick_v2.py` (k1/eval/rs_kick.py). Mean ± std (median).

Policies: **p** = `/home/peter/Desktop/Project/RL/runswift_mjlab/logs/rsl_rl/k1_kick_stage3_amp/2026-10-28_04-13-12_q6_q4_lowcap03/model_19950.pt`.

## Overall

| Metric | p |
|---|---|
| **Score** | **0.811** |
| Kicked / fell | 200 / 0 |
| Kicks within 15° | 184 |
| Weak kicks (< 0.3 m) | 0 |
| Time to kick [s] | 1.56 ± 0.53 (1.47) |
| Direction error [°] | 8.04 ± 4.68 (7.79) |
| Avg ball speed [m/s] | 1.87 ± 0.35 (1.84) |
| Peak ball speed [m/s] | 3.84 ± 0.73 (3.74) |
| Distance [m] | 1.42 ± 0.46 (1.35) |
| Path length [m] | 1.42 ± 0.46 (1.36) |

## Per kick-direction sector

| Sector | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward | p | 0.813 | 50/50 | 0 | 48 | 1.04 ± 0.22 (1.08) | 6.87 ± 4.64 (5.74) | 1.58 ± 0.30 (1.57) | 3.28 ± 0.58 (3.24) | 1.04 ± 0.33 (1.01) |
| left | p | 0.822 | 50/50 | 0 | 47 | 1.49 ± 0.35 (1.52) | 8.47 ± 4.65 (8.15) | 1.91 ± 0.34 (1.89) | 3.93 ± 0.69 (3.85) | 1.47 ± 0.43 (1.38) |
| back | p | 0.804 | 50/50 | 0 | 47 | 2.24 ± 0.29 (2.21) | 8.04 ± 3.88 (8.00) | 2.00 ± 0.27 (1.94) | 4.15 ± 0.63 (4.04) | 1.63 ± 0.44 (1.49) |
| right | p | 0.805 | 50/50 | 0 | 42 | 1.47 ± 0.33 (1.45) | 8.76 ± 5.22 (8.63) | 1.96 ± 0.30 (1.94) | 4.03 ± 0.67 (4.00) | 1.53 ± 0.40 (1.47) |

## Per ball side

| Ball side | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| left | p | 0.811 | 100/100 | 0 | 96 | 1.57 ± 0.53 (1.49) | 7.88 ± 4.17 (7.54) | 1.86 ± 0.32 (1.81) | 3.83 ± 0.69 (3.69) | 1.40 ± 0.44 (1.34) |
| right | p | 0.811 | 100/100 | 0 | 88 | 1.55 ± 0.52 (1.47) | 8.19 ± 5.13 (7.92) | 1.87 ± 0.37 (1.85) | 3.86 ± 0.77 (3.75) | 1.43 ± 0.48 (1.36) |

## Per cell (sector / ball side)

| Cell | Policy | Score | Kicked | Fell | Within 15° | Time [s] | Dir err [°] | Avg speed | Peak speed | Distance [m] |
|---|---|---|---|---|---|---|---|---|---|---|
| forward/left | p | 0.809 | 25/25 | 0 | 25 | 1.05 ± 0.22 (1.08) | 7.16 ± 3.63 (6.13) | 1.64 ± 0.28 (1.66) | 3.39 ± 0.54 (3.31) | 1.11 ± 0.32 (1.05) |
| forward/right | p | 0.817 | 25/25 | 0 | 23 | 1.04 ± 0.23 (1.08) | 6.58 ± 5.45 (4.52) | 1.53 ± 0.31 (1.48) | 3.16 ± 0.60 (3.14) | 0.98 ± 0.33 (0.93) |
| left/left | p | 0.802 | 25/25 | 0 | 24 | 1.40 ± 0.35 (1.46) | 9.57 ± 4.39 (9.62) | 1.81 ± 0.31 (1.73) | 3.71 ± 0.62 (3.61) | 1.31 ± 0.35 (1.28) |
| left/right | p | 0.841 | 25/25 | 0 | 23 | 1.58 ± 0.33 (1.56) | 7.36 ± 4.64 (7.63) | 2.02 ± 0.34 (1.93) | 4.15 ± 0.69 (3.93) | 1.62 ± 0.45 (1.48) |
| back/left | p | 0.806 | 25/25 | 0 | 24 | 2.26 ± 0.29 (2.22) | 7.64 ± 3.22 (7.58) | 1.96 ± 0.26 (1.90) | 4.04 ± 0.63 (4.00) | 1.57 ± 0.46 (1.48) |
| back/right | p | 0.802 | 25/25 | 0 | 23 | 2.22 ± 0.29 (2.20) | 8.45 ± 4.40 (9.64) | 2.05 ± 0.28 (1.98) | 4.25 ± 0.62 (4.11) | 1.69 ± 0.41 (1.65) |
| right/left | p | 0.826 | 25/25 | 0 | 23 | 1.55 ± 0.30 (1.54) | 7.16 ± 4.79 (5.47) | 2.04 ± 0.29 (2.12) | 4.18 ± 0.67 (4.21) | 1.63 ± 0.40 (1.57) |
| right/right | p | 0.785 | 25/25 | 0 | 19 | 1.38 ± 0.32 (1.40) | 10.36 ± 5.15 (9.04) | 1.89 ± 0.29 (1.81) | 3.87 ± 0.64 (3.70) | 1.43 ± 0.38 (1.36) |

## Strong (20 m) vs normal (0.5-20 m, log-uniform) kicks

| Policy | Kick type | Score | Dir err [°] | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|
| p | strong | 0.827 | 7.7 | 4.05 | 1.53 |
| p | normal | 0.795 | 8.4 | 3.64 | 1.30 |

## Power by kick class

Small < 4 m and medium 4-8 m: power = 1 - |peak / need - 1|, need = sqrt(2 x 0.95 x range). Strong >= 8 m: power = min(1, peak / 7.5 m/s).

| Policy | Class | Trials | Score | Power | Peak / need | Peak speed [m/s] | Distance [m] |
|---|---|---|---|---|---|---|---|
| p | small | 58 | 0.757 | 0.21 | 2.10 ± 0.66 (1.98) | 3.35 | 1.12 |
| p | medium | 16 | 0.865 | 0.86 | 1.00 ± 0.17 (1.04) | 3.25 | 1.09 |
| p | strong | 126 | 0.829 | 0.55 | - | 4.15 | 1.60 |

## Notes

- p: score 0.811, 200/200 kicked, 0 fell; worst sector back (0.804).
