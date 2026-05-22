"""Deprecated: use mmwave_v2i_sim.sim_engine."""

import warnings

warnings.warn(
    "mmwave_v2i_sim.matlab_port is deprecated; use mmwave_v2i_sim.sim_engine",
    DeprecationWarning,
    stacklevel=2,
)

from mmwave_v2i_sim.sim_engine import *  # noqa: F403
