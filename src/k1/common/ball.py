"""The kick ball every K1 ball task uses (shared default: change deliberately)."""

import os

# B-Human's K1 ball (MachineLearning/IsaacGymRL K1_Ball.yaml asset.ball),
# 0.095 m / 0.29 kg, solid: the only ball since 2026-10-28 (user: "get rid of
# the old ball, and use bhuman ball ever since now"). Our old 0.08 m / 0.1 kg
# ball with wide size and mass randomisation (every model up to S8 / u4 was
# trained on it) is removed; K1_BALL is kept only to refuse old run setups.
K1_BALL = os.environ.get("K1_BALL") or "bhuman"
if K1_BALL != "bhuman":
  raise ValueError(
    f"K1_BALL={K1_BALL!r}: our old ball was removed on 2026-10-28; "
    "B-Human's ball is the only ball (unset K1_BALL or set it to 'bhuman')"
  )
BALL_RADIUS = 0.095
BALL_MASS = 0.290
# Per-episode randomisation: radius uniform in BALL_RADIUS_RANGE, mass
# BALL_MASS * e^{2 alpha} with alpha uniform in BALL_ALPHA_RANGE
# (0.095 +- 0.01 m, 0.29 +- 0.01 kg).
BALL_RADIUS_RANGE = (0.085, 0.105)
BALL_ALPHA_RANGE = (-0.0175, 0.0170)
# Inertia: solid sphere (Isaac Gym recomputeInertia on the collision sphere).
BALL_SOLID = True
