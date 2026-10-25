"""Our deploy contract matches the runner's RL development interface.

Reads ``../k1_policy_runner`` (branch dev: docs/rl-development, docs/policies,
the kick policy's constants); skipped when the runner is not present. A failure
means training and the runner disagree on what a policy sees or outputs: fix
our side, or agree a runner change and a new policy version.
"""

import re

import pytest

import mjlab.tasks  # noqa: F401
from k1.deploy import contract, intake, runner_spec
from k1.deploy.obs_layout import LAYOUTS, parse_spec_layout, spec_metadata
from mjlab.tasks.registry import load_env_cfg

pytestmark = pytest.mark.skipif(
  not runner_spec.present(), reason="k1_policy_runner (dev) not present"
)
STAGE3 = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"
SPEC_LAYOUTS = [lay for lay in LAYOUTS.values() if lay.policy_id]


def _for_joint(table: dict, joint: str):
  return next(v for pattern, v in table.items() if re.fullmatch(pattern, joint))


def test_joint_table_matches_the_contract() -> None:
  rows = runner_spec.joint_table()
  assert [r["joint"] for r in rows] == list(contract.JOINT_ORDER)
  for r in rows:
    j = r["joint"]
    assert r["default"] == pytest.approx(contract.DEFAULT_POSE.get(j, 0.0)), j
    assert r["action_scale"] == pytest.approx(_for_joint(contract.ACTION_SCALE, j)), j
    assert (r["kp"], r["kd"]) == pytest.approx(_for_joint(contract.PD_GAINS, j)), j
    limits = _for_joint(contract.DEPLOY_Q_LIMITS, j)
    assert r["q_limits"] == pytest.approx(limits), j


def test_required_metadata_is_what_the_export_writes() -> None:
  ours = {"joint_names", "default_joint_pos", "action_scale", "joint_stiffness",
          "joint_damping"} | set(spec_metadata(SPEC_LAYOUTS[0]))  # fmt: skip
  assert set(runner_spec.required_metadata()) == ours


@pytest.mark.parametrize("layout", SPEC_LAYOUTS, ids=lambda lay: lay.name)
def test_layout_matches_its_policy_spec(layout) -> None:
  spec = runner_spec.policy_spec(layout.policy_id)
  assert spec is not None, f"no runner spec {layout.policy_id}"
  assert spec["spec_version"] == layout.spec_version
  assert spec["obs_layout"] == layout.spec_layout
  entries = parse_spec_layout(spec["obs_layout"])
  assert sum(n for _, n in entries) == layout.size
  # Our blocks must start where spec entries start (a block may hold several
  # spec entries, e.g. "command" = ball_xy + ball_age; never the reverse).
  starts, total = set(), 0
  for _, n in entries:
    starts.add(total)
    total += n
  edge = 0
  for b in layout.blocks:
    assert edge in starts, f"{layout.name}: block {b.term} splits a spec entry"
    edge += b.size


@pytest.mark.parametrize("layout", SPEC_LAYOUTS, ids=lambda lay: lay.name)
def test_training_actor_inputs_follow_the_layout(layout) -> None:
  terms = list(load_env_cfg(layout.task).observations["actor"].terms)
  assert terms == [b.term for b in layout.blocks]


def test_layouts_without_a_spec_are_not_deliverable() -> None:
  for lay in LAYOUTS.values():
    if lay.policy_id is None:
      assert spec_metadata(lay) == {}
      assert runner_spec.policy_spec(lay.name) is None, (
        f"the runner now has a spec for {lay.name}: bind the layout to it"
      )


def _stage3_command():
  return load_env_cfg(STAGE3).commands["twist"]


def test_kick_lost_rule_and_memory_match_the_runner() -> None:
  c, r = _stage3_command(), runner_spec.constants()
  assert c.ball_memory and c.memory_invalidate and c.lost_virtual_ball
  assert not c.memory_odometry  # the runner has no odometry
  assert c.ball_memory_tau == r["MEMORY_TAU_S"]
  assert c.memory_lost_in_view_s == r["LOST_IN_VIEW_S"]
  assert c.memory_lost_timeout_s == r["LOST_TIMEOUT_S"]
  assert c.memory_view_range == r["LOST_VIEW_RANGE"]
  assert c.lost_virtual_bearing == r["LOST_VIRTUAL_BEARING"]
  assert c.lost_virtual_range == r["LOST_VIRTUAL_RANGE"]


def test_kick_camera_and_head_tracker_match_the_runner() -> None:
  from k1.tasks.kick import env_cfg
  from k1.tasks.kick.mdp import kick_loop

  r = runner_spec.constants()
  assert env_cfg.K1_CAMERA_HALF_FOV == pytest.approx(r["CAMERA_HALF_FOV"])
  for name in ("HEAD_PIVOT_B", "HEAD_LOOK_DOWN", "HEAD_LOST_AFTER"):
    assert getattr(kick_loop, name) == pytest.approx(r[name]), name


@pytest.mark.xfail(
  strict=True,
  reason="decision pending (2026-10-25): training samples caps up to vy 2.0, wz 3.0 "
  "(chase caps since 2026-10-23); the kick_loop_v1 spec and runner say trained "
  "vy <= 1.5, wz <= 1.5 (the h022 champion's caps)",
)
def test_kick_trained_speed_ranges_match_the_runner() -> None:
  c, r = _stage3_command(), runner_spec.constants()
  assert tuple(c.speed_cap_final) == r["SPEED_LIMIT_RANGES"]


@pytest.mark.parametrize(
  "rel",
  ["kick_loop_models/iter23.onnx", "amp_models/2026-10-17_21-58-53_softland_v1.onnx"],
)
def test_intake_of_the_runners_models(rel) -> None:
  path = runner_spec.RUNNER / rel
  if not path.is_file():
    pytest.skip(f"{rel} not present")
  # The runner's own worked example: legacy v1 models, missing the four keys.
  report = intake.intake(path)
  assert report["verdict"] == "TAKE AS LEGACY", report["report"]
