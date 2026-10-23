"""Old path of ``k1.tasks.bhuman`` (see ``k1.compat``)."""

from k1.compat import alias_submodules

_new = alias_submodules(
  __name__,
  "k1.tasks.bhuman",
  (
    "actuator",
    "amp_style",
    "env_cfg",
    "kick_command",
    "mdp",
    "robot",
    "runner",
    "stages",
    "terrain",
  ),
)


def __getattr__(name: str):
  return getattr(_new, name)
