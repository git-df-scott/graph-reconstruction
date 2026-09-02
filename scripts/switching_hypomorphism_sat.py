#!/usr/bin/env python3
"""SAT search for switching-type counterexamples: H = G switched by a set U.

For a graph G and U subset V, the switching G^U flips every pair between U
and V - U.  Then (G^U) - v = (G - v)^{U - v}, so

    D(G) = D(G^U)   iff   G - v ~= (G - v)^{U - v}  for every v,

with the identity card matching, and the pair is a counterexample iff in
addition G is not isomorphic to G^U.  This is a one-graph search: the second
parent is determined by (G, U).

Symmetry breaking.  U = {0, ..., u-1} without loss of generality.  The
labelled degree vector d of G is fixed per instance and, because matched
deleted vertices have equal degree, G^U has the same labelled degrees; that
forces every vertex of U to be adjacent to exactly (n-u)/2 outside vertices
and every outside vertex to exactly u/2 vertices of U (half-adjacency, the
Godsil-McKay switching condition), which is encoded as cardinality
constraints.  Optionally U is required to induce an r-regular graph, which
makes (G, G^U) a Godsil-McKay pair and hence cospectral, a necessary
condition for any counterexample.

Card constraints.  For each v a permutation P_v on V - {v} with

    P_v[a][x] and P_v[b][y]  ->  (G[a,b] <-> G[x,y] xor [x in U] xor [y in U]),

for x, y both different from v, pruned by degree compatibility inside the
card exactly as in scripts/hypomorphism_sat.py.

Non-isomorphism.  Every isomorphism G -> G^U preserves degrees, so it lies in
W = prod Sym(degree classes); each tau in W is blocked exactly when |W| is at
most --tau-limit, otherwise by CEGAR with nauty.

Any SAT answer is replayed through the Python deck and isomorphism checkers.
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

try:
    import pynauty
except ImportError:  # pragma: no cover
    pynauty = None


class Enc:
    def __init__(self, n, u, degrees, inner_regular):
        self.n, self.u, self.d = n, u, degrees
        self.nv = 0
        self.clauses = []
        self.g = {}
        for a in range(n):
            for b in range(a + 1, n):
                self.g[(a, b)] = self.new()
        self.p = {}
        self.inner_regular = inner_regular

    def new(self):
        self.nv += 1
        return self.nv

    def gv(self, a, b):
        return self.g[(min(a, b), max(a, b))]

    def in_u(self, x):
        return x < self.u

    def flipped(self, x, y):
        return self.in_u(x) != self.in_u(y)

    def add(self, c):
        self.clauses.append(list(c))

    def card(self, lits, bound, kind):
        f = {"eq": CardEnc.equals, "le": CardEnc.atmost, "ge": CardEnc.atleast}[kind]
        cnf = f(lits=lits, bound=bound, top_id=self.nv, encoding=EncType.totalizer)
        self.nv = max(self.nv, cnf.nv)
        for c in cnf.clauses:
            self.add(c)

    def encode_structure(self):
        n, u, d = self.n, self.u, self.d
        for v in range(n):
            self.card([self.gv(v, w) for w in range(n) if w != v], d[v], "eq")
        for v in range(u):
            self.card([self.gv(v, w) for w in range(u, n)], (n - u) // 2, "eq")
        for w in range(u, n):
            self.card([self.gv(v, w) for v in range(u)], u // 2, "eq")
        if self.inner_regular is not None:
            for v in range(u):
                self.card([self.gv(v, w) for w in range(u) if w != v], self.inner_regular, "eq")

    def encode_cards(self):
        n, d = self.n, self.d
        for v in range(n):
            others = [a for a in range(n) if a != v]
            for a in others:
                for x in others:
                    self.p[(v, a, x)] = self.new()
            for a in others:
                row = [self.p[(v, a, x)] for x in others]
                self.add(row)
                for s, t in itertools.combinations(row, 2):
                    self.add([-s, -t])
            for x in others:
                col = [self.p[(v, a, x)] for a in others]
                self.add(col)
                for s, t in itertools.combinations(col, 2):
                    self.add([-s, -t])
            # degree compatibility: deg_{G-v}(a) = d_a - G[a,v]; deg_{G^U - v}(x) = d_x - G^U[x,v]
            for a in others:
                for x in others:
                    pv = self.p[(v, a, x)]
                    if abs(d[a] - d[x]) > 1:
                        self.add([-pv])
                        continue
                    ga = self.gv(a, v)
                    hx = self.gv(x, v)
                    fl = self.flipped(x, v)
                    # H[x,v] = G[x,v] xor fl : literal for H[x,v] true
                    h_true = [-hx] if fl else [hx]
                    h_false = [hx] if fl else [-hx]
                    if d[a] == d[x]:
                        # G[a,v] <-> H[x,v]
                        self.add([-pv, -ga] + h_true)
                        self.add([-pv, ga] + h_false)
                    elif d[a] == d[x] + 1:
                        self.add([-pv, ga])
                        self.add([-pv] + h_false)
                    else:
                        self.add([-pv, -ga])
                        self.add([-pv] + h_true)
            for a, b in itertools.combinations(others, 2):
                for x in others:
                    if abs(d[a] - d[x]) > 1:
                        continue
                    for y in others:
                        if x == y or abs(d[b] - d[y]) > 1:
                            continue
                        base = [-self.p[(v, a, x)], -self.p[(v, b, y)]]
                        gab, gxy = self.gv(a, b), self.gv(x, y)
                        if self.flipped(x, y):
                            # G[a,b] <-> not G[x,y]
                            self.add(base + [-gab, -gxy])
                            self.add(base + [gab, gxy])
                        else:
                            self.add(base + [-gab, gxy])
                            self.add(base + [gab, -gxy])

    def block(self, tau):
        lits = []
        for a in range(self.n):
            for b in range(a + 1, self.n):
                ga = self.gv(a, b)
                gt = self.gv(tau[a], tau[b])
                x = self.new()
                if self.flipped(tau[a], tau[b]):
                    # x <-> (ga xor (not gt)) = (ga <-> gt)
                    self.add([-x, -ga, gt]); self.add([-x, ga, -gt]); self.add([x, ga, gt]); self.add([x, -ga, -gt])
                else:
                    # x <-> (ga xor gt)
                    self.add([-x, ga, gt]); self.add([-x, -ga, -gt]); self.add([x, -ga, gt]); self.add([x, ga, -gt])
                lits.append(x)
        self.add(lits)


def degree_group(d):
    classes = {}
    for v, x in enumerate(d):
        classes.setdefault(x, []).append(v)
    size = 1
    for c in classes.values():
        size *= math.factorial(len(c))
    return classes, size


def all_taus(classes, n):
    blocks = list(classes.values())
    for perms in itertools.product(*[itertools.permutations(b) for b in blocks]):
        tau = [0] * n
        for block, perm in zip(blocks, perms):
            for s, t in zip(block, perm):
                tau[s] = t
        yield tau


def decode(model, enc):
    val = set(l for l in model if l > 0)
    rows = [0] * enc.n
    for (a, b), x in enc.g.items():
        if x in val:
            rows[a] |= 1 << b
            rows[b] |= 1 << a
    G = Graph(tuple(rows))
    rows2 = list(rows)
    for a in range(enc.n):
        for b in range(a + 1, enc.n):
            if enc.flipped(a, b):
                rows2[a] ^= 1 << b
                rows2[b] ^= 1 << a
    return G, Graph(tuple(rows2))


def nauty_iso(g, h):
    def lab(x):
        adj = {v: [w for w in range(x.n) if x.edge(v, w)] for v in range(x.n)}
        gr = pynauty.Graph(x.n, adjacency_dict=adj)
        return pynauty.certificate(gr), pynauty.canon_label(gr)
    cg, lg = lab(g)
    ch, lh = lab(h)
    if cg != ch:
        return None
    tau = [0] * g.n
    for k in range(g.n):
        tau[lg[k]] = lh[k]
    return tau


def run(n, u, degrees, inner_regular, tau_limit, verbose):
    enc = Enc(n, u, degrees, inner_regular)
    enc.encode_structure()
    enc.encode_cards()
    classes, wsize = degree_group(degrees)
    exact = wsize <= tau_limit
    if exact:
        for tau in all_taus(classes, n):
            enc.block(tau)
    if verbose:
        print(f"n={n} u={u} d={degrees} r={inner_regular} |W|={wsize} exact={exact} vars={enc.nv} clauses={len(enc.clauses)}", flush=True)
    t0 = time.time()
    rounds = 0
    while True:
        with Cadical153(bootstrap_with=enc.clauses) as s:
            if not s.solve():
                return {"status": "UNSAT", "rounds": rounds, "time": round(time.time() - t0, 2)}
            model = s.get_model()
        G, H = decode(model, enc)
        tau = None if exact else nauty_iso(G, H)
        if tau is not None:
            rounds += 1
            enc.block(tau)
            continue
        ok = same_deck(G, H) and not is_isomorphic(G, H)
        return {"status": "SAT", "verified": ok, "G": G.to_graph6(), "H": H.to_graph6(), "rounds": rounds, "time": round(time.time() - t0, 2)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--u", type=int, required=True)
    ap.add_argument("--degrees", type=str, required=True, help="labelled degree vector, U first")
    ap.add_argument("--inner-regular", type=int, default=None)
    ap.add_argument("--tau-limit", type=int, default=100000)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    d = [int(x) for x in a.degrees.split(",")]
    assert len(d) == a.n and a.u % 2 == 0 and (a.n - a.u) % 2 == 0
    print(run(a.n, a.u, d, a.inner_regular, a.tau_limit, True))


if __name__ == "__main__":
    main()
