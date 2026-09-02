#!/usr/bin/env python3
"""Emit structured candidate graphs (graph6, one per line) for the verifier.

Twin blow-ups (--blowup q): every connected twin-free quotient Q of order q
from geng, cells of size 1 or 2 summing to --n, each doubled cell either
independent or a clique (false or true twins).  This is the regime the
vector-deck theorem leaves open (class size 2 plus singletons); the earlier
blow-up deck search compared blow-ups only against other blow-ups, whereas
the verifier compares against every graph.

Automorphism-invariant graphs (--aut c1,c2,...): random graphs on
sum(c_i) vertices invariant under a permutation with the given cycle
type, i.e. random unions of the permutation's orbits on vertex pairs.
Bi-circulants are the cycle type 7,7 at order 14; this covers every
other cycle type, in particular involutions and order-3 automorphisms
with few fixed points, where the reattachment ambiguity a counterexample
needs is available but the cyclic-orbit searches did not look.

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


def twin_free(g):
    return all((g.adj[x] | (1 << x)) != (g.adj[y] | (1 << y)) and g.adj[x] != g.adj[y]
               for x in range(g.n) for y in range(x + 1, g.n))


def blowups(q, n, geng, sample, rng):
    import subprocess
    out = subprocess.run([geng, "-q", "-c", str(q)], capture_output=True, text=True, check=True).stdout.split()
    quotients = [Graph.from_graph6(l) for l in out]
    quotients = [Q for Q in quotients if twin_free(Q)]
    k = n - q  # number of doubled cells
    combos = list(itertools.combinations(range(q), k))
    def build(Q, doubled, kinds):
        verts, rows, idx = [], [0] * n, 0
        for c in range(q):
            sz = 2 if c in doubled else 1
            verts.append(list(range(idx, idx + sz))); idx += sz
        for c in range(q):
            if len(verts[c]) == 2 and kinds[c]:
                x, y = verts[c]; rows[x] |= 1 << y; rows[y] |= 1 << x
            for d in range(c + 1, q):
                if Q.edge(c, d):
                    for x in verts[c]:
                        for y in verts[d]:
                            rows[x] |= 1 << y; rows[y] |= 1 << x
        return Graph(tuple(rows))
    if sample:
        for _ in range(sample):
            Q = rng.choice(quotients); doubled = rng.choice(combos)
            yield build(Q, doubled, [rng.random() < 0.5 for _ in range(q)])
    else:
        for Q in quotients:
            for doubled in combos:
                for kinds in itertools.product((False, True), repeat=k):
                    kk = [False] * q
                    for c, t in zip(doubled, kinds):
                        kk[c] = t
                    yield build(Q, doubled, kk)


def aut_invariant(cycles, sample, rng, p):
    n = sum(cycles)
    perm = []
    start = 0
    for c in cycles:
        perm.extend([start + (i + 1) % c for i in range(c)])
        start += c
    # orbits on pairs
    seen, orbits = set(), []
    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) in seen:
                continue
            orb, x, y = [], a, b
            while True:
                e = (min(x, y), max(x, y))
                if e in seen:
                    break
                seen.add(e); orb.append(e)
                x, y = perm[x], perm[y]
            orbits.append(orb)
    for _ in range(sample):
        rows = [0] * n
        for orb in orbits:
            if rng.random() < p:
                for a, b in orb:
                    rows[a] |= 1 << b; rows[b] |= 1 << a
        yield Graph(tuple(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--m", type=int, default=0)
    ap.add_argument("--aut", type=str, default="", help="cycle type, e.g. 2,2,2,2,2,2,2")
    ap.add_argument("--p", type=float, default=0.5)
    ap.add_argument("--twocard", action="store_true", help="keep only graphs passing the repeated-2-card filter")
    ap.add_argument("--blowup", type=int, default=0, help="quotient order q for twin blow-ups")
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--geng", default="geng")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    if a.aut:
        rng = random.Random(a.seed)
        cycles = [int(x) for x in a.aut.split(",")]
        seen, emitted, tested = set(), 0, 0
        if a.twocard:
            sys.path.insert(0, str(Path(__file__).parent))
            from twocard_filter import passes
        for g in aut_invariant(cycles, a.sample, rng, a.p):
            if len(set(g.degrees)) < 2 or not connected(g):
                continue
            c = cert(g)
            if c in seen:
                continue
            seen.add(c); tested += 1
            if a.twocard and not passes(g):
                continue
            emitted += 1
            print(g.to_graph6(), flush=True)
        print(f"aut-invariant cycle type {cycles} n={sum(cycles)}: distinct connected non-regular {tested}, emitted {emitted}", file=sys.stderr)
        return
    if a.blowup:
        rng = random.Random(a.seed)
        seen, emitted = set(), 0
        for g in blowups(a.blowup, a.n, a.geng, a.sample, rng):
            if len(set(g.degrees)) < 2:
                continue
            c = cert(g)
            if c in seen:
                continue
            seen.add(c); emitted += 1
            print(g.to_graph6(), flush=True)
        print(f"blow-ups q={a.blowup} n={a.n}: emitted {emitted} distinct non-regular graphs", file=sys.stderr)
        return
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
