#!/usr/bin/env python3
"""One-graph SAT for graphs whose deck is closed under complementation.

If D(G) = D(complement(G)) and G is not self-complementary, then
(G, complement(G)) is a counterexample.  Equal edge counts force
e(G) = C(n,2)/2, so n must be 0 or 1 mod 4: impossible at 14 and 15, first
possible at 16 (60 edges) and 17 (68 edges).

Unlike the difference-graph search, the card matching psi cannot be made
the identity by relabelling (relabelling G relabels its complement the same
way), so psi is a permutation variable with deg(psi(v)) = n - 1 - deg(v).
The labelled degree vector d is fixed per instance and must be symmetric
about (n-1)/2.  Card constraints: P_v maps V - v onto V - psi(v) with

    P_v[a][x] and P_v[b][y]  ->  (G[a,b] <-> not G[x,y]),

pruned by degree compatibility: deg_{G-v}(a) = deg_{Gbar - psi(v)}(x) where
deg_{Gbar}(x) = n-1-d[x].  Self-complementary solutions (Gbar = tau(G)) are
blocked at class level for the tau nauty returns (CEGAR); when the
degree-class group W is small every tau in W is blocked up front.
"""

from __future__ import annotations

import argparse
import itertools
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck  # noqa: E402

from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.solvers import Cadical153  # noqa: E402

import pynauty  # noqa: E402


class Enc:
    def __init__(self, n, d):
        self.n, self.d = n, d
        self.nv = 0
        self.clauses = []
        self.g = {}
        for a in range(n):
            for b in range(a + 1, n):
                self.g[(a, b)] = self.new()

    def new(self):
        self.nv += 1
        return self.nv

    def gv(self, a, b):
        return self.g[(min(a, b), max(a, b))]

    def add(self, c):
        self.clauses.append(list(c))

    def card(self, lits, bound):
        cnf = CardEnc.equals(lits=lits, bound=bound, top_id=self.nv, encoding=EncType.totalizer)
        self.nv = max(self.nv, cnf.nv)
        for c in cnf.clauses:
            self.add(c)

    def encode(self):
        n, d = self.n, self.d
        for v in range(n):
            self.card([self.gv(v, w) for w in range(n) if w != v], d[v])
        # psi: permutation with d[psi(v)] = n-1-d[v]
        self.psi = {}
        for v in range(n):
            for w in range(n):
                if d[w] == n - 1 - d[v]:
                    self.psi[(v, w)] = self.new()
        for v in range(n):
            row = [self.psi[(v, w)] for w in range(n) if (v, w) in self.psi]
            self.add(row)
            for s, t in itertools.combinations(row, 2):
                self.add([-s, -t])
        for w in range(n):
            col = [self.psi[(v, w)] for v in range(n) if (v, w) in self.psi]
            self.add(col)
            for s, t in itertools.combinations(col, 2):
                self.add([-s, -t])
        # cards
        for v in range(n):
            others = [a for a in range(n) if a != v]
            p = {}
            for a in others:
                for x in range(n):
                    # deg_{G-v}(a) in {d[a]-1, d[a]}; deg_{Gbar-psi(v)}(x) in {n-1-d[x]-1, n-1-d[x]}
                    if abs(d[a] - (n - 1 - d[x])) > 1:
                        continue
                    p[(a, x)] = self.new()
            for a in others:
                row = [p[(a, x)] for x in range(n) if (a, x) in p]
                self.add(row)
                for s, t in itertools.combinations(row, 2):
                    self.add([-s, -t])
            for x in range(n):
                col = [p[(a, x)] for a in others if (a, x) in p]
                # column x is used unless x = psi(v)
                if (v, x) in self.psi:
                    self.add(col + [self.psi[(v, x)]])
                    for c in col:
                        self.add([-c, -self.psi[(v, x)]])
                else:
                    self.add(col)
                for s, t in itertools.combinations(col, 2):
                    self.add([-s, -t])
            # degree inside the card: d[a] - G[a,v] == (n-1-d[x]) - (1 - G[x,psi(v)])
            for (a, x), pv in p.items():
                ga = self.gv(a, v)
                dx = n - 1 - d[x]
                # need: d[a] - ga == dx - 1 + gx_psi, where gx_psi = G[x, psi(v)] (unknown psi(v))
                # encode via: for each candidate w = psi(v), w != x
                for w in range(n):
                    if (v, w) not in self.psi or w == x:
                        continue
                    gx = self.gv(x, w)
                    base = [-pv, -self.psi[(v, w)]]
                    # d[a] - ga == dx - 1 + gx
                    if d[a] == dx:
                        # ga == 1 - gx  -> ga xor gx = 1
                        self.add(base + [ga, gx]); self.add(base + [-ga, -gx])
                    elif d[a] == dx + 1:
                        # ga = 1 - gx + 1 -> ga=1, gx=1
                        self.add(base + [ga]); self.add(base + [gx])
                    elif d[a] == dx - 1:
                        self.add(base + [-ga]); self.add(base + [-gx])
                    else:
                        self.add(base)
            for a, b in itertools.combinations(others, 2):
                gab = self.gv(a, b)
                for x in range(n):
                    if (a, x) not in p:
                        continue
                    for y in range(n):
                        if y == x or (b, y) not in p:
                            continue
                        gxy = self.gv(x, y)
                        base = [-p[(a, x)], -p[(b, y)]]
                        self.add(base + [gab, gxy]); self.add(base + [-gab, -gxy])

    def block_tau(self, tau):
        """Some pair has G[a,b] == G[tau a, tau b] (so Gbar != tau(G))."""
        lits = []
        for a in range(self.n):
            for b in range(a + 1, self.n):
                ga, gt = self.gv(a, b), self.gv(tau[a], tau[b])
                x = self.new()
                self.add([-x, -ga, gt]); self.add([-x, ga, -gt]); self.add([x, ga, gt]); self.add([x, -ga, -gt])
                lits.append(x)
        return lits


def degree_group(d):
    classes = {}
    for v, x in enumerate(d):
        classes.setdefault(x, []).append(v)
    size = 1
    for c in classes.values():
        size *= math.factorial(len(c))
    return classes, size


def decode(model, enc):
    val = set(l for l in model if l > 0)
    rows = [0] * enc.n
    for (a, b), x in enc.g.items():
        if x in val:
            rows[a] |= 1 << b; rows[b] |= 1 << a
    full = (1 << enc.n) - 1
    comp = tuple((full ^ rows[a]) & ~(1 << a) for a in range(enc.n))
    return Graph(tuple(rows)), Graph(comp)


def nauty_iso(g, h):
    def lab(x):
        adj = {v: [w for w in range(x.n) if x.edge(v, w)] for v in range(x.n)}
        gr = pynauty.Graph(x.n, adjacency_dict=adj)
        return pynauty.certificate(gr), pynauty.canon_label(gr)
    cg, lg = lab(g); ch, lh = lab(h)
    if cg != ch:
        return None
    tau = [0] * g.n
    for k in range(g.n):
        tau[lg[k]] = lh[k]
    return tau


def run(n, d, verbose):
    enc = Enc(n, d)
    enc.encode()
    t0 = time.time()
    rounds = 0
    if verbose:
        _, w = degree_group(d)
        print(f"n={n} d={d} |W|={w} vars={enc.nv} clauses={len(enc.clauses)}", flush=True)
    with Cadical153(bootstrap_with=enc.clauses) as s:
        while True:
            if not s.solve():
                return {"status": "UNSAT", "rounds": rounds, "time": round(time.time() - t0, 2)}
            G, H = decode(s.get_model(), enc)
            tau = nauty_iso(G, H)
            if tau is not None:
                rounds += 1
                mark = len(enc.clauses)
                lits = enc.block_tau(tau)
                for c in enc.clauses[mark:]:
                    s.add_clause(c)
                s.add_clause(lits)
                continue
            ok = same_deck(G, H) and not is_isomorphic(G, H)
            return {"status": "SAT", "verified": ok, "G": G.to_graph6(), "rounds": rounds, "time": round(time.time() - t0, 2)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--degrees", type=str, required=True)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    d = [int(x) for x in a.degrees.split(",")]
    assert len(d) == a.n
    assert sum(d) == a.n * (a.n - 1) // 2, "edge count must be half of C(n,2), i.e. degree sum C(n,2)"
    assert sorted(d) == sorted(a.n - 1 - x for x in d), "degree vector must be symmetric about (n-1)/2"
    print(run(a.n, d, a.verbose))


if __name__ == "__main__":
    main()
