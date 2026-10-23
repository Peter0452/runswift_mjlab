"""Old module paths of code moved into ``k1``, kept so old commands, scripts
and run-log params still resolve.

An alias package calls ``alias_submodules`` from its ``__init__``: each old
submodule name then points at the moved module itself, so classes stay
identical and nothing registers twice.
"""

import importlib
import sys
from types import ModuleType


def alias_submodules(old: str, new: str, names: tuple[str, ...]) -> ModuleType:
  """Point ``old.<name>`` at ``new.<name>``; returns the ``new`` package."""
  for name in names:
    sys.modules[f"{old}.{name}"] = importlib.import_module(f"{new}.{name}")
  return importlib.import_module(new)
