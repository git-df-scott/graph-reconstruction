#!/usr/bin/env python3
"""Repeated-2-card filter, a necessary condition for a counterexample.

Let (G, H) be hypomorphic with the card matching made the identity, and
let phi_v : G - v -> H - v be card isomorphisms.  For v != w the composite
phi_w^{-1} phi_v is an isomorphism from G - {v, a} to G - {w, b} with
a = phi_v^{-1}(w) and b = phi_w^{-1}(v).  Since no phi_v is the identity
(otherwise G = H as labelled graphs), for every v some w has phi_v(w) != w,
so a != w and the 2-subsets {v, a} and {w, b} are different.  Hence:

    in a counterexample, every vertex v lies in a 2-subset {v, a} whose
    deletion subgraph G - {v, a} is isomorphic to G - {w, b} for a
    different 2-subset {w, b}.

Equivalently every vertex is covered by a repeated entry of the 2-deck.
The test costs C(n,2) certificates of (n-2)-vertex graphs, about 3 ms at
order 14, thirty times faster than the deck-fixed verifier, and rejects 97 of 100
random order-14 graphs (self-test); it is useful in front of the verifier for
semi-structured sweeps.  Symmetric graphs pass trivially.
"""

from __future__ import annotations

import itertools
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402

import pynauty  # noqa: E402


def cert2(G: Graph, a: int, b: int) -> bytes:
    idx = [x for x in range(G.n) if x != a and x != b]
    pos = {x: i for i, x in enumerate(idx)}
    adj = {pos[x]: [pos[y] for y in idx if G.edge(x, y)] for x in idx}
    return pynauty.certificate(pynauty.Graph(G.n - 2, adjacency_dict=adj))


def uncovered_vertices(G: Graph):
    """Vertices not covered by any repeated 2-card (empty list = passes the filter)."""
    groups = defaultdict(list)
    for a, b in itertools.combinations(range(G.n), 2):
        groups[cert2(G, a, b)].append((a, b))
    covered = set()
    for pairs in groups.values():
        if len(pairs) >= 2:
            for a, b in pairs:
                covered.add(a); covered.add(b)
    return [v for v in range(G.n) if v not in covered]


def passes(G: Graph) -> bool:
    return not uncovered_vertices(G)


def _selftest():
    import random
    rng = random.Random(3)
    fails = 0
    for _ in range(100):
        n = 14
        rows = [0] * n
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < 0.5:
                    rows[a] |= 1 << b; rows[b] |= 1 << a
        if passes(Graph(tuple(rows))):
            fails += 1
    print(f"random order-14 graphs passing: {fails}/100 (expected 0)")
    # C_14 (vertex-transitive) must pass
    rows = [0] * 14
    for i in range(14):
        j = (i + 1) % 14; rows[i] |= 1 << j; rows[j] |= 1 << i
    print("C_14 passes:", passes(Graph(tuple(rows))))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("graphs", nargs="*")
    a = ap.parse_args()
    if a.selftest:
        _selftest()
    lines = a.graphs
    if lines == ["-"]:
        lines = [l.strip() for l in sys.stdin if l.strip()]
    for g6 in lines:
        G = Graph.from_graph6(g6)
        u = uncovered_vertices(G)
        print(g6, "PASS" if not u else f"REJECT uncovered={u}", flush=True)
