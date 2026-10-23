"""Registers the K1 tasks (imported by mjlab's ``mjlab.tasks`` entry point).

Tasks move here from ``mjlab.tasks`` one family at a time; the ones not yet
moved still register from ``mjlab.tasks.velocity``, ``kick`` and ``tracking``.
"""

import k1.tasks.bhuman  # noqa: F401
import k1.tasks.legacy.kick.config.k1  # noqa: F401
