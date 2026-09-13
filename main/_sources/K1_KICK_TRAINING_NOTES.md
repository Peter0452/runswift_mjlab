# K1 Kick Training Notes

Task: `Mjlab-Kick-Booster-K1` (full kick).  
Stage-1: `Mjlab-Kick-Approach-Booster-K1` (approach ball only).  
Stage-2: `Mjlab-Kick-Near-Booster-K1` (near-ball kick, no dribble).  
Logs: `logs/rsl_rl/k1_arc_kick/` / `logs/rsl_rl/k1_kick_approach/` / `logs/rsl_rl/k1_kick_near/`.  
Train: `MUJOCO_GL=egl uv run train …` from project `.venv`.

Last updated: 2026-09-12.

---

## Goal

Robot **approaches** the ball, **aligns**, delivers a **strong kick toward the goal**,
**stays balanced**, and does **not dribble**.

---

## Stage-1: approach only (`Mjlab-Kick-Approach-Booster-K1`)

Train walking to the ball **before** enabling kick payday.

| Keep | Change |
|---|---|
| Twist tracking | **orbit** to waypoint; **face path** with FOV clamp (±0.69 rad); cruise **1.1** m/s |
| BaseWalk regularizers | far tracking `plant_far_scale=1.0` (full credit at range); fall penalties ↑ (orient −20, height −18) |
| — | `waypoint_approach` (+4), `waypoint_proximity` (+4, std 0.35), `waypoint_inv_distance` (+2) |
| — | `ball_proximity` [0.3, 0.8] (+2), `ball_touch_keepout` (−8) |
| — | `ball_camera_cone` (+0.5, soft_limit 0.69) FOV insurance |
| — | soft success: ball [0.3, 0.8] **or** waypoint &lt; 0.35 m |
| Spawn | (0.4, 4.0) m; `spawn_on_approach_side=False`; episode 15 s |

```bash
cd /workspace/runswift_mjlab && MUJOCO_GL=egl uv run train Mjlab-Kick-Approach-Booster-K1 \
  --env.scene.num-envs 8000 \
  --agent.run_name approach_v1
```

Watch: `Metrics/near_ball_reached` ↑, waypoint terms ↑.

---

## Stage-2: near kick (`Mjlab-Kick-Near-Booster-K1`)

Plant → strike → recover. Spawn one step outside the plant box.

### Payday

| Role | Term | Weight | Notes |
|---|---|---|---|
| **Plant** | `support_plant_score` | **4** | support foot: sag ~0.14 m behind, lat ~0.175 m |
| Plant still | `support_foot_planted` | 2 | |
| **Bridge** | `kick_contact_bridge` | **5** | gated on plant≥0.25; swing closing + `Δ(v·d̂)` |
| Instep | `strike_ankle_pitch` | 2 | swing ankle ~−0.5 rad at contact |
| **Main kick** | `ball_velocity_toward_goal` | **4** | `clip(v·d̂, 0, 6)` |
| Impulse | `ball_acceleration_toward_goal` | **4** | |
| Direction aux | `ball_approach_target` | 1.5 | |
| Settle | `target_reached` | 5 | |
| Balance | `post_kick_upright` | **5** | upright × height@0.52 |
| Stance | `post_kick_stance` | **4** | feet ~0.19 m × flat |
| Anti-lunge | `premature_kick_lunge` | −3 | |
| No dribble | `ball_dribble_penalty` | −8 | |

**Spawn:** (0.50, 0.70) m, approach side, `approach_spread=π/4`.  
**Plant box:** support foot lateral 0.15–0.20 m, sagittal 0.10–0.18 m behind ball.


```bash
# FT from latest approach ckpt (logs often under k1_arc_kick/)
MUJOCO_GL=egl uv run train Mjlab-Kick-Near-Booster-K1 \
  --env.scene.num-envs 8000 --agent.resume True \
  --agent.experiment-name k1_arc_kick \
  --agent.load_run <approach_run> \
  --agent.load_checkpoint model_XXXX.pt \
  --agent.run_name near_kick_from_approach
```

Watch: `Metrics/ball_vel_toward_goal` ↑, dribble penalty near 0,
strong kick / target hit ↑.

Then stage-3: full-range `Mjlab-Kick-Booster-K1`.

---

## Paper reward recipe (full kick, legacy)

| Role | Term | Weight |
|---|---|---|
| Approach | `agent_approach_ball` | 2 |
| **Kick** | `ball_approach_target` | **8** |
| Kick | `ball_acceleration_toward_goal` | 2 |
| Settle | `target_reached` | 5 |
| Balance | `post_kick_upright` (≥5 m/s) | 2 |
| No dribble | `ball_dribble_penalty` | −8 |
| Wait | `near_ball_wait` | −4 |

**Termination:** `near_ball_no_kick` (&lt;1 m for 2.5 s without kick).  
Spawn curriculum: **(0.8, 1.5) → (2.0, 3.0)** over 20k steps.

---

## Key files

- `src/mjlab/tasks/kick/arc_kick_env_cfg.py` — full + approach + `make_near_kick_env_cfg`
- `src/mjlab/tasks/kick/config/k1/` — task registration
- `tests/test_kick_approach_config.py`, `tests/test_kick_near_config.py`
