"""Packing algorithm registry: Guillotine, Shelf, MaxRects."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from mmwave_v2i_sim.sim_engine.guillotine_packer import (
    PackingResult,
    _Rect,
    _merge_free_list,
    _score_best_short_side_fit,
    _split_free_rect,
    determine_packing,
)

_MAXRECTS_BIN = (
    Path(__file__).resolve().parents[3] / "vendor" / "RectangleBinPack" / "2drbp_maxrects"
)

ALGORITHMS = ["guillotine", "shelf", "max_rects"]
ALGORITHM_LABELS = {
    "guillotine": "Guillotine Packing",
    "shelf": "Shelf Packing",
    "max_rects": "MaxRects Packing",
}


def pack(rb: tuple[int, int], items: list[tuple[int, int]], algorithm: str = "guillotine") -> PackingResult:
    if not items:
        return PackingResult(
            data=np.zeros((0, 4)),
            n_rsb_left_unpacked=0,
            ind_rsb_left_unpacked=[],
            trim_loss=0.0,
        )
    if algorithm == "shelf":
        return _shelf_pack(rb, items)
    if algorithm == "max_rects":
        return _max_rects_pack(rb, items)
    return determine_packing(rb, items)


# ---------------------------------------------------------------------------
# Shelf packer
# ---------------------------------------------------------------------------

def _shelf_pack(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    bin_w, bin_h = rb
    placed: list[tuple[int, int, int, int]] = []
    unpacked_indices: list[int] = []
    shelf_y = 0
    shelf_h = 0
    cur_x = 0

    for idx, (iw, ih) in enumerate(items, start=1):
        if cur_x + iw <= bin_w and shelf_y + ih <= bin_h:
            placed.append((cur_x, shelf_y, iw, ih))
            cur_x += iw
            shelf_h = max(shelf_h, ih)
        else:
            new_y = shelf_y + shelf_h
            if iw <= bin_w and new_y + ih <= bin_h:
                shelf_y = new_y
                shelf_h = ih
                cur_x = iw
                placed.append((0, shelf_y, iw, ih))
            else:
                unpacked_indices.append(idx)

    data = (
        np.array([[x, y, w, h] for x, y, w, h in placed], dtype=float)
        if placed
        else np.zeros((0, 4))
    )
    clean = np.array(items, dtype=float)
    for rm in sorted(unpacked_indices, reverse=True):
        clean = np.delete(clean, rm - 1, axis=0)
    bin_area = float(bin_w * bin_h)
    packed_area = float(np.sum(clean[:, 0] * clean[:, 1])) if len(clean) else 0.0
    trim_loss = float((bin_area - packed_area) / bin_area) if bin_area else 0.0

    return PackingResult(
        data=data,
        n_rsb_left_unpacked=len(unpacked_indices),
        ind_rsb_left_unpacked=unpacked_indices,
        trim_loss=trim_loss,
    )


# ---------------------------------------------------------------------------
# MaxRects packer (Best-Area-Fit, with rotation)
# ---------------------------------------------------------------------------

def _max_rects_pack(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    if _MAXRECTS_BIN.is_file():
        try:
            return _max_rects_native(rb, items)
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return _max_rects_python(rb, items)


def _max_rects_native(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    cmd = [str(_MAXRECTS_BIN), str(rb[0]), str(rb[1])]
    for w, h in items:
        cmd.extend([str(w), str(h)])
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    lines = proc.stdout.strip().splitlines()
    packed_line = lines[0].strip() if lines else ""
    unpacked: list[int] = []
    if len(lines) > 1 and lines[1].startswith("UNPACKED"):
        tail = lines[1][len("UNPACKED"):].strip()
        if tail:
            unpacked = [int(x) for x in tail.split()]
    if packed_line:
        vals = [float(x) for x in packed_line.split()]
        data = np.array(vals, dtype=float).reshape(-1, 4)
        data = data[~np.all(data == -1, axis=1)]
    else:
        data = np.zeros((0, 4))
    clean = np.array(items, dtype=float)
    for idx in sorted(unpacked, reverse=True):
        clean = np.delete(clean, idx - 1, axis=0)
    bin_area = float(rb[0] * rb[1])
    packed_area = float(np.sum(clean[:, 0] * clean[:, 1])) if len(clean) else 0.0
    trim_loss = float((bin_area - packed_area) / bin_area) if bin_area else 0.0
    return PackingResult(
        data=data,
        n_rsb_left_unpacked=len(unpacked),
        ind_rsb_left_unpacked=unpacked,
        trim_loss=trim_loss,
    )


def _max_rects_python(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    bin_w, bin_h = rb
    # Free rectangles as (x, y, w, h)
    free: list[tuple[int, int, int, int]] = [(0, 0, bin_w, bin_h)]
    placed: list[tuple[int, int, int, int]] = []
    unpacked_indices: list[int] = []

    for idx, (iw, ih) in enumerate(items, start=1):
        best_area: int | None = None
        best_pos: tuple[int, int] | None = None
        best_w, best_h = iw, ih

        for fx, fy, fw, fh in free:
            for w, h in ((iw, ih), (ih, iw)):
                if w <= fw and h <= fh:
                    area = fw * fh
                    if best_area is None or area < best_area:
                        best_area = area
                        best_pos = (fx, fy)
                        best_w, best_h = w, h

        if best_pos is None:
            unpacked_indices.append(idx)
            continue

        px, py = best_pos
        placed.append((px, py, best_w, best_h))
        new_free: list[tuple[int, int, int, int]] = []
        for rfx, rfy, rfw, rfh in free:
            if _intersects(rfx, rfy, rfw, rfh, px, py, best_w, best_h):
                if rfy < py:
                    new_free.append((rfx, rfy, rfw, py - rfy))
                if rfy + rfh > py + best_h:
                    new_free.append((rfx, py + best_h, rfw, rfy + rfh - py - best_h))
                if rfx < px:
                    new_free.append((rfx, rfy, px - rfx, rfh))
                if rfx + rfw > px + best_w:
                    new_free.append((px + best_w, rfy, rfx + rfw - px - best_w, rfh))
            else:
                new_free.append((rfx, rfy, rfw, rfh))
        free = _prune_contained(new_free)

    data = (
        np.array([[x, y, w, h] for x, y, w, h in placed], dtype=float)
        if placed
        else np.zeros((0, 4))
    )
    clean = np.array(items, dtype=float)
    for rm in sorted(unpacked_indices, reverse=True):
        clean = np.delete(clean, rm - 1, axis=0)
    bin_area = float(bin_w * bin_h)
    packed_area = float(np.sum(clean[:, 0] * clean[:, 1])) if len(clean) else 0.0
    trim_loss = float((bin_area - packed_area) / bin_area) if bin_area else 0.0
    return PackingResult(
        data=data,
        n_rsb_left_unpacked=len(unpacked_indices),
        ind_rsb_left_unpacked=unpacked_indices,
        trim_loss=trim_loss,
    )


def _intersects(ax: int, ay: int, aw: int, ah: int, bx: int, by: int, bw: int, bh: int) -> bool:
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def _prune_contained(rects: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    result = []
    for i, (ix, iy, iw, ih) in enumerate(rects):
        dominated = False
        for j, (jx, jy, jw, jh) in enumerate(rects):
            if i != j and jx <= ix and jy <= iy and jx + jw >= ix + iw and jy + jh >= iy + ih:
                if (jx, jy, jw, jh) != (ix, iy, iw, ih) or j < i:
                    dominated = True
                    break
        if not dominated:
            result.append((ix, iy, iw, ih))
    return result
