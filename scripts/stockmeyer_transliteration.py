#!/usr/bin/env python3
"""Stockmeyer's edge-weighted hypomorphic digraphs (A Census of
Non-Reconstructable Digraphs II, matrices M_p and M_p*, p = 2^n) turned into
graphs.  M_p is antisymmetric and M_p, M_p* are hypomorphic as weighted
digraphs (his Theorem 1: M_p[i,j] = M_p*[s_k(i), s_k(j)] for i, j != k), so
for any set S of absolute weights the graphs

    G_S(M)  : i ~ j  iff  |M[i,j]| in S
    G_S(M*) : i ~ j  iff  |M*[i,j]| in S

have the same deck.  A non-isomorphic pair would be a counterexample.  This
script builds the matrices from Definition 2, checks antisymmetry and the
Lemma 1 identities, verifies equal decks independently with nauty, and
tests isomorphism for every S.  Order 8 is a control: all pairs must be
isomorphic (graphs of order 8 are reconstructible).
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from grc import Graph  # noqa: E402

import pynauty  # noqa: E402

M4 = [[0, 1, 2, 3], [-1, 0, 3, -2], [-2, -3, 0, 1], [-3, 2, -1, 0]]
M4s = [[0, -2, -3, -1], [2, 0, 1, -3], [3, -1, 0, 2], [1, 3, -2, 0]]


def v2(d):
    x = 0
    while d % 2 == 0:
        d //= 2
        x += 1
    return x, d


def block(base, d, star):
    """4x4 block for block-difference d (Definition 2)."""
    I = [[4 if r == c else 0 for c in range(4)] for r in range(4)]
    if d == 0:
        return [row[:] for row in base]
    if d % 2:
        sign = 1 if d % 4 == 1 else -1        # +1: d = 1 mod 4, -1: d = -1 mod 4
        if star:
            sign = -sign
        return [[-base[r][c] + sign * I[r][c] for c in range(4)] for r in range(4)]
    x, y = v2(abs(d))
    y = y if d > 0 else -y
    sign = 1 if y % 4 == 1 else -1
    if star:
        sign = -sign
    return [[base[r][c] + sign * (x + 4) * (1 if r == c else 0) for c in range(4)] for r in range(4)]


def matrix(p, star):
    base = M4s if star else M4
    b = p // 4
    M = [[0] * p for _ in range(p)]
    for bi in range(b):
        for bj in range(b):
            B = block(base, bj - bi, star)
            for r in range(4):
                for c in range(4):
                    M[4 * bi + r][4 * bj + c] = B[r][c]
    return M


def check(M, Ms, p, n):
    for i in range(p):
        for j in range(p):
            assert M[i][j] == -M[j][i] and Ms[i][j] == -Ms[j][i], "not antisymmetric"
    if p >= 8:
        for i in range(p // 2):
            assert M[i][i + p // 2] == n + 1 and Ms[i + p // 2][i] == n + 1, "Lemma 1(d) fails"
    if p == 8:
        for i in range(4):
            for j in range(4):
                if i != j:
                    assert M[i][j] == -M[i][j + 4] == -M[i + 4][j], "Lemma 1(b) fails"


def graph_from(M, S):
    p = len(M)
    rows = [0] * p
    for i in range(p):
        for j in range(p):
            if i != j and abs(M[i][j]) in S:
                rows[i] |= 1 << j
    return Graph(tuple(rows))


def cert(g):
    return pynauty.certificate(pynauty.Graph(g.n, adjacency_dict={v: [w for w in range(g.n) if g.edge(v, w)] for v in range(g.n)}))


def deck(g):
    return sorted(cert(g.delete_vertex(v)) for v in range(g.n))


def main():
    for n in (2, 3, 4, 5):
        p = 2 ** n
        M, Ms = matrix(p, False), matrix(p, True)
        check(M, Ms, p, n)
        weights = sorted({abs(M[i][j]) for i in range(p) for j in range(p) if i != j})
        ws = sorted({abs(Ms[i][j]) for i in range(p) for j in range(p) if i != j})
        print(f"p={p}: weights {weights} / {ws}")
        found = 0
        for r in range(1, len(weights)):
            for S in itertools.combinations(weights, r):
                S = set(S)
                g, h = graph_from(M, S), graph_from(Ms, S)
                same = deck(g) == deck(h)
                iso = cert(g) == cert(h)
                if not same:
                    print(f"  S={sorted(S)}: DECKS DIFFER (construction error?)")
                if same and not iso:
                    found += 1
                    print(f"  S={sorted(S)}: SAME DECK, NON-ISOMORPHIC  G={g.to_graph6()} H={h.to_graph6()}")
        print(f"  {found} non-isomorphic hypomorphic pairs at order {p}")


if __name__ == "__main__":
    main()
