"""Small resonance-coordinate helpers for pi-fs research notes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResonanceCoordinates:
    """A zero-based index decomposed as M = q K + r."""

    m_zero_based: int
    k: int
    n: int
    q: int
    r: int

    @property
    def position_one_based(self) -> int:
        return self.m_zero_based + 1


def resonance_coordinates(m_zero_based: int, k: int = 1221, n: int = 2456) -> ResonanceCoordinates:
    """Return resonance coordinates for a zero-based position M."""

    if m_zero_based < 0:
        raise ValueError("m_zero_based must be non-negative")
    if k <= 0 or n <= 0:
        raise ValueError("k and n must be positive")
    q, r = divmod(m_zero_based, k)
    return ResonanceCoordinates(m_zero_based=m_zero_based, k=k, n=n, q=q, r=r)
