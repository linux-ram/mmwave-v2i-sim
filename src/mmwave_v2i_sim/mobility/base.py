"""Shared mobility data structures and protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VehicleState:
    vehicle_id: int
    x_m: float
    y_m: float
    z_m: float
    speed_mps: float


class MobilityProvider(Protocol):
    """Contract for synthetic and map-matched mobility implementations."""

    def states_at_step(self, step: int) -> list[VehicleState]:
        """Return vehicle states for a simulation step."""
