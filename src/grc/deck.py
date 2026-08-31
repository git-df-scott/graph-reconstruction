from __future__ import annotations

from collections import Counter

from .canon import canonical_code
from .graph import Graph


def canonical_deck(g: Graph) -> tuple[tuple[int, int], ...]:
    """Canonical vertex deck, sorted with multiplicities preserved."""

    return tuple(sorted(canonical_code(g.delete_vertex(v)) for v in range(g.n)))


def deck_types(g: Graph) -> Counter[tuple[int, int]]:
    return Counter(canonical_deck(g))


def same_deck(g: Graph, h: Graph) -> bool:
    return g.n == h.n and canonical_deck(g) == canonical_deck(h)

