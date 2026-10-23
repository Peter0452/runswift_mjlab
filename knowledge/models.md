# Models

The models that matter, where their checkpoints and ONNX files are, and why
each one is kept. Checkpoint paths are under `logs/rsl_rl/`; ONNX files are in
`../k1_policy_runner/` unless stated. The deployed-model table at the end is
generated from `restructure/summary.json` (exact ONNX hash match first, then
name heuristics, labelled).

## Current best per skill

| Skill | Model | Checkpoint | ONNX | Evidence |
|---|---|---|---|---|
| Walk (gold) | wwcmu50 stageA / 9950 | `k1_velocity_amp_symmetric_muon_wwcmu50_roughft/2026-09-21_20-34-24_stageA/model_9950.pt` | `amp_models/model_9950.onnx` (byte-identical to the run's export) | user's smoothness / stability reference; 73 % flat stance; walk skill of the striker |
| Walk (alt) | wwcmu30 / 29999 | `k1_velocity_amp_symmetric_muon_wwcmu30/2026-09-20_21-17-22/model_29999.pt` | `amp_models/model_29999.onnx` | 1.06 / 1.42 / 1.72 m/s at 1.0 / 1.5 / 2.0 commands (runner sim) |
| Kick loop (champion) | h022_c2_18450 | `k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt` | `kick_loop_models/k1_kick_loop_h022_c2_18450.onnx` | promoted by the user 2026-10-09; quietest landings; runswift camera goal grid 90/90, 0 falls |
| Kick loop (runswift grid) | h012_c1_18000_x50 | `k1_kick_stage3_amp/blends/h012_c1_18000_x50.pt` | — | 170/180 official goal grid (B-Human 165); −47 on bench v2 |
| Kick loop (power) | h011_c2_17750 | `k1_kick_stage3_amp/2026-10-08_12-04-08_h011_c2/model_17750.pt` | `kick_loop_models/k1_kick_loop_h011_c2_17750.onnx` | long 3D 4.4–4.5 m/s; dribble kick teacher |
| Kick loop (robot-verified) | x4_g004_70 | `k1_kick_stage3_amp/2026-10-06_08-40-00_blend_x4_g004_70/model_14200.pt` | `kick_loop_models/k1_kick_loop_blend_x4_g004_70.onnx` | accurate on the real K1, 2026-10-06 |
| Self-play flat striker | swa_v15v16 / 9100 | `k1_kick_selfplay_amp/swa_v15v16/model_9100.pt` | `kick_loop_models/k1_kick_loop_swa_v15v16_9100.onnx` (86 inputs) | +0.019 goal share vs h022 kick, 6/6 seeds |
| Striker controller | controller_v2 / 1750 | `k1_striker_controller/2026-10-11_19-43-56_controller_v2/model_1750.pt` | — (GRU, ONNX with `h_in`/`h_out`) | 0.441 vs h022 (big eval); no retrain beat it |
| Dribble (balanced) | v51 / 11750 | `k1_dribble_amp/2026-10-23_08-22-20_dribble_aimhead_v51/model_11750.pt` | `dribble_models/k1_dribble_aimhead_v51_11750.onnx` | power 3.07 / p90 5.10, 14.6°, search 55 % |
| Dribble (kick technique) | v51 / 11250 | same run, `model_11250.pt` | `..._v51_11250.onnx` | inside foot 41 %, fastest straight kicks |
| Dribble (cleanest gates) | v51 / 10750 | same run, `model_10750.pt` | `..._v51_10750.onnx` | 3 gate fails, search 59 % |
| Dribble only (no kick mode) | swa_v17 | `k1_dribble_amp/swa_v15/swa_v17_14200-15400.pt` | `dribble_models/k1_dribble_flat_swa_v17_14200-15400.onnx` | flat-foot dribble; the v17 gate bench |
| Tracking kick | stage 2 / 99000 | `k1_kick_tracking/2026-09-29_08-23-57/model_99000.pt` | none here (the notes' `kick_tracking_models/model_85500.onnx` is not on the runner's current branch) | frozen kicker replayed by KickHandoff |
| B-Human (reference) | K1_kick_inner | `../MachineLearning/IsaacGymRL/pre-trained/WalkAndKick/K1_kick_inner.pth` | their ONNX | bench v2 0.925 in the port |

Dribble checkpoints from v20 on need the run's `DRIBBLE_GENES` to load
(`genes.json` in the run dir).

## Removed from the working tree (recoverable)

On branch `archive/pre-restructure-2026-10-23` (and the `runswift_mjlab-archive`
GitHub repo), deleted from the working tree by the user on 2026-10-23:

- `checkpoints/`: curated BaseWalk walks (`k1_basewalk_tracking_spdgate_37800`,
  `k1_basewalk_robust_rough80_39300`, `k1_basewalk_fast_track3_54299`), the
  September approach `k1_approach_plant1_65600` and the strongest legacy kick
  `k1_kick_near_stance_81800`, with a README of their lineage. These were the
  only copies of their source runs.
- `nubots_models/`: HTWK / NUbots walk ONNX exports (torso_swing, htwk_robust_ft,
  htwk_25000_terrain...). Copies of the torso-swing model are in
  `k1_policy_runner/nubots_models/`.

Restore one with `git checkout archive/pre-restructure-2026-10-23 -- <path>`.

## Deployed models in `k1_policy_runner` → source checkpoints

### `amp_models/`

| ONNX | Source checkpoint under `logs/rsl_rl/` |
|---|---|
| `model_29999.onnx` | `k1_velocity_amp_symmetric_muon_wwcmu30/2026-09-20_21-17-22/model_29999.pt` (match by name tokens) |
| `model_9950.onnx` | `k1_velocity_amp_symmetric_muon_wwcmu50_roughft/2026-09-21_20-34-24_stageA/model_9950.pt` (exact: identical export in run dir) |

### `dribble_models/`

| ONNX | Source checkpoint under `logs/rsl_rl/` |
|---|---|
| `k1_dribble_aimcurr_v46b_9750.onnx` | `k1_dribble_amp/2026-10-23_01-52-45_dribble_aimcurrb_v46b/model_9750.pt` (match by version+step) |
| `k1_dribble_aimhead_v51_10750.onnx` | `k1_dribble_amp/2026-10-23_08-22-20_dribble_aimhead_v51/model_10750.pt` |
| `k1_dribble_aimhead_v51_11250.onnx` | `k1_dribble_amp/2026-10-23_08-22-20_dribble_aimhead_v51/model_11250.pt` |
| `k1_dribble_aimhead_v51_11750.onnx` | `k1_dribble_amp/2026-10-23_08-22-20_dribble_aimhead_v51/model_11750.pt` |
| `k1_dribble_aimwide_v49_10250.onnx` | `k1_dribble_amp/2026-10-23_05-35-32_dribble_aimwide_v49/model_10250.pt` |
| `k1_dribble_aimwide_v49_9750.onnx` | `k1_dribble_amp/2026-10-23_05-35-32_dribble_aimwide_v49/model_9750.pt` |
| `k1_dribble_balanced_v39_8750.onnx` | `k1_dribble_amp/2026-10-22_05-34-23_dribble_v36cont_v39/model_8750.pt` (match by version+step) |
| `k1_dribble_deploy_swa_v16_13300-13900.onnx` | `k1_dribble_amp/swa_v15/swa_v16_13300-13900.pt` (match by name tokens)<br>`k1_dribble_amp/2026-10-19_17-44-27_dribble_deploymatch_v16/model_13900.pt` (match by version+step) |
| `k1_dribble_findball_v30_7250.onnx` | `k1_dribble_amp/2026-10-21_17-17-41_dribble_findball_v30/model_7250.pt` |
| `k1_dribble_flat_swa_v17_14200-15400.onnx` | `k1_dribble_amp/swa_v15/swa_v17_14200-15400.pt` (match by name tokens)<br>`k1_dribble_amp/2026-10-20_10-07-53_dribble_flatfoot_v17/model_15400.pt` (match by version+step) |
| `k1_dribble_headup_v50_9750.onnx` | `k1_dribble_amp/2026-10-23_07-21-01_dribble_headup_v50/model_9750.pt` |
| `k1_dribble_power_v33_7750.onnx` | `k1_dribble_amp/2026-10-21_23-01-21_dribble_power_v33/model_7750.pt` |
| `k1_dribble_push_v27_6750.onnx` | `k1_dribble_amp/2026-10-21_09-43-51_dribble_pushside_v27/model_6750.pt` (match by version+step) |
| `k1_dribble_push_v27_7250.onnx` | `k1_dribble_amp/2026-10-21_09-43-51_dribble_pushside_v27/model_7250.pt` (match by version+step) |
| `k1_dribble_safefast_v28b_7250.onnx` | `k1_dribble_amp/2026-10-21_14-09-21_dribble_safefast_v28b/model_7250.pt` |
| `k1_dribble_sidegate_v35_8250.onnx` | `k1_dribble_amp/2026-10-22_01-19-57_dribble_sidegate_v35/model_8250.pt` |
| `k1_dribble_sideteach_v36_8250.onnx` | `k1_dribble_amp/2026-10-22_02-10-44_dribble_teachstraight_v36/model_8250.pt` (match by version+step) |
| `k1_dribble_sidew_v42_8750.onnx` | `k1_dribble_amp/2026-10-22_08-42-34_dribble_sidew_v42/model_8750.pt` |
| `k1_dribble_sidew_v42_9250.onnx` | `k1_dribble_amp/2026-10-22_08-42-34_dribble_sidew_v42/model_9250.pt` |
| `k1_dribble_sidew_v42_9750.onnx` | `k1_dribble_amp/2026-10-22_08-42-34_dribble_sidew_v42/model_9750.pt` |
| `k1_dribble_skills_v25_5550.onnx` | `k1_dribble_amp/2026-10-21_03-20-16_dribble_lightteacher_v25/model_5550.pt` (match by version+step) |
| `k1_dribble_skills_v26_6250.onnx` | `k1_dribble_amp/2026-10-21_05-24-53_dribble_kickfix_v26/model_6250.pt` (match by version+step) |
| `k1_dribble_swaA_v15b_12400.onnx` | `k1_dribble_amp/swa_v15/swaA_v15b_12150-12400.pt` (match by name tokens) |

### `(top level)`

| ONNX | Source checkpoint under `logs/rsl_rl/` |
|---|---|
| `k1_v24_model_100800.onnx` | `k1_kick_approach/2026-09-19_11-36-19_near_kick_gated_v1/model_100800.pt` (probable: unique step) |

### `kick_loop_models/`

| ONNX | Source checkpoint under `logs/rsl_rl/` |
|---|---|
| `2026-10-02_17-25-32_stage3_v31.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5700.pt` (exact: identical export in run dir) |
| `2026-10-03_12-12-18_stage3_v50.onnx` | `k1_kick_stage3_amp/2026-10-03_12-12-18_stage3_v50/model_10500.pt` |
| `2026-10-03_12-51-41_stage3_v50b.onnx` | `k1_kick_stage3_amp/2026-10-03_12-51-41_stage3_v50b/model_10300.pt` |
| `k1_kick_loop_bh_prec2_18949.onnx` | `k1_kick_stage3_amp/2026-10-09_11-20-44_bh_prec2/model_18949.pt` |
| `k1_kick_loop_blend_x3_g003_60.onnx` | `k1_kick_stage3_amp/2026-10-06_06-45-00_blend_x3_g003_60/model_14200.pt` |
| `k1_kick_loop_blend_x4_g004_70.onnx` | `k1_kick_stage3_amp/2026-10-06_08-40-00_blend_x4_g004_70/model_14200.pt` |
| `k1_kick_loop_capfoot_18949.onnx` | `k1_kick_stage3_amp/2026-10-09_11-26-40_capfoot/model_18949.pt` |
| `k1_kick_loop_evo_g014_14550.onnx` | `k1_kick_stage3_amp/2026-10-06_15-25-11_evo_g014/model_14550.pt` |
| `k1_kick_loop_h001_blend.onnx` | `k1_kick_stage3_amp/blends/h001_c0_17300_x70.pt` (match by name tokens) |
| `k1_kick_loop_h007_c1_17650_x50.onnx` | `k1_kick_stage3_amp/blends/h007_c1_17650_x50.pt` (match by name tokens) |
| `k1_kick_loop_h010_c2_17850_x70.onnx` | `k1_kick_stage3_amp/blends/h010_c2_17850_x70.pt` (match by name tokens) |
| `k1_kick_loop_h011_c2_17750.onnx` | `k1_kick_stage3_amp/2026-10-08_12-04-08_h011_c2/model_17750.pt` |
| `k1_kick_loop_h012_c1_18000_x50.onnx` | `k1_kick_stage3_amp/blends/h012_c1_18000_x50.pt` (match by name tokens) |
| `k1_kick_loop_h022_c2_18450.onnx` | `k1_kick_stage3_amp/2026-10-09_07-17-43_h022_c2/model_18450.pt` |
| `k1_kick_loop_mouthnarrow_14050.onnx` | `k1_kick_stage3_amp/2026-10-16_10-18-11_h022_mouthnarrow/model_14050.pt` |
| `k1_kick_loop_sty_power_17149.onnx` | `k1_kick_stage3_amp/2026-10-07_05-08-47_sty_power/model_17149.pt` |
| `k1_kick_loop_swa_v15v16_9100.onnx` | `k1_kick_selfplay_amp/swa_v15v16/model_9100.pt` |
| `k1_kick_loop_v17_model_1800.onnx` | `k1_kick_stage3_amp/2026-10-02_08-25-15_stage3_v17/model_1800.pt` |
| `k1_kick_loop_v18_model_1950.onnx` | `k1_kick_stage3_amp/2026-10-02_12-08-27_stage3_v18/model_1950.pt` |
| `k1_kick_loop_v18_model_2150.onnx` | `k1_kick_stage3_amp/2026-10-02_12-08-27_stage3_v18/model_2150.pt` |
| `k1_kick_loop_v19_model_2300.onnx` | `k1_kick_stage3_amp/2026-10-02_12-22-54_stage3_v19/model_2300.pt` |
| `k1_kick_loop_v19_model_2500.onnx` | `k1_kick_stage3_amp/2026-10-02_12-22-54_stage3_v19/model_2500.pt` |
| `k1_kick_loop_v20_model_2350.onnx` | `k1_kick_stage3_amp/2026-10-02_12-44-00_stage3_v20/model_2350.pt` |
| `k1_kick_loop_v20_model_2550.onnx` | `k1_kick_stage3_amp/2026-10-02_12-44-00_stage3_v20/model_2550.pt` |
| `k1_kick_loop_v21_model_2500.onnx` | `k1_kick_stage3_amp/2026-10-02_13-14-11_stage3_v21/model_2500.pt` |
| `k1_kick_loop_v21_model_2650.onnx` | `k1_kick_stage3_amp/2026-10-02_13-14-11_stage3_v21/model_2650.pt` |
| `k1_kick_loop_v21_model_2800.onnx` | `k1_kick_stage3_amp/2026-10-02_13-14-11_stage3_v21/model_2800.pt` |
| `k1_kick_loop_v21_model_2950.onnx` | `k1_kick_stage3_amp/2026-10-02_13-14-11_stage3_v21/model_2950.pt` |
| `k1_kick_loop_v22_model_2900.onnx` | `k1_kick_stage3_amp/2026-10-02_13-38-50_stage3_v22/model_2900.pt` |
| `k1_kick_loop_v22_model_3000.onnx` | `k1_kick_stage3_amp/2026-10-02_13-38-50_stage3_v22/model_3000.pt` |
| `k1_kick_loop_v23_model_3100.onnx` | `k1_kick_stage3_amp/2026-10-02_13-47-46_stage3_v23/model_3100.pt` |
| `k1_kick_loop_v23_model_3150.onnx` | `k1_kick_stage3_amp/2026-10-02_13-47-46_stage3_v23/model_3150.pt` |
| `k1_kick_loop_v23_model_3250.onnx` | `k1_kick_stage3_amp/2026-10-02_13-47-46_stage3_v23/model_3250.pt` |
| `k1_kick_loop_v23_model_3350.onnx` | `k1_kick_stage3_amp/2026-10-02_13-47-46_stage3_v23/model_3350.pt` |
| `k1_kick_loop_v24_model_3450.onnx` | `k1_kick_stage3_amp/2026-10-02_14-02-06_stage3_v24/model_3450.pt` |
| `k1_kick_loop_v24_model_3550.onnx` | `k1_kick_stage3_amp/2026-10-02_14-02-06_stage3_v24/model_3550.pt` |
| `k1_kick_loop_v25_model_3550.onnx` | `k1_kick_stage3_amp/2026-10-02_14-13-20_stage3_v25/model_3550.pt` |
| `k1_kick_loop_v25_model_3650.onnx` | `k1_kick_stage3_amp/2026-10-02_14-13-20_stage3_v25/model_3650.pt` |
| `k1_kick_loop_v25_model_3750.onnx` | `k1_kick_stage3_amp/2026-10-02_14-13-20_stage3_v25/model_3750.pt` |
| `k1_kick_loop_v25_model_3850.onnx` | `k1_kick_stage3_amp/2026-10-02_14-13-20_stage3_v25/model_3850.pt` |
| `k1_kick_loop_v27_model_3800.onnx` | `k1_kick_stage3_amp/2026-10-02_14-33-18_stage3_v27/model_3800.pt` |
| `k1_kick_loop_v27_model_3900.onnx` | `k1_kick_stage3_amp/2026-10-02_14-33-18_stage3_v27/model_3900.pt` |
| `k1_kick_loop_v27_model_4050.onnx` | `k1_kick_stage3_amp/2026-10-02_14-33-18_stage3_v27/model_4050.pt` |
| `k1_kick_loop_v27_model_4150.onnx` | `k1_kick_stage3_amp/2026-10-02_14-33-18_stage3_v27/model_4150.pt` |
| `k1_kick_loop_v28_model_4150.onnx` | `k1_kick_stage3_amp/2026-10-02_14-55-07_stage3_v28/model_4150.pt` |
| `k1_kick_loop_v28_model_4250.onnx` | `k1_kick_stage3_amp/2026-10-02_14-55-07_stage3_v28/model_4250.pt` |
| `k1_kick_loop_v28_model_4400.onnx` | `k1_kick_stage3_amp/2026-10-02_14-55-07_stage3_v28/model_4400.pt` |
| `k1_kick_loop_v28_model_4500.onnx` | `k1_kick_stage3_amp/2026-10-02_14-55-07_stage3_v28/model_4500.pt` |
| `k1_kick_loop_v28_model_4650.onnx` | `k1_kick_stage3_amp/2026-10-02_14-55-07_stage3_v28/model_4650.pt` |
| `k1_kick_loop_v28_model_4750.onnx` | `k1_kick_stage3_amp/2026-10-02_14-55-07_stage3_v28/model_4750.pt` |
| `k1_kick_loop_v29_model_4500.onnx` | `k1_kick_stage3_amp/2026-10-02_16-55-34_stage3_v29/model_4500.pt` |
| `k1_kick_loop_v29_model_4600.onnx` | `k1_kick_stage3_amp/2026-10-02_16-55-34_stage3_v29/model_4600.pt` |
| `k1_kick_loop_v29_model_4750.onnx` | `k1_kick_stage3_amp/2026-10-02_16-55-34_stage3_v29/model_4750.pt` |
| `k1_kick_loop_v29_model_4850.onnx` | `k1_kick_stage3_amp/2026-10-02_16-55-34_stage3_v29/model_4850.pt` |
| `k1_kick_loop_v30_model_4900.onnx` | `k1_kick_stage3_amp/2026-10-02_17-11-37_stage3_v30/model_4900.pt` |
| `k1_kick_loop_v30_model_5000.onnx` | `k1_kick_stage3_amp/2026-10-02_17-11-37_stage3_v30/model_5000.pt` |
| `k1_kick_loop_v31_model_5150.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5150.pt` |
| `k1_kick_loop_v31_model_5250.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5250.pt` |
| `k1_kick_loop_v31_model_5300.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5300.pt` |
| `k1_kick_loop_v31_model_5350.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5350.pt` |
| `k1_kick_loop_v31_model_5400.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5400.pt` |
| `k1_kick_loop_v31_model_5450.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5450.pt` |
| `k1_kick_loop_v31_model_5500.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5500.pt` |
| `k1_kick_loop_v31_model_5700.onnx` | `k1_kick_stage3_amp/2026-10-02_17-25-32_stage3_v31/model_5700.pt` |
| `k1_kick_loop_v32_model_5650.onnx` | `k1_kick_stage3_amp/2026-10-02_17-48-20_stage3_v32/model_5650.pt` |
| `k1_kick_loop_v32_model_5750.onnx` | `k1_kick_stage3_amp/2026-10-02_17-48-20_stage3_v32/model_5750.pt` |
| `k1_kick_loop_v35_model_5950.onnx` | `k1_kick_stage3_amp/2026-10-03_00-06-53_stage3_v35/model_5950.pt` |
| `k1_kick_loop_v37_model_6350.onnx` | `k1_kick_stage3_amp/2026-10-03_00-37-18_stage3_v37/model_6350.pt` |
| `k1_kick_loop_v38_model_6800.onnx` | `k1_kick_stage3_amp/2026-10-03_01-03-24_stage3_v38/model_6800.pt` |
| `k1_kick_loop_v43_model_7550.onnx` | `k1_kick_stage3_amp/2026-10-03_02-21-32_stage3_v43/model_7550.pt` |
| `k1_kick_loop_v44_model_7800.onnx` | `k1_kick_stage3_amp/2026-10-03_02-39-19_stage3_v44/model_7800.pt` |
| `k1_kick_loop_v47_model_8300.onnx` | `k1_kick_stage3_amp/2026-10-03_03-14-12_stage3_v47/model_8300.pt` |
| `k1_kick_loop_v47_model_8700.onnx` | `k1_kick_stage3_amp/2026-10-03_03-14-12_stage3_v47/model_8700.pt` |
| `k1_kick_loop_v49_model_9900.onnx` | `k1_kick_stage3_amp/2026-10-03_10-42-58_stage3_v49/model_9900.pt` |
| `k1_kick_loop_v50_model_10400.onnx` | `k1_kick_stage3_amp/2026-10-03_12-12-18_stage3_v50/model_10400.pt` |
| `k1_kick_loop_v50d_model_10200.onnx` | `k1_kick_stage3_amp/2026-10-03_13-37-15_stage3_v50d/model_10200.pt` |
| `k1_kick_loop_v52b_model_10700.onnx` | `k1_kick_stage3_amp/2026-10-03_16-27-00_stage3_v52b/model_10700.pt` |
| `k1_kick_loop_v53_model_10450.onnx` | `k1_kick_stage3_amp/2026-10-03_17-40-12_stage3_v53/model_10450.pt` |
| `k1_kick_loop_v55b_model_12200.onnx` | `k1_kick_stage3_amp/2026-10-05_13-21-06_stage3_v55b/model_12200.pt` |
| `k1_kick_loop_v56d_model_13450.onnx` | `k1_kick_stage3_amp/2026-10-05_16-52-58_stage3_v56d/model_13450.pt` |

### Deployed with no source checkpoint here

The ONNX in `k1_policy_runner` is the only copy: `k1_v24_model_105600.onnx`, `k1_v28_model_116000.onnx`, `kick_loop_models/stage2_approach_8550.onnx`, `kick_models/model_10600.onnx`, `nubots_models/2026-08-21_06-32-23.onnx`, `nubots_models/k1_walk_htwk_k1_walk_htwk.onnx`.

Also 26 August models in `v2_models/`–`v6_models/` (robocup_s2r, k1_minimal, booster_ppo), trained before this repo existed.
