"""Registers the K1 tasks (imported by mjlab's ``mjlab.tasks`` entry point).

Every K1 task registers from here; the old ``mjlab.tasks.*`` module paths are
served by ``k1.compat``.
"""

import k1.tasks.bhuman  # noqa: F401
import k1.tasks.dribble.tasks  # noqa: F401
import k1.tasks.getup.config.k1  # noqa: F401
import k1.tasks.kick.tasks  # noqa: F401
import k1.tasks.legacy.kick.config.k1  # noqa: F401
import k1.tasks.legacy.tracking  # noqa: F401
import k1.tasks.selfplay.tasks  # noqa: F401
import k1.tasks.striker.tasks  # noqa: F401
import k1.tasks.velocity.config.k1  # noqa: F401
import k1.tasks.walk.tasks  # noqa: F401
