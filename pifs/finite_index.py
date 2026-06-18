"""Finite matrix-sector locate reference engine.

This module intentionally stays small and dependency-free. It builds a sparse
phase-cell index from a finite digit dump and can certify decimal zero-block
targets through a transformed sector grid.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import ceil, log
from typing import Iterable, Sequence

from .resonance import ResonanceCoordinates, resonance_coordinates
from .sector_transform import (
    TransformCells,
    cell_range_for_interval,
    certifying_cells,
    flatten_ranges,
    range_to_list,
)

_DIGITS = {ch: i for i, ch in enumerate("0123456789abcdefghijklmnopqrstuvwxyz")}


@dataclass(frozen=True)
class PhaseRecord:
    """One exact finite-index record."""

    m_zero_based: int
    cell: int
    margin: Fraction
    resonance: ResonanceCoordinates

    @property
    def position_one_based(self) -> int:
        return self.m_zero_based + 1


@dataclass(frozen=True)
class LocateResult:
    """Locate result with certificate metadata."""

    found: bool
    record: PhaseRecord | None
    certificate: str
    target_cells: TransformCells | None = None


class SparsePhaseIndex:
    """Sparse map from phase cells to earliest exact position."""

    def __init__(self, source_base: int, cert_base: int, depth: int, records: Sequence[PhaseRecord]):
        self.source_base = source_base
        self.cert_base = cert_base
        self.depth = depth
        self.records = tuple(sorted(records, key=lambda record: record.m_zero_based))
        self._min_by_cell: dict[int, PhaseRecord] = {}
        for record in self.records:
            current = self._min_by_cell.get(record.cell)
            if current is None or record.m_zero_based < current.m_zero_based:
                self._min_by_cell[record.cell] = record

    def locate_cells(self, cells: Iterable[int]) -> LocateResult:
        """Return the earliest record in any of the given cells."""

        best: PhaseRecord | None = None
        for cell in cells:
            record = self._min_by_cell.get(cell)
            if record is not None and (best is None or record.m_zero_based < best.m_zero_based):
                best = record
        if best is None:
            return LocateResult(found=False, record=None, certificate="not-found-within-horizon")
        return LocateResult(found=True, record=best, certificate="cell-contained")

    def locate_cell_range(self, cells: range) -> LocateResult:
        return self.locate_cells(cells)

    def locate_decimal_pattern(self, pattern: str, mode: str = "contained") -> LocateResult:
        """Locate a decimal pattern through this index grid.

        `contained` mode returns only cells fully inside the decimal target
        sector, so a hit is a cross-base certificate. `intersecting` mode also
        includes boundary cells, so the returned candidate needs refinement.
        """

        if self.source_base != 10:
            raise ValueError("decimal pattern locate requires a decimal source orbit")
        if not pattern:
            raise ValueError("pattern must not be empty")
        target = certifying_cells(10, len(pattern), parse_digits(pattern, 10), self.cert_base, self.depth)
        if mode == "contained":
            cells = target.contained
            hit_certificate = "matrix-sector-contained"
        elif mode == "intersecting":
            cells = target.intersecting
            hit_certificate = "matrix-sector-intersecting"
        else:
            raise ValueError("mode must be 'contained' or 'intersecting'")

        result = self.locate_cells(cells)
        return LocateResult(
            found=result.found,
            record=result.record,
            certificate=hit_certificate if result.found else result.certificate,
            target_cells=target,
        )

    def locate_decimal_zero_block(self, digits: int) -> LocateResult:
        """Locate a decimal zero block through contained cells in this index grid."""

        if self.source_base != 10:
            raise ValueError("decimal zero-block locate requires a decimal source orbit")
        if digits <= 0:
            raise ValueError("digits must be positive")
        return self.locate_decimal_pattern("0" * digits, mode="contained")


def digit_value(ch: str, base: int) -> int:
    value = _DIGITS.get(ch.lower())
    if value is None or value >= base:
        raise ValueError(f"invalid digit {ch!r} for base {base}")
    return value


def parse_digits(digits: str, base: int) -> int:
    value = 0
    for ch in digits:
        value = value * base + digit_value(ch, base)
    return value


def precision_digits_for_grid(source_base: int, cert_base: int, depth: int, guard_digits: int = 2) -> int:
    """Return a conservative finite suffix length for resolving grid cells."""

    if source_base <= 1 or cert_base <= 1:
        raise ValueError("bases must be greater than one")
    if depth < 0:
        raise ValueError("depth must be non-negative")
    if depth == 0:
        return max(1, guard_digits)
    return max(1, ceil(depth * log(cert_base) / log(source_base)) + guard_digits)


def certifying_depth(q_from: int, depth_from: int, q_to: int) -> int:
    """Smallest L such that q_to^-L <= q_from^-depth_from."""

    if q_from <= 1 or q_to <= 1:
        raise ValueError("bases must be greater than one")
    if depth_from < 0:
        raise ValueError("depth_from must be non-negative")
    estimate = max(0, ceil(depth_from * log(q_from) / log(q_to)))
    while q_to**estimate < q_from**depth_from:
        estimate += 1
    while estimate > 0 and q_to ** (estimate - 1) >= q_from**depth_from:
        estimate -= 1
    return estimate


def _cell_from_known_suffix(
    suffix: str,
    source_base: int,
    cert_base: int,
    depth: int,
) -> tuple[int, Fraction] | None:
    """Return a unique target cell and certified margin if finite digits prove one."""

    if not suffix:
        return None
    denom = source_base ** len(suffix)
    lower = Fraction(parse_digits(suffix, source_base), denom)
    upper = lower + Fraction(1, denom)
    cells = cell_range_for_interval(lower, upper, cert_base, depth)
    if len(cells) != 1:
        return None
    cell = cells.start
    total = cert_base**depth
    margin = min(lower - Fraction(cell, total), Fraction(cell + 1, total) - upper)
    if margin < 0:
        return None
    return cell, margin


def build_phase_index_from_digits(
    digits: str,
    source_base: int,
    cert_base: int,
    depth: int,
    horizon: int | None = None,
    precision_digits: int | None = None,
    resonance_k: int = 1221,
    resonance_n: int = 2456,
) -> SparsePhaseIndex:
    """Build a sparse index from finite fractional digits of pi.

    `digits` must contain fractional digits in `source_base`, starting at
    zero-based position M = 0. Only positions whose target cell is uniquely
    determined by the available suffix window are indexed.
    """

    if precision_digits is None:
        precision_digits = precision_digits_for_grid(source_base, cert_base, depth)
    if precision_digits <= 0:
        raise ValueError("precision_digits must be positive")

    max_horizon = max(0, len(digits) - precision_digits + 1)
    if horizon is None:
        horizon = max_horizon
    horizon = min(horizon, max_horizon)
    if horizon < 0:
        raise ValueError("horizon must be non-negative")

    records: list[PhaseRecord] = []
    for m_zero_based in range(horizon):
        suffix = digits[m_zero_based : m_zero_based + precision_digits]
        cell_margin = _cell_from_known_suffix(suffix, source_base, cert_base, depth)
        if cell_margin is None:
            continue
        cell, margin = cell_margin
        records.append(
            PhaseRecord(
                m_zero_based=m_zero_based,
                cell=cell,
                margin=margin,
                resonance=resonance_coordinates(m_zero_based, resonance_k, resonance_n),
            )
        )
    return SparsePhaseIndex(source_base, cert_base, depth, records)


def describe_result(result: LocateResult) -> dict[str, object]:
    """Return a JSON-friendly summary for demos and tests."""

    if not result.found or result.record is None:
        return {"found": False, "certificate": result.certificate}
    record = result.record
    out: dict[str, object] = {
        "found": True,
        "position": record.position_one_based,
        "M": record.m_zero_based,
        "cell": record.cell,
        "margin": f"{record.margin.numerator}/{record.margin.denominator}",
        "certificate": result.certificate,
        "resonance": {
            "K": record.resonance.k,
            "N": record.resonance.n,
            "q": record.resonance.q,
            "r": record.resonance.r,
        },
    }
    if result.target_cells is not None:
        out["target_cells"] = {
            "intersecting": range_to_list(result.target_cells.intersecting),
            "contained": range_to_list(result.target_cells.contained),
            "boundary": [range_to_list(r) for r in result.target_cells.boundary],
        }
    return out


def _self_test() -> None:
    pi_digits = "14159265358979323846264338327950288419716939937510"

    decimal = build_phase_index_from_digits(pi_digits, 10, 10, 1, precision_digits=2)
    zero_decimal = decimal.locate_cells([0])
    assert zero_decimal.found
    assert zero_decimal.record is not None
    assert pi_digits[zero_decimal.record.m_zero_based] == "0"

    l4 = certifying_depth(10, 1, 4)
    assert l4 == 2
    quaternary_cert = build_phase_index_from_digits(pi_digits, 10, 4, l4, precision_digits=4)
    zero_cert = quaternary_cert.locate_decimal_zero_block(1)
    assert zero_cert.found
    assert zero_cert.record is not None
    assert pi_digits[zero_cert.record.m_zero_based] == "0"
    assert list(zero_cert.target_cells.contained) == [0]
    assert flatten_ranges(zero_cert.target_cells.boundary) == [1]

    toy_digits = "314159000012345"
    depth4 = certifying_depth(10, 4, 4)
    toy_index = build_phase_index_from_digits(toy_digits, 10, 4, depth4, precision_digits=8)
    toy_zero = toy_index.locate_decimal_zero_block(4)
    assert toy_zero.found
    assert toy_zero.record is not None
    assert toy_zero.record.m_zero_based == toy_digits.find("0000")


if __name__ == "__main__":
    _self_test()
    sample = "14159265358979323846264338327950288419716939937510"
    depth = certifying_depth(10, 1, 4)
    index = build_phase_index_from_digits(sample, 10, 4, depth, precision_digits=4)
    print(describe_result(index.locate_decimal_zero_block(1)))
