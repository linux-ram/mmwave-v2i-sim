"""Research plugin contracts for plug-and-play model components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AllocationInput:
    available_time_blocks: int
    available_freq_blocks: int
    requests: list[tuple[int, int]]
    objective: str


@dataclass(frozen=True)
class AllocationResult:
    accepted_requests: int
    rejected_requests: int
    utilization: float


class SchedulerPackingPlugin(ABC):
    """Interface for runtime-selectable scheduler/packing strategies."""

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def allocate(self, data: AllocationInput) -> AllocationResult:
        raise NotImplementedError
