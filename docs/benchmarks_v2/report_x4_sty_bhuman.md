# Kick benchmark v2

- **x4**: logs/rsl_rl/k1_kick_stage3_amp/2026-10-06_08-40-00_blend_x4_g004_70/model_14200.pt (full, 2026-10-07 12:15)
- **sty_power_17149**: logs/rsl_rl/k1_kick_stage3_amp/2026-10-07_05-08-47_sty_power/model_17149.pt (full, 2026-10-07 12:18)
- **bhuman**: bhuman (full, 2026-10-07 12:18)

## approach/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_kick_pct | low | 61.5 [57.4, 65.6] | 68 [64.1, 72.1] | — |
| first_kick_pct | high | 88.3 [85.5, 91] | 83.2 [79.9, 86.5] | — |
| first_kick_s | low | 13.9 [13.5, 14.3] | 13 [12.6, 13.4] | — |
| first_kick_s | high | 8.45 [8.21, 8.67] | 8.27 [8.04, 8.51] | — |
| fall_pct | low | 7.23 [4.88, 9.38] | 21.5 [18.2, 25.2] | — |
| fall_pct | high | 10.9 [8.4, 13.7] | 15.4 [12.5, 18.8] | — |
| fall_pct_front | low | 0 [0, 0] | 0 [0, 0] | — |
| fall_pct_front | high | 0 [0, 0] | 0 [0, 0] | — |
| fall_pct_side | low | 0 [0, 0] | 21.7 [15.8, 27.2] | — |
| fall_pct_side | high | 1.69 [0, 3.93] | 5.62 [2.25, 9.55] | — |
| fall_pct_behind | low | 22.7 [16.5, 29.4] | 42.9 [35.6, 50.3] | — |
| fall_pct_behind | high | 34.4 [26.6, 41.6] | 44.8 [37, 52.6] | — |
| first_kick_pct_behind | low | 55.2 [47.9, 62.6] | 49.1 [41.1, 57.1] | — |
| first_kick_pct_behind | high | 64.9 [57.8, 72.1] | 53.9 [46.1, 62.3] | — |
| cap_use | low | 0.508 [0.48, 0.535] | 0.443 [0.404, 0.482] | — |
| cap_use | high | 0.266 [0.251, 0.281] | 0.238 [0.221, 0.254] | — |

## approach/camera/zero

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_kick_pct | low | 68 [64.1, 72.1] | 58.6 [54.5, 62.9] | — |
| first_kick_pct | high | 88.3 [85.4, 91] | 72.7 [68.8, 76.6] | — |
| first_kick_s | low | 13.6 [13.2, 14] | 11.2 [10.8, 11.6] | — |
| first_kick_s | high | 7.49 [7.26, 7.74] | 7.48 [7.18, 7.78] | — |
| fall_pct | low | 18.8 [15.2, 22.1] | 32.6 [28.7, 36.9] | — |
| fall_pct | high | 9.57 [7.03, 12.1] | 24.6 [20.7, 28.5] | — |
| fall_pct_front | low | 0 [0, 0] | 0 [0, 0] | — |
| fall_pct_front | high | 0 [0, 0] | 0 [0, 0] | — |
| fall_pct_side | low | 2.47 [0.617, 4.94] | 36.4 [29, 43.8] | — |
| fall_pct_side | high | 0.568 [0, 1.7] | 21.6 [15.9, 27.8] | — |
| fall_pct_behind | low | 48.2 [41.4, 55.5] | 56.5 [49.7, 63.4] | — |
| fall_pct_behind | high | 27.4 [21.1, 33.7] | 50.3 [43.4, 57.7] | — |
| first_kick_pct_behind | low | 34.6 [27.7, 41.4] | 35.6 [28.3, 41.9] | — |
| first_kick_pct_behind | high | 69.1 [61.7, 76] | 48 [40.6, 54.9] | — |
| cap_use | low | 0.545 [0.508, 0.58] | 0.42 [0.375, 0.467] | — |
| cap_use | high | 0.319 [0.301, 0.336] | 0.242 [0.224, 0.259] | — |

## approach/world/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_kick_pct | low | 61.7 [57.6, 65.8] | 70.1 [66, 74.2] | — |
| first_kick_pct | high | 88.7 [85.7, 91.4] | 84.2 [80.9, 87.3] | — |
| first_kick_s | low | 13.3 [12.8, 13.7] | 12.7 [12.3, 13.1] | — |
| first_kick_s | high | 8.11 [7.9, 8.31] | 7.82 [7.61, 8.01] | — |
| fall_pct | low | 11.3 [8.59, 14.1] | 21.9 [18.4, 25.6] | — |
| fall_pct | high | 11.3 [8.59, 14.3] | 15.8 [12.7, 18.9] | — |
| fall_pct_front | low | 0 [0, 0] | 0 [0, 0] | — |
| fall_pct_front | high | 0 [0, 0] | 0 [0, 0] | — |
| fall_pct_side | low | 1.63 [0, 3.8] | 19.6 [13.6, 25] | — |
| fall_pct_side | high | 1.12 [0, 2.81] | 5.62 [2.25, 8.99] | — |
| fall_pct_behind | low | 33.7 [27, 41.1] | 46.6 [39.3, 54.6] | — |
| fall_pct_behind | high | 36.4 [28.6, 44.8] | 46.1 [39, 53.9] | — |
| first_kick_pct_behind | low | 52.8 [44.8, 60.7] | 51.5 [43.6, 58.9] | — |
| first_kick_pct_behind | high | 63.6 [55.8, 71.4] | 53.9 [46.1, 62.3] | — |
| cap_use | low | 0.501 [0.472, 0.53] | 0.485 [0.447, 0.523] | — |
| cap_use | high | 0.276 [0.261, 0.292] | 0.248 [0.231, 0.264] | — |

## close_any/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_touch_15_pct | low | 49.6 [45.1, 54.1] | 73 [68.9, 76.8] | 24.2 [20.7, 27.9] |
| first_touch_15_pct | high | 43.4 [39.1, 47.7] | 50.2 [45.9, 54.5] | 21.1 [17.8, 24.4] |
| first_kick_pct | low | 80.9 [77.5, 84.2] | 85.2 [82, 88.3] | 45.9 [41.6, 50.2] |
| first_kick_pct | high | 88.5 [85.7, 90.8] | 89.3 [86.7, 91.8] | 35.9 [31.6, 40.4] |
| first_kick_s | low | 4.93 [4.69, 5.19] | 4.3 [4.09, 4.51] | 3.62 [3.39, 3.86] |
| first_kick_s | high | 4.28 [4.07, 4.53] | 3.9 [3.68, 4.1] | 3.71 [3.43, 3.99] |
| kicks_20_pct | low | 78.8 [75.1, 82.5] | 94.8 [92.9, 96.7] | 74.3 [69.7, 78.9] |
| kicks_20_pct | high | 70.3 [66.7, 74] | 75.6 [72.4, 78.5] | 77.4 [72.5, 82.5] |
| long_3d | low | 4.54 [4.22, 4.83] | 3.62 [3.4, 3.84] | 4.27 [3.87, 4.65] |
| long_3d | high | 4.28 [3.97, 4.59] | 3.43 [3.25, 3.61] | 4.31 [3.85, 4.79] |
| fall_pct | low | 2.15 [0.977, 3.52] | 3.52 [1.95, 5.08] | 54.9 [50.4, 59.4] |
| fall_pct | high | 3.12 [1.76, 4.69] | 3.91 [2.34, 5.47] | 61.5 [57, 65.4] |

## close_any/perfect/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_touch_15_pct | low | 47.3 [42.8, 51.6] | 78.3 [75.2, 81.8] | 64.8 [60.7, 68.8] |
| first_touch_15_pct | high | 37.1 [33, 41] | 40.6 [36.3, 45.3] | 69.1 [65, 72.9] |
| first_kick_pct | low | 97.1 [95.7, 98.4] | 91.6 [89.1, 93.8] | 95.9 [94.1, 97.5] |
| first_kick_pct | high | 96.9 [95.3, 98.2] | 91.8 [89.5, 94.1] | 98.4 [97.3, 99.4] |
| first_kick_s | low | 3.61 [3.48, 3.75] | 3.36 [3.22, 3.49] | 2.89 [2.81, 2.98] |
| first_kick_s | high | 2.92 [2.82, 3.02] | 2.9 [2.78, 3.02] | 2.85 [2.76, 2.95] |
| kicks_20_pct | low | 74.3 [70.6, 77.8] | 93.6 [91.8, 95.3] | 99.3 [98.5, 99.8] |
| kicks_20_pct | high | 66 [62.8, 69.2] | 73.4 [70.6, 76.3] | 99.3 [98.6, 99.9] |
| long_3d | low | 4.48 [4.18, 4.79] | 3.67 [3.46, 3.86] | 5.85 [5.52, 6.16] |
| long_3d | high | 4.64 [4.4, 4.88] | 3.54 [3.36, 3.72] | 5.97 [5.62, 6.32] |
| fall_pct | low | 3.91 [2.34, 5.66] | 7.03 [4.88, 9.38] | 33 [28.7, 37.3] |
| fall_pct | high | 3.12 [1.76, 4.69] | 8.59 [6.05, 10.9] | 29.7 [25.6, 33.8] |

## full_loop/bumps/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goals_per_ep | low | 0.736 [0.682, 0.787] | 1.18 [1.12, 1.25] | — |
| goals_per_ep | high | 1.3 [1.23, 1.37] | 1.64 [1.57, 1.71] | — |
| kicks_20_pct | low | 67.7 [64.5, 70.8] | 91.1 [89.6, 92.6] | — |
| kicks_20_pct | high | 57.4 [54.9, 59.6] | 69.2 [67.4, 71] | — |
| first_kick_s | low | 6.67 [6.42, 6.96] | 5.76 [5.52, 6.03] | — |
| first_kick_s | high | 4.39 [4.17, 4.64] | 4.09 [3.87, 4.34] | — |
| long_3d | low | 4.61 [4.38, 4.86] | 3.61 [3.47, 3.76] | — |
| long_3d | high | 4.82 [4.62, 5] | 3.45 [3.33, 3.56] | — |
| long_x_needed | low | 0.943 [0.89, 0.998] | 0.754 [0.722, 0.786] | — |
| long_x_needed | high | 0.992 [0.953, 1.03] | 0.728 [0.703, 0.755] | — |
| short_stop_m | low | 3.04 [2.92, 3.15] | 2.64 [2.5, 2.79] | — |
| short_stop_m | high | 2.82 [2.72, 2.92] | 2.69 [2.6, 2.77] | — |
| fall_pct | low | 1.95 [0.781, 3.32] | 2.34 [1.17, 3.71] | — |
| fall_pct | high | 2.34 [1.17, 3.71] | 2.54 [1.37, 4.1] | — |
| knee_peak_at_kick | low | 16.9 [16.4, 17.3] | 19 [18.4, 19.7] | — |
| knee_peak_at_kick | high | 23.6 [23, 24.1] | 23.3 [22.6, 23.9] | — |
| torque_sat_pct | low | 0.569 [0.273, 0.946] | 0.824 [0.451, 1.24] | — |
| torque_sat_pct | high | 0.759 [0.408, 1.21] | 0.697 [0.397, 1.09] | — |
| fast_height_m | low | 0.512 [0.506, 0.518] | 0.504 [0.499, 0.509] | — |
| fast_height_m | high | 0.492 [0.451, 0.514] | 0.497 [0.479, 0.507] | — |
| fast_pitch_deg | low | 2.36 [0.959, 3.73] | 0.838 [-0.422, 2.19] | — |
| fast_pitch_deg | high | -0.00423 [-0.21, 0.227] | -1.4 [-1.62, -1.14] | — |
| action_rate | low | 0.0977 [0.0958, 0.1] | 0.114 [0.111, 0.116] | — |
| action_rate | high | 0.126 [0.124, 0.128] | 0.143 [0.141, 0.145] | — |

## full_loop/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goals_per_ep | low | 0.74 [0.686, 0.793] | 1.11 [1.05, 1.17] | — |
| goals_per_ep | high | 1.29 [1.21, 1.36] | 1.57 [1.51, 1.64] | — |
| kicks_20_pct | low | 80 [77.1, 83] | 96.5 [95.3, 97.5] | — |
| kicks_20_pct | high | 67.3 [65.1, 69.7] | 79.5 [77.7, 81.3] | — |
| first_kick_s | low | 6.73 [6.52, 6.97] | 5.73 [5.54, 5.95] | — |
| first_kick_s | high | 4.54 [4.32, 4.77] | 4.09 [3.89, 4.31] | — |
| long_3d | low | 4.72 [4.47, 4.98] | 3.7 [3.55, 3.86] | — |
| long_3d | high | 4.86 [4.66, 5.07] | 3.56 [3.44, 3.66] | — |
| long_x_needed | low | 0.949 [0.897, 0.998] | 0.757 [0.726, 0.788] | — |
| long_x_needed | high | 1 [0.955, 1.05] | 0.741 [0.714, 0.768] | — |
| short_stop_m | low | 3.29 [3.14, 3.45] | 2.86 [2.73, 2.98] | — |
| short_stop_m | high | 3.16 [3.05, 3.27] | 2.95 [2.87, 3.04] | — |
| fall_pct | low | 2.54 [1.37, 3.91] | 2.54 [1.17, 3.91] | — |
| fall_pct | high | 2.93 [1.56, 4.49] | 2.15 [0.977, 3.52] | — |
| knee_peak_at_kick | low | 16.7 [16.2, 17.1] | 18.4 [17.7, 19] | — |
| knee_peak_at_kick | high | 22.3 [21.9, 22.9] | 22.1 [21.4, 22.8] | — |
| torque_sat_pct | low | 0.656 [0.321, 1.06] | 0.787 [0.438, 1.18] | — |
| torque_sat_pct | high | 0.656 [0.393, 1.01] | 0.632 [0.354, 0.957] | — |
| fast_height_m | low | 0.507 [0.502, 0.512] | 0.5 [0.495, 0.505] | — |
| fast_height_m | high | 0.504 [0.503, 0.505] | 0.498 [0.497, 0.499] | — |
| fast_pitch_deg | low | 2.5 [1.18, 3.78] | 1.52 [0.245, 2.67] | — |
| fast_pitch_deg | high | -0.237 [-0.486, 0.0619] | -1.56 [-1.79, -1.3] | — |
| action_rate | low | 0.0967 [0.0944, 0.0992] | 0.113 [0.11, 0.115] | — |
| action_rate | high | 0.127 [0.125, 0.13] | 0.142 [0.14, 0.146] | — |

## full_loop/late_detect/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goals_per_ep | low | 0.684 [0.631, 0.742] | 1.06 [0.994, 1.12] | — |
| goals_per_ep | high | 1.2 [1.13, 1.27] | 1.41 [1.33, 1.48] | — |
| kicks_20_pct | low | 76.9 [74.1, 80] | 91.1 [89.4, 92.6] | — |
| kicks_20_pct | high | 59.8 [57.5, 62.2] | 63.3 [61.4, 65.4] | — |
| first_kick_s | low | 6.87 [6.65, 7.1] | 5.81 [5.6, 6.01] | — |
| first_kick_s | high | 5.15 [4.85, 5.48] | 4.78 [4.46, 5.12] | — |
| long_3d | low | 4.72 [4.46, 4.97] | 3.7 [3.55, 3.83] | — |
| long_3d | high | 4.34 [4.16, 4.52] | 3.42 [3.29, 3.54] | — |
| long_x_needed | low | 0.95 [0.896, 1.01] | 0.759 [0.724, 0.792] | — |
| long_x_needed | high | 0.902 [0.864, 0.942] | 0.724 [0.695, 0.755] | — |
| short_stop_m | low | 3.3 [3.15, 3.46] | 2.93 [2.79, 3.08] | — |
| short_stop_m | high | 3 [2.89, 3.11] | 2.96 [2.86, 3.06] | — |
| fall_pct | low | 2.73 [1.37, 4.3] | 2.34 [1.17, 3.71] | — |
| fall_pct | high | 2.73 [1.37, 4.3] | 2.34 [1.17, 3.52] | — |
| knee_peak_at_kick | low | 17.2 [16.8, 17.7] | 19 [18.4, 19.6] | — |
| knee_peak_at_kick | high | 23.5 [22.8, 24.1] | 22.8 [22, 23.6] | — |
| torque_sat_pct | low | 0.736 [0.361, 1.14] | 0.755 [0.386, 1.21] | — |
| torque_sat_pct | high | 0.673 [0.403, 1.03] | 0.621 [0.364, 0.974] | — |
| fast_height_m | low | 0.508 [0.502, 0.512] | 0.501 [0.496, 0.505] | — |
| fast_height_m | high | 0.504 [0.503, 0.505] | 0.498 [0.497, 0.498] | — |
| fast_pitch_deg | low | 2.58 [1.48, 4.01] | 1.69 [0.589, 2.9] | — |
| fast_pitch_deg | high | -0.373 [-0.647, -0.0609] | -1.71 [-1.93, -1.45] | — |
| action_rate | low | 0.0968 [0.0944, 0.0995] | 0.112 [0.109, 0.115] | — |
| action_rate | high | 0.125 [0.123, 0.128] | 0.138 [0.136, 0.141] | — |

## full_loop/moving/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goals_per_ep | low | 0.764 [0.705, 0.818] | 1.15 [1.09, 1.21] | — |
| goals_per_ep | high | 1.29 [1.22, 1.36] | 1.59 [1.52, 1.66] | — |
| kicks_20_pct | low | 78.7 [75.8, 81.7] | 96.4 [95.2, 97.4] | — |
| kicks_20_pct | high | 66.1 [63.8, 68.4] | 78.8 [77.2, 80.6] | — |
| first_kick_s | low | 6.83 [6.58, 7.05] | 5.78 [5.57, 5.99] | — |
| first_kick_s | high | 4.44 [4.22, 4.65] | 4.14 [3.9, 4.38] | — |
| long_3d | low | 4.63 [4.39, 4.88] | 3.66 [3.51, 3.8] | — |
| long_3d | high | 4.73 [4.54, 4.92] | 3.41 [3.28, 3.54] | — |
| long_x_needed | low | 0.955 [0.896, 1.01] | 0.759 [0.724, 0.792] | — |
| long_x_needed | high | 0.97 [0.931, 1.01] | 0.71 [0.685, 0.739] | — |
| short_stop_m | low | 3.21 [3.08, 3.35] | 2.8 [2.68, 2.93] | — |
| short_stop_m | high | 3.08 [2.98, 3.18] | 2.95 [2.87, 3.03] | — |
| fall_pct | low | 1.76 [0.781, 3.12] | 1.76 [0.781, 2.93] | — |
| fall_pct | high | 1.76 [0.781, 2.93] | 1.56 [0.586, 2.73] | — |
| knee_peak_at_kick | low | 17.4 [16.9, 17.9] | 19.1 [18.4, 19.7] | — |
| knee_peak_at_kick | high | 22.8 [22.2, 23.4] | 21.4 [20.7, 22.1] | — |
| torque_sat_pct | low | 0.486 [0.25, 0.826] | 0.492 [0.267, 0.765] | — |
| torque_sat_pct | high | 0.74 [0.37, 1.2] | 0.722 [0.365, 1.14] | — |
| fast_height_m | low | 0.506 [0.502, 0.51] | 0.497 [0.493, 0.501] | — |
| fast_height_m | high | 0.505 [0.504, 0.506] | 0.499 [0.498, 0.499] | — |
| fast_pitch_deg | low | 1.41 [0.308, 2.55] | 1.19 [0.265, 2.1] | — |
| fast_pitch_deg | high | -0.553 [-0.761, -0.323] | -1.72 [-1.92, -1.47] | — |
| action_rate | low | 0.0954 [0.0935, 0.0978] | 0.11 [0.108, 0.112] | — |
| action_rate | high | 0.126 [0.124, 0.128] | 0.141 [0.139, 0.143] | — |

## full_loop/push/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goals_per_ep | low | 0.791 [0.736, 0.848] | 1.13 [1.07, 1.19] | — |
| goals_per_ep | high | 1.23 [1.17, 1.29] | 1.56 [1.5, 1.63] | — |
| kicks_20_pct | low | 73.2 [70, 76] | 92.2 [90.5, 93.7] | — |
| kicks_20_pct | high | 64.5 [62.2, 66.8] | 72.5 [70.6, 74.2] | — |
| first_kick_s | low | 7 [6.72, 7.27] | 5.99 [5.72, 6.26] | — |
| first_kick_s | high | 4.84 [4.55, 5.13] | 4.21 [3.98, 4.45] | — |
| long_3d | low | 4.38 [4.11, 4.63] | 3.63 [3.47, 3.8] | — |
| long_3d | high | 4.56 [4.38, 4.73] | 3.52 [3.4, 3.64] | — |
| long_x_needed | low | 0.887 [0.835, 0.938] | 0.739 [0.707, 0.773] | — |
| long_x_needed | high | 0.94 [0.9, 0.981] | 0.734 [0.707, 0.758] | — |
| short_stop_m | low | 3.08 [2.95, 3.23] | 2.9 [2.76, 3.04] | — |
| short_stop_m | high | 3.08 [2.96, 3.2] | 2.84 [2.75, 2.94] | — |
| fall_pct | low | 1.17 [0.391, 2.15] | 1.76 [0.781, 3.12] | — |
| fall_pct | high | 1.76 [0.781, 2.93] | 1.56 [0.586, 2.73] | — |
| knee_peak_at_kick | low | 18.1 [17.6, 18.7] | 19.2 [18.4, 19.9] | — |
| knee_peak_at_kick | high | 23.2 [22.6, 23.9] | 22.9 [22.1, 23.6] | — |
| torque_sat_pct | low | 0.427 [0.213, 0.701] | 0.695 [0.381, 1.05] | — |
| torque_sat_pct | high | 0.594 [0.363, 0.893] | 0.731 [0.437, 1.14] | — |
| fast_height_m | low | 0.505 [0.504, 0.506] | 0.497 [0.496, 0.499] | — |
| fast_height_m | high | 0.503 [0.502, 0.503] | 0.497 [0.496, 0.497] | — |
| fast_pitch_deg | low | 1.82 [1.41, 2.21] | 0.867 [0.541, 1.2] | — |
| fast_pitch_deg | high | -0.0963 [-0.267, 0.107] | -1.32 [-1.51, -1.11] | — |
| action_rate | low | 0.0982 [0.0967, 0.1] | 0.113 [0.111, 0.115] | — |
| action_rate | high | 0.126 [0.124, 0.128] | 0.142 [0.139, 0.144] | — |

## full_loop/robust/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goals_per_ep | low | 0.678 [0.623, 0.729] | 1.01 [0.949, 1.07] | — |
| goals_per_ep | high | 1.17 [1.11, 1.24] | 1.44 [1.37, 1.51] | — |
| kicks_20_pct | low | 73.1 [70, 76] | 93.8 [92.4, 95.2] | — |
| kicks_20_pct | high | 63 [60.4, 65.5] | 71.6 [69.4, 73.8] | — |
| first_kick_s | low | 7.51 [7.14, 7.87] | 6.22 [5.94, 6.56] | — |
| first_kick_s | high | 4.85 [4.56, 5.15] | 4.4 [4.14, 4.7] | — |
| long_3d | low | 4.57 [4.34, 4.8] | 3.57 [3.4, 3.73] | — |
| long_3d | high | 4.46 [4.27, 4.65] | 3.43 [3.3, 3.56] | — |
| long_x_needed | low | 0.926 [0.878, 0.979] | 0.742 [0.709, 0.779] | — |
| long_x_needed | high | 0.93 [0.887, 0.972] | 0.717 [0.691, 0.745] | — |
| short_stop_m | low | 3.14 [3, 3.29] | 2.82 [2.69, 2.98] | — |
| short_stop_m | high | 3.14 [3.02, 3.26] | 2.82 [2.72, 2.92] | — |
| fall_pct | low | 3.52 [2.15, 5.08] | 4.1 [2.54, 5.86] | — |
| fall_pct | high | 3.71 [2.15, 5.47] | 2.93 [1.56, 4.3] | — |
| knee_peak_at_kick | low | 17.1 [16.6, 17.7] | 19 [18.3, 19.8] | — |
| knee_peak_at_kick | high | 22.9 [22.2, 23.6] | 22.9 [22.1, 23.5] | — |
| torque_sat_pct | low | 0.966 [0.588, 1.39] | 1.13 [0.721, 1.57] | — |
| torque_sat_pct | high | 0.905 [0.581, 1.31] | 1.11 [0.708, 1.56] | — |
| fast_height_m | low | 0.499 [0.494, 0.504] | 0.489 [0.484, 0.494] | — |
| fast_height_m | high | 0.501 [0.5, 0.502] | 0.496 [0.494, 0.497] | — |
| fast_pitch_deg | low | 1.46 [0.414, 2.57] | 0.199 [-0.832, 1.25] | — |
| fast_pitch_deg | high | 0.36 [0.0662, 0.68] | -1.2 [-1.48, -0.909] | — |
| action_rate | low | 0.0993 [0.0968, 0.102] | 0.116 [0.113, 0.119] | — |
| action_rate | high | 0.129 [0.126, 0.132] | 0.144 [0.141, 0.147] | — |

## goal_grid/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goal_pct | low | 42.2 [32.2, 52.2] | 61.1 [51.1, 71.1] | — |
| goal_pct | high | 36.7 [27.8, 46.7] | 58.9 [50, 68.9] | — |
| goal_s | low | 33.6 [28.4, 38.9] | 31.6 [28.4, 34.8] | — |
| goal_s | high | 18.5 [15.7, 21.5] | 20.2 [17.5, 23.3] | — |
| fall_pct | low | 12.2 [5.56, 20] | 18.9 [11.1, 26.7] | — |
| fall_pct | high | 16.7 [8.89, 25.6] | 17.8 [11.1, 25.6] | — |
| fall_before_contact_pct | low | 0 [0, 0] | 0 [0, 0] | — |
| fall_before_contact_pct | high | 0 [0, 0] | 0 [0, 0] | — |

## goal_grid/world/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| goal_pct | low | 25.6 [16.7, 34.4] | 47.8 [36.7, 57.8] | — |
| goal_pct | high | 23.3 [15.6, 32.2] | 34.4 [24.4, 44.4] | — |
| goal_s | low | 29.6 [22.2, 37.9] | 22.4 [19.3, 25.5] | — |
| goal_s | high | 15.6 [11.8, 19.7] | 12.1 [10.5, 13.7] | — |
| fall_pct | low | 35.6 [26.7, 45.6] | 37.8 [27.8, 47.8] | — |
| fall_pct | high | 34.4 [24.4, 44.4] | 31.1 [21.1, 41.1] | — |
| fall_before_contact_pct | low | 0 [0, 0] | 0 [0, 0] | — |
| fall_before_contact_pct | high | 0 [0, 0] | 0 [0, 0] | — |

## near_grid/camera/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_touch_15_pct | low | 26.9 [19.4, 36.1] | 57.4 [48.1, 66.7] | 54.6 [44.4, 63.9] |
| first_touch_15_pct | high | 23.1 [15.7, 31.5] | 17.6 [11.1, 25] | 48.1 [38, 57.4] |
| first_touch_err_deg | low | 21.3 [19.5, 23.3] | 13.7 [12, 15.5] | 21.8 [16.3, 27.7] |
| first_touch_err_deg | high | 23.9 [21.9, 25.9] | 24.8 [22.9, 26.9] | 19.9 [16.8, 23.2] |
| first_touch_speed | low | 4.32 [4.1, 4.51] | 4.02 [3.84, 4.19] | 2.86 [2.61, 3.14] |
| first_touch_speed | high | 3.9 [3.71, 4.08] | 3.41 [3.25, 3.55] | 2.92 [2.66, 3.16] |
| first_kick_s | low | 1.92 [1.83, 2] | 1.62 [1.55, 1.69] | 2.76 [2.32, 3.27] |
| first_kick_s | high | 1.9 [1.58, 2.26] | 1.46 [1.33, 1.67] | 2.74 [2.33, 3.24] |
| fall_pct | low | 0 [0, 0] | 0 [0, 0] | 1.85 [0, 4.63] |
| fall_pct | high | 0 [0, 0] | 0 [0, 0] | 0.926 [0, 2.78] |
| joint_stop_pct | low | 0.971 [0.901, 1.04] | 1.45 [1.33, 1.57] | 0 [0, 0] |
| joint_stop_pct | high | 1.55 [1.46, 1.64] | 2.74 [2.57, 2.89] | 0 [0, 0] |

## near_grid/camera/zero

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_touch_15_pct | low | 13.9 [7.41, 20.4] | 26.9 [19.4, 35.2] | 56.5 [46.3, 65.7] |
| first_touch_15_pct | high | 19.4 [12, 26.9] | 10.2 [4.63, 15.7] | 55.6 [46.3, 64.8] |
| first_touch_err_deg | low | 23.4 [21.5, 25.4] | 20.3 [18.7, 21.9] | 18 [14.1, 22.5] |
| first_touch_err_deg | high | 25.6 [23.6, 27.5] | 29 [26.9, 31] | 18.8 [14, 24.9] |
| first_touch_speed | low | 2.56 [2.43, 2.71] | 3.3 [3.15, 3.46] | 2.99 [2.71, 3.27] |
| first_touch_speed | high | 2.71 [2.56, 2.88] | 3.07 [2.93, 3.22] | 2.96 [2.69, 3.22] |
| first_kick_s | low | 1.7 [1.57, 1.86] | 1.44 [1.34, 1.58] | 2.21 [1.87, 2.64] |
| first_kick_s | high | 1.88 [1.51, 2.3] | 1.38 [1.18, 1.68] | 2.34 [1.98, 2.77] |
| fall_pct | low | 0 [0, 0] | 0 [0, 0] | 2.78 [0, 6.48] |
| fall_pct | high | 0 [0, 0] | 0 [0, 0] | 2.78 [0, 6.48] |
| joint_stop_pct | low | 2.01 [1.83, 2.19] | 2.1 [1.92, 2.26] | 0 [0, 0] |
| joint_stop_pct | high | 2.44 [2.25, 2.62] | 3 [2.72, 3.26] | 0 [0, 0] |

## near_grid/perfect/typical

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_touch_15_pct | low | 10.2 [4.63, 16.7] | 55.6 [46.3, 64.8] | 75.9 [67.6, 83.3] |
| first_touch_15_pct | high | 0.926 [0, 2.78] | 8.33 [3.7, 13.9] | 66.7 [57.4, 75] |
| first_touch_err_deg | low | 24.4 [23.2, 25.6] | 15 [13.8, 16.2] | 3.37 [2.63, 4.26] |
| first_touch_err_deg | high | 29.1 [27.9, 30.3] | 28.1 [26.4, 29.9] | 3.95 [3.09, 4.93] |
| first_touch_speed | low | 4.52 [4.38, 4.68] | 4.23 [4.12, 4.33] | 3.65 [3.44, 3.92] |
| first_touch_speed | high | 4.3 [4.14, 4.46] | 3.94 [3.84, 4.04] | 3.64 [3.45, 3.89] |
| first_kick_s | low | 1.79 [1.71, 1.87] | 1.48 [1.41, 1.55] | 1.38 [1.27, 1.49] |
| first_kick_s | high | 1.47 [1.42, 1.52] | 1.36 [1.26, 1.5] | 1.39 [1.25, 1.57] |
| fall_pct | low | 0 [0, 0] | 0 [0, 0] | 21.3 [13.9, 29.6] |
| fall_pct | high | 0 [0, 0] | 0 [0, 0] | 27.8 [20.3, 36.1] |
| joint_stop_pct | low | 0.961 [0.921, 1.01] | 1.77 [1.66, 1.89] | 0 [0, 0] |
| joint_stop_pct | high | 1.95 [1.87, 2.02] | 3.1 [3.03, 3.18] | 0 [0, 0] |

## near_grid/perfect/zero

| metric | caps | x4 | sty_power_17149 | bhuman |
|---|---|---|---|---|
| first_touch_15_pct | low | 5.56 [1.85, 10.2] | 27.8 [19.4, 37.1] | 89.8 [83.3, 95.4] |
| first_touch_15_pct | high | 0.926 [0, 2.78] | 0.926 [0, 2.78] | 87 [81.5, 92.6] |
| first_touch_err_deg | low | 24.9 [23.6, 25.9] | 19.4 [18.2, 20.5] | 5.22 [4.1, 6.6] |
| first_touch_err_deg | high | 28 [27, 29] | 29.4 [28.1, 30.7] | 5.07 [4.12, 6.16] |
| first_touch_speed | low | 2.64 [2.49, 2.79] | 3.27 [3.16, 3.37] | 2.93 [2.71, 3.16] |
| first_touch_speed | high | 3.11 [2.97, 3.27] | 3.41 [3.31, 3.51] | 2.82 [2.64, 3.01] |
| first_kick_s | low | 1.54 [1.46, 1.62] | 1.36 [1.23, 1.54] | 1.22 [1.11, 1.35] |
| first_kick_s | high | 1.27 [1.21, 1.34] | 1.13 [1.09, 1.17] | 1.14 [1.05, 1.23] |
| fall_pct | low | 0 [0, 0] | 0 [0, 0] | 7.41 [2.78, 13] |
| fall_pct | high | 0 [0, 0] | 0 [0, 0] | 8.33 [3.7, 13.9] |
| joint_stop_pct | low | 2.31 [2.15, 2.48] | 2.51 [2.37, 2.63] | 0 [0, 0] |
| joint_stop_pct | high | 2.66 [2.53, 2.8] | 3.65 [3.44, 3.86] | 0 [0, 0] |

## CPU engine (runner code, runswift harness)

| policy | run | ball | result |
|---|---|---|---|
| x4 | goal-high-camera | light-small | goals 16/90, falls during attempt 2, contact 40 |
| x4 | goal-high-camera | heavy-large | goals 22/90, falls during attempt 2, contact 39 |
| x4 | goal-high-world | light-small | goals 34/90, falls during attempt 35, contact 56 |
| x4 | goal-high-world | heavy-large | goals 49/90, falls during attempt 34, contact 56 |
| x4 | goal-low-camera | light-small | goals 9/90, falls during attempt 8, contact 14 |
| x4 | goal-low-camera | heavy-large | goals 8/90, falls during attempt 10, contact 12 |
| x4 | goal-low-world | light-small | goals 47/90, falls during attempt 32, contact 55 |
| x4 | goal-low-world | heavy-large | goals 47/90, falls during attempt 32, contact 56 |
| x4 | near-low-camera | light-small | first strike ≤ 15° 25/108, err p50 21.3°, speed p50 2.09 m/s, upright 102/108 |
| x4 | near-low-camera | heavy-large | first strike ≤ 15° 23/108, err p50 20.3°, speed p50 1.82 m/s, upright 105/108 |
| x4 | near-low-perfect | light-small | first strike ≤ 15° 3/108, err p50 31.9°, speed p50 2.62 m/s, upright 108/108 |
| x4 | near-low-perfect | heavy-large | first strike ≤ 15° 5/108, err p50 28.2°, speed p50 2.34 m/s, upright 108/108 |
| sty_power_17149 | goal-low-camera | light-small | goals 5/90, falls during attempt 10, contact 10 |
| sty_power_17149 | goal-low-camera | heavy-large | goals 9/90, falls during attempt 10, contact 10 |
| sty_power_17149 | goal-low-world | light-small | goals 33/90, falls during attempt 47, contact 41 |
| sty_power_17149 | goal-low-world | heavy-large | goals 19/90, falls during attempt 53, contact 32 |
| sty_power_17149 | near-low-camera | light-small | first strike ≤ 15° 45/108, err p50 16.3°, speed p50 2.79 m/s, upright 107/108 |
| sty_power_17149 | near-low-camera | heavy-large | first strike ≤ 15° 44/108, err p50 18.4°, speed p50 2.82 m/s, upright 106/108 |
| sty_power_17149 | near-low-perfect | light-small | first strike ≤ 15° 34/108, err p50 18.2°, speed p50 3.72 m/s, upright 107/108 |
| sty_power_17149 | near-low-perfect | heavy-large | first strike ≤ 15° 17/108, err p50 20.9°, speed p50 3.57 m/s, upright 106/108 |
