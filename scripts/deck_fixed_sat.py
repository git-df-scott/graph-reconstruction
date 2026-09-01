#!/usr/bin/env python3
"""Hostile verification of a single graph: is G reconstructible?

Given G, search by SAT for a graph H with D(H) = D(G) and H not isomorphic
to G.  Relabelling H by the card matching makes the matching the identity,
so H - v ~= G - v for every v and, because the edge counts agree, the
labelled degrees of H equal those of G.  With G fixed the card constraints
are one-sided (each permutation P_v maps the known card G - v onto the
unknown H - v), which makes this far cheaper than the two-graph encoder in
scripts/hypomorphism_sat.py, so it scales to the orders 14 to 20 where a
candidate can be tested against every possible mate.

Non-isomorphism.  Any isomorphism G -> H preserves labelled degrees, so H
is tau(G) for some tau in W = prod Sym(degree classes).  When |W| is at
most --tau-limit every labelled copy tau(G) is blocked by one clause
(exact); otherwise the copies found by the solver are blocked one at a
time with nauty deciding isomorphism (CEGAR).

Any SAT answer is replayed through the Python deck and isomorphism
checkers.  --drop k removes the constraints of k cards (positive control:
the search must then find mates sharing the remaining cards).
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
    def __init__(self, G: Graph):
        self.G = G
        self.n = G.n
        self.d = list(G.degrees)
        self.nv = 0
        self.clauses = []
        self.h = {}
        for a in range(self.n):
            for b in range(a + 1, self.n):
                self.h[(a, b)] = self.new()
        self.p = {}

    def new(self):
        self.nv += 1
        return self.nv

    def hv(self, a, b):
        return self.h[(min(a, b), max(a, b))]

    def add(self, c):
        self.clauses.append(list(c))

    def card(self, lits, bound):
        cnf = CardEnc.equals(lits=lits, bound=bound, top_id=self.nv, encoding=EncType.totalizer)
        self.nv = max(self.nv, cnf.nv)
        for c in cnf.clauses:
            self.add(c)

    def encode(self, dropped=()):
        n, d, G = self.n, self.d, self.G
        for v in range(n):
            self.card([self.hv(v, w) for w in range(n) if w != v], d[v])
        for v in range(n):
            if v in dropped:
                continue
            others = [a for a in range(n) if a != v]
            cdeg = {a: d[a] - (1 if G.edge(a, v) else 0) for a in others}
            allowed = {}
            for a in others:
                for x in others:
                    diff = d[x] - cdeg[a]
                    if diff in (0, 1):
                        allowed[(a, x)] = self.new()
            for a in others:
                row = [allowed[(a, x)] for x in others if (a, x) in allowed]
                self.add(row)
                for s, t in itertools.combinations(row, 2):
                    self.add([-s, -t])
            for x in others:
                col = [allowed[(a, x)] for a in others if (a, x) in allowed]
                self.add(col)
                for s, t in itertools.combinations(col, 2):
                    self.add([-s, -t])
            for (a, x), pv in allowed.items():
                # deg_{H-v}(x) = d_x - H[x,v] must equal cdeg[a]
                if d[x] - cdeg[a] == 1:
                    self.add([-pv, self.hv(x, v)])
                else:
                    self.add([-pv, -self.hv(x, v)])
            for a, b in itertools.combinations(others, 2):
                e = G.edge(a, b)
                for x in others:
                    if (a, x) not in allowed:
                        continue
                    for y in others:
                        if y == x or (b, y) not in allowed:
                            continue
                        lit = self.hv(x, y) if e else -self.hv(x, y)
                        self.add([-allowed[(a, x)], -allowed[(b, y)], lit])
            self.p[v] = allowed

    def block_labelled(self, rows):
        clause = []
        for (a, b), var in self.h.items():
            clause.append(-var if rows[a] >> b & 1 else var)
        self.add(clause)


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


def relabel(G: Graph, tau):
    rows = [0] * G.n
    for a in range(G.n):
        for b in range(G.n):
            if G.edge(a, b):
                rows[tau[a]] |= 1 << tau[b]
    return tuple(rows)


def decode(model, enc):
    val = set(l for l in model if l > 0)
    rows = [0] * enc.n
    for (a, b), x in enc.h.items():
        if x in val:
            rows[a] |= 1 << b
            rows[b] |= 1 << a
    return Graph(tuple(rows))


def nauty_cert(g):
    adj = {v: [w for w in range(g.n) if g.edge(v, w)] for v in range(g.n)}
    return pynauty.certificate(pynauty.Graph(g.n, adjacency_dict=adj))


def run(G: Graph, tau_limit=200000, dropped=(), verbose=False, max_rounds=100000):
    enc = Enc(G)
    enc.encode(dropped)
    classes, wsize = degree_group(enc.d)
    exact = wsize <= tau_limit
    if exact:
        seen = set()
        for tau in all_taus(classes, G.n):
            rows = relabel(G, tau)
            if rows not in seen:
                seen.add(rows)
                enc.block_labelled(rows)
    if verbose:
        print(f"n={G.n} G={G.to_graph6()} d={sorted(enc.d)} |W|={wsize} exact={exact} vars={enc.nv} clauses={len(enc.clauses)} dropped={list(dropped)}", flush=True)
    t0 = time.time()
    rounds = 0
    cg = nauty_cert(G) if pynauty else None
    with Cadical153(bootstrap_with=enc.clauses) as s:
        while True:
            if not s.solve():
                return {"status": "UNSAT", "rounds": rounds, "time": round(time.time() - t0, 2)}
            H = decode(s.get_model(), enc)
            iso = (nauty_cert(H) == cg) if pynauty else is_isomorphic(G, H)
            if iso:
                rounds += 1
                if rounds > max_rounds:
                    return {"status": "GAVE-UP", "rounds": rounds, "time": round(time.time() - t0, 2)}
                clause = []
                for (a, b), var in enc.h.items():
                    clause.append(-var if H.edge(a, b) else var)
                s.add_clause(clause)
                continue
            ok = (not dropped and same_deck(G, H) and not is_isomorphic(G, H))
            common = sum(1 for v in range(G.n) if v not in dropped)
            return {"status": "SAT", "verified_counterexample": ok, "H": H.to_graph6(), "iso": False, "matched_cards": common, "rounds": rounds, "time": round(time.time() - t0, 2)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("graphs", nargs="*", help="graph6 strings (or - for stdin, one per line)")
    ap.add_argument("--drop", type=int, default=0, help="drop the constraints of this many cards (control)")
    ap.add_argument("--tau-limit", type=int, default=200000)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    lines = a.graphs
    if lines == ["-"]:
        lines = [l.strip() for l in sys.stdin if l.strip()]
    for g6 in lines:
        G = Graph.from_graph6(g6)
        dropped = tuple(range(G.n - a.drop, G.n)) if a.drop else ()
        r = run(G, a.tau_limit, dropped, a.verbose)
        print(g6, r, flush=True)


if __name__ == "__main__":
    main()
