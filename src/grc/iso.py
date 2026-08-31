from __future__ import annotations

from .graph import Graph


def find_isomorphism(
    g: Graph,
    h: Graph,
    fixed: dict[int, int] | None = None,
) -> tuple[int, ...] | None:
    """Independent exact backtracking isomorphism checker.

    The return value maps each vertex of `g` to a vertex of `h`.  This code does
    not call or compare canonical forms.
    """

    if g.n != h.n or g.m != h.m or sorted(g.degrees) != sorted(h.degrees):
        return None
    n = g.n
    by_degree: dict[int, list[int]] = {}
    for w, degree in enumerate(h.degrees):
        by_degree.setdefault(degree, []).append(w)
    mapping = [-1] * n
    used = [False] * n
    for v, w in (fixed or {}).items():
        if not (0 <= v < n and 0 <= w < n) or used[w] or g.degrees[v] != h.degrees[w]:
            return None
        mapping[v] = w
        used[w] = True
    fixed_items = [(v, w) for v, w in enumerate(mapping) if w >= 0]
    if any(g.edge(v, u) != h.edge(w, x) for v, w in fixed_items for u, x in fixed_items):
        return None

    def candidates(v: int) -> list[int]:
        out = []
        for w in by_degree[g.degrees[v]]:
            if used[w]:
                continue
            if all(g.edge(v, u) == h.edge(w, mapping[u]) for u in range(n) if mapping[u] >= 0):
                out.append(w)
        return out

    def search(remaining: tuple[int, ...]) -> bool:
        if not remaining:
            return True
        choices = [(len(candidates(v)), -g.degrees[v], v) for v in remaining]
        _, _, v = min(choices)
        rest = tuple(u for u in remaining if u != v)
        for w in candidates(v):
            mapping[v] = w
            used[w] = True
            if search(rest):
                return True
            used[w] = False
            mapping[v] = -1
        return False

    remaining = tuple(v for v in range(n) if mapping[v] < 0)
    return tuple(mapping) if search(remaining) else None


def is_isomorphic(g: Graph, h: Graph) -> bool:
    return find_isomorphism(g, h) is not None
