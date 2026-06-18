"""Small certificate helpers for finite phase-sector lookup."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .sector_transform import SectorInterval, sector_interval


@dataclass(frozen=True)
class IntervalCertificate:
    """Three-way interval certificate result."""

    status: str
    reason: str


def _as_fraction(value: Fraction | int) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def interval_contained(phase_low: Fraction, phase_high: Fraction, target: SectorInterval) -> bool:
    """Return whether `[phase_low, phase_high]` lies inside a target sector."""

    phase_low = _as_fraction(phase_low)
    phase_high = _as_fraction(phase_high)
    return target.left <= phase_low and phase_high < target.right


def interval_disjoint(phase_low: Fraction, phase_high: Fraction, target: SectorInterval) -> bool:
    """Return whether `[phase_low, phase_high]` is disjoint from a target sector."""

    phase_low = _as_fraction(phase_low)
    phase_high = _as_fraction(phase_high)
    return phase_high < target.left or phase_low >= target.right


def certify_interval(phase_low: Fraction, phase_high: Fraction, target: SectorInterval) -> IntervalCertificate:
    """Classify an approximate phase interval against a target sector."""

    if interval_contained(phase_low, phase_high, target):
        return IntervalCertificate("hit", "interval-contained")
    if interval_disjoint(phase_low, phase_high, target):
        return IntervalCertificate("miss", "interval-disjoint")
    return IntervalCertificate("refine", "interval-overlaps-boundary")


def certify_cell_containment(
    q_from: int,
    depth_from: int,
    cell_from: int,
    q_to: int,
    depth_to: int,
    cell_to: int,
) -> bool:
    """Return whether target-grid cell `cell_to` certifies source cell `cell_from`.

    The intended use is cross-base certification, for example a quaternary
    cell fully contained in a decimal target sector.
    """

    source = sector_interval(q_from, depth_from, cell_from)
    target = sector_interval(q_to, depth_to, cell_to)
    return source.left <= target.left and target.right <= source.right


__all__ = [
    "IntervalCertificate",
    "interval_contained",
    "interval_disjoint",
    "certify_interval",
    "certify_cell_containment",
]
