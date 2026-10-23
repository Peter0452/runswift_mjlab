# caps

**What.** CAPS smoothness regularisers on the deterministic action: temporal (change between consecutive steps) and spatial (change under input noise), optionally weighted up near the ball.

**Source.** CAPS (Mysore et al. 2021); `src/mjlab/amp/algorithms/amp_ppo.py`.

**Where it plugs in.** `algorithm.caps_temporal_coef`, `caps_spatial_coef`, `caps_spatial_sigma`, `caps_near_ball_scale`, `caps_near_ball_dist`, `caps_ball_slot`.

**Deployment impact.** Training-only.

**Status.** experimental: on in the dribble (temporal 1.0).

**Evidence.** Dribble: CAPS 2.0 made recoveries sluggish (skills/dribble.md). Kick stage 3 v24: CAPS 1.0 with a strong foot-flat penalty made the policy stand still in front of far balls (env_cfg comment on `walk_speed`). E7: a smooth policy can be standing still.

**Pitfalls.** Track idle time when raising it; runner leg jitter is the deployed smoothness measure (dribble lineage 0.066 → ~0.10).

Registry entry: `k1/methods/registry.py` (extension points, parameter fields, `detect`).
Promotion rule and statuses: `knowledge/architecture.md`.
