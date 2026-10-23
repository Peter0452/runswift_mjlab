# ruff: noqa: I001
# Order matters: later star imports win on duplicate names, so keep it fixed.
# The family modules (kick, dribble, selfplay, striker, walk) are re-exported
# here so env configs keep using one ``mdp`` namespace.
from mjlab.envs.mdp import *  # noqa: F401, F403

from k1.tasks.walk.mdp import walk_params as walk_params  # noqa: F401
from k1.tasks.kick.mdp.approach import *  # noqa: F403
from .curriculums import *  # noqa: F403
from k1.tasks.dribble.mdp.dribble import *  # noqa: F403
from k1.tasks.dribble.mdp.dribble_rewards import *  # noqa: F403
from .events import *  # noqa: F403
from k1.tasks.kick.mdp.kick_handoff import DEFAULT_KICK_CKPTS as DEFAULT_KICK_CKPTS
from k1.tasks.kick.mdp.kick_handoff import kick_handoff_reset as kick_handoff_reset
from k1.tasks.kick.mdp.kick_loop import *  # noqa: F403
from k1.tasks.kick.mdp.kick_prior import *  # noqa: F403
from .observations import *  # noqa: F403
from .rewards import *  # noqa: F403
from k1.tasks.selfplay.mdp.self_play import ball_race as ball_race
from k1.tasks.selfplay.mdp.self_play import contest_concede as contest_concede
from k1.tasks.selfplay.mdp.self_play import contest_score as contest_score
from k1.tasks.selfplay.mdp.self_play import dribble_progress as dribble_progress
from k1.tasks.selfplay.mdp.self_play import opponent_detection as opponent_detection
from k1.tasks.selfplay.mdp.self_play import possession_change as possession_change
from k1.tasks.selfplay.mdp.self_play import territory_progress as territory_progress
from k1.tasks.selfplay.mdp.self_play import walk_engage as walk_engage
from .symmetry import mirror_joints16 as mirror_joints16
from .symmetry import nubots_symmetry as nubots_symmetry
from .terminations import *  # noqa: F403
from .velocity_command import *  # noqa: F403

# The moved modules stay reachable as attributes (``mdp.kick_loop``), as before.
from k1.tasks.dribble.mdp import dribble as dribble  # noqa: E402
from k1.tasks.dribble.mdp import dribble_rewards as dribble_rewards  # noqa: E402
from k1.tasks.kick.mdp import approach as approach  # noqa: E402
from k1.tasks.kick.mdp import kick_handoff as kick_handoff  # noqa: E402
from k1.tasks.kick.mdp import kick_loop as kick_loop  # noqa: E402
from k1.tasks.kick.mdp import kick_prior as kick_prior  # noqa: E402
from k1.tasks.selfplay.mdp import self_play as self_play  # noqa: E402
from k1.tasks.striker.mdp import striker_skills as striker_skills  # noqa: E402
