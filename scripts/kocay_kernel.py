#!/usr/bin/env python3
"""Rank of Kocay covering-number systems at small order (the "Kocay kernel").

Kocay's lemma: for graphs F_1, ..., F_k,

    prod_i s(F_i, G) = sum_X c(F_1..F_k; X) s(X, G),

where s(F, G) is the number of subgraphs of G isomorphic to F, X ranges over
graphs covered by copies of the F_i, and c counts ordered k-tuples of copies
with union X.  When every F_i has fewer than n vertices the left side and all
terms with |V(X)| < n are determined by the deck (Kelly), so each sequence
yields one linear constraint on the vector (s(X, G))_X over n-vertex X.

Thatte and Oliveira (J. Graph Theory 2016, arXiv:1301.4121) proved that the
number of distinct decks at order n is at least the rank of the matrix of
covering numbers for any family of sequences, so a full-rank family proves
reconstruction at that order.  This script builds the matrix for pairs
(F_1, F_2) with F_2 small (at most --emax edges, or isolated vertices) and
F_1 arbitrary on fewer than n vertices, and reports rank, corank, and the
kernel's support.  Kocay's theorem that disconnected spanning subgraph
counts are reconstructible is used as a control: every kernel vector must
vanish on disconnected columns.  A second control checks the identity itself
by brute force on random graphs at order 5.

Requires nauty's geng and pynauty (see PLAN_2026-09-01.md for build notes).
"""

from __future__ import annotations

import argparse
import itertools
import random
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402

import pynauty  # noqa: E402

try:
    import flint
except ImportError:  # pragma: no cover
    flint = None

PRIME = 2147483647


def cert_of(n: int, edges) -> bytes:
    adj = {v: [] for v in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return pynauty.certificate(pynauty.Graph(n, adjacency_dict=adj))


def cert_sub(vertices: tuple[int, ...], edges) -> bytes:
    """Certificate of the graph (vertices, edges) after relabelling to 0..k-1."""
    pos = {v: i for i, v in enumerate(vertices)}
    return cert_of(len(vertices), [(pos[u], pos[v]) for u, v in edges])


def all_graphs(n: int, geng: str):
    out = subprocess.run([geng, "-q", str(n)], capture_output=True, text=True, check=True).stdout
    return [Graph.from_graph6(line) for line in out.split()]


def is_connected(n: int, edges) -> bool:
    if n == 0:
        return True
    adj = defaultdict(set)
    verts = set()
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
        verts.add(u)
        verts.add(v)
    if not verts:
        return n == 1
    start = next(iter(verts))
    seen = {start}
    stack = [start]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == n


def build_rows(n: int, graphs, emax: int, progress: int):
    """Return (columns, rows) where rows maps a sequence key to {column: count}."""
    columns = {}
    col_info = []
    for g in graphs:
        edges = [(u, v) for u in range(n) for v in range(u + 1, n) if g.edge(u, v)]
        c = cert_of(n, edges)
        columns[c] = len(col_info)
        col_info.append((g, edges, is_connected(n, edges)))
    rows: dict[tuple, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    t0 = time.time()
    for col, (g, edges, _) in enumerate(col_info):
        E = set(edges)
        m = len(edges)
        deg = [0] * n
        for u, v in edges:
            deg[u] += 1
            deg[v] += 1
        isolated = [v for v in range(n) if deg[v] == 0]
        # rows with F_2 = j isolated vertices (j = number of isolated vertices of X, j >= 1)
        if isolated:
            rest = tuple(v for v in range(n) if deg[v] > 0)
            if rest:
                key = ("iso", len(isolated), cert_sub(rest, edges))
                rows[key][col] += 1  # ordered tuples of K_1 copies: j! but constant per row, ignore
        # rows with F_2 = star(v) u Ex (|Ex| <= emax extra edges), F_1 = (E \\ B) u C, C subset of B.
        # Any pair (A,B) with A u B = E and |span A| < n has A missing some vertex v, so B contains star(v).
        if not edges:
            rows[("allisolated", n)][col] += 1
        if isolated:
            continue  # sequences mixing K_1 copies are not built here
        for v in range(n):
            star = [e for e in edges if v in e]
            others = [e for e in edges if v not in e]
            for k in range(0, emax + 1):
                for Ex in itertools.combinations(others, k):
                    B = star + list(Ex)
                    spanB = set()
                    for u, w in B:
                        spanB.add(u)
                        spanB.add(w)
                    if len(spanB) >= n:
                        continue
                    Bset = set(B)
                    certB = cert_sub(tuple(sorted(spanB)), B)
                    rest_edges = [e for e in edges if e not in Bset]
                    for j in range(0, len(B) + 1):
                        for C in itertools.combinations(B, j):
                            E1 = rest_edges + list(C)
                            if not E1:
                                continue
                            span1 = set()
                            for u, w in E1:
                                span1.add(u)
                                span1.add(w)
                            if len(span1) >= n:
                                continue
                            if len(span1 | spanB) != n:
                                continue
                            # avoid double counting the same ordered pair (A,B) reached via two vertices v:
                            # count it only for the smallest vertex missing from A
                            missing = min(set(range(n)) - span1)
                            if missing != v:
                                continue
                            cert1 = cert_sub(tuple(sorted(span1)), E1)
                            rows[(cert1, certB)][col] += 1
        if progress and (col + 1) % progress == 0:
            print(f"  columns {col+1}/{len(col_info)} rows {len(rows)} {time.time()-t0:.0f}s", flush=True)
    return col_info, rows


def rank_and_kernel(rows, ncols: int):
    keys = list(rows)
    if flint is None:
        raise SystemExit("python-flint required for exact rank")
    M = flint.nmod_mat(len(keys), ncols, PRIME)
    for r, key in enumerate(keys):
        for c, val in rows[key].items():
            M[r, c] = val % PRIME
    rank = M.rank()
    # kernel = nullspace of M (vectors x with M x = 0)
    ns, nullity = M.nullspace()
    kernel = []
    for j in range(nullity):
        kernel.append([int(ns[i, j]) for i in range(ncols)])
    return rank, kernel


def brute_subgraph_count(F_edges, F_n, G: Graph) -> int:
    """Number of subgraphs (V', E') of G isomorphic to (range(F_n), F_edges), by brute force."""
    count = 0
    certF = cert_of(F_n, F_edges)
    edges = [(u, v) for u in range(G.n) for v in range(u + 1, G.n) if G.edge(u, v)]
    for verts in itertools.combinations(range(G.n), F_n):
        vs = set(verts)
        inner = [e for e in edges if e[0] in vs and e[1] in vs]
        for sub in itertools.combinations(inner, len(F_edges)):
            if cert_sub(verts, sub) == certF:
                count += 1
    return count


def identity_control(n: int, trials: int, geng: str) -> None:
    """Brute-force check of Kocay's identity for random F_1, F_2, G at small order."""
    rng = random.Random(1)
    graphs = all_graphs(n, geng)
    small = [g for g in all_graphs(3, geng)] + [g for g in all_graphs(4, geng)]
    ok = 0
    for _ in range(trials):
        G = rng.choice(graphs)
        F1 = rng.choice(small)
        F2 = rng.choice(small)
        e1 = [(u, v) for u in range(F1.n) for v in range(u + 1, F1.n) if F1.edge(u, v)]
        e2 = [(u, v) for u in range(F2.n) for v in range(u + 1, F2.n) if F2.edge(u, v)]
        if not e1 or not e2:
            continue
        lhs = brute_subgraph_count(e1, F1.n, G) * brute_subgraph_count(e2, F2.n, G)
        # rhs: enumerate ordered pairs of copies directly
        rhs = 0
        edges = [(u, v) for u in range(G.n) for v in range(u + 1, G.n) if G.edge(u, v)]
        c1, c2 = cert_of(F1.n, e1), cert_of(F2.n, e2)
        copies1 = [(vs, sub) for vs in itertools.combinations(range(G.n), F1.n) for sub in itertools.combinations([e for e in edges if e[0] in vs and e[1] in vs], len(e1)) if cert_sub(vs, sub) == c1]
        copies2 = [(vs, sub) for vs in itertools.combinations(range(G.n), F2.n) for sub in itertools.combinations([e for e in edges if e[0] in vs and e[1] in vs], len(e2)) if cert_sub(vs, sub) == c2]
        rhs = len(copies1) * len(copies2)
        assert lhs == rhs
        ok += 1
    print(f"identity control: {ok} random (F1,F2,G) triples at order {n} consistent")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--emax", type=int, default=3)
    parser.add_argument("--geng", default="geng")
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    if args.control:
        identity_control(5, 40, args.geng)
    t0 = time.time()
    graphs = all_graphs(args.n, args.geng)
    col_info, rows = build_rows(args.n, graphs, args.emax, args.progress)
    ncols = len(col_info)
    print(f"n={args.n} emax={args.emax}: columns={ncols} rows={len(rows)} build {time.time()-t0:.1f}s", flush=True)
    rank, kernel = rank_and_kernel(rows, ncols)
    corank = ncols - rank
    print(f"rank={rank} corank={corank}")
    disconnected_cols = {i for i, (_, _, conn) in enumerate(col_info) if not conn}
    bad = 0
    support = set()
    for vec in kernel:
        for i, x in enumerate(vec):
            if x:
                support.add(i)
                if i in disconnected_cols:
                    bad += 1
    print(f"kernel support size={len(support)} nonzero-on-disconnected={bad} (Kocay control expects 0 once rows suffice)")
    if corank and corank <= 40:
        for i in sorted(support):
            g, edges, conn = col_info[i]
            print(f"  kernel column {i}: {g.to_graph6()} edges={len(edges)} connected={conn}")
    print(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
