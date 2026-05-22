"""Deterministic baseline scheduling/packing strategy implementations."""

from __future__ import annotations

import math

from mmwave_v2i_sim.plugins.base import AllocationInput, AllocationResult, SchedulerPackingPlugin
from mmwave_v2i_sim.plugins.registry import PluginRegistry


def _total_capacity(data: AllocationInput) -> int:
    return max(data.available_time_blocks, 1) * max(data.available_freq_blocks, 1)


class MaxCqiStrategy(SchedulerPackingPlugin):
    @property
    def plugin_name(self) -> str:
        return "max_cqi"

    def allocate(self, data: AllocationInput) -> AllocationResult:
        capacity = _total_capacity(data)
        bonus = 1.15 if data.objective == "throughput" else 1.0
        scored = sorted(
            data.requests,
            key=lambda r: ((r[0] * r[1]) * bonus, r[0]),
            reverse=True,
        )
        used = 0
        accepted = 0
        for t_req, f_req in scored:
            area = t_req * f_req
            if used + area <= capacity:
                used += area
                accepted += 1
        utilization = used / capacity
        return AllocationResult(
            accepted_requests=accepted,
            rejected_requests=len(data.requests) - accepted,
            utilization=float(min(utilization, 1.0)),
        )


class ProportionalFairStrategy(SchedulerPackingPlugin):
    @property
    def plugin_name(self) -> str:
        return "proportional_fair"

    def allocate(self, data: AllocationInput) -> AllocationResult:
        capacity = _total_capacity(data)
        fairness_weight = 0.6 if data.objective == "fairness" else 1.0
        scored = sorted(
            data.requests,
            key=lambda r: abs(r[0] - r[1]) * fairness_weight,
        )
        used = 0
        accepted = 0
        for t_req, f_req in scored:
            area = t_req * f_req
            if used + area <= capacity:
                used += area
                accepted += 1
        utilization = used / capacity
        return AllocationResult(
            accepted_requests=accepted,
            rejected_requests=len(data.requests) - accepted,
            utilization=float(min(utilization, 1.0)),
        )


class LatencyAwareStrategy(SchedulerPackingPlugin):
    @property
    def plugin_name(self) -> str:
        return "latency_aware"

    def allocate(self, data: AllocationInput) -> AllocationResult:
        capacity = _total_capacity(data)
        strictness = 0.9 if data.objective == "latency_reliability" else 0.93
        scored = sorted(
            data.requests,
            key=lambda r: (r[0], -r[1]),
        )
        used = 0
        accepted = 0
        for t_req, f_req in scored:
            area = t_req * f_req
            # keep a small headroom to avoid full saturation.
            if used + area <= int(math.floor(strictness * capacity)):
                used += area
                accepted += 1
        utilization = used / capacity
        return AllocationResult(
            accepted_requests=accepted,
            rejected_requests=len(data.requests) - accepted,
            utilization=float(min(utilization, 1.0)),
        )


def register_builtin_strategies(registry: PluginRegistry) -> None:
    for strategy in [MaxCqiStrategy(), ProportionalFairStrategy(), LatencyAwareStrategy()]:
        registry.register(strategy)
