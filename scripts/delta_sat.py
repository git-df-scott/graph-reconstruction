#!/usr/bin/env python3
"""One-graph SAT over the symmetric difference of a hypomorphic pair.

Let (G, H) be a counterexample with the card matching made the identity by
relabelling H (any counterexample admits this).  Then deg_G(v) = deg_H(v)
for every v, so the 2-coloured difference graph Delta = (E(G) - E(H)) red,
(E(H) - E(G)) blue is balanced: every vertex has equal red and blue degree.
Balanced 2-coloured graphs decompose into alternating closed trails, and
enumerating them by edge count gives a complete stratification of all
counterexamples: |Delta| = 4 is a single 2-switch, |Delta| = 6 an
alternating hexagon, and so on.  This script fixes Delta on the vertices
0..k-1 and searches for G with

    G - v  ~=  (G - v) (+) (Delta - v)     for every v,

with H = G (+) Delta not isomorphic to G.  Delta is given as red and blue
edge lists; G must contain the red edges and avoid the blue ones.

Symmetry.  The constraint system is invariant under Aut(Delta) x Sym(rest)
(simultaneous relabelling of G and H that fixes Delta), so an
adjacent-transposition lex-leader predicate is imposed on the vertices
outside Delta.  Non-isomorphism is CEGAR with nauty: each labelled H found
isomorphic to G is blocked as a clause on the G variables; the loop
terminates because the number of labelled graphs is finite, and in
practice ends in a few rounds.  --degrees pins the labelled degree vector,
which enables degree pruning of the card maps and exact tau-blocking.

Any SAT answer is replayed through the Python deck and isomorphism
checkers.  --enumerate k lists all balanced 2-coloured graphs with k
edges up to isomorphism (nauty on a vertex-coloured encoding).
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


def nauty_cert(g):
    adj = {v: [w for w in range(g.n) if g.edge(v, w)] for v in range(g.n)}
    return pynauty.certificate(pynauty.Graph(g.n, adjacency_dict=adj))


class Enc:
    def __init__(self, n, red, blue, degrees=None):
        self.n = n
        self.red = {tuple(sorted(e)) for e in red}
        self.blue = {tuple(sorted(e)) for e in blue}
        self.delta = self.red | self.blue
        self.dverts = sorted({x for e in self.delta for x in e})
        self.d = degrees
        self.nv = 0
        self.clauses = []
        self.g = {}
        for a in range(n):
            for b in range(a + 1, n):
                self.g[(a, b)] = self.new()
        for e in self.red:
            self.add([self.g[e]])
        for e in self.blue:
            self.add([-self.g[e]])

    def new(self):
        self.nv += 1
        return self.nv

    def gv(self, a, b):
        return self.g[(min(a, b), max(a, b))]

    def flipped(self, a, b):
        return (min(a, b), max(a, b)) in self.delta

    def add(self, c):
        self.clauses.append(list(c))

    def card(self, lits, bound):
        cnf = CardEnc.equals(lits=lits, bound=bound, top_id=self.nv, encoding=EncType.totalizer)
        self.nv = max(self.nv, cnf.nv)
        for c in cnf.clauses:
            self.add(c)

    def encode(self):
        n, d = self.n, self.d
        if d is not None:
            for v in range(n):
                self.card([self.gv(v, w) for w in range(n) if w != v], d[v])
        # H[x,y] literal: G[x,y] xor flipped
        def h_true(x, y):
            return -self.gv(x, y) if self.flipped(x, y) else self.gv(x, y)
        for v in range(n):
            others = [a for a in range(n) if a != v]
            p = {}
            for a in others:
                for x in others:
                    if d is not None and abs(d[a] - d[x]) > 1:
                        continue
                    p[(a, x)] = self.new()
            for a in others:
                row = [p[(a, x)] for x in others if (a, x) in p]
                self.add(row)
                for s, t in itertools.combinations(row, 2):
                    self.add([-s, -t])
            for x in others:
                col = [p[(a, x)] for a in others if (a, x) in p]
                self.add(col)
                for s, t in itertools.combinations(col, 2):
                    self.add([-s, -t])
            if d is not None:
                for (a, x), pv in p.items():
                    ga = self.gv(a, v)
                    hx = h_true(x, v)
                    if d[a] == d[x]:
                        self.add([-pv, -ga, hx]); self.add([-pv, ga, -hx])
                    elif d[a] == d[x] + 1:
                        self.add([-pv, ga]); self.add([-pv, -hx])
                    else:
                        self.add([-pv, -ga]); self.add([-pv, hx])
            for a, b in itertools.combinations(others, 2):
                gab = self.gv(a, b)
                for x in others:
                    if (a, x) not in p:
                        continue
                    for y in others:
                        if y == x or (b, y) not in p:
                            continue
                        base = [-p[(a, x)], -p[(b, y)]]
                        hxy = h_true(x, y)
                        self.add(base + [-gab, hxy]); self.add(base + [gab, -hxy])

    def block_tau(self, tau):
        """Clause family: H != tau(G), i.e. some pair (a,b) has G[a,b] != H[tau a, tau b]
        where H[x,y] = G[x,y] xor flipped(x,y).  Blocks every G for which tau is an
        isomorphism G -> G (+) Delta, not just the labelled solution found."""
        lits = []
        for a in range(self.n):
            for b in range(a + 1, self.n):
                ga = self.gv(a, b)
                gt = self.gv(tau[a], tau[b])
                x = self.new()
                if self.flipped(tau[a], tau[b]):
                    # x <-> (ga <-> gt)
                    self.add([-x, -ga, gt]); self.add([-x, ga, -gt]); self.add([x, ga, gt]); self.add([x, -ga, -gt])
                else:
                    # x <-> (ga xor gt)
                    self.add([-x, ga, gt]); self.add([-x, -ga, -gt]); self.add([x, -ga, gt]); self.add([x, ga, -gt])
                lits.append(x)
        return lits

    def lex_leader_rest(self):
        rest = [v for v in range(self.n) if v not in self.dverts]
        if self.d is not None:
            groups = {}
            for v in rest:
                groups.setdefault(self.d[v], []).append(v)
            chains = list(groups.values())
        else:
            chains = [rest]
        for cl in chains:
            for i, j in zip(cl, cl[1:]):
                others = [k for k in range(self.n) if k not in (i, j)]
                prev = None
                for k in others:
                    a, b = self.gv(i, k), self.gv(j, k)
                    ctx = [-prev] if prev is not None else []
                    self.add(ctx + [-a, b])
                    e = self.new()
                    self.add([-e, a, -b]); self.add([-e, -a, b])
                    if prev is not None:
                        self.add([-e, prev]); self.add([e, -prev, a, b]); self.add([e, -prev, -a, -b])
                    else:
                        self.add([e, a, b]); self.add([e, -a, -b])
                    prev = e


def nauty_iso(g, h):
    """A permutation tau with h = tau(g), or None."""
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


def decode(model, enc):
    val = set(l for l in model if l > 0)
    rows = [0] * enc.n
    for (a, b), x in enc.g.items():
        if x in val:
            rows[a] |= 1 << b; rows[b] |= 1 << a
    G = Graph(tuple(rows))
    rows2 = list(rows)
    for a, b in enc.delta:
        rows2[a] ^= 1 << b; rows2[b] ^= 1 << a
    return G, Graph(tuple(rows2))


def run(n, red, blue, degrees, verbose, max_rounds=200000, allow_iso=False):
    enc = Enc(n, red, blue, degrees)
    enc.encode()
    enc.lex_leader_rest()
    if verbose:
        print(f"n={n} red={sorted(enc.red)} blue={sorted(enc.blue)} d={degrees} vars={enc.nv} clauses={len(enc.clauses)}", flush=True)
    t0 = time.time()
    rounds = 0
    with Cadical153(bootstrap_with=enc.clauses) as s:
        while True:
            if not s.solve():
                return {"status": "UNSAT", "rounds": rounds, "time": round(time.time() - t0, 2)}
            G, H = decode(s.get_model(), enc)
            if allow_iso:
                # control: the card constraints alone must be satisfiable by pairs with H ~= G
                return {"status": "SAT-CONTROL", "iso": nauty_cert(G) == nauty_cert(H), "same_deck": same_deck(G, H), "G": G.to_graph6(), "H": H.to_graph6()}
            tau = nauty_iso(G, H)
            if tau is not None:
                rounds += 1
                if rounds > max_rounds:
                    return {"status": "GAVE-UP", "rounds": rounds, "time": round(time.time() - t0, 2)}
                mark = len(enc.clauses)
                lits = enc.block_tau(tau)
                for c in enc.clauses[mark:]:
                    s.add_clause(c)
                s.add_clause(lits)
                continue
            ok = same_deck(G, H) and not is_isomorphic(G, H)
            return {"status": "SAT", "verified": ok, "G": G.to_graph6(), "H": H.to_graph6(), "rounds": rounds, "time": round(time.time() - t0, 2)}


def balanced_deltas(k):
    """All balanced 2-coloured graphs with k edges (k/2 red, k/2 blue), up to
    isomorphism.  Red edge sets are enumerated up to isomorphism (graphs with k/2
    edges and no isolated vertex); blue is then an edge-disjoint graph on the same
    vertex set with the same degree at every vertex, found by backtracking.
    Deduplicated by nauty on a coloured subdivision."""
    h = k // 2

    def canon(red, blue):
        verts = sorted({x for e in list(red) + list(blue) for x in e})
        idx = {v: i for i, v in enumerate(verts)}
        m = len(verts)
        n = m + len(red) + len(blue)
        adj = {i: [] for i in range(n)}
        cr, cb = [], []
        j = m
        for (a, b) in sorted(red):
            adj[j] = [idx[a], idx[b]]; adj[idx[a]].append(j); adj[idx[b]].append(j); cr.append(j); j += 1
        for (a, b) in sorted(blue):
            adj[j] = [idx[a], idx[b]]; adj[idx[a]].append(j); adj[idx[b]].append(j); cb.append(j); j += 1
        return pynauty.certificate(pynauty.Graph(n, adjacency_dict=adj, vertex_coloring=[set(range(m)), set(cr), set(cb)]))

    def plain_canon(edges):
        verts = sorted({x for e in edges for x in e})
        idx = {v: i for i, v in enumerate(verts)}
        adj = {i: [] for i in range(len(verts))}
        for a, b in edges:
            adj[idx[a]].append(idx[b]); adj[idx[b]].append(idx[a])
        return pynauty.certificate(pynauty.Graph(len(verts), adjacency_dict=adj))

    # red sets: h edges on vertices 0..m-1 with every vertex covered, m from ceil(sqrt) to 2h
    reds = {}
    for m in range(2, 2 * h + 1):
        alle = list(itertools.combinations(range(m), 2))
        for es in itertools.combinations(alle, h):
            if len({x for e in es for x in e}) != m:
                continue
            c = plain_canon(es)
            if c not in reds:
                reds[c] = (m, es)
    found = {}
    for m, red in reds.values():
        deg = [0] * m
        for a, b in red:
            deg[a] += 1; deg[b] += 1
        redset = set(red)
        cand = [e for e in itertools.combinations(range(m), 2) if e not in redset]
        # backtrack blue with exact degrees
        def bt(i, need, chosen):
            if sum(need) == 0:
                c = canon(red, chosen)
                if c not in found:
                    found[c] = (list(red), list(chosen))
                return
            if i == len(cand):
                return
            a, b = cand[i]
            if need[a] > 0 and need[b] > 0:
                need[a] -= 1; need[b] -= 1
                bt(i + 1, need, chosen + [cand[i]])
                need[a] += 1; need[b] += 1
            # remaining capacity check
            rem = len(cand) - i - 1
            if rem * 2 >= sum(need):
                bt(i + 1, need, chosen)
        bt(0, deg[:], [])
    return list(found.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int)
    ap.add_argument("--red", type=str, help="e.g. 0-1,2-3")
    ap.add_argument("--blue", type=str, help="e.g. 0-2,1-3")
    ap.add_argument("--degrees", type=str, default=None)
    ap.add_argument("--enumerate", type=int, default=0, help="run every balanced Delta with this many edges")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--allow-iso", action="store_true", help="control: return the first solution even if H is isomorphic to G")
    a = ap.parse_args()
    parse = lambda s: [tuple(int(x) for x in e.split("-")) for e in s.split(",")] if s else []
    d = [int(x) for x in a.degrees.split(",")] if a.degrees else None
    if a.enumerate:
        deltas = balanced_deltas(a.enumerate)
        print(f"balanced 2-coloured graphs with {a.enumerate} edges: {len(deltas)}", flush=True)
        for red, blue in deltas:
            r = run(a.n, red, blue, d, a.verbose, allow_iso=a.allow_iso)
            print(f"n={a.n} red={red} blue={blue}", r, flush=True)
        return
    print(run(a.n, parse(a.red), parse(a.blue), d, a.verbose, allow_iso=a.allow_iso))


if __name__ == "__main__":
    main()
