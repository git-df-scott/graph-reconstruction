#!/usr/bin/env python3
"""Direct deck search over twin-class blow-ups with singleton cells allowed.

Let Q be a twin-free graph on m vertices and a in {1,2,...}^m.  The blow-up
G(a) replaces vertex i by an independent set of size a_i (size 1 keeps the
vertex as it is).  Because Q is twin-free and every cell is nonempty, the
cells of G(a) are its maximal false-twin classes, so

    G(a) ~= G(b)   iff   b lies in the Aut(Q)-orbit of a.

Deleting a vertex from a cell of size >= 2 gives G(a - e_i); deleting a
singleton cell s gives the blow-up of Q - s, which has fewer than m twin
classes and therefore never matches a card of the first kind.

Vector-deck theorem (proved in docs/PLAN_2026-09-01.md): if every
non-singleton cell of a and of b has size at least 3, then D(G(a)) = D(G(b))
forces b in Aut(Q) a.  Hence a counterexample among blow-ups must have a cell
of size exactly 2 whose deletion card is matched with the class
correspondence displaced onto a singleton cell.  Ivanov's near-miss family
(arXiv:2608.11930) is of this type: its unmatched cards are the gadget
singletons and the smallest port class.

This script does not rely on the theorem.  For every twin-free Q on m
vertices (from geng) and every a in {1..B}^m it computes the exact deck of
G(a) with nauty (one certificate per cell, with multiplicity), buckets by
deck, and reports any bucket containing two parents with different
certificates.  Every reported pair is replayed through the independent
Python deck and isomorphism checkers.
"""

from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck  # noqa: E402

import pynauty  # noqa: E402


def geng_graphs(m: int, geng: str):
    out = subprocess.run([geng, "-q", str(m)], capture_output=True, text=True, check=True).stdout
    return [Graph.from_graph6(line) for line in out.split()]


def twin_free(g: Graph) -> bool:
    return len({g.adj[v] for v in range(g.n)}) == g.n


def certificate(g: Graph) -> bytes:
    adj = {v: [w for w in range(g.n) if g.edge(v, w)] for v in range(g.n)}
    return pynauty.certificate(pynauty.Graph(g.n, adjacency_dict=adj))


def blow_up(q: Graph, vec) -> tuple[Graph, list[int]]:
    offsets = [0]
    for a in vec:
        offsets.append(offsets[-1] + a)
    n = offsets[-1]
    rows = [0] * n
    for u in range(q.n):
        for v in range(u + 1, q.n):
            if q.edge(u, v):
                for x in range(offsets[u], offsets[u + 1]):
                    for y in range(offsets[v], offsets[v + 1]):
                        rows[x] |= 1 << y
                        rows[y] |= 1 << x
    return Graph(tuple(rows)), offsets


def deck_signature(q: Graph, vec) -> tuple:
    g, offsets = blow_up(q, vec)
    items = []
    for i, a in enumerate(vec):
        card = g.delete_vertex(offsets[i])
        items.append((certificate(card), a))
    return tuple(sorted(items)), g


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m", type=int, default=5)
    parser.add_argument("--B", type=int, default=3, help="maximum cell size")
    parser.add_argument("--geng", default="geng")
    parser.add_argument("--min-aut", type=int, default=1)
    parser.add_argument("--progress", type=int, default=0)
    args = parser.parse_args()
    t0 = time.time()
    quotients = [q for q in geng_graphs(args.m, args.geng) if twin_free(q)]
    total_vectors = total_hits = 0
    for qi, q in enumerate(quotients):
        if args.min_aut > 1:
            adj = {v: [w for w in range(q.n) if q.edge(v, w)] for v in range(q.n)}
            order = pynauty.autgrp(pynauty.Graph(q.n, adjacency_dict=adj))[1]
            if order < args.min_aut:
                continue
        buckets: dict[tuple, dict[bytes, tuple]] = defaultdict(dict)
        for vec in itertools.product(range(1, args.B + 1), repeat=args.m):
            sig, g = deck_signature(q, vec)
            cert = certificate(g)
            buckets[sig].setdefault(cert, vec)
            total_vectors += 1
        for sig, parents in buckets.items():
            if len(parents) > 1:
                vecs = list(parents.values())
                for a, b in itertools.combinations(vecs, 2):
                    ga, _ = blow_up(q, a)
                    gb, _ = blow_up(q, b)
                    ok = same_deck(ga, gb) and not is_isomorphic(ga, gb)
                    total_hits += 1
                    print(
                        ("HIT" if ok else "REFUTED-ON-REPLAY"),
                        f"Q={q.to_graph6()} a={a} b={b} n={ga.n} G={ga.to_graph6()} H={gb.to_graph6()}",
                        flush=True,
                    )
        if args.progress and (qi + 1) % args.progress == 0:
            print(f"  quotient {qi+1}/{len(quotients)} vectors={total_vectors} hits={total_hits} {time.time()-t0:.0f}s", flush=True)
    print(
        f"m={args.m} B={args.B}: twin-free quotients={len(quotients)} vectors={total_vectors} "
        f"deck collisions between nonisomorphic blow-ups={total_hits} {time.time()-t0:.1f}s"
    )


if __name__ == "__main__":
    main()
