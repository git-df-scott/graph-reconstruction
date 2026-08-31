from __future__ import annotations

from .graph import Graph

Partition = tuple[tuple[int, ...], ...]


def _initial_partition(g: Graph) -> Partition:
    cells: dict[int, list[int]] = {}
    for v, degree in enumerate(g.degrees):
        cells.setdefault(degree, []).append(v)
    return tuple(tuple(cells[d]) for d in sorted(cells))


def _refine(g: Graph, partition: Partition) -> Partition:
    while True:
        cell_masks = [sum(1 << v for v in cell) for cell in partition]
        refined: list[tuple[int, ...]] = []
        changed = False
        for cell in partition:
            buckets: dict[tuple[int, ...], list[int]] = {}
            for v in cell:
                signature = tuple((g.adj[v] & mask).bit_count() for mask in cell_masks)
                buckets.setdefault(signature, []).append(v)
            if len(buckets) > 1:
                changed = True
            for signature in sorted(buckets):
                refined.append(tuple(buckets[signature]))
        new = tuple(refined)
        if not changed:
            return new
        partition = new


def canonical_code(g: Graph) -> tuple[int, int]:
    """Return an exact isomorphism-invariant `(n, adjacency_bits)` code.

    This minimizes over the individualization/refinement search tree.  It is
    intentionally optimized for correctness and small structured graphs, not
    as a replacement for nauty on large censuses.
    """

    best: int | None = None

    def visit(partition: Partition) -> None:
        nonlocal best
        partition = _refine(g, partition)
        target = next((i for i, cell in enumerate(partition) if len(cell) > 1), None)
        if target is None:
            order = tuple(cell[0] for cell in partition)
            code = g.edge_mask(order)
            if best is None or code < best:
                best = code
            return
        cell = partition[target]
        for v in cell:
            remainder = tuple(w for w in cell if w != v)
            child = partition[:target] + ((v,), remainder) + partition[target + 1 :]
            visit(child)

    visit(_initial_partition(g))
    assert best is not None
    return (g.n, best)

