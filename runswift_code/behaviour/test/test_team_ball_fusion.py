#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from team_ball_fusion import BallEstimateInput, fuse_team_ball


def _always_inside(_x: float, _y: float) -> bool:
    return True


class TeamBallFusionTest(unittest.TestCase):
    def test_clusters_agreeing_peers(self) -> None:
        now = 10.0
        local = BallEstimateInput(
            player_id=2,
            position=np.array([1.0, 0.0]),
            velocity=np.zeros(2),
            entry_time_sec=9.8,
            valid=True,
        )
        peers = [
            BallEstimateInput(
                player_id=3,
                position=np.array([1.1, 0.05]),
                velocity=np.zeros(2),
                entry_time_sec=9.9,
                valid=True,
            ),
            BallEstimateInput(
                player_id=4,
                position=np.array([5.0, 5.0]),
                velocity=np.zeros(2),
                entry_time_sec=9.9,
                valid=True,
            ),
        ]
        est = fuse_team_ball(
            now_sec=now,
            local=local,
            peers=peers,
            peer_timeout_sec=2.0,
            local_timeout_sec=3.0,
            inside_field=_always_inside,
        )
        self.assertTrue(est.valid)
        self.assertLess(abs(est.position[0] - 1.05), 0.2)
        self.assertGreater(abs(est.position[0] - 5.0), 1.0)

    def test_stale_peer_ignored(self) -> None:
        now = 10.0
        local = BallEstimateInput(
            player_id=1,
            position=np.array([0.0, 0.0]),
            velocity=np.zeros(2),
            entry_time_sec=9.9,
            valid=True,
        )
        peers = [
            BallEstimateInput(
                player_id=2,
                position=np.array([3.0, 3.0]),
                velocity=np.zeros(2),
                entry_time_sec=5.0,
                valid=True,
            ),
        ]
        est = fuse_team_ball(
            now_sec=now,
            local=local,
            peers=peers,
            peer_timeout_sec=2.0,
            local_timeout_sec=3.0,
            inside_field=_always_inside,
        )
        self.assertTrue(est.valid)
        self.assertLess(abs(est.position[0]), 0.1)

    def test_propagates_velocity_over_receive_age(self) -> None:
        now = 10.0
        local = BallEstimateInput(
            player_id=1,
            position=np.array([0.0, 0.0]),
            velocity=np.array([1.0, 0.0]),
            entry_time_sec=9.5,
            valid=False,
        )
        peers = [
            BallEstimateInput(
                player_id=2,
                position=np.array([0.0, 0.0]),
                velocity=np.array([1.0, 0.0]),
                entry_time_sec=9.0,
                valid=True,
            ),
        ]
        est = fuse_team_ball(
            now_sec=now,
            local=local,
            peers=peers,
            peer_timeout_sec=2.0,
            local_timeout_sec=3.0,
            inside_field=_always_inside,
        )
        self.assertTrue(est.valid)
        self.assertGreater(est.position[0], 0.5)

    def test_local_survives_past_vision_timeout_with_coast(self) -> None:
        """Local estimate should stay in fusion for coast_sec, not vision timeout."""
        now = 10.0
        local = BallEstimateInput(
            player_id=1,
            position=np.array([1.0, 0.0]),
            velocity=np.zeros(2),
            entry_time_sec=8.0,
            valid=True,
        )
        short = fuse_team_ball(
            now_sec=now,
            local=local,
            peers=[],
            peer_timeout_sec=2.0,
            local_timeout_sec=1.2,
            inside_field=_always_inside,
        )
        long = fuse_team_ball(
            now_sec=now,
            local=local,
            peers=[],
            peer_timeout_sec=2.0,
            local_timeout_sec=5.0,
            inside_field=_always_inside,
        )
        self.assertFalse(short.valid)
        self.assertTrue(long.valid)
        self.assertAlmostEqual(long.position[0], 1.0, places=2)


if __name__ == "__main__":
    unittest.main()
