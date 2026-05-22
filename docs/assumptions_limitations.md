# Assumptions and Limitations

## Default (MATLAB parity)

- Single base station position from bundled `vehicularRoutes.mat` / `vehicular_routes.npz`
- Vehicle motion follows 50 precomputed street routes (`loadVehRouteData.m` logic)
- LoS probability uses `lambda_S = 0.001`, threshold `0.5`
- RSB dimensions from `generateRSB.m` (randomized per step; full-RB shortcut for n≤5 removed so trim loss varies at all vehicle counts)
- Guillotine packing via vendored juj/RectangleBinPack (native `2drbp_parity` or Python fallback)
- GUI shows MATLAB Figure 1 (map) and Figure 2 (packing) side-by-side

## Legacy research engine (`configs/scenario_legacy_research.yaml`)

- Synthetic lane-grid mobility and multi-BS channel abstraction remain available for experiments
- Scheduler strategies (`max_cqi`, `proportional_fair`, `latency_aware`) are not part of the original MATLAB simulator

## Out of scope

- 3GPP TR 38.901 as default channel model
- OSM city presets as default geometry
- Photorealistic 3D rendering
