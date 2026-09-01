#!/usr/bin/env python3
"""Emit structured candidate graphs (graph6, one per line) for the verifier.

Bi-circulants on Z_m x {0,1}: orbit A = (i,0), orbit B = (i,1);
(i,0)~(j,0) iff j-i in S_A (symmetric), (i,1)~(j,1) iff j-i in S_B,
(i,0)~(j,1) iff j-i in T.  Regular graphs are reconstructible (Kelly) and
disconnected ones too, so only connected non-regular members are emitted,
deduplicated by nauty certificate.  Optional --sample draws that many random
members instead of enumerating.
"""

from __future__ import annotations

import argparse
import itertools
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402

import pynauty  # noqa: E402


def cert(g):
    return pynauty.certificate(pynauty.Graph(g.n, adjacency_dict={x: [y for y in range(g.n) if g.edge(x, y)] for x in range(g.n)}))


def bicirc(m, SA, SB, T):
    n = 2 * m
    rows = [0] * n
    for i in range(m):
        for s in SA:
            j = (i + s) % m
            rows[i] |= 1 << j; rows[j] |= 1 << i
        for s in SB:
            j = (i + s) % m
            rows[m + i] |= 1 << (m + j); rows[m + j] |= 1 << (m + i)
        for t in T:
            j = (i + t) % m
            rows[i] |= 1 << (m + j); rows[m + j] |= 1 << i
    return Graph(tuple(rows))


def connected(g):
    seen = 1
    stack = [0]
    while stack:
        x = stack.pop()
        nb = g.rows[x] if hasattr(g, "rows") else 0
        for y in range(g.n):
            if g.edge(x, y) and not seen >> y & 1:
                seen |= 1 << y
                stack.append(y)
    return seen == (1 << g.n) - 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    m = a.m
    half = list(range(1, m // 2 + 1))
    seen = set()
    emitted = 0

    def consider(SA, SB, T):
        nonlocal emitted
        g = bicirc(m, SA, SB, T)
        degs = set(g.degrees)
        if len(degs) < 2 or not connected(g):
            return
        c = cert(g)
        if c in seen:
            return
        seen.add(c)
        emitted += 1
        print(g.to_graph6(), flush=True)

    if a.sample:
        rng = random.Random(a.seed)
        for _ in range(a.sample):
            SA = [s for s in half if rng.random() < 0.5]
            SB = [s for s in half if rng.random() < 0.5]
            T = [t for t in range(m) if rng.random() < 0.5]
            consider(SA, SB, T)
    else:
        subsets = lambda xs: itertools.chain.from_iterable(itertools.combinations(xs, k) for k in range(len(xs) + 1))
        for SA in subsets(half):
            for SB in subsets(half):
                for T in subsets(range(m)):
                    consider(SA, SB, T)
    print(f"m={m} n={2*m}: emitted {emitted} distinct connected non-regular bi-circulants", file=sys.stderr)


if __name__ == "__main__":
    main()
