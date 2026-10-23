"""The kick ball every K1 ball task uses (shared default: change deliberately)."""

import os

# Ball model, chosen per run with the K1_BALL environment variable (read at
# import). "ours" (default): the 0.08 m / 0.1 kg ball with wide size and mass
# randomisation (user 2026-10-08), which every kept model was trained on.
# "bhuman": B-Human's K1 ball (MachineLearning/IsaacGymRL K1_Ball.yaml
# asset.ball), 0.095 m / 0.29 kg, solid; future training should move to it
# (user 2026-10-23).
K1_BALL = os.environ.get("K1_BALL", "ours")
if K1_BALL not in ("ours", "bhuman"):
  raise ValueError(f"K1_BALL must be 'ours' or 'bhuman', got {K1_BALL!r}")
BHUMAN_BALL = K1_BALL == "bhuman"
BALL_RADIUS = 0.095 if BHUMAN_BALL else 0.08
BALL_MASS = 0.290 if BHUMAN_BALL else 0.1
# Per-episode randomisation: radius uniform in BALL_RADIUS_RANGE, mass
# BALL_MASS * e^{2 alpha} with alpha uniform in BALL_ALPHA_RANGE
# (ours: 0.07-0.13 m, 0.05-0.45 kg; B-Human: 0.095 +- 0.01 m, 0.29 +- 0.01 kg).
BALL_RADIUS_RANGE = (0.085, 0.105) if BHUMAN_BALL else (0.07, 0.13)
BALL_ALPHA_RANGE = (-0.0175, 0.0170) if BHUMAN_BALL else (-0.347, 0.752)
# Inertia: solid sphere for B-Human's ball (Isaac Gym recomputeInertia on the
# collision sphere), thin shell for ours.
BALL_SOLID = BHUMAN_BALL
