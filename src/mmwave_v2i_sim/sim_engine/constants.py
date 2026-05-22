"""MATLAB simulation constants from vehicleBinPackSimulation.m."""

from __future__ import annotations

DELTA_T = 0.16e-6
DELTA_B = 25e3
MRU = (DELTA_T, DELTA_B)
T_TOT = 1.0
B_TOT = 1e9
LAMBDA_S = 0.001
P_LOS_THRESH = 0.5
MAP_XLIM = (50.0, 1069.0)
MAP_YLIM = (-50.0, 620.0)
N_VEHICLE_OPTIONS = [1, 2, 5, 10, 50]

# Render defaults (fixed MATLAB plotArc wedge span)
BEAM_ARC_DEG = 15.0
ROUTE_SEGMENT_WINDOW = 40  # ± timesteps shown in active_segment mode
PACK_PAD = 0.06  # symmetric padding around normalized packing bin
