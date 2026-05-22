---
name: m5 — 3D viewport and live KPI panel
about: Post-v0.1 milestone for professional GUI enhancements
title: "[m5] 3D viewport and live KPI side panel"
labels: milestone:m5, enhancement
---

## Goal

Extend the desktop GUI beyond the current 2D MATLAB-parity matplotlib views.

## Acceptance criteria

- [ ] Optional 3D city viewport (e.g. PyVista) with vehicles, BS, and beam overlays
- [ ] Right-side live KPI panel wired from `ui/viewmodel.py` (utilization, LoS ratio, per-step metrics)
- [ ] KPI values match exported session metrics at the same step index
- [ ] Playback controls remain functional with new viewport

## Context

v0.1 ships 2D Figure 1/2 layout in `ui/app.py` + `sim_engine/visualize.py`. See `docs/MILESTONE_STATUS.md`.
