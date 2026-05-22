"""Simplified beam-management modes for dual-band channel evaluation."""

from __future__ import annotations

BEAM_MODES = ("codebook", "ideal")


def adjust_sinr_db(
    base_sinr_db: float,
    *,
    mode: str,
    vehicle_id: int,
    step: int,
) -> float:
    """Apply deterministic beam-training effects (codebook misalignment vs ideal steering)."""
    if mode not in BEAM_MODES:
        raise ValueError(f"Unknown beam mode '{mode}'. Choose from {BEAM_MODES}")
    if mode == "ideal":
        return base_sinr_db + 3.0
    misalign = (vehicle_id * 7 + step * 3) % 11
    return base_sinr_db - misalign * 0.45
