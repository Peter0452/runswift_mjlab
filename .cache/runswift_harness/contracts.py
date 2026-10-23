"""Pinned kick assets, fixed cases and B-Human's published 59-value contract.

B-Human's observation order and clipping follow the Apache-2.0 reference
WalkingEngine.cpp in bhuman/MachineLearning, revision pinned below.
"""

import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

REPOSITORIES = {
    "bhuman": (
        "bhuman/MachineLearning",
        "5d54ac1441cd3270801782dfc90ee8bdfa752f1f",
        ("IsaacGymRL",),
    ),
    "peter-training": (
        "Peter0452/runswift_mjlab",
        "b3752d979c4e8df6ad25ab64491d9c73461ba116",
        ("logs/rsl_rl/k1_kick_stage3_amp/blends", "src/mjlab", "docs"),
    ),
    "peter-runner": (
        "UNSWComputing/k1_policy_runner",
        "01c849225ca107fc40dc60ef9947d7058c1e6a07",
        ("python-implementation", "assets", "kick_loop_models"),
    ),
}
MODELS = {
    "bhuman": (
        "bhuman/IsaacGymRL/pre-trained/WalkAndKick/K1_kick_inner.onnx",
        "7fb9ea33c36e14332861025f22e92f2f4a7ae7681f4532bdd6e1e78975fe3452",
    ),
    "peter": (
        "peter-runner/kick_loop_models/k1_kick_loop_blend_x4_g004_70.onnx",
        "a7a66944702746d62b936bb941eeb856ed6266d60afc541fed2dc591eaf8b0b9",
    ),
    "peter-checkpoint": (
        "peter-training/logs/rsl_rl/k1_kick_stage3_amp/blends/x4_g004_70.pt",
        "1cdc87cb16dcceaba081a076fc670473123cb43541ade882e0722660f55f8329",
    ),
}
DEFAULT_ASSETS = Path.home() / ".cache/runswift/kick-comparison-20261006"
BALLS = {
    "light-small": {"radius_m": 0.08, "mass_kg": 0.10},
    "heavy-large": {"radius_m": 0.095, "mass_kg": 0.29},
}
LEG_DEFAULT = np.array([-0.2, 0, 0, 0.4, -0.25, 0] * 2, dtype=float)
LEG_KP = np.array([80, 80, 80, 80, 50, 60] * 2, dtype=float)
LEG_KD = np.array([4, 4, 4, 4, 2, 2] * 2, dtype=float)
LEG_EFFORT = np.array([50, 50, 30, 60, 30, 30] * 2, dtype=float)
ARM_POSE = np.array([0, -1.35, 0, 0, 0, 1.35, 0, 0], dtype=float)


@dataclass(frozen=True)
class Case:
    name: str
    ball_x: float
    ball_y: float
    heading_deg: float = 0
    range_m: float = 3
    ball_vx: float = 0
    ball_vy: float = 0


def cases(suite="full"):
    grid = [
        Case(f"near-x{x:.2f}-y{y:+.2f}-aim{a:+g}", x, y, a)
        for x in (0.4, 0.75, 1.1)
        for y in (-0.12, 0, 0.12)
        for a in (-15, 0, 15)
    ]
    grid += [
        Case(f"range-{r:g}-y{y:+.2f}", 0.75, y, range_m=r)
        for r in (6, 9)
        for y in (-0.12, 0, 0.12)
    ]
    grid += [
        Case(f"incoming-y{y:+.2f}", 0.9, y, ball_vx=-0.2) for y in (-0.12, 0, 0.12)
    ]
    if suite == "smoke":
        return [grid[4], grid[15], grid[20]]
    return grid


def perturbation(repeat):
    """Baseline, then paired small joint and yaw perturbations; no score fitting."""
    if repeat == 0:
        return 0.0, np.zeros(22)
    rng = np.random.default_rng(20261006 + repeat)
    yaw = math.radians(2 if repeat % 2 else -2)
    return yaw, rng.normal(0, 0.003, 22)


def bhuman_observation(
    gravity,
    gyro,
    ball,
    ball_velocity,
    direction,
    phase,
    q,
    dq,
    previous,
    previous_ball,
    range_m,
):
    direction = math.atan2(math.sin(direction), math.cos(direction))
    velocity = np.array(ball_velocity, dtype=float)
    velocity *= 2 / max(2, float(np.linalg.norm(velocity)))
    strong = float(range_m >= 8)
    requested_speed = (
        3.4 if strong else float(np.clip(math.sqrt(0.6 * range_m), 0.5, 3.4))
    )
    result = np.concatenate(
        [
            gravity,
            gyro,
            np.asarray(ball) * 0.1,
            [direction / math.pi],
            [math.cos(2 * math.pi * phase), math.sin(2 * math.pi * phase)],
            np.asarray(q) - LEG_DEFAULT,
            np.asarray(dq) * 0.1,
            previous,
            [strong, 0, 0],
            velocity * 0.1,
            [0],
            [math.sin(direction), math.cos(direction), requested_speed * 0.1],
            np.asarray(previous_ball) * 0.1,
        ]
    ).astype(np.float32)
    if result.shape != (59,) or not np.isfinite(result).all():
        raise ValueError("Invalid B-Human observation")
    return result


def protocol(suite, repeats, duration):
    return {
        "schema": "runswift-kick-comparison/1",
        "suite": suite,
        "cases": [asdict(c) for c in cases(suite)],
        "repeats": repeats,
        "duration_s": duration,
        "control_dt_s": 0.02,
        "physics_dt_s": 0.002,
        "settle_s": 0.4,
        "ball_profiles": BALLS,
        "truth_inputs": True,
        "seed": 20261006,
        "launch_speed_m_s": 0.5,
        "launch_velocity_change_m_s": 0.3,
        "contact_force_n": 0.2,
        "contact_lease_s": 0.15,
        "separate_contact_gap_s": 0.2,
        "launch_window_s": 0.2,
        "aim_tolerance_deg": 15,
        "target_plane_m": 3,
        "target_half_width_m": 0.5,
        "secondary_fast_foot_launch_m_s": 2.0,
        "fall": {"height_m": 0.25, "up_dot": 0.5},
        "initial_states": "Each policy's home posture, plus matched yaw/joint perturbations.",
        "first_strike": "Stops measuring travel at a later separated robot contact; falls terminate the trial.",
    }
