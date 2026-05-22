# City presets (Boston, San Francisco, RTP)

Open-license **synthetic city extents** for the research simulation path (`core/` + `channel/`). Each preset sets geographic bounds used by lane-grid mobility and geometric 3D LOS checks against random building blocks.

| Preset key | City | Extent (m) | Config |
|------------|------|------------|--------|
| `boston_seaport` | Boston Seaport | 1200 × 800 | [`configs/scenario_city_boston.yaml`](../configs/scenario_city_boston.yaml) |
| `sfo_soma` | San Francisco SoMa | 1400 × 1000 | [`configs/scenario_city_sfo.yaml`](../configs/scenario_city_sfo.yaml) |
| `rtp_campus` | RTP Campus | 1800 × 1200 | [`configs/scenario_city_rtp.yaml`](../configs/scenario_city_rtp.yaml) |

## Run all three presets

```bash
python scripts/demo_city_presets.py
# Summary: artifacts/city_preset_summary.json
```

## Map-matched routes

Use CSV routes clipped to preset bounds:

```bash
python -m mmwave_v2i_sim.cli --config configs/scenario_legacy_research.yaml
# mobility.mode: map_matched + mobility.route_source: configs/routes_example_mapmatched.csv
```

## Default GUI path (MATLAB parity)

The desktop app uses bundled/OSM **vehicular routes** in `sim_engine`, not these presets. See [USER_GUIDE.md](USER_GUIDE.md).
