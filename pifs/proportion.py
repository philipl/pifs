"""Exact proportional sector arithmetic for pi-fs.

This module implements the "school proportion" layer:

    I_A^(Q,L) = [A / Q^L, (A + 1) / Q^L)

A transform between sector grids is not a symbolic conversion of digits.
It is an exact interval relation between two partitions of the same unit
circle / unit interval.

All certification functions use integer arithmetic only. No floating-point
rounding is used in overlap or containment certificates.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import log
from typing import Iterable, Iterator, Optional


@dataclass(frozen=True)
class CellRange:
    """Inclusive integer cell range.

    Empty ranges are represented by start=0, end=-1.
    """

    start: int
    end: int

    @property
    def empty(self) -> bool:
        return self.end < self.start

    @property
    def count(self) -> int:
        return 0 if self.empty else self.end - self.start + 1

    def as_tuple(self) -> tuple[int, int] | None:
        return None if self.empty else (self.start, self.end)

    def iter_cells(self, max_items: Optional[int] = None) -> Iterator[int]:
        """Iterate cells, optionally guarding against huge ranges."""
        if self.empty:
            return
        count = self.count
        if max_items is not None and count > max_items:
            raise ValueError(f"range has {count} cells, exceeds max_items={max_items}")
        for x in range(self.start, self.end + 1):
            yield x

    def to_list(self, max_items: Optional[int] = None) -> list[int]:
        return list(self.iter_cells(max_items=max_items))

    def __contains__(self, x: int) -> bool:
        return (not self.empty) and self.start <= x <= self.end


@dataclass(frozen=True)
class SectorTransform:
    """Overlap and containment ranges for a source sector in a target grid."""

    source_base: int
    source_depth: int
    source_cell: int
    target_base: int
    target_depth: int
    intersect: CellRange
    contained: CellRange

    @property
    def boundary(self) -> int:
        return self.intersect.count - self.contained.count

    def summary(self) -> dict[str, int | tuple[int, int] | None]:
        return {
            "source_base": self.source_base,
            "source_depth": self.source_depth,
            "source_cell": self.source_cell,
            "target_base": self.target_base,
            "target_depth": self.target_depth,
            "intersect": self.intersect.as_tuple(),
            "intersect_count": self.intersect.count,
            "contained": self.contained.as_tuple(),
            "contained_count": self.contained.count,
            "boundary_count": self.boundary,
        }


def floor_div(a: int, b: int) -> int:
    """Floor division, explicit for formula readability."""
    if b <= 0:
        raise ValueError("denominator must be positive")
    return a // b


def ceil_div(a: int, b: int) -> int:
    """Ceiling division for integers."""
    if b <= 0:
        raise ValueError("denominator must be positive")
    return -((-a) // b)


def denominator(base: int, depth: int) -> int:
    """Return base**depth with validation."""
    if base < 2:
        raise ValueError("base must be >= 2")
    if depth < 0:
        raise ValueError("depth must be >= 0")
    return base ** depth


def validate_cell(cell: int, base: int, depth: int) -> None:
    den = denominator(base, depth)
    if not (0 <= cell < den):
        raise ValueError(f"cell {cell} outside [0, {den}) for base={base}, depth={depth}")


def sector_interval(cell: int, base: int, depth: int) -> tuple[int, int, int]:
    """Return integer interval representation [num0/den, num1/den)."""
    validate_cell(cell, base, depth)
    den = denominator(base, depth)
    return cell, cell + 1, den


def sector_center(cell: int, base: int, depth: int) -> Fraction:
    """Exact center of a sector."""
    validate_cell(cell, base, depth)
    den = denominator(base, depth)
    return Fraction(2 * cell + 1, 2 * den)


def required_depth_cover(source_base: int, source_depth: int, target_base: int) -> int:
    """Minimal L such that target_base**L >= source_base**source_depth.

    Exact integer version of ceil(source_depth * log(source_base, target_base)).
    """
    target = denominator(source_base, source_depth)
    if target <= 1:
        return 0

    guess = max(0, int(source_depth * log(source_base) / log(target_base)))
    while denominator(target_base, guess) < target:
        guess += 1
    while guess > 0 and denominator(target_base, guess - 1) >= target:
        guess -= 1
    return guess


def _clip_range(start: int, end: int, limit: int) -> CellRange:
    start = max(0, start)
    end = min(limit - 1, end)
    if end < start:
        return CellRange(0, -1)
    return CellRange(start, end)


def intersecting_cells(
    source_cell: int,
    source_base: int,
    source_depth: int,
    target_base: int,
    target_depth: int,
) -> CellRange:
    """Cells of target grid whose sectors intersect the source sector.

    Source:

        I_A = [A / Q^L, (A + 1) / Q^L)

    Target cells:

        J_B = [B / Q2^L2, (B + 1) / Q2^L2)

    Intersect iff:

        B / N < (A + 1) / M
        (B + 1) / N > A / M

    Therefore:

        B_min = floor(A N / M)
        B_max = ceil((A + 1) N / M) - 1
    """
    validate_cell(source_cell, source_base, source_depth)
    M = denominator(source_base, source_depth)
    N = denominator(target_base, target_depth)

    b_min = floor_div(source_cell * N, M)
    b_max = ceil_div((source_cell + 1) * N, M) - 1

    return _clip_range(b_min, b_max, N)


def contained_cells(
    source_cell: int,
    source_base: int,
    source_depth: int,
    target_base: int,
    target_depth: int,
) -> CellRange:
    """Cells of target grid fully contained inside the source sector.

    Containment:

        [B/N, (B+1)/N) subset [A/M, (A+1)/M)

    iff:

        B / N >= A / M
        (B + 1) / N <= (A + 1) / M

    Therefore:

        B_min = ceil(A N / M)
        B_max = floor((A + 1) N / M) - 1
    """
    validate_cell(source_cell, source_base, source_depth)
    M = denominator(source_base, source_depth)
    N = denominator(target_base, target_depth)

    b_min = ceil_div(source_cell * N, M)
    b_max = floor_div((source_cell + 1) * N, M) - 1

    return _clip_range(b_min, b_max, N)


def transform_sector(
    source_cell: int,
    source_base: int,
    source_depth: int,
    target_base: int,
    target_depth: int,
) -> SectorTransform:
    """Return overlap and containment ranges for one sector transform."""
    return SectorTransform(
        source_base=source_base,
        source_depth=source_depth,
        source_cell=source_cell,
        target_base=target_base,
        target_depth=target_depth,
        intersect=intersecting_cells(source_cell, source_base, source_depth, target_base, target_depth),
        contained=contained_cells(source_cell, source_base, source_depth, target_base, target_depth),
    )


def boundary_cells(transform: SectorTransform, max_items: Optional[int] = None) -> list[int]:
    """Cells that intersect the source sector but are not fully contained."""
    inter = set(transform.intersect.iter_cells(max_items=max_items))
    cont = set(transform.contained.iter_cells(max_items=max_items))
    return sorted(inter - cont)


def decimal_zero_certifying_cells(zero_length: int, target_base: int = 4) -> SectorTransform:
    """Certifying target-base cells for a decimal zero block.

    Decimal zero block of length D is sector:

        [0, 10^-D)

    In sector notation this is source_cell=0, source_base=10, source_depth=D.

    We choose the minimal target depth L such that:

        target_base^L >= 10^D

    Then contained cells give strict certificates.
    """
    if zero_length < 1:
        raise ValueError("zero_length must be positive")
    target_depth = required_depth_cover(10, zero_length, target_base)
    return transform_sector(0, 10, zero_length, target_base, target_depth)


def is_cell_contained_in_sector(
    target_cell: int,
    source_cell: int,
    source_base: int,
    source_depth: int,
    target_base: int,
    target_depth: int,
) -> bool:
    """Check if one target cell is fully inside a source sector."""
    return target_cell in contained_cells(source_cell, source_base, source_depth, target_base, target_depth)


def exact_binary_quaternary_cell(base4_cell: int, base4_depth: int) -> int:
    """Return the equivalent binary cell for a base-4 cell at depth L.

    Since one base-4 digit is exactly two binary bits, the cell number is the
    same integer at binary depth 2L.
    """
    validate_cell(base4_cell, 4, base4_depth)
    return base4_cell


def continued_fraction_terms(x: float, max_terms: int = 32) -> list[int]:
    """Simple continued fraction terms for a positive real x."""
    if x <= 0:
        raise ValueError("x must be positive")
    terms: list[int] = []
    y = float(x)
    for _ in range(max_terms):
        a = int(y)
        terms.append(a)
        frac = y - a
        if abs(frac) < 1e-15:
            break
        y = 1.0 / frac
    return terms


def convergents_from_terms(terms: Iterable[int]) -> list[tuple[int, int]]:
    """Return (p,q) convergents from continued fraction terms."""
    p_m2, p_m1 = 0, 1
    q_m2, q_m1 = 1, 0
    convs = []
    for a in terms:
        p = a * p_m1 + p_m2
        q = a * q_m1 + q_m2
        convs.append((p, q))
        p_m2, p_m1 = p_m1, p
        q_m2, q_m1 = q_m1, q
    return convs


def logarithmic_resonance_pairs(base_from: float, base_to: float, max_terms: int = 32) -> list[dict[str, float | int]]:
    """Approximate log_{base_to}(base_from) by K/N.

    If base_from^N ~= base_to^K, then:

        K / N ~= log_{base_to}(base_from)

    Returns dicts with N, K and log error.
    """
    alpha = log(base_from) / log(base_to)
    pairs = []
    for K, N in convergents_from_terms(continued_fraction_terms(alpha, max_terms=max_terms)):
        error = N * log(base_from) - K * log(base_to)
        pairs.append({
            "N": N,
            "K": K,
            "K_over_N": K / N,
            "log_error": error,
            "relative_error_approx": error,
        })
    return pairs


def decimal_medium_resonance() -> dict[str, int | float]:
    """Return the medium resonance pi^2456 ~= 10^1221."""
    import math
    N = 2456
    K = 1221
    log_error = N * math.log(math.pi) - K * math.log(10)
    return {
        "N": N,
        "K": K,
        "log_error": log_error,
        "ratio_minus_1_approx": math.exp(log_error) - 1,
    }

# Backwards-compatible aliases used by the surrounding reference helpers.
def sector_ratio(cell: int, q: int, depth: int) -> Fraction:
    """Return the left-edge ratio `cell / q^depth` for one sector."""
    validate_cell(cell, q, depth)
    return Fraction(cell, denominator(q, depth))


def sector_proportion(cell: int, q: int, depth: int) -> tuple[int, int]:
    """Return the integer proportion `cell : q^depth`."""
    validate_cell(cell, q, depth)
    return cell, denominator(q, depth)


def intersect_range(cell: int, q: int, depth: int, q2: int, depth2: int) -> range:
    """Return intersecting cells as a half-open Python range."""
    cells = intersecting_cells(cell, q, depth, q2, depth2)
    return range(cells.start, cells.end + 1) if not cells.empty else range(0, 0)


def contained_range(cell: int, q: int, depth: int, q2: int, depth2: int) -> range:
    """Return contained cells as a half-open Python range."""
    cells = contained_cells(cell, q, depth, q2, depth2)
    return range(cells.start, cells.end + 1) if not cells.empty else range(0, 0)


def resonance_ratio(base_a: float, base_b: float, max_denominator: int) -> Fraction:
    """Approximate `N:K` for `base_a^N ~= base_b^K`.

    This is a floating-point convenience for research notes, not a certificate.
    For example, `resonance_ratio(pi, 10, 1300)` returns `2456/1221`.
    """
    if base_a <= 1 or base_b <= 1:
        raise ValueError("bases must be greater than one")
    if max_denominator <= 0:
        raise ValueError("max_denominator must be positive")
    return Fraction(log(base_b) / log(base_a)).limit_denominator(max_denominator)


__all__ = [
    "CellRange",
    "SectorTransform",
    "floor_div",
    "ceil_div",
    "denominator",
    "validate_cell",
    "sector_interval",
    "sector_center",
    "required_depth_cover",
    "intersecting_cells",
    "contained_cells",
    "transform_sector",
    "boundary_cells",
    "decimal_zero_certifying_cells",
    "is_cell_contained_in_sector",
    "exact_binary_quaternary_cell",
    "continued_fraction_terms",
    "convergents_from_terms",
    "logarithmic_resonance_pairs",
    "decimal_medium_resonance",
    "sector_ratio",
    "sector_proportion",
    "intersect_range",
    "contained_range",
    "resonance_ratio",
]
