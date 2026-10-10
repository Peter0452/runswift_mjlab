"""Independent scoring, contact evidence and mirrored input contracts without ROS."""

import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from math import cos, hypot, pi, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "behaviour/scripts"))
sys.path.insert(0, str(ROOT / "behaviour/examples/booster_match"))

from render_score_benchmark import render_cases
from run_score_benchmark import (
    checkpoint,
    pending_cases,
    prepare_run,
    run_lock,
    write_json,
)
from score_benchmark import (
    GRID_X,
    GRID_Y,
    BenchmarkInputs,
    cases,
    execution_budget,
    grid_cases,
    robot_starts,
    suite_cases,
    team_frame,
    validate_case,
)
from score_evaluator import GoalSpec, analyse_run, evaluate, stage_results
from world_model.adapters.booster import K1_MODEL, Frame, Robot


def rows(points, *, dt=0.05, contacts=()):
    return [
        {
            "wall_ns": round((1 + i * dt) * 1e9),
            "data": {
                "time": 10 + i * dt,
                "frame_id": i,
                "world": {
                    "ballPosition": list(p),
                    "ballContacts": [{"name": "robot1"}] if i in contacts else [],
                },
            },
        }
        for i, p in enumerate(points)
    ]


def score(values, direction=1):
    return evaluate(
        values,
        direction=direction,
        start_wall_ns=values[0]["wall_ns"],
        end_wall_ns=values[-1]["wall_ns"],
    )


class EvaluatorTest(unittest.TestCase):
    def test_whole_ball_must_cross_not_just_its_centre(self):
        self.assertIsNone(score(rows([(6.95, 0, 0.11), (7.05, 0, 0.11)]))["goal"])
        result = score(rows([(6.95, 0, 0.11), (7.2, 0, 0.11)], contacts=(1,)))
        self.assertTrue(result["goal"])
        self.assertAlmostEqual(result["first_boundary_crossing"]["time"], 10.032)
        self.assertTrue(result["contact_confirmed"])
        self.assertIsNone(result["strike_count"])

    def test_both_goal_directions_and_own_goal_are_distinct(self):
        values = rows([(-6.9, 0, 0.11), (-7.2, 0, 0.11)])
        self.assertTrue(score(values, -1)["goal"])
        self.assertEqual(score(values, 1)["outcome"], "own_goal")

    def test_post_and_crossbar_clearance_include_ball_radius(self):
        for y, z in [(1.15, 0.11), (0, 1.65), (1.3, 0.11)]:
            with self.subTest(y=y, z=z):
                self.assertFalse(score(rows([(6.9, y, z), (7.2, y, z)]))["goal"])
        self.assertTrue(score(rows([(6.9, 1.13, 1.63), (7.2, 1.13, 1.63)]))["goal"])

    def test_goal_is_latched_if_ball_rebounds_and_first_exit_wins(self):
        self.assertTrue(
            score(rows([(6.9, 0, 0.11), (7.2, 0, 0.11), (6.9, 0, 0.11)]))["goal"]
        )
        values = rows(
            [(6.9, 4.4, 0.11), (6.9, 4.7, 0.11), (6.9, 0, 0.11), (7.2, 0, 0.11)]
        )
        self.assertEqual(score(values)["outcome"], "out")

    def test_sampling_gap_or_clock_reset_cannot_prove_a_goal(self):
        values = rows([(6.9, 0, 0.11), (7.2, 0, 0.11)], dt=0.2)
        self.assertIsNone(score(values)["goal"])
        self.assertFalse(score(values)["valid"])
        values = rows([(6.9, 0, 0.11), (7.2, 0, 0.11)])
        values[-1]["data"]["time"] = 9
        self.assertFalse(score(values)["valid"])

    def test_duplicate_packet_is_not_new_evidence(self):
        values = rows([(6.9, 0, 0.11), (7.2, 0, 0.11)])
        result = score([values[0], values[0], values[1]])
        self.assertTrue(result["goal"])
        self.assertEqual(result["samples"], 2)

    def test_absent_contact_evidence_is_unknown_and_episodes_are_not_strikes(self):
        values = rows([(4, 0, 0.11)] * 45, contacts=(2, 3, 5))
        result = score(values)
        self.assertEqual(result["observed_contact_episodes"], 2)
        self.assertEqual(result["contact_windows"], 3)
        self.assertIsNone(result["foot_contact_count"])
        for row in values:
            row["data"]["world"].pop("ballContacts")
        self.assertIsNone(score(values)["contact_confirmed"])

    def test_settling_requires_progressing_time_and_fresh_coverage(self):
        values = rows([(4, 0, 0.11)] * 45)
        self.assertEqual(score(values)["outcome"], "short_or_wide")
        result = evaluate(
            values,
            direction=1,
            start_wall_ns=values[0]["wall_ns"],
            end_wall_ns=values[-1]["wall_ns"] + 1_000_000_000,
        )
        self.assertFalse(result["valid"])
        self.assertIsNone(result["goal"])
        self.assertIsNone(score(rows([(4, 0, 0.11), (4.2, 0, 0.11)]))["goal"])

    def test_invalid_or_missing_ball_never_becomes_a_miss(self):
        for value in ([float("nan"), 0, 0.11], None, [0, 0]):
            values = rows([(4, 0, 0.11), (4, 0, 0.11)])
            values[1]["data"]["world"]["ballPosition"] = value
            with self.assertRaises(ValueError):
                score(values)
        with self.assertRaises(ValueError):
            GoalSpec(ball_radius=2)


class ReplayTest(unittest.TestCase):
    def fixture(self, root):
        case = {"name": "example", "direction": 1}
        folder = root / "example"
        folder.mkdir()
        truth = rows([(6.9, 0, 0.11), (7.2, 0, 0.11)], contacts=(1,))
        controls = [
            {
                "wall_ns": truth[0]["wall_ns"],
                "result": {"intent": None},
                "stop_reason": None,
            }
        ]
        files = {}
        for name, values in (("truth.jsonl", truth), ("controller.jsonl", controls)):
            path = folder / name
            path.write_text("".join(json.dumps(v) + "\n" for v in values))
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        summary = {
            "start_wall_ns": truth[0]["wall_ns"],
            "end_wall_ns": truth[-1]["wall_ns"],
            "valid_trial": True,
            "execution_reason": "shot_departed_and_stopped",
            "files_sha256": files,
            "evaluation": {"goal": False},
        }
        (folder / "summary.json").write_text(json.dumps(summary))
        (root / "manifest.json").write_text(
            json.dumps({"geometry": vars(GoalSpec()), "cases": [case]})
        )
        return folder

    def test_offline_replay_scores_raw_truth_and_preserves_original_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = self.fixture(root)
            original = (folder / "summary.json").read_bytes()
            result = analyse_run(root)
            self.assertTrue(result["results"][0]["evaluation"]["goal"])
            self.assertEqual((folder / "summary.json").read_bytes(), original)

    def test_changed_recording_fails_hash_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = self.fixture(root)
            with (folder / "truth.jsonl").open("a") as stream:
                stream.write("{}\n")
            with self.assertRaisesRegex(ValueError, "hash changed"):
                analyse_run(root)

    def test_scoring_and_execution_fault_are_reported_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = self.fixture(root)
            path = folder / "controller.jsonl"
            value = json.loads(path.read_text())
            value["motion"] = {"failure": "sdk_feedback_stale", "stop_errors": []}
            path.write_text(json.dumps(value) + "\n")
            summary_path = folder / "summary.json"
            summary = json.loads(summary_path.read_text())
            summary["files_sha256"][path.name] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            summary_path.write_text(json.dumps(summary))
            result = analyse_run(root)["results"][0]
            self.assertTrue(result["evaluation"]["goal"])
            self.assertFalse(result["valid_trial"])
            self.assertFalse(result["benchmark_success"])


class CasesTest(unittest.TestCase):
    def test_grid_is_full_cartesian_product_with_identical_physical_starts(self):
        values = grid_cases()
        self.assertEqual(len(values), 90)
        self.assertEqual(len({c.name for c in values}), 90)
        self.assertEqual(
            {c.ball for c in values}, {(x, y) for x in GRID_X for y in GRID_Y}
        )
        self.assertEqual(len({(c.start, c.yaw) for c in values}), 5)
        for ball in {c.ball for c in values}:
            subset = [c for c in values if c.ball == ball]
            for start_id, start, yaw in robot_starts():
                pair = [c for c in subset if c.start_id == start_id]
                self.assertEqual({c.direction for c in pair}, {-1, 1})
                self.assertTrue(all((c.start, c.yaw) == (start, yaw) for c in pair))
        self.assertEqual(values, grid_cases())
        self.assertNotEqual(values, grid_cases(seed=42))

    def test_every_ball_and_goal_has_wrong_side_and_facing_away_starts(self):
        for ball in {(x, y) for x in GRID_X for y in GRID_Y}:
            for direction in (-1, 1):
                subset = [
                    c
                    for c in grid_cases()
                    if c.ball == ball and c.direction == direction
                ]
                # Projection along the ball-to-goal ray is positive on the wrong side.
                gx, gy = direction * 7 - ball[0], -ball[1]
                self.assertTrue(
                    any(
                        (c.start[0] - ball[0]) * gx + (c.start[1] - ball[1]) * gy > 0
                        for c in subset
                    )
                )
                self.assertTrue(
                    any(
                        (c.start[0] - ball[0]) * gx + (c.start[1] - ball[1]) * gy < 0
                        for c in subset
                    )
                )
                self.assertGreaterEqual(
                    sum(
                        (ball[0] - c.start[0]) * cos(c.yaw)
                        + (ball[1] - c.start[1]) * sin(c.yaw)
                        < 0
                        for c in subset
                    ),
                    4,
                )
                self.assertEqual(sum(abs(c.start[1]) >= 3.7 for c in subset), 2)
                for case in subset:
                    validate_case(case)

    def test_invalid_or_overlapping_placements_are_rejected(self):
        case = grid_cases()[0]
        for invalid in (
            replace(case, start=case.ball),
            replace(case, start=(6.9, 0)),
            replace(case, ball=(0, float("nan"))),
            replace(case, direction=0),
        ):
            with self.assertRaises(ValueError):
                validate_case(invalid)

    def test_preflight_is_a_balanced_subset_and_long_travel_has_time_to_finish(self):
        subset = suite_cases("preflight")
        self.assertEqual(len(subset), 6)
        self.assertTrue(set(subset) <= set(grid_cases()))
        self.assertEqual(sum(c.direction > 0 for c in subset), 3)
        for case in grid_cases():
            budget = execution_budget(case)
            distance = hypot(case.ball[0] - case.start[0], case.ball[1] - case.start[1])
            self.assertGreater(budget, distance / 0.2 + 10)
            self.assertLessEqual(budget, 180)
        self.assertGreater(max(map(execution_budget, subset)), 90)

    def test_cases_are_fixed_mirrored_and_require_an_approach(self):
        values = cases()
        self.assertEqual(len(values), 6)
        self.assertEqual(values, cases())
        for a, b in zip(values[:3], values[3:]):
            self.assertEqual(a.ball, tuple(-v for v in b.ball))
            self.assertEqual(a.start, tuple(-v for v in b.start))
            self.assertAlmostEqual(cos(a.yaw - b.yaw), -1)
            self.assertGreater(
                hypot(a.ball[0] - a.start[0], a.ball[1] - a.start[1]), 1.5
            )

    def test_team_rotation_preserves_time_height_and_local_ball(self):
        original = Frame(
            123, 4, (Robot("robot1", (-3, 1, 0.55), pi - 0.2, 1),), (-4, 0, 0.11)
        )
        mapped = team_frame(original, -1)
        self.assertEqual((mapped.ns, mapped.sequence, mapped.ball[2]), (123, 4, 0.11))

        def local(frame):
            r = frame.robots[0]
            x, y = frame.ball[0] - r.position[0], frame.ball[1] - r.position[1]
            return cos(r.yaw) * x + sin(r.yaw) * y, -sin(r.yaw) * x + cos(r.yaw) * y

        for a, b in zip(local(original), local(mapped)):
            self.assertAlmostEqual(a, b)
        self.assertIs(team_frame(original, 1), original)
        self.assertIsNone(team_frame(replace(original, ball=None), -1).ball)

    def test_builder_emits_scripted_permissions_with_original_capture_time(self):
        builder = BenchmarkInputs(
            "test", robot="robot1", radii={}, model=K1_MODEL, direction=-1
        )
        builder.state = "playing"
        batch = builder.build(
            Frame(0, 0, (Robot("robot1", (-3, 0, 0.55), pi, 1),), (-4, 0, 0.11))
        )
        self.assertEqual(batch.as_of.ns, 0)
        self.assertEqual(batch.events[-1].payload.state, "playing")
        self.assertEqual(batch.events[-1].meta.id.source, "scripted-referee")


class CheckpointTest(unittest.TestCase):
    def test_planned_run_can_resume_without_changing_placements_or_budgets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, selected = prepare_run(root)
            original = (root / "manifest.json").read_bytes()
            resumed, again = prepare_run(root, resume=True)
            self.assertEqual((manifest, selected), (resumed, again))
            self.assertEqual((root / "manifest.json").read_bytes(), original)
            self.assertEqual(len(pending_cases(root, resumed, again)), 90)

    def test_resume_skips_completed_failed_and_interrupted_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, selected = prepare_run(root, suite="preflight")
            for index, case in enumerate(selected[:3]):
                folder = root / case.name
                folder.mkdir()
                write_json(folder / "case.json", asdict(case))
                if index < 2:
                    write_json(
                        folder / "summary.json",
                        {
                            "case": asdict(case),
                            "execution_reason": "shot_departed_and_stopped"
                            if index == 0
                            else "trial_timeout",
                            "valid_trial": index == 0,
                            "benchmark_success": index == 0,
                            "evaluation": {"goal": index == 0},
                        },
                    )
            untouched = (root / selected[0].name / "summary.json").read_bytes()
            self.assertEqual(pending_cases(root, manifest, selected), selected[3:])
            results = checkpoint(root, manifest)
            self.assertEqual(len(results), 6)
            self.assertEqual(results[2]["execution_reason"], "interrupted")
            self.assertEqual(results[3]["execution_reason"], "not_started")
            totals = json.loads((root / "totals.json").read_text())
            self.assertEqual(
                (totals["planned"], totals["interrupted"], totals["not_started"]),
                (6, 1, 3),
            )
            self.assertEqual(
                (root / selected[0].name / "summary.json").read_bytes(), untouched
            )

    def test_resume_rejects_changed_settings_and_mismatched_case_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, selected = prepare_run(root)
            for settings in ({"seed": 42}, {"timeout": 45}, {"suite": "smoke"}):
                with self.assertRaises(ValueError):
                    prepare_run(root, resume=True, **settings)
            folder = root / selected[0].name
            folder.mkdir()
            write_json(folder / "case.json", {"name": "different"})
            with self.assertRaises(ValueError):
                pending_cases(root, manifest, selected)

    def test_a_second_writer_cannot_enter_the_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            with (
                run_lock(root),
                self.assertRaises(RuntimeError),
                run_lock(root, resume=True),
            ):
                self.fail("A second writer acquired the lock")
            with run_lock(root, resume=True):
                pass

    def test_offline_evaluation_keeps_unstarted_and_interrupted_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _manifest, selected = prepare_run(root, suite="preflight")
            (root / selected[0].name).mkdir()
            result = analyse_run(root)
            self.assertEqual(result["totals"]["planned"], 6)
            self.assertEqual(result["totals"]["unknown_or_unresolved"], 6)
            self.assertEqual(result["totals"]["interrupted"], 1)
            self.assertEqual(result["totals"]["goals_observed"], 0)

    def test_approach_shot_completion_and_goal_are_separate_metrics(self):
        controls = [{"result": {"intent": {"kick": {"power": 1.5}}}}]
        summary = {
            "start_wall_ns": 1,
            "execution_reason": "shot_departed_and_stopped",
            "controller_stopped": True,
            "evaluation": {"goal": False, "contact_confirmed": True},
        }
        stages = stage_results(summary, controls)
        self.assertEqual(stages["approach"], "kick_requested")
        self.assertTrue(stages["shot_completed"])
        self.assertTrue(stages["contact_confirmed"])
        self.assertFalse(stages["goal"])

    def test_video_keeps_all_cases_and_continues_after_missing_or_broken_recording(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _manifest, selected = prepare_run(root, suite="preflight")
            for case in selected[:3]:
                folder = root / case.name
                folder.mkdir()
                write_json(
                    folder / "summary.json", {"start_wall_ns": 1, "end_wall_ns": 2}
                )
            corrupt = root / selected[3].name
            corrupt.mkdir()
            (corrupt / "summary.json").write_text("{broken")
            output = root / "videos"
            output.mkdir()

            def clip(model, folder, output):
                if folder.name == selected[1].name:
                    raise ValueError("Corrupt physics recording")
                return {"file": folder.name + ".mp4"}

            def card(case, output, reason):
                return {
                    "file": case["name"] + "-unavailable.mp4",
                    "kind": "unavailable_card",
                    "reason": reason,
                }

            results = render_cases(
                None, root, output, render_clip=clip, render_card=card
            )
            self.assertEqual([r["case"] for r in results], [c.name for c in selected])
            self.assertEqual(
                [r["kind"] for r in results[:3]],
                ["recorded_physics", "unavailable_card", "recorded_physics"],
            )
            self.assertEqual(results[-1]["reason"], "not_started")
            self.assertEqual(results[3]["kind"], "unavailable_card")


if __name__ == "__main__":
    unittest.main()
