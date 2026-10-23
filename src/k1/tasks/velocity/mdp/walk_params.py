"""ParameterWalk-derived gait parameters for mjlab velocity tasks.

Source: ``runswift-gym/envs/K1/Parameter_Walk.yaml`` commands / rewards.
"""

from __future__ import annotations

# commands.gait_frequency [Hz]
GAIT_FREQUENCY_RANGE: tuple[float, float] = (1.5, 2.4)

# Forced-obs / deploy default used by Gym parameter_walk.py and
# k1_policy_runner parameter_walk_policy (Hz).
GAIT_FREQUENCY_DEFAULT: float = 1.9

# rewards.swing_period — fraction of gait cycle for each swing window.
SWING_PERIOD: float = 0.2
