"""Minimal finite matrix-sector locate flow."""

from __future__ import annotations

from .finite_index import (
    LocateResult,
    SparsePhaseIndex,
    build_phase_index_from_digits,
    certifying_depth,
    describe_result,
)


def direct_search_digits(digits: str, pattern: str) -> int | None:
    """Return the zero-based direct occurrence of a digit pattern, if present."""

    found = digits.find(pattern)
    return None if found < 0 else found


def build_decimal_quaternary_index(
    digits: str,
    depth: int,
    horizon: int | None = None,
    precision_digits: int | None = None,
) -> SparsePhaseIndex:
    """Build the Experiment-005-style `B=10, Q=4` finite index."""

    return build_phase_index_from_digits(
        digits,
        source_base=10,
        cert_base=4,
        depth=depth,
        horizon=horizon,
        precision_digits=precision_digits,
    )


def locate_digits(index: SparsePhaseIndex, pattern: str, mode: str = "contained") -> LocateResult:
    """Locate a decimal pattern in an already built finite index."""

    return index.locate_decimal_pattern(pattern, mode=mode)


def locate_decimal_digits(
    digits: str,
    pattern: str,
    cert_base: int = 4,
    depth: int | None = None,
    horizon: int | None = None,
    mode: str = "contained",
    precision_digits: int | None = None,
) -> LocateResult:
    """Build a small finite index and locate one decimal pattern."""

    if depth is None:
        depth = certifying_depth(10, len(pattern), cert_base)
    index = build_phase_index_from_digits(
        digits,
        source_base=10,
        cert_base=cert_base,
        depth=depth,
        horizon=horizon,
        precision_digits=precision_digits,
    )
    return index.locate_decimal_pattern(pattern, mode=mode)


__all__ = [
    "LocateResult",
    "SparsePhaseIndex",
    "build_decimal_quaternary_index",
    "direct_search_digits",
    "locate_digits",
    "locate_decimal_digits",
    "describe_result",
]
