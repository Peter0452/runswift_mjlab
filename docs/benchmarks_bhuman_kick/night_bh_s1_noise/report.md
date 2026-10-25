# B-Human K1_Ball kick benchmark v2: results

Port env `Mjlab-BHuman-Kick-Booster-K1`, plane, seed 1, 25 trials per cell, observation noise on, robot randomization off, ball rolling friction 0.1. Cells: mean ± std (median).

## Overall

| Metric | pretrained |
|---|---|
| **Priority score** | 0.921 |
| Worst sector | back 0.910 |
| Kicked / fell | 200 / 0 |
| Kicks within 15° of command | 190 |
| Time to kick [s] | 1.51 ± 0.58 (1.48) |
| Direction error [deg] | 6.37 ± 4.25 (5.68) |
| Avg ball speed [m/s] | 1.57 ± 0.85 (1.28) |
| Peak ball speed [m/s] | 3.08 ± 1.68 (2.55) |
| Ball distance [m] | 1.18 ± 0.92 (0.76) |
| Ball path length [m] | 1.18 ± 0.93 (0.76) |

## Per kick-direction sector

### Forward

| Metric | pretrained |
|---|---|
| Score | 0.933 |
| Kicked / fell | 50 / 0 |
| Within 15° | 48 |
| Time to kick [s] | 0.97 ± 0.35 (0.97) |
| Direction error [deg] | 5.78 ± 3.85 (5.47) |
| Avg ball speed [m/s] | 1.53 ± 0.77 (1.27) |
| Peak ball speed [m/s] | 3.05 ± 1.58 (2.49) |
| Ball distance [m] | 1.16 ± 0.88 (0.70) |

### Left

| Metric | pretrained |
|---|---|
| Score | 0.911 |
| Kicked / fell | 50 / 0 |
| Within 15° | 47 |
| Time to kick [s] | 1.50 ± 0.50 (1.41) |
| Direction error [deg] | 7.39 ± 4.52 (6.85) |
| Avg ball speed [m/s] | 1.64 ± 0.89 (1.68) |
| Peak ball speed [m/s] | 3.17 ± 1.72 (3.36) |
| Ball distance [m] | 1.23 ± 0.93 (1.21) |

### Back

| Metric | pretrained |
|---|---|
| Score | 0.910 |
| Kicked / fell | 50 / 0 |
| Within 15° | 48 |
| Time to kick [s] | 2.08 ± 0.34 (2.02) |
| Direction error [deg] | 6.42 ± 3.87 (5.66) |
| Avg ball speed [m/s] | 1.60 ± 0.86 (1.44) |
| Peak ball speed [m/s] | 3.12 ± 1.70 (2.86) |
| Ball distance [m] | 1.21 ± 0.94 (0.90) |

### Right

| Metric | pretrained |
|---|---|
| Score | 0.929 |
| Kicked / fell | 50 / 0 |
| Within 15° | 47 |
| Time to kick [s] | 1.51 ± 0.49 (1.48) |
| Direction error [deg] | 5.88 ± 4.52 (4.93) |
| Avg ball speed [m/s] | 1.50 ± 0.86 (1.42) |
| Peak ball speed [m/s] | 2.96 ± 1.72 (2.76) |
| Ball distance [m] | 1.12 ± 0.94 (0.84) |

## Per ball side

| Metric | pretrained |
|---|---|
| ball-left score | 0.922 |
| ball-left time [s] / dir. error [deg] | 1.45 / 6.5 |
| ball-right score | 0.920 |
| ball-right time [s] / dir. error [deg] | 1.58 / 6.2 |

## Per cell: score / time [s] / direction error [deg] / within 15°

| Sector / ball side | pretrained |
|---|---|
| forward / left | 0.935 / 0.87 / 5.7 / 23 |
| forward / right | 0.932 / 1.06 / 5.9 / 25 |
| left / left | 0.920 / 1.26 / 6.9 / 24 |
| left / right | 0.902 / 1.74 / 7.9 / 23 |
| back / left | 0.908 / 2.06 / 7.0 / 23 |
| back / right | 0.912 / 2.10 / 5.9 / 25 |
| right / left | 0.926 / 1.59 / 6.5 / 23 |
| right / right | 0.933 / 1.43 / 5.3 / 24 |
