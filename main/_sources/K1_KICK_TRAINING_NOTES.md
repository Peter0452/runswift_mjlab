# K1 Kick Training Notes

Task: `Mjlab-Kick-Booster-K1` (full kick).  
Stage-1: `Mjlab-Kick-Approach-Booster-K1` (approach ball only).  
Stage-2: `Mjlab-Kick-Near-Booster-K1` (near-ball kick, no dribble).  
Logs: `logs/rsl_rl/k1_arc_kick/` / `logs/rsl_rl/k1_kick_approach/` / `logs/rsl_rl/k1_kick_near/`.  
Train: `MUJOCO_GL=egl uv run train …` from project `.venv`.

Last updated: 2026-09-19.

---

## Goal

Robot **approaches** the ball, **aligns**, delivers a **strong kick toward the goal**,
**stays balanced**, and does **not dribble**.

---

## Stage-1: approach only (`Mjlab-Kick-Approach-Booster-K1`)

Train walking to the ball **before** enabling kick payday.

| Keep | Change |
|---|---|
| Twist tracking | **orbit** to waypoint; **face path** with FOV clamp (±0.69 rad); cruise **1.35** m/s; **creep** through plant |
| BaseWalk regularizers | far tracking `plant_far_scale=1.0` (full credit at range); fall penalties ↑ (orient −20, height −18) |
| — | `waypoint_approach` (+5), `waypoint_proximity` (+5, std 0.22 × facing σ=0.40), `waypoint_inv_distance` (+3) |
| — | yellow **0.15 m** behind + spawn-side **0.08–0.12 m**; keep-out **0.09 m**, released after plant latch |
| — | after latch: yellow → ball (lateral stays), `ball_velocity_toward_goal` + swing-foot strike |
| — | `ball_proximity` [0.09, 0.25] (+2), `ball_touch_keepout` (−8, 0.09 m) |
| — | `ball_camera_cone` (+0.5, soft_limit 0.69) FOV insurance |
| — | success: ball [0.09, 0.25] **or** waypoint &lt; 0.12 m; standoff **0.15** m |
| Spawn | (0.4, 4.0) m; `spawn_on_approach_side=False`; episode 15 s |

```bash
cd /workspace/runswift_mjlab && MUJOCO_GL=egl uv run train Mjlab-Kick-Approach-Booster-K1 \
  --env.scene.num-envs 8000 \
  --agent.run_name approach_v1
```

Watch: `Metrics/near_ball_reached` ↑, waypoint terms ↑.

---

## Stage-2: near kick (`Mjlab-Kick-Near-Booster-K1`)

Fine-tune the finished approach policy to **walk through the ball and kick**.
There is no explicit plant box. Built by `make_near_kick_env_cfg` on top of
approach-only, then registered in `config/k1/`.

### What this revision changed

Previous near-kick still treated yellow as a **stand-off plant** (behind the
ball, 0.10 m lateral, keep-out disk). The policy farmed that marker, backed
off when keep-out fired, and almost never latched, so kick terms stayed off.

Current near-kick does this instead:

1. **Yellow is the ball.** Standoff 0, lateral 0. Teacher, waypoint rewards,
   and play debug vis all aim at ball centre.
2. **No stand-off ring.** `ball_touch_keepout` (−8 disk) and `ball_proximity`
   ([0.09, 0.25] m) are removed so they cannot shove the robot back or fight
   walking onto the ball.
3. **Waypoint terms are progress, not magnets.** They pay heading-gated
   closing speed toward the ball. Standing still is 0; backing up is
   negative. They **turn off after latch**.
4. **Latch is the mode switch.** 0.05 s within 0.22 m of the ball and 20° of
   ball→goal. Sticky `at_plant`. One-shot `plant_latch_bonus` (+3) on the
   rising edge. After that, kick payday is allowed and waypoint payday stops.
5. **Kick foot is the spawn-inside leg**, not a fixed right foot. Facing the
   ball, both feet are the same distance from the centre, so “closer” means
   smaller offset from the ball→goal axis.
6. **`ball_velocity_toward_goal` is back** so strength scales (`clip(v·d̂, 0, 6)`,
   no decay, latch-gated). Windowed direction / speed-match still exist.

### Geometry and latch

| Knob | Value |
|---|---|
| Goal range | 8–12 m |
| Yellow | ball centre (standoff 0, lateral 0) |
| Spawn | (0.50, 0.70) m, approach side, `approach_spread=π/4` |
| Episode | 7 s (play: infinite) |
| Latch distance | 0.22 m |
| Latch facing | 20° (`cos` gate) |
| Latch hold | 0.05 s, then sticky |
| Kick foot | hip closer to ball→goal axis at spawn (`fixed_kick_side=None`) |

`Metrics/waypoint_at_plant` is the fraction currently latched.
`Metrics/plant_latch_arrival` is the rising-edge rate (same signal as the
bonus).

### Teacher (`pref_pose_twist` + tracking)

| Knob | Value |
|---|---|
| Drive target | ball (same as yellow) |
| `orbit_to_approach` | True |
| `creep_through_plant` | True, 0.25 m/s after latch |
| Close-zone heading | ball→goal when latched **or** yellow dist ≤ 0.80 m |
| Speed | fixed cruise 0.9 / min 0.30 (`use_sampled_magnitudes=False`) |
| FOV clamp | ±0.69 rad so the ball stays in camera |

Tracking weights stay 1.5 / 1.5 / 1.0. After latch the linear command keeps
walking **through** the ball (does not freeze).

### Rewards before latch

| Term | Weight | Pays |
|---|---|---|
| `waypoint_approach` | +5 | `max(0, v · d̂_ball)` × facing (`σ=0.40`); off after latch |
| `waypoint_proximity` | +5 | same closing speed × facing; off after latch |
| `waypoint_inv_distance` | +3 | signed closing speed (retreat negative); off after latch |
| `ball_camera_cone` | +0.5 | ball in FOV |
| `plant_latch_bonus` | +3 | **one step** when `at_plant` becomes 1 |

These three waypoint terms are the dense approach payday. They stay on until
latch, so a policy that walks in fast and never plants can farm them for the
whole 7 s. That is the current failure mode (see below).

`plant_latch_bonus` is meant to make crossing the latch worth losing those
terms. The function returns 0 or 1; weight 3. If `scale_rewards_by_dt` is
on (`dt=0.02`), the episode sum is only ~0.06 — much smaller than a
waypoint farm. `action_rate` is **−1.5 always** (BaseWalk); it does not
change at latch.

### Rewards after latch

| Term | Weight | Pays |
|---|---|---|
| `kicking_foot_strike` | +2 | spawn-closer foot closing speed × proximity; latch required |
| `ball_velocity_toward_goal` | +4 | `clip(v · d̂_goal, 0, 6)`, no time decay, latch required |
| `kick_direction_accuracy` | +2 | 0.3 s after detected foot–ball strike; angle Gaussian `σ=0.25` |
| `kick_speed_loose` | +2 | same 0.3 s window; `‖v‖` vs `sqrt(g R)`, relative `σ=0.35` |
| `kick_speed_tight` | +2 | same window, `σ=0.12` |
| `post_kick_upright` | +2 | after ≥1.2 m/s toward goal; 1.5 s window |
| `wrong_ball_contact` | −4 | support foot or trunk (selected foot allowed) |
| `ball_dribble_penalty` | −2 | slow motion that is not a ≥1.2 m/s kick |

Direction and both speed-match terms are **exactly zero** until a foot-contact
speed jump, then zero again after 0.3 s. They are not “faster = more”.
`ball_velocity_toward_goal` **is** speed-scaled, but capped at 6 m/s, so a
6 m/s and an 11 m/s shot pay the same on that term. Ballistic expected speed
for 8–12 m is about 8.9–10.8 m/s
(`v = sqrt(g R / sin(2θ))`, `θ=45°`). The actor `kick_range` slot carries
that expected speed in a warm-start-safe encoding.

At latch, `feet_swing`, `knee_flex_cmd_excess`, `feet_offset_x`, and
`feet_offset_y` turn off (`disable_when_planted`) so walk foot-placement
does not fight the swing.

### Walk regularizers (always on unless noted)

| Term | Weight |
|---|---|
| `tracking_lin_vel_x/y` | +1.5 / +1.5 |
| `tracking_ang_vel` | +1.0 |
| `orientation` | −18 |
| `base_height` / `trunk_height_floor` | −14 / −14 |
| `feet_offset_x/y` | −8 / −12 (off after latch) |
| `feet_swing` | +3 (off after latch) |
| `knee_flex_cmd_excess` | −2.5 (off after latch) |
| `action_rate` | −1.5 |
| `survival` | +0.15 |

### Removed on near-kick (and why)

| Term | Why |
|---|---|
| `ball_touch_keepout` | −8 disk made the robot back off before latch |
| `ball_proximity` | [0.09, 0.25] ring fought yellow-on-ball |
| `support_plant_score` / plant extras | no explicit plant stage |
| `ball_approach_target` | scale-free cosine; replaced by projected speed + windows |
| `ball_acceleration_toward_goal` | noisy; not used |
| `target_reached` / `post_kick_stance` / `near_ball_wait` | leftover settle/wait magnets |
| `kick_contact_bridge`, `strike_ankle_pitch`, `premature_kick_lunge` | over-shaped the swing |

### Terminations (train)

| Term | Notes |
|---|---|
| `time_out` | 7 s |
| `root_height` | fall / crouch |
| `near_ball_no_kick` | &lt;1 m for 5 s without a kick |
| `double_touch` | second contact in 0.10 s after kick |
| `target_hit` / `target_missed` | ball vs 1 m goal disk |

Play pops `target_hit`, `target_missed`, `double_touch`, and
`near_ball_no_kick`, and never times out, so bumps look like repeated
“hits”. That is not a kick (`kicking_foot_strike` still needs latch).

### Known failure: waypoint farming

PPO can treat walking toward yellow as the task. Those three terms pay every
step until latch; kick terms almost never fire if latch is rare. Mean reward
then climbs while `Metrics/waypoint_at_plant` collapses and
`behind_ball_distance` grows (policy stays ~2 m out). Watch latch and
`target_hit`, not mean reward.

`plant_latch_bonus` is supposed to break that, but it is one-shot and small
next to +5/+5/+3 closing speed over a full episode.

### Train / play

Logs often land under `logs/rsl_rl/k1_kick_approach/` when
`--agent.experiment-name k1_kick_approach` is set for warm-start. The
registered near-kick experiment name is `k1_kick_near`.

```bash
MUJOCO_GL=egl uv run train Mjlab-Kick-Near-Booster-K1 \
  --env.scene.num-envs 10000 --agent.resume True \
  --agent.experiment-name k1_kick_approach \
  --agent.load-run <approach_run> \
  --agent.load-checkpoint model_XXXX.pt \
  --agent.run_name near_kick_gated_v1

MUJOCO_GL=egl uv run play Mjlab-Kick-Near-Booster-K1 \
  --checkpoint-file logs/rsl_rl/k1_kick_approach/<run>/model_XXXX.pt \
  --num-envs 1 --viewer viser
```

Watch: `Metrics/waypoint_at_plant` ↑, `Metrics/plant_latch_arrival` ↑,
`Episode_Reward/ball_velocity_toward_goal` ↑, `Metrics/target_hit` ↑,
dribble near 0. Waypoint episode sums should **fall** once latch is common.

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
- `src/mjlab/tasks/kick/config/k1/` — task registration, play overrides
- `src/mjlab/tasks/kick/mdp/rewards.py` — latch bonus, strike, ball-vel, windows
- `src/mjlab/tasks/kick/mdp/geometry.py` — latch, nearest-foot kick side
- `src/mjlab/tasks/kick/mdp/events.py` — teacher, spawn foot latch
- `tests/test_kick_approach_config.py`, `tests/test_kick_near_config.py`,
  `tests/test_kick_waypoint_geometry.py`
