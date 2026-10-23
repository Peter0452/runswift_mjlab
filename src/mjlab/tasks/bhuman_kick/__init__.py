"""Old path of ``k1.tasks.bhuman``, kept so old commands and run logs resolve.

Each old submodule name points at the moved module itself, so classes stay
identical and the tasks register once.
"""

import sys

import k1.tasks.bhuman
from k1.tasks.bhuman import (
  actuator,
  amp_style,
  env_cfg,
  kick_command,
  mdp,
  robot,
  runner,
  stages,
  terrain,
)

for _module in (
  actuator,
  amp_style,
  env_cfg,
  kick_command,
  mdp,
  robot,
  runner,
  stages,
  terrain,
):
  sys.modules[f"{__name__}.{_module.__name__.rsplit('.', 1)[1]}"] = _module


def __getattr__(name: str):
  return getattr(k1.tasks.bhuman, name)
