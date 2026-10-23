"""Check coordinate contracts and scoring that could otherwise favour a policy."""

import math
import unittest

import numpy as np
from contracts import LEG_DEFAULT, bhuman_observation, cases, perturbation
from metrics import StrikeMeasurement


class ContractTests(unittest.TestCase):
    def test_grid_and_paired_initial_states(self):
        grid = cases()
        self.assertEqual(len(grid), 36)
        self.assertEqual(len({c.name for c in grid}), 36)
        self.assertEqual(len(cases("smoke")), 3)
        self.assertTrue(all(c in grid for c in cases("smoke")))
        yaw, q = perturbation(0)
        self.assertEqual(yaw, 0)
        np.testing.assert_array_equal(q, np.zeros(22))
        np.testing.assert_array_equal(perturbation(1)[1], perturbation(1)[1])

    def test_bhuman_layout_scale_and_direction(self):
        x = bhuman_observation(
            [0, 0, -1],
            [1, 2, 3],
            [0.8, -0.2],
            [4, 0],
            math.pi / 2,
            0.25,
            LEG_DEFAULT,
            np.ones(12),
            np.arange(13),
            [0.9, 0.1],
            3,
        )
        self.assertEqual(x.shape, (59,))
        np.testing.assert_allclose(x[:6], [0, 0, -1, 1, 2, 3])
        np.testing.assert_allclose(x[6:9], [0.08, -0.02, 0.5])
        np.testing.assert_allclose(x[9:11], [0, 1], atol=1e-7)
        np.testing.assert_allclose(x[11:23], 0)
        np.testing.assert_allclose(x[23:35], 0.1)
        np.testing.assert_allclose(x[35:48], np.arange(13))
        np.testing.assert_allclose(x[51:54], [0.2, 0, 0])
        np.testing.assert_allclose(x[54:56], [1, 0], atol=1e-7)
        np.testing.assert_allclose(x[57:], [0.09, 0.01])

    def test_moving_ball_without_contact_is_not_a_kick(self):
        m = StrikeMeasurement(0)
        m.update(0, [0, 0], [0.8, 0], False, False)
        m.update(1, [0.8, 0], [0.8, 0], False, False)
        self.assertIsNone(m.result(True)["launch_s"])

    def test_push_by_body_is_not_a_foot_launch(self):
        m = StrikeMeasurement(0)
        m.update(0, [0, 0], [0, 0], False, False)
        m.update(0.2, [0, 0], [1, 0], True, False)
        self.assertFalse(m.result(True)["foot_launch"])
        self.assertFalse(m.result(True)["successful_trial"])

    def test_second_contact_cannot_extend_first_strike(self):
        m = StrikeMeasurement(0)
        m.update(0, [0, 0], [0, 0], False, False)
        m.update(0.2, [0, 0], [1, 0], True, True)
        m.update(0.4, [0.2, 0], [1, 0], False, False)
        m.update(0.6, [0.4, 0], [2, 0], True, True)
        m.update(2, [4, 0], [2, 0], False, False)
        result = m.result(True)
        self.assertAlmostEqual(result["first_strike_forward_m"], 0.2)
        self.assertFalse(result["target_plane_hit"])
        self.assertEqual(result["contact_bouts"], 2)
        self.assertAlmostEqual(result["strongest_foot_linked_speed_m_s"], 2)
        self.assertAlmostEqual(result["first_2mps_foot_launch_s"], 0.6)

    def test_crossing_interpolation_and_fall_are_separate(self):
        m = StrikeMeasurement(0)
        m.update(0, [0, 0], [0, 0], False, False)
        m.update(0.2, [0, 0], [2, 0], True, True)
        m.update(1, [2, 0.2], [2, 0], False, False)
        m.update(2, [4, 0.4], [2, 0], False, False)
        result = m.result(False)
        self.assertAlmostEqual(result["target_plane_lateral_error_m"], 0.3)
        self.assertTrue(result["target_plane_hit"])
        self.assertFalse(result["successful_trial"])
        self.assertTrue(result["travel_censored_by_fall"])


if __name__ == "__main__":
    unittest.main()
