"""Typed configuration schema for deterministic simulation runs."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class CityConfig(BaseModel):
    name: str = Field(default="synthetic_grid")
    preset: str = Field(default="boston_seaport")
    length_m: float = Field(default=1000.0, gt=0)
    width_m: float = Field(default=1000.0, gt=0)


class RadioBandConfig(BaseModel):
    enabled_bands_ghz: list[float] = Field(default_factory=lambda: [28.0, 39.0])
    bandwidth_hz: float = Field(default=400e6, gt=0)
    beam_mode: str = Field(
        default="codebook",
        description="codebook (training overhead / misalignment) or ideal (upper bound)",
    )


class ScaleConfig(BaseModel):
    max_vehicles: int = Field(default=50, ge=1)
    max_base_stations: int = Field(default=4, ge=1)


class RunConfig(BaseModel):
    seed: int = 12345
    steps: int = Field(default=20, ge=1)
    timestep_s: float = Field(default=0.1, gt=0)
    scheduler_objective: str = Field(default="throughput")
    scheduler_strategy: str = Field(default="max_cqi")
    frame_phases: list[str] = Field(
        default_factory=lambda: [
            "beacon",
            "beam_training",
            "access_grant",
            "uplink_data",
        ]
    )


class RenderConfig(BaseModel):
    quality: str = Field(default="balanced", description="fast, balanced, high")
    max_draw_vehicles: int = Field(default=80, ge=1)
    max_route_points: int = Field(default=120, ge=10)


class MobilityConfig(BaseModel):
    mode: str = Field(default="route_file", description="route_file, synthetic, or map_matched")
    synthetic_style: str = Field(default="lane_grid")
    route_source: Optional[str] = Field(
        default=None,
        description="Optional CSV path for map-matched routes",
    )
    speed_mps_mean: float = Field(default=11.0, gt=0)
    speed_mps_std: float = Field(default=2.5, ge=0)


class SimConfig(BaseModel):
    engine: str = Field(default="sim_engine")
    n_vehicle: int = Field(default=10)
    seed: int = 12345
    num_trials: int = Field(default=5)
    packing_algorithm: str = Field(default="guillotine", description="guillotine, shelf, max_rects")
    p_los_thresh: float = Field(default=0.5, ge=0.0, le=1.0)
    route_display: str = Field(default="full", description="full or off")
    beam_arc_deg: float = Field(default=15.0, ge=5.0, le=60.0)


class ScenarioConfig(BaseModel):
    city: CityConfig = Field(default_factory=CityConfig)
    radio: RadioBandConfig = Field(default_factory=RadioBandConfig)
    scale: ScaleConfig = Field(default_factory=ScaleConfig)
    mobility: MobilityConfig = Field(default_factory=MobilityConfig)
    render: RenderConfig = Field(default_factory=RenderConfig)
    run: RunConfig = Field(default_factory=RunConfig)
    matlab: SimConfig = Field(default_factory=SimConfig)


def load_scenario_config(path: Path) -> ScenarioConfig:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return ScenarioConfig.model_validate(data)
