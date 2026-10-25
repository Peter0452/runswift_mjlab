# B-Human K1_Ball kick benchmark v2: results

Port env `Mjlab-BHuman-Kick-Booster-K1`, plane, seed 1, 25 trials per cell, observation noise off, robot randomization off, ball rolling friction 0.1. Cells: mean ± std (median).

## Overall

| Metric | pretrained |
|---|---|
| **Priority score** | 0.931 |
| Worst sector | back 0.919 |
| Kicked / fell | 200 / 0 |
| Kicks within 15° of command | 195 |
| Time to kick [s] | 1.48 ± 0.56 (1.48) |
| Direction error [deg] | 5.73 ± 3.59 (5.21) |
| Avg ball speed [m/s] | 1.62 ± 0.85 (1.40) |
| Peak ball speed [m/s] | 3.18 ± 1.69 (2.80) |
| Ball distance [m] | 1.23 ± 0.94 (0.87) |
| Ball path length [m] | 1.24 ± 0.94 (0.88) |

## Per kick-direction sector

### Forward

| Metric | pretrained |
|---|---|
| Score | 0.937 |
| Kicked / fell | 50 / 0 |
| Within 15° | 48 |
| Time to kick [s] | 0.96 ± 0.33 (0.96) |
| Direction error [deg] | 5.64 ± 3.77 (4.83) |
| Avg ball speed [m/s] | 1.61 ± 0.81 (1.40) |
| Peak ball speed [m/s] | 3.22 ± 1.65 (2.80) |
| Ball distance [m] | 1.25 ± 0.96 (0.87) |

### Left

| Metric | pretrained |
|---|---|
| Score | 0.922 |
| Kicked / fell | 50 / 0 |
| Within 15° | 49 |
| Time to kick [s] | 1.49 ± 0.49 (1.37) |
| Direction error [deg] | 6.62 ± 3.77 (6.01) |
| Avg ball speed [m/s] | 1.69 ± 0.92 (1.75) |
| Peak ball speed [m/s] | 3.27 ± 1.78 (3.43) |
| Ball distance [m] | 1.29 ± 0.97 (1.31) |

### Back

| Metric | pretrained |
|---|---|
| Score | 0.919 |
| Kicked / fell | 50 / 0 |
| Within 15° | 48 |
| Time to kick [s] | 2.03 ± 0.33 (2.09) |
| Direction error [deg] | 6.04 ± 3.83 (5.61) |
| Avg ball speed [m/s] | 1.62 ± 0.80 (1.52) |
| Peak ball speed [m/s] | 3.19 ± 1.62 (2.96) |
| Ball distance [m] | 1.23 ± 0.91 (0.97) |

### Right

| Metric | pretrained |
|---|---|
| Score | 0.945 |
| Kicked / fell | 50 / 0 |
| Within 15° | 50 |
| Time to kick [s] | 1.44 ± 0.45 (1.48) |
| Direction error [deg] | 4.63 ± 2.53 (4.48) |
| Avg ball speed [m/s] | 1.56 ± 0.86 (1.57) |
| Peak ball speed [m/s] | 3.03 ± 1.69 (3.07) |
| Ball distance [m] | 1.16 ± 0.91 (1.09) |

## Per ball side

| Metric | pretrained |
|---|---|
| ball-left score | 0.934 |
| ball-left time [s] / dir. error [deg] | 1.42 / 5.7 |
| ball-right score | 0.928 |
| ball-right time [s] / dir. error [deg] | 1.54 / 5.8 |

## Per cell: score / time [s] / direction error [deg] / within 15°

| Sector / ball side | pretrained |
|---|---|
| forward / left | 0.946 / 0.87 / 5.0 / 25 |
| forward / right | 0.928 / 1.04 / 6.3 / 23 |
| left / left | 0.932 / 1.25 / 6.1 / 24 |
| left / right | 0.912 / 1.73 / 7.2 / 25 |
| back / left | 0.914 / 2.01 / 6.8 / 23 |
| back / right | 0.925 / 2.05 / 5.3 / 25 |
| right / left | 0.943 / 1.55 / 4.9 / 25 |
| right / right | 0.947 / 1.34 / 4.4 / 25 |
