"""Small sector-geometry helpers for pi-fs locate notes."""

from __future__ import annotations

from fractions import Fraction
from math import cos, pi, sin

from .sector_transform import SectorInterval, floor_fraction, sector_count, sector_interval


def sector_width(q: int, depth: int) -> Fraction:
    """Return the width of one sector in a `(q, depth)` grid."""

    return Fraction(1, sector_count(q, depth))


def sector_center(q: int, depth: int, cell: int) -> Fraction:
    """Return the center coordinate of one sector."""

    interval = sector_interval(q, depth, cell)
    return (interval.left + interval.right) / 2


def sector_cell(value: Fraction, q: int, depth: int) -> int:
    """Return the cell containing a phase value in `[0, 1)`."""

    if not isinstance(value, Fraction):
        value = Fraction(value)
    if value < 0 or value >= 1:
        raise ValueError("value must satisfy 0 <= value < 1")
    total = sector_count(q, depth)
    return floor_fraction(value * total)


def chord_angle(q: int, depth: int, cell: int) -> float:
    """Return the central angle of a sector as a float."""

    return float(2 * pi * sector_center(q, depth, cell))


def chord_vector(q: int, depth: int, cell: int) -> tuple[float, float]:
    """Return the unit vector pointing at a sector center."""

    theta = chord_angle(q, depth, cell)
    return cos(theta), sin(theta)


def chord_threshold(q: int, depth: int, radius: float = 1.0) -> float:
    """Return the chord threshold for a sector at the given radius."""

    return radius * cos(float(pi / sector_count(q, depth)))


__all__ = [
    "SectorInterval",
    "sector_count",
    "sector_interval",
    "sector_width",
    "sector_center",
    "sector_cell",
    "chord_angle",
    "chord_vector",
    "chord_threshold",
]
