from __future__ import annotations

import pytest

from mmwave_v2i_sim.sim_engine.guillotine_packer import determine_packing
from mmwave_v2i_sim.sim_engine.packing import pack


# ---------------------------------------------------------------------------
# Guillotine (existing baseline)
# ---------------------------------------------------------------------------

def test_readme_packing_trim_loss() -> None:
    items = [(30, 20), (50, 20), (10, 60), (40, 20), (30, 50), (20, 30)]
    result = determine_packing((70, 80), items)
    assert result.n_rsb_left_unpacked == 0
    assert result.trim_loss == pytest.approx(500 / 5600, rel=1e-6)


def test_packing_is_deterministic() -> None:
    items = [(12, 8), (20, 10), (15, 15), (8, 20)]
    rb = (40, 30)
    a = determine_packing(rb, items)
    b = determine_packing(rb, items)
    assert a.trim_loss == b.trim_loss
    assert a.data.tolist() == b.data.tolist()


def test_unpacked_items_increase_trim_loss() -> None:
    items = [(70, 80)]
    result = determine_packing((70, 80), items)
    assert result.n_rsb_left_unpacked == 0
    assert result.trim_loss == pytest.approx(0.0, abs=1e-9)

    too_big = determine_packing((70, 80), [(80, 80)])
    assert too_big.n_rsb_left_unpacked == 1
    assert too_big.trim_loss == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Pack dispatcher smoke tests — all three algorithms
# ---------------------------------------------------------------------------

_ITEMS = [(625_000, 4_000), (2_500_000, 16_000), (1_250_000, 8_000)]
_RB = (6_250_000, 40_000)


@pytest.mark.parametrize("algorithm", ["guillotine", "shelf", "max_rects"])
def test_pack_returns_valid_trim_loss(algorithm: str) -> None:
    result = pack(_RB, _ITEMS, algorithm=algorithm)
    assert 0.0 <= result.trim_loss <= 1.0


@pytest.mark.parametrize("algorithm", ["guillotine", "shelf", "max_rects"])
def test_pack_is_deterministic(algorithm: str) -> None:
    a = pack(_RB, _ITEMS, algorithm=algorithm)
    b = pack(_RB, _ITEMS, algorithm=algorithm)
    assert a.trim_loss == b.trim_loss


@pytest.mark.parametrize("algorithm", ["guillotine", "shelf", "max_rects"])
def test_pack_empty_items(algorithm: str) -> None:
    result = pack(_RB, [], algorithm=algorithm)
    assert result.n_rsb_left_unpacked == 0
    assert result.trim_loss == 0.0


@pytest.mark.parametrize("algorithm", ["guillotine", "shelf", "max_rects"])
def test_pack_item_too_large_is_unpacked(algorithm: str) -> None:
    oversized = [(_RB[0] + 1, _RB[1] + 1)]
    result = pack(_RB, oversized, algorithm=algorithm)
    assert result.n_rsb_left_unpacked == 1
    assert result.trim_loss == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("algorithm", ["guillotine", "shelf", "max_rects"])
def test_pack_perfect_fit_zero_trim(algorithm: str) -> None:
    result = pack((100, 50), [(100, 50)], algorithm=algorithm)
    assert result.n_rsb_left_unpacked == 0
    assert result.trim_loss == pytest.approx(0.0, abs=1e-9)
