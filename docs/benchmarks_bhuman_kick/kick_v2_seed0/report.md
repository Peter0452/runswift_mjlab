# B-Human K1_Ball kick benchmark v2: results

Port env `Mjlab-BHuman-Kick-Booster-K1`, plane, seed 0, 25 trials per cell, observation noise off, robot randomization off, ball rolling friction 0.1. Cells: mean ± std (median).

## Overall

| Metric | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| **Priority score** | 0.925 | 0.272 | 0.178 |
| Worst sector | left 0.921 | forward 0.215 | right 0.021 |
| Kicked / fell | 200 / 0 | 105 / 6 | 128 / 0 |
| Kicks within 15° of command | 196 | 9 | 31 |
| Time to kick [s] | 1.47 ± 0.52 (1.38) | 2.43 ± 1.39 (2.22) | 7.31 ± 2.32 (7.19) |
| Direction error [deg] | 6.34 ± 3.90 (5.77) | 88.39 ± 52.15 (98.76) | 46.07 ± 42.38 (27.47) |
| Avg ball speed [m/s] | 1.60 ± 0.85 (1.43) | 0.41 ± 0.22 (0.39) | 0.13 ± 0.07 (0.11) |
| Peak ball speed [m/s] | 3.13 ± 1.67 (2.96) | 0.84 ± 0.47 (0.80) | 0.23 ± 0.12 (0.19) |
| Ball distance [m] | 1.20 ± 0.92 (0.87) | 0.14 ± 0.12 (0.10) | 0.02 ± 0.01 (0.01) |
| Ball path length [m] | 1.20 ± 0.92 (0.88) | 0.14 ± 0.13 (0.10) | 0.02 ± 0.01 (0.01) |

## Per kick-direction sector

### Forward

| Metric | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| Score | 0.926 | 0.215 | 0.224 |
| Kicked / fell | 50 / 0 | 19 / 2 | 38 / 0 |
| Within 15° | 50 | 5 | 11 |
| Time to kick [s] | 0.97 ± 0.28 (0.97) | 2.86 ± 1.79 (2.43) | 7.22 ± 2.13 (7.12) |
| Direction error [deg] | 6.77 ± 3.99 (6.37) | 51.09 ± 46.20 (34.61) | 26.97 ± 18.62 (20.25) |
| Avg ball speed [m/s] | 1.51 ± 0.81 (1.37) | 0.45 ± 0.21 (0.42) | 0.13 ± 0.08 (0.11) |
| Peak ball speed [m/s] | 3.03 ± 1.69 (2.84) | 0.95 ± 0.47 (0.89) | 0.24 ± 0.13 (0.19) |
| Ball distance [m] | 1.15 ± 0.93 (0.87) | 0.17 ± 0.15 (0.11) | 0.01 ± 0.01 (0.01) |

### Left

| Metric | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| Score | 0.921 | 0.223 | 0.306 |
| Kicked / fell | 50 / 0 | 21 / 1 | 50 / 0 |
| Within 15° | 48 | 2 | 18 |
| Time to kick [s] | 1.45 ± 0.43 (1.39) | 2.61 ± 0.92 (2.30) | 7.26 ± 1.77 (7.58) |
| Direction error [deg] | 6.79 ± 3.97 (6.30) | 66.49 ± 46.33 (53.24) | 24.80 ± 23.28 (20.00) |
| Avg ball speed [m/s] | 1.68 ± 0.79 (1.66) | 0.39 ± 0.21 (0.37) | 0.14 ± 0.06 (0.13) |
| Peak ball speed [m/s] | 3.27 ± 1.57 (3.31) | 0.75 ± 0.44 (0.65) | 0.26 ± 0.12 (0.24) |
| Ball distance [m] | 1.26 ± 0.88 (1.14) | 0.11 ± 0.10 (0.08) | 0.02 ± 0.02 (0.01) |

### Back

| Metric | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| Score | 0.922 | 0.375 | 0.162 |
| Kicked / fell | 50 / 0 | 38 / 2 | 31 / 0 |
| Within 15° | 48 | 2 | 2 |
| Time to kick [s] | 2.03 ± 0.34 (2.02) | 2.31 ± 1.12 (2.26) | 6.58 ± 2.77 (6.72) |
| Direction error [deg] | 6.15 ± 3.81 (5.32) | 116.50 ± 48.61 (125.66) | 88.80 ± 47.17 (105.20) |
| Avg ball speed [m/s] | 1.65 ± 0.86 (1.66) | 0.41 ± 0.24 (0.37) | 0.11 ± 0.05 (0.10) |
| Peak ball speed [m/s] | 3.21 ± 1.69 (3.34) | 0.85 ± 0.53 (0.78) | 0.19 ± 0.09 (0.19) |
| Ball distance [m] | 1.25 ± 0.94 (1.18) | 0.15 ± 0.14 (0.09) | 0.01 ± 0.01 (0.01) |

### Right

| Metric | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| Score | 0.932 | 0.274 | 0.021 |
| Kicked / fell | 50 / 0 | 27 / 1 | 9 / 0 |
| Within 15° | 50 | 0 | 0 |
| Time to kick [s] | 1.43 ± 0.40 (1.32) | 2.16 ± 1.62 (1.60) | 10.55 ± 1.16 (10.30) |
| Direction error [deg] | 5.63 ± 3.70 (5.41) | 92.96 ± 40.19 (100.58) | 97.63 ± 20.19 (100.10) |
| Avg ball speed [m/s] | 1.57 ± 0.90 (1.32) | 0.41 ± 0.18 (0.42) | 0.08 ± 0.04 (0.09) |
| Peak ball speed [m/s] | 3.02 ± 1.74 (2.67) | 0.83 ± 0.37 (0.83) | 0.15 ± 0.06 (0.14) |
| Ball distance [m] | 1.14 ± 0.94 (0.77) | 0.13 ± 0.09 (0.11) | 0.01 ± 0.00 (0.01) |

## Per ball side

| Metric | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| ball-left score | 0.926 | 0.234 | 0.173 |
| ball-left time [s] / dir. error [deg] | 1.41 / 6.3 | 2.97 / 87.6 | 7.60 / 47.3 |
| ball-right score | 0.924 | 0.309 | 0.184 |
| ball-right time [s] / dir. error [deg] | 1.53 / 6.4 | 1.95 / 89.1 | 7.00 / 44.7 |

## Per cell: score / time [s] / direction error [deg] / within 15°

| Sector / ball side | pretrained | walk_start | stage1_400 |
|---|---|---|---|
| forward / left | 0.930 / 0.88 / 6.5 / 25 | 0.168 / 3.76 / 66.2 / 2 | 0.182 / 7.33 / 35.4 / 3 |
| forward / right | 0.921 / 1.06 / 7.1 / 25 | 0.262 / 2.14 / 39.0 / 3 | 0.267 / 7.12 / 20.2 / 8 |
| left / left | 0.919 / 1.23 / 7.1 / 23 | 0.160 / 3.36 / 56.8 / 0 | 0.307 / 7.06 / 24.5 / 9 |
| left / right | 0.922 / 1.67 / 6.5 / 25 | 0.285 / 2.05 / 73.8 / 2 | 0.304 / 7.45 / 25.1 / 9 |
| back / left | 0.926 / 2.00 / 5.9 / 24 | 0.337 / 2.72 / 97.7 / 2 | 0.170 / 7.34 / 69.3 / 2 |
| back / right | 0.918 / 2.05 / 6.4 / 24 | 0.413 / 1.95 / 133.3 / 0 | 0.153 / 5.65 / 112.5 / 0 |
| right / left | 0.930 / 1.52 / 5.6 / 25 | 0.273 / 2.58 / 107.4 / 0 | 0.032 / 10.84 / 104.2 / 0 |
| right / right | 0.934 / 1.34 / 5.6 / 25 | 0.275 / 1.67 / 76.1 / 0 | 0.010 / 9.52 / 74.6 / 0 |
