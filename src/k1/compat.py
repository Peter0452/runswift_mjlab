"""Old module paths of code moved into ``k1``, kept so old commands, scripts
and run-log params still resolve.

``install()`` (run when ``k1`` is imported, which mjlab does at startup through
its ``mjlab.tasks`` entry point) puts a finder first on ``sys.meta_path`` that
serves ``<old>.<x>`` as the module ``<new>.<x>`` itself: classes stay
identical, nothing is imported twice and nothing registers twice.
"""

import importlib
import importlib.abc
import importlib.machinery
import sys
from types import ModuleType

# Old prefix -> new prefix. Add a line when a family moves.
ALIASES = {
  "mjlab.tasks.bhuman_kick": "k1.tasks.bhuman",
  "mjlab.asset_zoo.robots.booster_k1": "k1.robot",
  "mjlab.tasks.kick": "k1.tasks.legacy.kick",
  "mjlab.tasks.getup": "k1.tasks.getup",
  "mjlab.tasks.velocity": "k1.tasks.velocity",
  # Split out of velocity/mdp by family (old paths chain through the line above).
  "k1.tasks.velocity.mdp.approach": "k1.tasks.kick.mdp.approach",
  "k1.tasks.velocity.mdp.kick_loop": "k1.tasks.kick.mdp.kick_loop",
  "k1.tasks.velocity.mdp.kick_handoff": "k1.tasks.kick.mdp.kick_handoff",
  "k1.tasks.velocity.mdp.kick_prior": "k1.tasks.kick.mdp.kick_prior",
  "k1.tasks.velocity.mdp.dribble": "k1.tasks.dribble.mdp.dribble",
  "k1.tasks.velocity.mdp.dribble_rewards": "k1.tasks.dribble.mdp.dribble_rewards",
  "k1.tasks.velocity.mdp.self_play": "k1.tasks.selfplay.mdp.self_play",
  "k1.tasks.velocity.mdp.striker_skills": "k1.tasks.striker.mdp.striker_skills",
  "k1.tasks.velocity.mdp.walk_params": "k1.tasks.walk.mdp.walk_params",
  "mjlab.tasks.tracking.config.k1": "k1.tasks.legacy.tracking",
}


def _target(fullname: str) -> str | None:
  for old, new in ALIASES.items():
    if fullname == old or fullname.startswith(old + "."):
      return new + fullname[len(old) :]
  return None


class _AliasLoader(importlib.abc.Loader):
  def __init__(self, target: str) -> None:
    self.target = target

  def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
    module = importlib.import_module(self.target)
    self.real_spec, self.real_loader = module.__spec__, module.__loader__
    return module

  def exec_module(self, module: ModuleType) -> None:
    # Already executed under its new name; undo the import system's
    # overwrite of the spec so reload and tooling see the real module.
    module.__spec__ = self.real_spec
    module.__loader__ = self.real_loader


class _AliasFinder(importlib.abc.MetaPathFinder):
  def find_spec(self, fullname, path=None, target=None):
    new = _target(fullname)
    if new is None:
      return None
    return importlib.machinery.ModuleSpec(fullname, _AliasLoader(new))


def install() -> None:
  if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())
