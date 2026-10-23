"""Booster K1 robot-soccer work on mjlab: tasks, deployment contract, methods.

mjlab imports ``k1.tasks`` through its ``mjlab.tasks`` entry point, which
registers the K1 tasks. See ``knowledge/architecture.md`` for the layout.
"""

from k1 import compat

compat.install()
