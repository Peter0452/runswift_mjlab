# Selected K1 checkpoints

Picked from TensorBoard last-window / peak-window metrics. Each file is ~2.2 MB.

| File | Task | Why this one |
|---|---|---|
| `k1_basewalk_tracking_spdgate_37800.pt` | `Mjlab-Velocity-Flat-Booster-K1-BaseWalk` | Best tracking window on `spd_gate_trk` (smooth `tracking_lin_vel_x` ≈ 0.98 @ 37800). |
| `k1_basewalk_robust_rough80_39300.pt` | `Mjlab-Velocity-Rough-Booster-K1-BaseWalk` | Rough-terrain FT from the speed-gate walker (`rough80_trk`). |
| `k1_basewalk_fast_track3_54299.pt` | BaseWalk rough mix, `vx ∈ [-1.3, 2.0]` | Latest trained walk: survived rough FT, recovered tracking (~1.05 late), wide speed range. Default play/warm-start. |
| `k1_approach_plant1_65600.pt` | `Mjlab-Kick-Approach-Booster-K1` | End of the approach lineage (`… → fovpath 60000 → plant1 65600`). Best late tracking among approach runs; source for near-kick FT. |
| `k1_kick_near_stance_81800.pt` | `Mjlab-Kick-Near-Booster-K1` | Strongest measured kick (`ball_vel_toward_goal` peak ≈ 2.0 @ 81900). Same step as `logs/kick_kinematics/stance_81800`. |

## Lineage

```
spd_gate 37800  →  rough80 39300  →  track3 54299
                                      ↓
                         kick warm-start (walk 42600 mid-run)
                                      ↓
                         approach … → plant1 65600
                                      ↓
                         near-kick … → stance 81800
```

## Play

```bash
# walk
MUJOCO_GL=egl uv run play Mjlab-Velocity-Flat-Booster-K1-BaseWalk \
  --checkpoint-file checkpoints/k1_basewalk_fast_track3_54299.pt --num-envs 1 --viewer viser

# approach
MUJOCO_GL=egl uv run play Mjlab-Kick-Approach-Booster-K1 \
  --checkpoint-file checkpoints/k1_approach_plant1_65600.pt --num-envs 1 --viewer viser

# near kick
MUJOCO_GL=egl uv run play Mjlab-Kick-Near-Booster-K1 \
  --checkpoint-file checkpoints/k1_kick_near_stance_81800.pt --num-envs 1 --viewer viser
```
