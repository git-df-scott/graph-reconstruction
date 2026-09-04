#!/usr/bin/env python3
"""Emit every order-(2q-1) graph that is a twin blow-up of a twin-free
quotient of order q with all cells of size 2 except one singleton, one per
isomorphism class, for card_fibre.

A card of an order-2q graph in which every vertex has exactly one twin
(the regime left open by the vector-deck theorem and closed at order 14
only for blow-up totals by the deck-fixed sweeps) has this shape, so
running the fibre on this class is the exact statement: no counterexample
of order 2q has a card of this form, whatever the other extension looks
like.  Each doubled cell is independent (false twins) or an edge (true
twins).  --geng names the nauty generator.
"""
from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from grc import Graph  # noqa: E402

import pynauty  # noqa: E402


def twin_free(adj, q):
    for x in range(q):
        for y in range(x + 1, q):
            if adj[x] == adj[y] or (adj[x] | 1 << x) == (adj[y] | 1 << y):
                return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--q", type=int, default=7)
    ap.add_argument("--geng", default="geng")
    a = ap.parse_args()
    q = a.q
    out = subprocess.run([a.geng, "-q", str(q)], capture_output=True, text=True, check=True).stdout.split()
    seen = set()
    emitted = 0
    quotients = 0
    for g6 in out:
        Q = Graph.from_graph6(g6)
        adj = list(Q.adj)
        if not twin_free(adj, q):
            continue
        quotients += 1
        for single in range(q):
            cells = [c for c in range(q) if c != single]
            for kinds in itertools.product((0, 1), repeat=q - 1):
                # vertex map: cell c -> [2*i, 2*i+1] for doubled, singleton last
                idx = {}
                n = 0
                for c in cells:
                    idx[c] = [n, n + 1]
                    n += 2
                idx[single] = [n]
                n += 1
                rows = [0] * n
                for c in range(q):
                    for d in range(q):
                        if c != d and adj[c] >> d & 1:
                            for x in idx[c]:
                                for y in idx[d]:
                                    rows[x] |= 1 << y
                for c, kind in zip(cells, kinds):
                    if kind:
                        x, y = idx[c]
                        rows[x] |= 1 << y
                        rows[y] |= 1 << x
                cert = pynauty.certificate(pynauty.Graph(n, adjacency_dict={v: [w for w in range(n) if rows[v] >> w & 1] for v in range(n)}))
                if cert in seen:
                    continue
                seen.add(cert)
                emitted += 1
                print(Graph(tuple(rows)).to_graph6())
    print(f"blow-up cards q={q}: {quotients} twin-free quotients, {emitted} distinct cards of order {2*q-1}", file=sys.stderr)


if __name__ == "__main__":
    main()
