"""Old path of ``k1.robot``, the Booster K1 model (see ``k1.compat``)."""

from k1.compat import alias_submodules

_new = alias_submodules(
  __name__,
  "k1.robot",
  (
    "k1_constants",
    "k1_whirlwind_constants",
    "whirlwind_actuators",
    "whirlwind_sensors",
  ),
)


def __getattr__(name: str):
  return getattr(_new, name)
