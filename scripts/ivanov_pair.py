#!/usr/bin/env python3
"""Rebuild Ivanov's 78-vertex near-miss pair and count common cards exactly.

Construction (arXiv:2608.11930, read in full on 2026-09-01):
  selector S_4: ports p_1..p_4; pair vertices q_ij for i<j, adjacent to p_i and
  p_j; six selector vertices z_F forming K_6, where F ranges over the six
  Hamiltonian paths of K_4 up to reversal (one per even permutation), and z_F
  is adjacent to q_ij exactly when ij is an edge of F.
  Each port p_i is replaced by an independent false-twin class P_i of size
  a_i, every member adjacent to the same three pair vertices as p_i.
  G uses sizes (15,16,17,18); H uses (16,15,17,18).

The number of common cards is the size of a maximum matching between the two
decks with cards compared by nauty certificate, i.e. the multiset
intersection size.  Ivanov reports at least 51; this script computes the exact
value and lists the unmatched deletions by type.
"""

from __future__ import annotations

import itertools
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402

import pynauty  # noqa: E402


def parity(p):
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p))) % 2


def build(sizes):
    pairs = list(itertools.combinations(range(4), 2))
    paths = sorted({frozenset(tuple(sorted((p[k], p[k + 1]))) for k in range(3)) for p in itertools.permutations(range(4)) if parity(p) == 0}, key=sorted)
    assert len(paths) == 6
    vid = {}
    types = []
    def add(kind, key):
        vid[(kind, key)] = len(types)
        types.append(kind)
    for i, a in enumerate(sizes):
        for c in range(a):
            add(f"P{i}", (i, c))
    for pr in pairs:
        add("q", pr)
    for F in paths:
        add("z", F)
    n = len(types)
    rows = [0] * n
    def edge(x, y):
        rows[x] |= 1 << y
        rows[y] |= 1 << x
    for i, a in enumerate(sizes):
        for c in range(a):
            for pr in pairs:
                if i in pr:
                    edge(vid[(f"P{i}", (i, c))], vid[("q", pr)])
    for F in paths:
        for pr in pairs:
            if pr in F:
                edge(vid[("z", F)], vid[("q", pr)])
    for F1, F2 in itertools.combinations(paths, 2):
        edge(vid[("z", F1)], vid[("z", F2)])
    return Graph(tuple(rows)), types


def cert(g):
    adj = {v: [w for w in range(g.n) if g.edge(v, w)] for v in range(g.n)}
    return pynauty.certificate(pynauty.Graph(g.n, adjacency_dict=adj))


def main():
    G, tG = build((15, 16, 17, 18))
    H, tH = build((16, 15, 17, 18))
    assert G.n == H.n == 78
    print("nonisomorphic parents:", cert(G) != cert(H), "degree sequences equal:", sorted(G.degrees) == sorted(H.degrees))
    dg = [(cert(G.delete_vertex(v)), tG[v]) for v in range(G.n)]
    dh = [(cert(H.delete_vertex(v)), tH[v]) for v in range(H.n)]
    cg, ch = Counter(c for c, _ in dg), Counter(c for c, _ in dh)
    common = sum((cg & ch).values())
    print("common cards (exact multiset intersection):", common, "of", G.n)
    matched = cg & ch
    unmatched_g = Counter()
    used = Counter()
    for c, t in dg:
        if used[c] < matched[c]:
            used[c] += 1
        else:
            unmatched_g[t] += 1
    print("unmatched deletions of G by vertex type:", dict(unmatched_g))


if __name__ == "__main__":
    main()
