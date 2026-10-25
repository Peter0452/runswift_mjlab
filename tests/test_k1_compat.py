"""Old module paths of moved K1 code resolve to the moved modules themselves."""

import importlib

import pytest

from k1.compat import ALIASES

SAMPLES = {
  "mjlab.tasks.bhuman_kick": "k1.tasks.bhuman",
  "mjlab.tasks.bhuman_kick.kick_command": "k1.tasks.bhuman.kick_command",
  "mjlab.asset_zoo.robots.booster_k1.k1_constants": "k1.robot.k1_constants",
  "mjlab.tasks.kick.mdp.rewards": "k1.tasks.legacy.kick.mdp.rewards",
  "k1.methods.registry": "k1.approaches.registry",
  "k1.evolve.designers": "k1.engine.designers",
}


@pytest.mark.parametrize("old", sorted(SAMPLES))
def test_old_path_is_the_new_module(old: str) -> None:
  new = importlib.import_module(SAMPLES[old])
  assert importlib.import_module(old) is new
  assert new.__spec__ is not None
  assert new.__name__ == new.__spec__.name == SAMPLES[old]


def test_every_alias_target_imports() -> None:
  for old, new in ALIASES.items():
    assert importlib.import_module(old) is importlib.import_module(new)
