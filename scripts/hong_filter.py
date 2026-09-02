#!/usr/bin/env python3
"""Hong's controllable-card filter.

A graph X is controllable when its walk matrix [1, A1, A^2 1, ..., A^{n-1} 1]
is nonsingular (equivalently, A has no eigenvector orthogonal to the all-ones
vector; graphs with a nontrivial automorphism are never controllable).
Hong (1982; see Godsil and McKay 1981 and the literature check) proved that
a graph with a controllable card is reconstructible.  This module decides
controllability exactly (integer Bareiss elimination) and exposes

    controllable_cards(G) -> list of vertices v with G - v controllable

A graph with at least one controllable card needs no SAT verification.
Self-test: every graph with a nontrivial automorphism must be
non-controllable (checked against nauty on geng output), and the exact rank
must agree with floating-point rank on random graphs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402


def walk_matrix(G: Graph):
    n = G.n
    cols = []
    v = [1] * n
    for _ in range(n):
        cols.append(v)
        v = [sum(v[y] for y in range(n) if G.adj[x] >> y & 1) for x in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def nonsingular(M):
    """Exact test by fraction-free Gaussian elimination over the integers."""
    M = [row[:] for row in M]
    n = len(M)
    for k in range(n):
        piv = next((i for i in range(k, n) if M[i][k] != 0), None)
        if piv is None:
            return False
        M[k], M[piv] = M[piv], M[k]
        for i in range(k + 1, n):
            if M[i][k]:
                f = M[i][k]
                p = M[k][k]
                M[i] = [(M[i][j] * p - f * M[k][j]) for j in range(n)]
                g = 0
                for x in M[i]:
                    g = _gcd(g, abs(x))
                if g > 1:
                    M[i] = [x // g for x in M[i]]
    return True


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def controllable(G: Graph) -> bool:
    return nonsingular(walk_matrix(G))


def controllable_cards(G: Graph):
    return [v for v in range(G.n) if controllable(G.delete_vertex(v))]


def _selftest(geng, n=7):
    import random
    import subprocess

    import pynauty
    out = subprocess.run([geng, "-q", str(n)], capture_output=True, text=True, check=True).stdout.split()
    bad = 0
    ctrl = 0
    for line in out:
        g = Graph.from_graph6(line)
        aut = pynauty.autgrp(pynauty.Graph(g.n, adjacency_dict={x: [y for y in range(g.n) if g.edge(x, y)] for x in range(g.n)}))[1]
        c = controllable(g)
        ctrl += c
        if c and aut != 1.0:
            bad += 1
    print(f"order {n}: graphs={len(out)} controllable={ctrl} controllable-with-automorphism={bad} (must be 0)")
    try:
        import numpy as np
        rng = random.Random(1)
        dis = 0
        for _ in range(200):
            m = 12
            rows = [0] * m
            for a in range(m):
                for b in range(a + 1, m):
                    if rng.random() < 0.5:
                        rows[a] |= 1 << b; rows[b] |= 1 << a
            g = Graph(tuple(rows))
            W = np.array(walk_matrix(g), dtype=float)
            if (np.linalg.matrix_rank(W) == m) != controllable(g):
                dis += 1
        print(f"random order-12 graphs: exact vs float rank disagreements={dis} (must be 0)")
    except ImportError:
        print("numpy unavailable; float cross-check skipped")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--geng", default="geng")
    ap.add_argument("graphs", nargs="*")
    a = ap.parse_args()
    if a.selftest:
        _selftest(a.geng)
    lines = a.graphs
    if lines == ["-"]:
        lines = [l.strip() for l in sys.stdin if l.strip()]
    for g6 in lines:
        G = Graph.from_graph6(g6)
        cc = controllable_cards(G)
        print(g6, "controllable cards:", len(cc), "HONG-RECONSTRUCTIBLE" if cc else "no controllable card")
