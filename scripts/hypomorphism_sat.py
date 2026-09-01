#!/usr/bin/env python3
"""Exact SAT / MaxSAT search for hypomorphic nonisomorphic pairs of fixed order.

Model.  Two graphs G, H on {0..n-1} with the same labelled degree vector d
(after relabelling H so that matched cards are (i, i); matched deleted
vertices have equal degree because the edge count is reconstructible).
For each card i a permutation matrix P_i on V - {i} with

    P_i[u][x] and P_i[v][y]  ->  (G[u,v] <-> H[x,y])     for u < v, x != y, all != i.

Non-isomorphism.  Every isomorphism G -> H preserves degrees, so it lies in
W = prod Sym(degree classes).  When |W| <= --tau-limit (default 10^5, fixed
before any run) every tau in W is blocked exactly:

    OR_{u<v} (G[u,v] xor H[tau u, tau v]).

Otherwise the solver runs a CEGAR loop: each model is checked with nauty and,
if isomorphic, the isomorphism tau found is blocked with the same clause,
which removes every pair (G, tau G) at once rather than one labelling.  In
that regime lex-leader clauses for adjacent transpositions within each
degree class are added on G so that each isomorphism class of G has few
labelled representatives.  Regime note (correction 3): the exact regime
excludes twin-heavy graphs, which is where the known near-miss families live.

MaxSAT.  With --maxsat each card constraint is guarded by a selector s_i,
and RC2 maximises the number of selected cards subject to hard
non-isomorphism.  This computes the maximum number of common cards between
nonisomorphic graphs with the given degree vector (under the identity
matching normalisation, which is without loss of generality).

Any SAT answer is replayed through the independent Python deck and
isomorphism checkers and reported with graph6 strings.  Nothing here is a
counterexample until it passes docs/PLAN_2026-09-01.md Phase 3.
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
from pysat.formula import WCNF, CNF  # noqa: E402
from pysat.solvers import Cadical153  # noqa: E402
from pysat.examples.rc2 import RC2  # noqa: E402

try:
    import pynauty
except ImportError:  # pragma: no cover
    pynauty = None


class Encoder:
    def __init__(self, n: int, degrees: list[int]):
        self.n = n
        self.degrees = degrees
        self.nv = 0
        self.clauses: list[list[int]] = []
        self.g = {}
        self.h = {}
        for u in range(n):
            for v in range(u + 1, n):
                self.g[(u, v)] = self.new()
                self.h[(u, v)] = self.new()
        self.p = {}  # (i, u, x) -> var
        self.sel = {}

    def new(self) -> int:
        self.nv += 1
        return self.nv

    def gv(self, u, v):
        return self.g[(min(u, v), max(u, v))]

    def hv(self, u, v):
        return self.h[(min(u, v), max(u, v))]

    def add(self, clause):
        self.clauses.append(list(clause))

    def encode_degrees(self):
        for side in (self.gv, self.hv):
            for v in range(self.n):
                lits = [side(v, w) for w in range(self.n) if w != v]
                cnf = CardEnc.equals(lits=lits, bound=self.degrees[v], top_id=self.nv, encoding=EncType.totalizer)
                self.nv = max(self.nv, cnf.nv)
                for cl in cnf.clauses:
                    self.add(cl)

    def encode_card(self, i: int, guard: int | None):
        n = self.n
        others = [u for u in range(n) if u != i]
        for u in others:
            for x in others:
                self.p[(i, u, x)] = self.new()
        # bijection: exactly one per row and per column
        for u in others:
            row = [self.p[(i, u, x)] for x in others]
            self.add(row if guard is None else row + [-guard])
            for a, b in itertools.combinations(row, 2):
                self.add([-a, -b])
        for x in others:
            col = [self.p[(i, u, x)] for u in others]
            self.add(col if guard is None else col + [-guard])
            for a, b in itertools.combinations(col, 2):
                self.add([-a, -b])
        # degree preservation inside the card prunes: deg_{G-i}(u) = deg_{H-i}(x) is implied; skip.
        # adjacency preservation
        for u, v in itertools.combinations(others, 2):
            for x in others:
                for y in others:
                    if x == y:
                        continue
                    base = [-self.p[(i, u, x)], -self.p[(i, v, y)]]
                    if guard is not None:
                        base = base + [-guard]
                    self.add(base + [-self.gv(u, v), self.hv(x, y)])
                    self.add(base + [self.gv(u, v), -self.hv(x, y)])

    def block_isomorphism(self, tau: list[int]):
        """Forbid H = tau(G): OR_{u<v} (G[u,v] xor H[tau u, tau v])."""
        lits = []
        for u in range(self.n):
            for v in range(u + 1, self.n):
                a, b = self.gv(u, v), self.hv(tau[u], tau[v])
                x = self.new()
                # x <-> (a xor b)
                self.add([-x, a, b])
                self.add([-x, -a, -b])
                self.add([x, -a, b])
                self.add([x, a, -b])
                lits.append(x)
        self.add(lits)

    def lex_leader_adjacent(self):
        """For consecutive vertices in the same degree class, vec(G) <=_lex vec(tau G) with tau = (v v+1)."""
        n = self.n
        for v in range(n - 1):
            if self.degrees[v] != self.degrees[v + 1]:
                continue
            tau = list(range(n))
            tau[v], tau[v + 1] = tau[v + 1], tau[v]
            pairs = [(u, w) for u in range(n) for w in range(u + 1, n)]
            # lex compare sequences a_k = G[u,w], b_k = G[tau u, tau w]; require a <= b
            # standard encoding: e_k = (a_j == b_j for all j < k); (e_k and a_k) -> b_k
            eq_prev = None
            for (u, w) in pairs:
                a, b = self.gv(u, w), self.gv(tau[u], tau[w])
                if a == b:
                    continue
                if eq_prev is None:
                    self.add([-a, b])
                else:
                    self.add([-eq_prev, -a, b])
                e = self.new()
                # e <-> eq_prev and (a == b)
                if eq_prev is None:
                    self.add([-e, -a, b]); self.add([-e, a, -b]); self.add([e, a, b]); self.add([e, -a, -b])
                else:
                    self.add([-e, eq_prev]); self.add([-e, -a, b]); self.add([-e, a, -b])
                    self.add([e, -eq_prev, a, b]); self.add([e, -eq_prev, -a, -b])
                eq_prev = e


def degree_group(degrees):
    classes = {}
    for v, d in enumerate(degrees):
        classes.setdefault(d, []).append(v)
    size = 1
    for c in classes.values():
        size *= math.factorial(len(c))
    return classes, size


def all_taus(classes, n):
    blocks = list(classes.values())
    for perms in itertools.product(*[itertools.permutations(b) for b in blocks]):
        tau = [0] * n
        for block, perm in zip(blocks, perms):
            for src, dst in zip(block, perm):
                tau[src] = dst
        yield tau


def decode(model, enc: Encoder):
    val = set(l for l in model if l > 0)
    rows_g = [0] * enc.n
    rows_h = [0] * enc.n
    for (u, v), x in enc.g.items():
        if x in val:
            rows_g[u] |= 1 << v
            rows_g[v] |= 1 << u
    for (u, v), x in enc.h.items():
        if x in val:
            rows_h[u] |= 1 << v
            rows_h[v] |= 1 << u
    return Graph(tuple(rows_g)), Graph(tuple(rows_h))


def nauty_iso(g: Graph, h: Graph):
    """Return an isomorphism g->h as a list, or None."""
    if pynauty is None:
        m = None
        from grc.iso import find_isomorphism
        return list(find_isomorphism(g, h)) if find_isomorphism(g, h) else None
    def lab(x):
        adj = {v: [w for w in range(x.n) if x.edge(v, w)] for v in range(x.n)}
        gr = pynauty.Graph(x.n, adjacency_dict=adj)
        return pynauty.certificate(gr), pynauty.canon_label(gr)
    cg, lg = lab(g)
    ch, lh = lab(h)
    if cg != ch:
        return None
    # canon_label gives ordering; tau maps g vertex lg[k] -> h vertex lh[k]
    tau = [0] * g.n
    for k in range(g.n):
        tau[lg[k]] = lh[k]
    return tau


def run(n, degrees, maxsat, tau_limit, verbose, atleast=None):
    enc = Encoder(n, degrees)
    enc.encode_degrees()
    for i in range(n):
        guard = None
        if maxsat or atleast is not None:
            guard = enc.new()
            enc.sel[i] = guard
        enc.encode_card(i, guard)
    if atleast is not None:
        cnf = CardEnc.atleast(lits=list(enc.sel.values()), bound=atleast, top_id=enc.nv, encoding=EncType.totalizer)
        enc.nv = max(enc.nv, cnf.nv)
        for cl in cnf.clauses:
            enc.add(cl)
    classes, wsize = degree_group(degrees)
    exact = wsize <= tau_limit
    if exact:
        for tau in all_taus(classes, n):
            enc.block_isomorphism(tau)
    else:
        enc.lex_leader_adjacent()
    if verbose:
        print(f"n={n} d={degrees} |W|={wsize} exact={exact} vars={enc.nv} clauses={len(enc.clauses)}", flush=True)
    t0 = time.time()
    if maxsat:
        wcnf = WCNF()
        for cl in enc.clauses:
            wcnf.append(cl)
        for i, s in enc.sel.items():
            wcnf.append([s], weight=1)
        best = None
        while True:
            with RC2(wcnf, solver="cd15") as rc2:
                model = rc2.compute()
                if model is None:
                    return {"status": "UNSAT", "time": time.time() - t0}
                cost = rc2.cost
            g, h = decode(model, enc)
            tau = None if exact else nauty_iso(g, h)
            if tau is not None:
                enc.block_isomorphism(tau)
                wcnf = WCNF()
                for cl in enc.clauses:
                    wcnf.append(cl)
                for i, s in enc.sel.items():
                    wcnf.append([s], weight=1)
                continue
            common = n - cost
            return {"status": "OPT", "common_cards": common, "G": g.to_graph6(), "H": h.to_graph6(),
                    "iso": is_isomorphic(g, h), "time": time.time() - t0}
    else:
        rounds = 0
        while True:
            with Cadical153(bootstrap_with=enc.clauses) as s:
                if not s.solve():
                    return {"status": "UNSAT", "rounds": rounds, "time": time.time() - t0}
                model = s.get_model()
            g, h = decode(model, enc)
            tau = None if exact else nauty_iso(g, h)
            if tau is not None:
                rounds += 1
                enc.block_isomorphism(tau)
                continue
            ok = same_deck(g, h) and not is_isomorphic(g, h)
            common = None
            if atleast is not None:
                val = set(l for l in model if l > 0)
                common = sum(1 for s_ in enc.sel.values() if s_ in val)
            return {"status": "SAT", "verified": ok, "common_cards_selected": common, "iso": is_isomorphic(g, h),
                    "G": g.to_graph6(), "H": h.to_graph6(), "rounds": rounds, "time": time.time() - t0}


def graphical(seq):
    s = sorted(seq, reverse=True)
    if sum(s) % 2:
        return False
    for k in range(1, len(s) + 1):
        if sum(s[:k]) > k * (k - 1) + sum(min(x, k) for x in s[k:]):
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--degrees", type=str, default=None, help="comma-separated degree vector; omit to sweep")
    parser.add_argument("--maxsat", action="store_true")
    parser.add_argument("--tau-limit", type=int, default=100000)
    parser.add_argument("--max-class", type=int, default=99, help="sweep: skip sequences with a degree class larger than this")
    parser.add_argument("--min-degree", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--atleast", type=int, default=None, help="require at least this many matched cards (SAT, not MaxSAT)")
    args = parser.parse_args()
    if args.degrees:
        d = [int(x) for x in args.degrees.split(",")]
        print(run(args.n, d, args.maxsat, args.tau_limit, True, args.atleast))
        return
    n = args.n
    seen = 0
    for seq in itertools.combinations_with_replacement(range(args.min_degree, n), n):
        d = sorted(seq)
        if not graphical(d) or len(set(d)) == 1:
            continue
        classes, w = degree_group(d)
        if max(len(c) for c in classes.values()) > args.max_class:
            continue
        seen += 1
        res = run(n, d, args.maxsat, args.tau_limit, args.verbose, args.atleast)
        print(d, res, flush=True)
    print(f"sequences run: {seen}")


if __name__ == "__main__":
    main()
