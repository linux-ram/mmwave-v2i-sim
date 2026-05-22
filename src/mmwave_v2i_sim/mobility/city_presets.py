"""Open-license city preset definitions used by mobility models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CityPreset:
    key: str
    city_name: str
    center_lat: float
    center_lon: float
    length_m: float
    width_m: float
    notes: str


CITY_PRESETS: dict[str, CityPreset] = {
    "boston_seaport": CityPreset(
        key="boston_seaport",
        city_name="Boston",
        center_lat=42.3522,
        center_lon=-71.0465,
        length_m=1200.0,
        width_m=800.0,
        notes="Dense mixed-use district suitable for urban canyon studies.",
    ),
    "sfo_soma": CityPreset(
        key="sfo_soma",
        city_name="San Francisco",
        center_lat=37.7784,
        center_lon=-122.4064,
        length_m=1400.0,
        width_m=1000.0,
        notes="Grid-like arteries and varied building heights.",
    ),
    "rtp_campus": CityPreset(
        key="rtp_campus",
        city_name="Research Triangle Park",
        center_lat=35.9074,
        center_lon=-78.8658,
        length_m=1800.0,
        width_m=1200.0,
        notes="Lower density with broader roads and open areas.",
    ),
}


def resolve_city_preset(preset_key: str) -> CityPreset:
    try:
        return CITY_PRESETS[preset_key]
    except KeyError as exc:
        available = ", ".join(sorted(CITY_PRESETS))
        raise KeyError(f"Unknown city preset '{preset_key}'. Available: {available}") from exc
