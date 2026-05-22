"""Guillotine bin packing port of determinePacking.m / 2DRBP."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_VENDOR_BIN = (
    Path(__file__).resolve().parents[3] / "vendor" / "RectangleBinPack" / "2drbp_parity"
)


@dataclass(frozen=True)
class PackingResult:
    data: np.ndarray
    n_rsb_left_unpacked: int
    ind_rsb_left_unpacked: list[int]
    trim_loss: float


@dataclass
class _Rect:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0



def determine_packing(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    if _VENDOR_BIN.is_file() and _vendor_bin_runnable():
        try:
            return _determine_packing_native(rb, items)
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return _determine_packing_python(rb, items)


def _vendor_bin_runnable() -> bool:
    """Skip macOS-only binaries when running on Linux CI or other hosts."""
    try:
        proc = subprocess.run(
            [str(_VENDOR_BIN), "1", "1", "1", "1"],
            capture_output=True,
            timeout=2,
        )
        return proc.returncode == 0 or bool(proc.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return False


def _determine_packing_native(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    cmd = [str(_VENDOR_BIN), str(rb[0]), str(rb[1])]
    for w, h in items:
        cmd.extend([str(w), str(h)])
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    lines = proc.stdout.strip().splitlines()
    packed_line = lines[0].strip() if lines else ""
    unpacked: list[int] = []
    if len(lines) > 1 and lines[1].startswith("UNPACKED"):
        tail = lines[1][len("UNPACKED") :].strip()
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


def _determine_packing_python(rb: tuple[int, int], items: list[tuple[int, int]]) -> PackingResult:
    bin_w, bin_h = rb
    pack_free = [_Rect(0, 0, bin_w, bin_h)]
    used: list[_Rect] = []
    unpacked_indices: list[int] = []

    for idx, (iw, ih) in enumerate(items, start=1):
        node, pack_free = _insert_single(pack_free, iw, ih)
        if node.width == 0 or node.height == 0:
            unpacked_indices.append(idx)
        else:
            used.append(node)

    data = (
        np.array([[r.x, r.y, r.width, r.height] for r in used], dtype=float)
        if used
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


def _insert_single(free: list[_Rect], width: int, height: int) -> tuple[_Rect, list[_Rect]]:
    best_score: int | None = None
    best_idx = 0
    best_flipped = False
    best_node = _Rect()
    found_perfect = False

    for free_idx, free_rect in enumerate(free):
        if found_perfect:
            break
        if width == free_rect.width and height == free_rect.height:
            best_idx = free_idx
            best_flipped = False
            best_node = _Rect(free_rect.x, free_rect.y, width, height)
            found_perfect = True
            break
        if height == free_rect.width and width == free_rect.height:
            best_idx = free_idx
            best_flipped = True
            best_node = _Rect(free_rect.x, free_rect.y, height, width)
            found_perfect = True
            break
        if width <= free_rect.width and height <= free_rect.height:
            score = _score_best_short_side_fit(width, height, free_rect)
            if best_score is None or score < best_score:
                best_score = score
                best_idx = free_idx
                best_flipped = False
                best_node = _Rect(free_rect.x, free_rect.y, width, height)
        if height <= free_rect.width and width <= free_rect.height:
            score = _score_best_short_side_fit(height, width, free_rect)
            if best_score is None or score < best_score:
                best_score = score
                best_idx = free_idx
                best_flipped = True
                best_node = _Rect(free_rect.x, free_rect.y, height, width)

    if best_score is None and not found_perfect:
        return _Rect(), free

    used_rect = free.pop(best_idx)
    _split_free_rect(free, used_rect, best_node)
    _merge_free_list(free)
    _ = best_flipped
    return best_node, free


def _score_best_short_side_fit(width: int, height: int, free_rect: _Rect) -> int:
    leftover_horiz = abs(free_rect.width - width)
    leftover_vert = abs(free_rect.height - height)
    return min(leftover_horiz, leftover_vert)


def _split_free_rect(free: list[_Rect], used_rect: _Rect, placed: _Rect) -> None:
    w = used_rect.width - placed.width
    h = used_rect.height - placed.height
    split_horizontal = w <= h
    bottom = _Rect(used_rect.x, used_rect.y + placed.height, 0, h)
    right = _Rect(used_rect.x + placed.width, used_rect.y, w, 0)
    if split_horizontal:
        bottom.width = used_rect.width
        right.height = placed.height
    else:
        bottom.width = placed.width
        right.height = used_rect.height
    if bottom.width > 0 and bottom.height > 0:
        free.append(bottom)
    if right.width > 0 and right.height > 0:
        free.append(right)


def _merge_free_list(free: list[_Rect]) -> None:
    i = 0
    while i < len(free):
        j = i + 1
        while j < len(free):
            a, b = free[i], free[j]
            merged = False
            if a.width == b.width and a.x == b.x:
                if a.y == b.y + b.height:
                    free[i] = _Rect(a.x, a.y - b.height, a.width, a.height + b.height)
                    free.pop(j)
                    merged = True
                elif a.y + a.height == b.y:
                    free[i] = _Rect(a.x, a.y, a.width, a.height + b.height)
                    free.pop(j)
                    merged = True
            elif a.height == b.height and a.y == b.y:
                if a.x == b.x + b.width:
                    free[i] = _Rect(a.x - b.width, a.y, a.width + b.width, a.height)
                    free.pop(j)
                    merged = True
                elif a.x + a.width == b.x:
                    free[i] = _Rect(a.x, a.y, a.width + b.width, a.height)
                    free.pop(j)
                    merged = True
            if not merged:
                j += 1
        i += 1
