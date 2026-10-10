"""Fuse local and teammate ball estimates (BHuman TeamBallModel-inspired)."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ball_physics import DEFAULT_BALL_FRICTION, propagate_ball_position_and_velocity

CLUSTER_RADIUS_M = 0.8
DEFAULT_PEER_POSE_QUALITY = 0.75
DEFAULT_LOCAL_POSE_QUALITY = 1.0


@dataclass
class BallEstimateInput:
    """One robot's ball state for fusion."""

    player_id: int
    position: np.ndarray
    velocity: np.ndarray
    entry_time_sec: float
    valid: bool
    pose_quality: float = DEFAULT_PEER_POSE_QUALITY


@dataclass
class TeamBallEstimate:
    valid: bool
    position: np.ndarray
    velocity: np.ndarray
    last_seen_sec: float
    newer_than_local: bool


def _recency_weight(age_sec: float, timeout_sec: float) -> float:
    if timeout_sec <= 0.0 or age_sec >= timeout_sec:
        return 0.0
    relative = age_sec / timeout_sec
    return 1.0 - math.tanh(relative * 2.0)


def _propagate_state(
    position: np.ndarray,
    velocity: np.ndarray,
    dt: float,
    friction: float,
) -> tuple[np.ndarray, np.ndarray]:
    pos = np.asarray(position, dtype=float).copy()
    vel = np.asarray(velocity, dtype=float).copy()
    if dt > 1e-6:
        propagate_ball_position_and_velocity(pos, vel, dt, friction)
    return pos, vel


def _cluster_indices(positions: list[np.ndarray], radius_m: float) -> list[list[int]]:
    n = len(positions)
    if n == 0:
        return []
    compatible: list[list[int]] = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if float(np.linalg.norm(positions[i] - positions[j])) <= radius_m:
                compatible[i].append(j)
                compatible[j].append(i)
    return compatible


def fuse_team_ball(
    *,
    now_sec: float,
    local: BallEstimateInput,
    peers: list[BallEstimateInput],
    peer_timeout_sec: float,
    local_timeout_sec: float,
    friction: float = DEFAULT_BALL_FRICTION,
    cluster_radius_m: float = CLUSTER_RADIUS_M,
    inside_field,
) -> TeamBallEstimate:
    """Weighted cluster fusion; peer times are receive times on this robot's clock."""
    active: list[tuple[BallEstimateInput, float, np.ndarray, np.ndarray]] = []

    def consider(entry: BallEstimateInput, timeout_sec: float) -> None:
        if not entry.valid:
            return
        age = now_sec - entry.entry_time_sec
        if age < 0.0 or age > timeout_sec:
            return
        pos, vel = _propagate_state(entry.position, entry.velocity, age, friction)
        if not inside_field(pos[0], pos[1]):
            return
        weight = _recency_weight(age, timeout_sec) * entry.pose_quality
        if weight <= 0.0:
            return
        active.append((entry, weight, pos, vel))

    consider(local, local_timeout_sec)
    for peer in peers:
        consider(peer, peer_timeout_sec)

    if not active:
        return TeamBallEstimate(
            valid=False,
            position=np.zeros(2, dtype=float),
            velocity=np.zeros(2, dtype=float),
            last_seen_sec=0.0,
            newer_than_local=False,
        )

    positions = [item[2] for item in active]
    compatible = _cluster_indices(positions, cluster_radius_m)

    best_cluster: list[int] = []
    best_weight_sum = -1.0
    for seed in range(len(active)):
        cluster = {seed}
        stack = [seed]
        while stack:
            idx = stack.pop()
            for other in compatible[idx]:
                if other not in cluster:
                    cluster.add(other)
                    stack.append(other)
        weight_sum = sum(active[i][1] for i in cluster)
        if len(cluster) > len(best_cluster) or (
            len(cluster) == len(best_cluster) and weight_sum > best_weight_sum
        ):
            best_cluster = sorted(cluster)
            best_weight_sum = weight_sum

    weight_sum = 0.0
    avg_pos = np.zeros(2, dtype=float)
    avg_vel = np.zeros(2, dtype=float)
    last_seen = 0.0
    local_entry_time = local.entry_time_sec if local.valid else 0.0
    best_peer_time = 0.0

    for idx in best_cluster:
        entry, weight, pos, vel = active[idx]
        weight_sum += weight
        avg_pos += pos * weight
        avg_vel += vel * weight
        last_seen = max(last_seen, entry.entry_time_sec)
        if entry.player_id != local.player_id:
            best_peer_time = max(best_peer_time, entry.entry_time_sec)

    if weight_sum <= 0.0:
        return TeamBallEstimate(
            valid=False,
            position=np.zeros(2, dtype=float),
            velocity=np.zeros(2, dtype=float),
            last_seen_sec=0.0,
            newer_than_local=False,
        )

    avg_pos /= weight_sum
    avg_vel /= weight_sum
    local_age = now_sec - local_entry_time if local.valid else float("inf")
    peer_age = now_sec - best_peer_time if best_peer_time > 0.0 else float("inf")
    newer_than_local = peer_age < local_age

    return TeamBallEstimate(
        valid=True,
        position=avg_pos,
        velocity=avg_vel,
        last_seen_sec=last_seen,
        newer_than_local=newer_than_local,
    )
