#!/usr/bin/env python3
"""Enumerate every graph of order n invariant under a permutation of a given
cycle type, up to isomorphism, as graph6 (one per line) for card_fibre.

A graph invariant under the permutation pi is a union of orbits of pi on
vertex pairs, so the class is exactly the 2^k subsets of the k pair-orbits;
each subset is emitted once per isomorphism class (nauty certificate).
With --count only the orbit count is printed.  Cycle types with at most
about 2^24 pair-orbits are practical; larger ones need sampling
(scripts/candidate_feed.py --aut).

Fed to card_fibre at order n this yields the exact statement: no
counterexample of order n + 1 has a card with an automorphism of the given
cycle type.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from grc import Graph  # noqa: E402

import pynauty  # noqa: E402


def orbits(cycle_type):
    n = sum(cycle_type)
    perm = list(range(n))
    start = 0
    for c in cycle_type:
        for i in range(c):
            perm[start + i] = start + (i + 1) % c
        start += c
    seen = set()
    orbs = []
    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) in seen:
                continue
            orb = []
            x, y = a, b
            while True:
                p = (min(x, y), max(x, y))
                if p in seen:
                    break
                seen.add(p)
                orb.append(p)
                x, y = perm[x], perm[y]
            orbs.append(orb)
    return n, orbs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cycle_type", help="e.g. 4,4,4,1")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--connected", action="store_true", help="emit only connected graphs")
    a = ap.parse_args()
    ct = [int(x) for x in a.cycle_type.split(",")]
    n, orbs = orbits(ct)
    k = len(orbs)
    if a.count:
        print(f"n={n} orbits={k} subsets={1 << k}")
        return
    masks = []
    for orb in orbs:
        rows = [0] * n
        for x, y in orb:
            rows[x] |= 1 << y
            rows[y] |= 1 << x
        masks.append(rows)
    seen = set()
    emitted = 0
    for sub in range(1 << k):
        rows = [0] * n
        s = sub
        i = 0
        while s:
            if s & 1:
                mk = masks[i]
                for v in range(n):
                    rows[v] |= mk[v]
            s >>= 1
            i += 1
        if a.connected:
            reach = 1
            frontier = 1
            while frontier:
                nxt = 0
                for v in range(n):
                    if frontier >> v & 1:
                        nxt |= rows[v]
                frontier = nxt & ~reach
                reach |= nxt
            if reach != (1 << n) - 1:
                continue
        c = pynauty.certificate(pynauty.Graph(n, adjacency_dict={v: [w for w in range(n) if rows[v] >> w & 1] for v in range(n)}))
        if c in seen:
            continue
        seen.add(c)
        emitted += 1
        print(Graph(tuple(rows)).to_graph6())
    print(f"cycle type {ct} n={n} orbits={k} distinct graphs {emitted}", file=sys.stderr)


if __name__ == "__main__":
    main()
