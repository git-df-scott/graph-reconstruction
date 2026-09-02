#!/usr/bin/env python3
"""Exhaustive deck search over two-orbit (bi-Cayley) graphs and cone-over-Cayley graphs.

Motivation (docs/PLAN_2026-09-01.md, results log): a graph whose degree set is
two values with a gap of at least 2 is reconstructible from any single card,
because every neighbour of the deleted vertex falls outside the degree set.
The surviving two-degree case is consecutive degrees k, k+1, and a
counterexample needs, at every vertex, a second inequivalent reattachment
giving the same graph.  Graphs with two card types impose only two such
conditions.  Two-orbit graphs are the natural family, and bi-Cayley graphs
are the ones with a regular group action on each orbit.

Family A (bi-Cayley).  Group Gamma of order g acting regularly on two copies
of itself.  Inside copy c: x ~ y iff x^{-1} y in S_c, S_c inverse-closed and
identity-free.  Between copies: (0,x) ~ (1,y) iff x^{-1} y in T, T any
subset.  Left multiplication is an automorphism on both copies, so the deck
has at most two card types: G - (0,e) with multiplicity g and G - (1,e) with
multiplicity g.  Regular graphs (|S_0| = |S_1|) are skipped since regular
graphs are reconstructible.  Swapping copies sends (S_0,S_1,T) to
(S_1,S_0,T^{-1}); right translation of copy 1 sends T to T h.  Both are
isomorphisms, so |S_0| < |S_1| and T minimal under right translation are
imposed.

Family B (cone over Cayley).  X = Cay(Gamma, C) plus one vertex v adjacent to
S subset Gamma.  Cards: X once, and (X - e) + v(x^{-1} S \\ {e}) for x in Gamma.

Graphs are bucketed by the SHA-256 of their exact card-certificate multiset.
Any bucket holding two parents with different nauty certificates is replayed
through the independent Python deck and isomorphism checkers and reported.
Orders searched are 2g and g+1, all above 13.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck  # noqa: E402

import pynauty  # noqa: E402


# ---------------------------------------------------------------- groups ----

def close(gens, deg):
    ident = tuple(range(deg))
    elems = {ident}
    frontier = [ident]
    while frontier:
        nxt = []
        for p in frontier:
            for q in gens:
                r = tuple(q[p[i]] for i in range(deg))
                if r not in elems:
                    elems.add(r)
                    nxt.append(r)
        frontier = nxt
    return sorted(elems)


def regular_rep(elems):
    """Left regular representation as a multiplication table on indices."""
    index = {e: i for i, e in enumerate(elems)}
    deg = len(elems[0])
    g = len(elems)
    mul = [[0] * g for _ in range(g)]
    for i, a in enumerate(elems):
        for j, b in enumerate(elems):
            ab = tuple(a[b[k]] for k in range(deg))
            mul[i][j] = index[ab]
    ident = index[tuple(range(deg))]
    inv = [0] * g
    for i in range(g):
        for j in range(g):
            if mul[i][j] == ident:
                inv[i] = j
    return mul, inv, ident


def cyclic(n):
    return close([tuple((i + 1) % n for i in range(n))], n)


def dihedral(m):
    r = tuple((i + 1) % m for i in range(m))
    s = tuple((-i) % m for i in range(m))
    return close([r, s], m)


def direct(a, b):
    """Direct product of Z_a x Z_b as permutations of a*b points."""
    pts = [(i, j) for i in range(a) for j in range(b)]
    idx = {p: k for k, p in enumerate(pts)}
    g1 = tuple(idx[((i + 1) % a, j)] for i, j in pts)
    g2 = tuple(idx[(i, (j + 1) % b)] for i, j in pts)
    return close([g1, g2], a * b)


def elementary(k):
    n = 2 ** k
    gens = [tuple(x ^ (1 << b) for x in range(n)) for b in range(k)]
    return close(gens, n)


def dicyclic(m):
    """Dic_m of order 4m as permutations of its own elements (left multiplication)."""
    elems = [(i, j) for j in range(2) for i in range(2 * m)]
    idx = {e: k for k, e in enumerate(elems)}

    def mult(x, y):
        i, j = x
        k, l = y
        if j == 0:
            return ((i + k) % (2 * m), l)
        return ((i - k + m * l) % (2 * m), (1 + l) % 2)

    gens = [(1, 0), (0, 1)]
    perms = [tuple(idx[mult(gn, e)] for e in elems) for gn in gens]
    return close(perms, len(elems))


def alternating4():
    return close([(1, 2, 0, 3), (1, 0, 3, 2)], 4)


def groups_of_order(g):
    out = {}
    out[f"Z{g}"] = cyclic(g)
    if g % 2 == 0 and g >= 6:
        out[f"D{g // 2}"] = dihedral(g // 2)
    if g == 8:
        out["Z4xZ2"] = direct(4, 2)
        out["Z2^3"] = elementary(3)
        out["Q8"] = dicyclic(2)
    if g == 9:
        out["Z3xZ3"] = direct(3, 3)
    if g == 12:
        out["Z6xZ2"] = direct(6, 2)
        out["A4"] = alternating4()
        out["Dic3"] = dicyclic(3)
    return out


# --------------------------------------------------------------- graphs ----

def certificate(gr: Graph) -> bytes:
    adj = {v: [w for w in range(gr.n) if gr.edge(v, w)] for v in range(gr.n)}
    return pynauty.certificate(pynauty.Graph(gr.n, adjacency_dict=adj))


def inverse_closed_sets(g, inv, ident):
    pairs = []
    seen = set()
    for x in range(g):
        if x == ident or x in seen:
            continue
        seen.add(x)
        seen.add(inv[x])
        pairs.append((x, inv[x]) if inv[x] != x else (x,))
    for mask in range(1 << len(pairs)):
        s = set()
        for b, pr in enumerate(pairs):
            if mask >> b & 1:
                s.update(pr)
        yield frozenset(s)


def bicayley(mul, inv, S0, S1, T):
    g = len(mul)
    n = 2 * g
    rows = [0] * n
    for x in range(g):
        for y in range(g):
            q = mul[inv[x]][y]
            if q in S0 and x < y:
                rows[x] |= 1 << y
                rows[y] |= 1 << x
            if q in S1 and x < y:
                rows[g + x] |= 1 << (g + y)
                rows[g + y] |= 1 << (g + x)
            if q in T:
                rows[x] |= 1 << (g + y)
                rows[g + y] |= 1 << x
    return Graph(tuple(rows))


def cone(mul, inv, C, S):
    g = len(mul)
    n = g + 1
    rows = [0] * n
    for x in range(g):
        for y in range(x + 1, g):
            if mul[inv[x]][y] in C:
                rows[x] |= 1 << y
                rows[y] |= 1 << x
        if x in S:
            rows[x] |= 1 << g
            rows[g] |= 1 << x
    return Graph(tuple(rows))


def right_translate_min(T, mul, g):
    best = None
    for h in range(g):
        m = 0
        for t in T:
            m |= 1 << mul[t][h]
        if best is None or m < best:
            best = m
    return best


def run_family_a(name, elems, consecutive_only, report):
    mul, inv, ident = regular_rep(elems)
    g = len(mul)
    invsets = list(inverse_closed_sets(g, inv, ident))
    buckets = {}
    count = hits = 0
    t0 = time.time()
    tmasks = []
    for mask in range(1 << g):
        T = [t for t in range(g) if mask >> t & 1]
        if right_translate_min(T, mul, g) == mask:
            tmasks.append(frozenset(T))
    for S0 in invsets:
        for S1 in invsets:
            if len(S0) >= len(S1):
                continue
            if consecutive_only and len(S1) - len(S0) != 1:
                continue
            for T in tmasks:
                G = bicayley(mul, inv, S0, S1, T)
                c0 = certificate(G.delete_vertex(0))
                c1 = certificate(G.delete_vertex(g))
                key = hashlib.sha256(b"A" + min(c0, c1) + b"|" + max(c0, c1) + bytes([g])).digest()
                cert = hashlib.sha256(certificate(G)).digest()
                count += 1
                prev = buckets.get(key)
                if prev is None:
                    buckets[key] = (cert, (sorted(S0), sorted(S1), sorted(T)))
                elif prev[0] != cert:
                    hits += 1
                    H = bicayley(mul, inv, frozenset(prev[1][0]), frozenset(prev[1][1]), frozenset(prev[1][2]))
                    ok = same_deck(G, H) and not is_isomorphic(G, H)
                    report(name, "A", ok, G, H, (sorted(S0), sorted(S1), sorted(T)), prev[1])
    print(f"family A {name} (order {g}, n={2*g}): graphs={count} distinct decks={len(buckets)} collisions={hits} {time.time()-t0:.0f}s", flush=True)


def run_family_b(name, elems, report):
    mul, inv, ident = regular_rep(elems)
    g = len(mul)
    invsets = list(inverse_closed_sets(g, inv, ident))
    buckets = {}
    count = hits = 0
    t0 = time.time()
    smasks = []
    for mask in range(1, (1 << g) - 1):
        S = [t for t in range(g) if mask >> t & 1]
        if right_translate_min(S, mul, g) == mask:
            smasks.append(frozenset(S))
    for C in invsets:
        for S in smasks:
            G = cone(mul, inv, C, S)
            certs = sorted(certificate(G.delete_vertex(v)) for v in range(g + 1))
            key = hashlib.sha256(b"B" + b"|".join(certs)).digest()
            cert = hashlib.sha256(certificate(G)).digest()
            count += 1
            prev = buckets.get(key)
            if prev is None:
                buckets[key] = (cert, (sorted(C), sorted(S)))
            elif prev[0] != cert:
                hits += 1
                H = cone(mul, inv, frozenset(prev[1][0]), frozenset(prev[1][1]))
                ok = same_deck(G, H) and not is_isomorphic(G, H)
                report(name, "B", ok, G, H, (sorted(C), sorted(S)), prev[1])
    print(f"family B {name} (order {g}, n={g+1}): graphs={count} distinct decks={len(buckets)} collisions={hits} {time.time()-t0:.0f}s", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=str, default="7,8,9,10,11,12")
    parser.add_argument("--family", choices=["A", "B", "AB"], default="AB")
    parser.add_argument("--consecutive-only", action="store_true")
    args = parser.parse_args()

    def report(name, fam, ok, G, H, p1, p2):
        print(("HIT" if ok else "REFUTED-ON-REPLAY"), fam, name, "n=", G.n, "G=", G.to_graph6(), "H=", H.to_graph6(), p1, p2, flush=True)

    for g in [int(x) for x in args.orders.split(",")]:
        for name, elems in groups_of_order(g).items():
            if "A" in args.family:
                run_family_a(name, elems, args.consecutive_only, report)
            if "B" in args.family:
                run_family_b(name, elems, report)


if __name__ == "__main__" and "--family-c" not in sys.argv:
    main()


# ------------------------------------------------ family C: cards of Cayley graphs ----

def run_family_c(name, elems, report):
    """G = Cay(Gamma, C) minus the identity vertex; bucket decks across all C."""
    mul, inv, ident = regular_rep(elems)
    g = len(mul)
    invsets = list(inverse_closed_sets(g, inv, ident))
    buckets = {}
    count = hits = 0
    t0 = time.time()
    for C in invsets:
        if len(C) in (0, g - 1):
            continue
        X = cone(mul, inv, C, frozenset())  # Cayley graph plus an isolated vertex g
        X = X.delete_vertex(g)
        G = X.delete_vertex(ident)
        certs = sorted(certificate(G.delete_vertex(v)) for v in range(G.n))
        key = hashlib.sha256(b"C" + b"|".join(certs)).digest()
        cert = hashlib.sha256(certificate(G)).digest()
        count += 1
        prev = buckets.get(key)
        if prev is None:
            buckets[key] = (cert, sorted(C))
        elif prev[0] != cert:
            hits += 1
            H = cone(mul, inv, frozenset(prev[1]), frozenset()).delete_vertex(g).delete_vertex(ident)
            ok = same_deck(G, H) and not is_isomorphic(G, H)
            report(name, "C", ok, G, H, sorted(C), prev[1])
    print(f"family C {name} (order {g}, n={g-1}): graphs={count} distinct decks={len(buckets)} collisions={hits} {time.time()-t0:.0f}s", flush=True)


def main_c():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orders", type=str, default="15,16,17,18,19,20,21,22,23,24")
    a = ap.parse_args()

    def report(name, fam, ok, G, H, p1, p2):
        print(("HIT" if ok else "REFUTED-ON-REPLAY"), fam, name, "n=", G.n, "G=", G.to_graph6(), "H=", H.to_graph6(), p1, p2, flush=True)

    for g in [int(x) for x in a.orders.split(",")]:
        groups = {f"Z{g}": cyclic(g)}
        if g % 2 == 0:
            groups[f"D{g // 2}"] = dihedral(g // 2)
        for name, elems in groups.items():
            run_family_c(name, elems, report)


if __name__ == "__main__" and "--family-c" in sys.argv:
    sys.argv.remove("--family-c")
    main_c()
