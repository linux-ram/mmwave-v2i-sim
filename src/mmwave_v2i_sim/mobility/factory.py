"""Mobility provider factory."""

from __future__ import annotations

from mmwave_v2i_sim.config.schema import ScenarioConfig
from mmwave_v2i_sim.mobility.base import MobilityProvider
from mmwave_v2i_sim.mobility.map_matched import MapMatchedMobilityProvider
from mmwave_v2i_sim.mobility.synthetic import SyntheticMobilityProvider


def build_mobility_provider(config: ScenarioConfig) -> MobilityProvider:
    mode = config.mobility.mode
    if mode == "synthetic":
        return SyntheticMobilityProvider(config)
    if mode == "map_matched":
        return MapMatchedMobilityProvider(config)
    raise ValueError(f"Unsupported mobility mode: {mode}")
