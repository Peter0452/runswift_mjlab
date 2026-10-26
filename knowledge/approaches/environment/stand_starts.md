---
id: stand_starts
title: Standing starts (a share of episodes starts still in the default pose)
element: environment
also: []
tags:
- safety
- stability
- speed
status: candidate
impact: training-only
sources: []
registry: null
trial:
  genes:
    stand_start_v2: 0.3
tune:
  genes.stand_start_v2:
    range:
    - 0.1
    - 0.5
    tags:
    - safety
    - stability
    step: up
---

# Standing starts

**What.** With probability `stand_start_v2`, an episode starts with the robot
still and upright in its default pose (position and heading from the motion
reset kept, soles 2 mm above the ground) instead of mid-stride from a motion
clip (`kick_loop.stand_start`, `env_cfg.with_stand_start`).

**Why.** h022's falls are almost all start-up falls: in its full benchmark,
falls in the first 2 s are 22.3 of 24.6 % (approach/behind/world), 13.3 of
14.4 % (goal_grid/world/zero) and 6.7 of 6.7 % (goal_grid/camera). The
benchmark, and a real match after kick-off or a stop, start standing; training
never did (every reset came from moving clips).

**History.** On 2026-10-09 every child with stand starts at 0.35 collapsed
80–140 iterations in (h018/h019: ~1 s episodes ending on illegal contact), so
the event was set to 0 and its gene (`stand_start_prob`) ignored. Those
children bundled it with alive +2/s, touchdown −15 and world ball 0.3. On
2026-10-26 h022 in the training env with every episode a stand start ended 3
episodes in 512 × 15 s (10 without): the reset itself is sound, so it returned
as `stand_start_v2` (default 0, so h022's recipe is unchanged).

**Where it plugs in.** Recipe gene `stand_start_v2`.

**Deployment impact.** Training-only.

Uses: `knowledge/uses/uses.yaml`.
