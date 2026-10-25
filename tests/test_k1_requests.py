"""Task requests: schema, links to judges, implementations and subtasks, freezing."""

import shutil

import pytest
import yaml

from k1 import requests


@pytest.fixture
def tasks_copy(tmp_path, monkeypatch):
  dest = tmp_path / "tasks"
  shutil.copytree(requests.TASKS, dest)
  monkeypatch.setattr(requests, "TASKS", dest)
  return dest


def _edit(tasks, name, change):
  path = tasks / name / "request.yaml"
  req = yaml.safe_load(path.read_text())
  change(req)
  path.write_text(yaml.safe_dump(req, sort_keys=False))


def test_every_request_checks() -> None:
  assert requests.names() == ["dribble", "kick", "striker"]
  for name in requests.names():
    assert requests.check(name) == [], name


def test_striker_tree_reaches_kick() -> None:
  tree = requests.tree("striker")
  assert tree[0].startswith("striker (level 1")
  assert any(line.strip().startswith("kick (level 0") for line in tree)


def test_a_request_needs_a_safety_requirement(tasks_copy) -> None:
  def drop_safety(req):
    req["requirements"] = [r for r in req["requirements"] if r["priority"] != 0]

  _edit(tasks_copy, "kick", drop_safety)
  assert "no priority-0 (safety) requirement" in requests.check("kick")


def test_subtask_must_be_lower_level(tasks_copy) -> None:
  _edit(
    tasks_copy,
    "kick",
    lambda r: r.update(level=1, subtasks={"x": {"deployed": "a.pt"}}),
  )
  assert any("lower level" in p for p in requests.check("striker"))


def test_unknown_judge_and_wrong_implementation(tasks_copy) -> None:
  def change(req):
    req["verification"]["judge"] = "dribble_gate"

  _edit(tasks_copy, "kick", change)
  problems = requests.check("kick")
  assert any("not judged by dribble_gate" in p for p in problems)


def test_freeze_then_change_is_caught(tasks_copy) -> None:
  def no_tbd(req):
    req["budget"] = {"gpu_hours": 10}

  _edit(tasks_copy, "dribble", no_tbd)
  _edit(
    tasks_copy, "dribble",
    lambda r: [q.update(target="1.0 s") for q in r["requirements"] if "TBD" in str(q["target"])],
  )  # fmt: skip
  digest = requests.freeze("dribble")
  assert requests.load("dribble")["frozen"] == digest
  assert requests.check("dribble") == []
  _edit(tasks_copy, "dribble", lambda r: r["requirements"][0].update(target="anything"))
  assert any("make a new version" in p for p in requests.check("dribble"))
