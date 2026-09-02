#!/usr/bin/env python3
"""Annealed search over one-vertex mutations for maximum common cards.

Any hypomorphic pair is a one-vertex mutation: if G - v ~= H - w then H is G
with the neighbourhood of v replaced (up to relabelling H).  So the search
space {(G, v, N')} with H = (G - v) + vertex v joined to N' contains every
counterexample, at every order, without loss of generality.

Objective: the number of common cards, i.e. the size of the multiset
intersection of the two decks (nauty certificates), with G ~= H scored as
zero.  Simulated annealing with three moves: toggle an edge of G - v (shared
by both graphs), toggle an edge at v in G, toggle a member of N'.  A score
of n is a counterexample and is replayed through the Python checkers.

This explores the mixed regime the blow-up theorem does not cover (partial
twin structure, small classes, asymmetric quotients) at orders 14 and
above, where exhaustive methods stop.

Seeds (--start): random graphs; bi-circulants on Z_m x {0,1}; or twin
blow-ups of a random quotient with cell sizes 1 and 2 (the only regime the
vector-deck theorem leaves open), each cell independent or a clique.  The
objective is graded: 10 per exactly common card plus 1 per card matched
under the coarse invariant (degree sequence, triangle count), so the
annealer can climb toward exact matches from random starts.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck  # noqa: E402

import pynauty  # noqa: E402


def cert(rows, n, skip):
    adj = {}
    idx = [x for x in range(n) if x != skip]
    pos = {x: i for i, x in enumerate(idx)}
    for x in idx:
        adj[pos[x]] = [pos[y] for y in idx if rows[x] >> y & 1]
    return pynauty.certificate(pynauty.Graph(n - 1, adjacency_dict=adj))


def full_cert(rows, n):
    adj = {x: [y for y in range(n) if rows[x] >> y & 1] for x in range(n)}
    return pynauty.certificate(pynauty.Graph(n, adjacency_dict=adj))


def coarse(rows, n, skip):
    idx = [x for x in range(n) if x != skip]
    mask = sum(1 << x for x in idx)
    degs = sorted(bin(rows[x] & mask).count("1") for x in idx)
    tri = 0
    for x in idx:
        nx = rows[x] & mask
        for y in idx:
            if y > x and nx >> y & 1:
                tri += bin(nx & rows[y] & mask & ~((1 << (y + 1)) - 1)).count("1")
    return (tuple(degs), tri)


class State:
    def __init__(self, n, rows, nprime, v):
        self.n, self.v = n, v
        self.g = list(rows)
        self.h = list(rows)
        self.h[v] = 0
        for x in range(n):
            self.h[x] &= ~(1 << v)
        for x in nprime:
            self.h[v] |= 1 << x
            self.h[x] |= 1 << v
        self.cg = [cert(self.g, n, x) for x in range(n)]
        self.ch = [cert(self.h, n, x) for x in range(n)]

    def exact(self):
        a, b = Counter(self.cg), Counter(self.ch)
        return sum(min(a[c], b[c]) for c in a)

    def score(self):
        if full_cert(self.g, self.n) == full_cert(self.h, self.n):
            return 0
        a, b = Counter(self.cg), Counter(self.ch)
        ex = sum(min(a[c], b[c]) for c in a)
        ca = Counter(coarse(self.g, self.n, x) for x in range(self.n))
        cb = Counter(coarse(self.h, self.n, x) for x in range(self.n))
        co = sum(min(ca[c], cb[c]) for c in ca)
        return 10 * ex + co

    def toggle(self, rows, certs, a, b, which):
        rows[a] ^= 1 << b
        rows[b] ^= 1 << a
        for x in range(self.n):
            if x != a and x != b:
                certs[x] = cert(rows, self.n, x)

    def move(self, rng):
        n, v = self.n, self.v
        kind = rng.random()
        if kind < 0.5:
            a, b = rng.sample([x for x in range(n) if x != v], 2)
            self.toggle(self.g, self.cg, a, b, "g")
            self.toggle(self.h, self.ch, a, b, "h")
            return ("shared", a, b)
        x = rng.choice([y for y in range(n) if y != v])
        if kind < 0.75:
            self.toggle(self.g, self.cg, v, x, "g")
            return ("g", v, x)
        self.toggle(self.h, self.ch, v, x, "h")
        return ("h", v, x)

    def undo(self, mv):
        kind, a, b = mv
        if kind == "shared":
            self.toggle(self.g, self.cg, a, b, "g")
            self.toggle(self.h, self.ch, a, b, "h")
        elif kind == "g":
            self.toggle(self.g, self.cg, a, b, "g")
        else:
            self.toggle(self.h, self.ch, a, b, "h")


def bicirc_start(n, rng):
    m = n // 2
    rows = [0] * n
    half = range(1, m // 2 + 1)
    SA = [s for s in half if rng.random() < 0.5]
    SB = [s for s in half if rng.random() < 0.5]
    T = [t for t in range(m) if rng.random() < 0.5]
    for i in range(m):
        for s in SA:
            j = (i + s) % m; rows[i] |= 1 << j; rows[j] |= 1 << i
        for s in SB:
            j = (i + s) % m; rows[m + i] |= 1 << (m + j); rows[m + j] |= 1 << (m + i)
        for t in T:
            j = (i + t) % m; rows[i] |= 1 << (m + j); rows[m + j] |= 1 << i
    v = rng.randrange(n)
    nprime = [x for x in range(n) if x != v and rng.random() < 0.5]
    return State(n, rows, nprime, v)


def blowup_start(n, rng, p):
    # quotient on q vertices, cells of size 1 or 2 summing to n, each cell independent or a clique
    while True:
        sizes = [rng.choice((1, 2)) for _ in range(n)]
        acc, cells = 0, []
        for sz in sizes:
            if acc + sz > n:
                sz = n - acc
            cells.append(sz); acc += sz
            if acc == n:
                break
        if all(cells):
            break
    q = len(cells)
    qrows = [0] * q
    for a in range(q):
        for b in range(a + 1, q):
            if rng.random() < p:
                qrows[a] |= 1 << b; qrows[b] |= 1 << a
    verts, rows = [], [0] * n
    k = 0
    for c, sz in enumerate(cells):
        verts.append(list(range(k, k + sz))); k += sz
    for a in range(q):
        if len(verts[a]) == 2 and rng.random() < 0.5:
            x, y = verts[a]; rows[x] |= 1 << y; rows[y] |= 1 << x
        for b in range(a + 1, q):
            if qrows[a] >> b & 1:
                for x in verts[a]:
                    for y in verts[b]:
                        rows[x] |= 1 << y; rows[y] |= 1 << x
    v = rng.randrange(n)
    nprime = [x for x in range(n) if x != v and rng.random() < p]
    return State(n, rows, nprime, v)


def random_start(n, rng, p):
    rows = [0] * n
    for a in range(n):
        for b in range(a + 1, n):
            if rng.random() < p:
                rows[a] |= 1 << b
                rows[b] |= 1 << a
    v = n - 1
    nprime = [x for x in range(n - 1) if rng.random() < p]
    return State(n, rows, nprime, v)


def anneal(n, steps, rng, t0, t1, p, start):
    st = {"random": lambda: random_start(n, rng, p), "bicirc": lambda: bicirc_start(n, rng), "blowup": lambda: blowup_start(n, rng, p)}[start]()
    cur = st.score()
    best = st.exact() if cur else 0
    best_pair = (list(st.g), list(st.h))
    for i in range(steps):
        t = t0 * (t1 / t0) ** (i / steps)
        mv = st.move(rng)
        s = st.score()
        if s >= cur or rng.random() < math.exp((s - cur) / t):
            cur = s
            ex = st.exact() if s else 0
            if ex > best:
                best, best_pair = ex, (list(st.g), list(st.h))
                if best == n:
                    break
        else:
            st.undo(mv)
    return best, best_pair


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--p", type=float, default=0.5)
    ap.add_argument("--t0", type=float, default=1.5)
    ap.add_argument("--t1", type=float, default=0.15)
    ap.add_argument("--start", choices=["random", "bicirc", "blowup"], default="blowup")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    overall = 0
    t_start = time.time()
    for r in range(a.restarts):
        best, (g, h) = anneal(a.n, a.steps, rng, a.t0, a.t1, a.p, a.start)
        G, H = Graph(tuple(g)), Graph(tuple(h))
        tag = ""
        if best == a.n:
            ok = same_deck(G, H) and not is_isomorphic(G, H)
            tag = " COUNTEREXAMPLE-VERIFIED" if ok else " REFUTED-ON-REPLAY"
        overall = max(overall, best)
        print(f"n={a.n} start={a.start} restart={r} best_common_cards={best}{tag} G={G.to_graph6()} H={H.to_graph6()} degG={sorted(G.degrees)} ({time.time()-t_start:.0f}s)", flush=True)
        if tag.endswith("VERIFIED"):
            break
    print(f"n={a.n}: max common cards over {a.restarts} restarts = {overall}")


if __name__ == "__main__":
    main()
