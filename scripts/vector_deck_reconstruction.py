#!/usr/bin/env python3
"""Vector-deck reconstruction over permutation groups (twin-class blow-ups).

Let Q be a twin-free graph on m vertices with automorphism group Gamma acting
on V(Q).  Replace vertex i by an independent false-twin class of size a_i >= 2.
The blow-up G(a) has n = sum(a) vertices.  Because Q is twin-free and every
class has size at least two, the classes of G(a) are exactly its maximal
false-twin classes, so

    G(a) ~= G(b)  iff  b lies in the Gamma-orbit of a,

and deleting one vertex of class i produces the blow-up G(a - e_i), with
multiplicity a_i.  Hence the ordinary vertex deck of G(a) is the multiset

    D(a) = {{ Gamma-orbit(a - e_i) : a_i copies, i = 1..m }},

as long as a_i - 1 >= 1 (a class never disappears).  A pair a, b with
D(a) = D(b) and Gamma a != Gamma b is therefore a genuine counterexample to the
Kelly-Ulam conjecture of order sum(a).

Ivanov's 2026 near-miss family (arXiv:2608.11930) is the case Gamma = A_4
acting on four port classes with a = (t+1, t+2, t+3, t+4) and b = a with the
first two swapped.  For Gamma = A_m the problem is closed by a short argument:
a and tau a (tau odd) have equal decks iff every a - e_i has a repeated entry,
and lie in different orbits iff a has no repeated entry; both hold only if
a_i - 1 appears in a for every i, which fails at the minimum entry.  That is
exactly why the smallest class in Ivanov's construction never matches.

This script searches every other realisable group: it enumerates all
twin-free graphs Q on m vertices, takes Gamma = Aut(Q) (via nauty), and
searches vectors a in a box for deck collisions across distinct orbits.
Every reported hit is expanded to the actual blow-up graphs and replayed
through the exact deck and isomorphism checkers before it is printed.
"""

from __future__ import annotations

import argparse
import itertools
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck  # noqa: E402

try:
    import pynauty
except ImportError:  # pragma: no cover
    pynauty = None


def all_graphs(m: int):
    """Yield one labelled representative of every isomorphism class on m vertices."""
    seen = set()
    edges = list(itertools.combinations(range(m), 2))
    for mask in range(1 << len(edges)):
        rows = [0] * m
        for b, (u, v) in enumerate(edges):
            if mask >> b & 1:
                rows[u] |= 1 << v
                rows[v] |= 1 << u
        g = Graph(tuple(rows))
        adj = {v: [w for w in range(m) if g.edge(v, w)] for v in range(m)}
        cert = pynauty.certificate(pynauty.Graph(m, adjacency_dict=adj))
        if cert in seen:
            continue
        seen.add(cert)
        yield g


def twin_free(g: Graph) -> bool:
    for u in range(g.n):
        for v in range(u + 1, g.n):
            if g.adj[u] == g.adj[v]:
                return False
    return True


def close_group(generators: list[tuple[int, ...]], m: int) -> tuple[tuple[int, ...], ...]:
    identity = tuple(range(m))
    group = {identity}
    frontier = [identity]
    gens = [tuple(g) for g in generators]
    while frontier:
        new = []
        for p in frontier:
            for g in gens:
                q = tuple(g[p[i]] for i in range(m))
                if q not in group:
                    group.add(q)
                    new.append(q)
        frontier = new
    return tuple(sorted(group))


def automorphism_group(g: Graph) -> tuple[tuple[int, ...], ...]:
    adj = {v: [w for w in range(g.n) if g.edge(v, w)] for v in range(g.n)}
    gens, order, _, _, _ = pynauty.autgrp(pynauty.Graph(g.n, adjacency_dict=adj))
    group = close_group([tuple(x) for x in gens], g.n)
    assert len(group) == round(order)
    return group


def orbit_canon(vec: tuple[int, ...], group) -> tuple[int, ...]:
    best = None
    for p in group:
        img = tuple(vec[p.index(i)] for i in range(len(vec)))  # (p.vec)[i] = vec[p^-1(i)]
        if best is None or img < best:
            best = img
    return best


def fast_orbit_canon_factory(group, m):
    inverse = [tuple(p.index(i) for i in range(m)) for p in group]

    def canon(vec):
        best = None
        for inv in inverse:
            img = tuple(vec[inv[i]] for i in range(m))
            if best is None or img < best:
                best = img
        return best

    return canon


def deck_signature(vec, canon):
    items = []
    for i, ai in enumerate(vec):
        card = list(vec)
        card[i] -= 1
        items.append((canon(tuple(card)), ai))
    return tuple(sorted(items))


def blow_up(q: Graph, vec: tuple[int, ...]) -> Graph:
    offsets = [0]
    for a in vec:
        offsets.append(offsets[-1] + a)
    n = offsets[-1]
    rows = [0] * n
    for u in range(q.n):
        for v in range(q.n):
            if u < v and q.edge(u, v):
                for x in range(offsets[u], offsets[u + 1]):
                    for y in range(offsets[v], offsets[v + 1]):
                        rows[x] |= 1 << y
                        rows[y] |= 1 << x
    return Graph(tuple(rows))


def search_group(q: Graph, group, low: int, high: int, report):
    m = q.n
    canon = fast_orbit_canon_factory(group, m)
    buckets: dict[tuple, list[tuple[int, ...]]] = defaultdict(list)
    reps = 0
    for vec in itertools.product(range(low, high + 1), repeat=m):
        if canon(vec) != vec:
            continue
        reps += 1
        buckets[deck_signature(vec, canon)].append(vec)
    hits = []
    for sig, vecs in buckets.items():
        if len(vecs) > 1:
            for a, b in itertools.combinations(vecs, 2):
                hits.append((a, b))
    for a, b in hits:
        ga, gb = blow_up(q, a), blow_up(q, b)
        verified = same_deck(ga, gb) and not is_isomorphic(ga, gb)
        report(q, group, a, b, verified)
    return reps, len(hits)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m", type=int, default=5, help="order of the twin-free quotient Q")
    parser.add_argument("--low", type=int, default=2, help="minimum class size (>= 2)")
    parser.add_argument("--high", type=int, default=4, help="maximum class size")
    parser.add_argument("--min-group", type=int, default=2, help="skip trivial automorphism groups")
    args = parser.parse_args()
    if pynauty is None:
        raise SystemExit("pynauty is required")
    if args.low < 2:
        raise SystemExit("class sizes must be at least 2 so every card is a blow-up of Q")

    def report(q, group, a, b, verified):
        print("HIT" if verified else "hash-collision-refuted", q.to_graph6(), len(group), a, b, flush=True)

    t0 = time.time()
    seen_groups = {}
    total_q = total_reps = total_hits = 0
    for q in all_graphs(args.m):
        if not twin_free(q):
            continue
        group = automorphism_group(q)
        if len(group) < args.min_group:
            continue
        key = group
        total_q += 1
        if key in seen_groups:
            seen_groups[key] += 1
            continue
        seen_groups[key] = 1
        reps, hits = search_group(q, group, args.low, args.high, report)
        total_reps += reps
        total_hits += hits
        print(f"Q={q.to_graph6()} |Aut|={len(group)} orbit-reps={reps} collisions={hits}", flush=True)
    print(
        f"m={args.m} box=[{args.low},{args.high}] twin-free Q with |Aut|>={args.min_group}: {total_q}; "
        f"distinct groups: {len(seen_groups)}; orbit reps searched: {total_reps}; "
        f"collisions: {total_hits}; {time.time()-t0:.1f}s"
    )


if __name__ == "__main__":
    main()
