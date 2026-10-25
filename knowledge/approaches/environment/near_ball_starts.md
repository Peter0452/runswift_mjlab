---
id: near_ball_starts
title: Near-ball starts with the kick line anywhere (benchmark trial distribution)
element: environment
also: []
tags:
- accuracy
- speed
- perception
status: candidate
impact: training-only
sources:
- bhuman_isaacgymrl
registry: null
trial:
  genes:
    s.side_drill_prob: 0.25
    s.side_drill_ball_distance: [0.35, 1.0]
    s.side_drill_angle: [0.0, 3.1416]
tune:
  genes.s.side_drill_prob:
    range:
    - 0.1
    - 0.5
    tags:
    - accuracy
    - speed
    step: up
---

# Near-ball starts with the kick line anywhere

**What.** A share of episodes starts with the ball 0.35–1.0 m ahead (within the
spawn view, ±23°) and the kick target in any direction from the robot's
heading, as in B-Human's kick training and the runswift-spec kick benchmark
(`k1/eval/rs_kick.py`: ball 0.35–1.0 m ahead at ±30°, kick direction in four
sectors). It reuses the v52 side drill (`side_drill_*` scenario fields of the
kick command) with the target angle widened to 0–180° either side; the v52
lined-up rule change (`side_kicks`) stays off.

**Why.** The kick loop's spawns never put the ball closer than 1.0 m
(`ball_distance_range` 1–4 m). On the runswift-spec benchmark (deployed path)
h022 loses to B-Human by 0.089, mostly through 22 kicks > 45° off the command,
almost all touches 0.7–1.2 s into the trial with the ball 0.36–0.6 m away and a
side or back target, plus 10 trials with no kick (2026-10-26).

**Where it plugs in.** Recipe genes `s.side_drill_prob`,
`s.side_drill_ball_distance`, `s.side_drill_angle`.

**Deployment impact.** Training-only.

Uses: `knowledge/uses/uses.yaml`.
