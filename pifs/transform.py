"""Readable aliases for exact sector-grid transforms."""

from __future__ import annotations

from .sector_transform import (
    TransformCells,
    certifying_cells,
    contained_range,
    flatten_ranges,
    intersect_range,
    range_to_list,
    transform_target,
)


def intersecting_cells(q_from: int, depth_from: int, cell_from: int, q_to: int, depth_to: int) -> range:
    """Return target cells that intersect one source sector."""

    return intersect_range(q_from, depth_from, cell_from, q_to, depth_to)


def contained_cells(q_from: int, depth_from: int, cell_from: int, q_to: int, depth_to: int) -> range:
    """Return target cells fully contained in one source sector."""

    return contained_range(q_from, depth_from, cell_from, q_to, depth_to)


def boundary_cells(q_from: int, depth_from: int, cell_from: int, q_to: int, depth_to: int) -> list[int]:
    """Return boundary cells as a small flat list for tests and demos."""

    return flatten_ranges(transform_target(q_from, depth_from, cell_from, q_to, depth_to).boundary)


__all__ = [
    "TransformCells",
    "transform_target",
    "certifying_cells",
    "intersecting_cells",
    "contained_cells",
    "boundary_cells",
    "range_to_list",
]
