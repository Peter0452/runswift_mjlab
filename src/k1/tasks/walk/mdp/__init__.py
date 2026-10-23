"""MDP terms of the K1 AMP walk.

The shared ``k1.tasks.velocity.mdp`` namespace re-exports these modules; it is
imported first so a direct import of a module here loads in the same order as
before the split (the aggregate star-imports these modules).
"""

import k1.tasks.velocity.mdp  # noqa: F401
