"""Exact sector-transform helpers for pi-fs research notes.

The functions here use rational arithmetic and half-open integer ranges. They
are intentionally small reference utilities, not part of the FUSE filesystem
runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class SectorInterval:
    """A half-open sector interval [left, right)."""

    left: Fraction
    right: Fraction


@dataclass(frozen=True)
class TransformCells:
    """Target-cell ranges for one source sector transform.

    Ranges use Python's half-open convention. For example, range(0, 2) means
    cells 0 and 1.
    """

    intersecting: range
    contained: range
    boundary: tuple[range, ...]


def _require_positive_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_nonnegative_int(name: str, value: int) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


def ceil_div(a: int, b: int) -> int:
    """Return ceil(a / b) for integers with b > 0."""

    _require_positive_int("b", b)
    return -(-a // b)


def ceil_fraction(value: Fraction) -> int:
    """Return ceil(value) exactly."""

    return ceil_div(value.numerator, value.denominator)


def floor_fraction(value: Fraction) -> int:
    """Return floor(value) exactly."""

    return value.numerator // value.denominator


def sector_count(q: int, depth: int) -> int:
    """Return q**depth after validating a sector grid."""

    _require_positive_int("q", q)
    _require_nonnegative_int("depth", depth)
    return q**depth


def sector_interval(q: int, depth: int, cell: int) -> SectorInterval:
    """Return the half-open sector interval for one cell.

    >>> sector_interval(10, 3, 7)
    SectorInterval(left=Fraction(7, 1000), right=Fraction(1, 125))
    """

    total = sector_count(q, depth)
    _require_nonnegative_int("cell", cell)
    if cell >= total:
        raise ValueError("cell is outside the sector grid")
    return SectorInterval(Fraction(cell, total), Fraction(cell + 1, total))


def cell_range_for_interval(left: Fraction, right: Fraction, q: int, depth: int) -> range:
    """Return target cells that intersect [left, right)."""

    if not isinstance(left, Fraction):
        left = Fraction(left)
    if not isinstance(right, Fraction):
        right = Fraction(right)
    if left < 0 or right > 1 or left > right:
        raise ValueError("interval must satisfy 0 <= left <= right <= 1")

    total = sector_count(q, depth)
    if left == right:
        return range(0, 0)
    start = floor_fraction(left * total)
    stop = ceil_fraction(right * total)
    return range(start, stop)


def contained_range_for_interval(left: Fraction, right: Fraction, q: int, depth: int) -> range:
    """Return target cells fully contained in [left, right)."""

    if not isinstance(left, Fraction):
        left = Fraction(left)
    if not isinstance(right, Fraction):
        right = Fraction(right)
    if left < 0 or right > 1 or left > right:
        raise ValueError("interval must satisfy 0 <= left <= right <= 1")

    total = sector_count(q, depth)
    start = ceil_fraction(left * total)
    stop = floor_fraction(right * total)
    return range(start, max(start, stop))


def _boundary_ranges(intersecting: range, contained: range) -> tuple[range, ...]:
    ranges = []
    if intersecting.start < contained.start:
        ranges.append(range(intersecting.start, min(intersecting.stop, contained.start)))
    if contained.stop < intersecting.stop:
        ranges.append(range(max(intersecting.start, contained.stop), intersecting.stop))
    return tuple(r for r in ranges if r.start < r.stop)


def transform_target(
    q_from: int,
    depth_from: int,
    cell_from: int,
    q_to: int,
    depth_to: int,
) -> TransformCells:
    """Map one source sector to intersecting/contained target cell ranges."""

    interval = sector_interval(q_from, depth_from, cell_from)
    intersecting = cell_range_for_interval(interval.left, interval.right, q_to, depth_to)
    contained = contained_range_for_interval(interval.left, interval.right, q_to, depth_to)
    return TransformCells(
        intersecting=intersecting,
        contained=contained,
        boundary=_boundary_ranges(intersecting, contained),
    )


def intersect_range(
    q_from: int,
    depth_from: int,
    cell_from: int,
    q_to: int,
    depth_to: int,
) -> range:
    """Return target cells intersecting one source sector."""

    return transform_target(q_from, depth_from, cell_from, q_to, depth_to).intersecting


def contained_range(
    q_from: int,
    depth_from: int,
    cell_from: int,
    q_to: int,
    depth_to: int,
) -> range:
    """Return target cells fully contained in one source sector."""

    return transform_target(q_from, depth_from, cell_from, q_to, depth_to).contained


def certifying_cells(
    q_from: int,
    depth_from: int,
    cell_from: int,
    q_to: int,
    depth_to: int,
) -> TransformCells:
    """Alias for target cells that can certify a source-sector hit."""

    return transform_target(q_from, depth_from, cell_from, q_to, depth_to)


def range_len(cells: range) -> int:
    """Return len(range) as a named helper for readability."""

    return len(cells)


def range_to_list(cells: range, limit: int = 20) -> list[int] | str:
    """Return a small range as a list, or a compact string for large ranges."""

    if len(cells) <= limit:
        return list(cells)
    return f"range({cells.start}, {cells.stop})"


def flatten_ranges(ranges: Iterable[range]) -> list[int]:
    """Flatten small boundary ranges for display and tests."""

    out: list[int] = []
    for cells in ranges:
        out.extend(cells)
    return out


def _self_test() -> None:
    result = certifying_cells(10, 1000, 0, 4, 1661)
    assert list(result.intersecting) == [0, 1]
    assert list(result.contained) == [0]
    assert flatten_ranges(result.boundary) == [1]
    assert list(intersect_range(10, 1000, 0, 4, 1661)) == [0, 1]
    assert list(contained_range(10, 1000, 0, 4, 1661)) == [0]

    for depth in range(1, 13):
        total = sector_count(4, depth)
        for cell in (0, total // 2, total - 1):
            mapped = transform_target(4, depth, cell, 2, 2 * depth)
            assert list(mapped.intersecting) == [cell]
            assert list(mapped.contained) == [cell]
            assert mapped.boundary == ()


if __name__ == "__main__":
    _self_test()
    zero = certifying_cells(10, 1000, 0, 4, 1661)
    print("0^1000 decimal -> base-4 depth 1661")
    print("intersecting:", range_to_list(zero.intersecting))
    print("contained:", range_to_list(zero.contained))
    print("boundary:", [range_to_list(r) for r in zero.boundary])
