"""Check walking input history, existing placements and whole-ball goal scoring."""

import json
import unittest

import numpy as np
from goal_controller import boundary_crossing, walk_observation
from goal_grid import GRID, PREFLIGHT, budget


class GoalGridTests(unittest.TestCase):
    def test_grid_pairs_and_preflight(self):
        cases = json.loads(GRID.read_text())["cases"]
        self.assertEqual(len(cases), 90)
        self.assertEqual(len({c["name"] for c in cases}), 90)
        self.assertTrue(set(PREFLIGHT).issubset(c["name"] for c in cases))
        for positive, negative in zip(cases[::2], cases[1::2], strict=True):
            self.assertEqual(positive["direction"], 1)
            self.assertEqual(negative["direction"], -1)
            for key in ("ball", "start", "yaw"):
                self.assertEqual(positive[key], negative[key])
            self.assertTrue(45 <= budget(positive) <= 115)

    def test_walk_contract_oldest_first_and_units(self):
        history = [np.full(32, i) for i in range(10)]
        obs = walk_observation(history, [0.5, -0.3, 0.6], 0.25, np.arange(12), -0.5)
        self.assertEqual(obs.shape, (344,))
        self.assertEqual(obs[0], 0)
        self.assertEqual(obs[319], 9)
        np.testing.assert_allclose(obs[320:323], [0.5, -0.3, 0.6])
        np.testing.assert_allclose(obs[323:325], [0, 1], atol=1e-7)
        np.testing.assert_allclose(obs[325:337], np.arange(12) * 0.1)
        self.assertEqual(obs[337], -0.5)
        np.testing.assert_array_equal(obs[338:], 0)

    def test_whole_ball_and_post_clearance(self):
        radius = 0.08
        self.assertIsNone(
            boundary_crossing(
                np.array([6.9, 0, radius]), np.array([7.04, 0, radius]), radius
            )
        )
        event = boundary_crossing(
            np.array([7.04, 0, radius]), np.array([7.10, 0, radius]), radius
        )
        self.assertTrue(event["inside_goal"])
        self.assertEqual(event["side"], 1)
        wide = boundary_crossing(
            np.array([7.04, 1.20, radius]), np.array([7.10, 1.20, radius]), radius
        )
        self.assertFalse(wide["inside_goal"])
        own = boundary_crossing(
            np.array([-7.04, 0, radius]), np.array([-7.10, 0, radius]), radius
        )
        self.assertEqual(own["side"], -1)

    def test_earliest_boundary_wins(self):
        event = boundary_crossing(
            np.array([7.00, 4.55, 0.08]), np.array([7.2, 4.8, 0.08]), 0.08
        )
        self.assertEqual(event["kind"], "touchline")


if __name__ == "__main__":
    unittest.main()
