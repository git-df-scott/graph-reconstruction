#!/usr/bin/env python3
"""Exactness check for the parity-selector weighted-deck abstraction.

Builds the 16-vertex selector quotient Q (4 ports, 6 pair vertices, 6
selector vertices; Ivanov 2026, arXiv:2608.11930), verifies that the 12
even port permutations used by weighted_selector_search act as
automorphisms, counts ALL automorphisms of Q by exact backtracking, checks
that no two quotient vertices are false twins, and finally expands a few
weight vectors to ordinary graphs and compares their exact canonical decks
with the weighted orbit decks.  If |Aut(Q)| = 12 and no twins exist, then
for every weight vector with all entries >= 2 the expanded graphs G(x) and
G(y) are isomorphic iff x and y lie in one A4-orbit, and the deck of G(x)
is exactly the weighted orbit deck; so a no-collision result on such a box
is a genuine exclusion, not merely a sufficient-condition search.
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from weighted_selector_search import COORDINATES, INVERSE_ACTIONS, weighted_deck, canonical_weight
from grc.graph import Graph
from grc.deck import canonical_deck
from grc.canon import canonical_code

def quotient_edges() -> set[tuple[int, int]]:
    idx = {c: i for i, c in enumerate(COORDINATES)}
    E = set()
    for kind, val in COORDINATES:
        if kind == "p":
            for pair in itertools.combinations(range(4), 2):
                if val in pair:
                    E.add(tuple(sorted((idx[(kind, val)], idx[("q", pair)]))))
        elif kind == "z":
            for edge in val:
                E.add(tuple(sorted((idx[("z", val)], idx[("q", edge)]))))
    zs = [idx[c] for c in COORDINATES if c[0] == "z"]
    for a, b in itertools.combinations(zs, 2):
        E.add((a, b))
    return E

def automorphisms(n: int, E: set[tuple[int, int]]) -> list[tuple[int, ...]]:
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    deg = [len(adj[v]) for v in range(n)]
    found = []
    perm = [-1] * n
    used = [False] * n
    def rec(v: int) -> None:
        if v == n:
            found.append(tuple(perm)); return
        for w in range(n):
            if used[w] or deg[w] != deg[v]:
                continue
            if all((perm[u] in adj[w]) == (u in adj[v]) for u in range(v)):
                perm[v] = w; used[w] = True
                rec(v + 1)
                used[w] = False; perm[v] = -1
    rec(0)
    return found

def expand(x: tuple[int, ...], E: set[tuple[int, int]]) -> Graph:
    start, n = [], 0
    for w in x:
        start.append(n); n += w
    rows = [0] * n
    for a, b in E:
        for u in range(start[a], start[a] + x[a]):
            for v in range(start[b], start[b] + x[b]):
                rows[u] |= 1 << v
                rows[v] |= 1 << u
    return Graph(tuple(rows))

def main() -> None:
    E = quotient_edges()
    n = 16
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    twins = [(u, v) for u, v in itertools.combinations(range(n), 2) if adj[u] - {v} == adj[v] - {u}]
    auts = automorphisms(n, E)
    # weighted_selector_search stores inverse actions; the action itself must map edges to edges
    a4 = set()
    for inv in INVERSE_ACTIONS:
        act = [0] * n
        for src, tgt in enumerate(inv):
            act[tgt] = src
        assert all(tuple(sorted((act[a], act[b]))) in E for a, b in E)
        a4.add(tuple(act))
    report = {"quotient_edges": len(E), "false_twin_pairs": twins,
              "automorphism_count": len(auts), "a4_count": len(a4),
              "a4_subset_of_aut": a4 <= set(auts), "aut_equals_a4": set(auts) == a4}
    # direct consistency: exact deck of the expanded graph vs weighted orbit deck
    samples = [tuple([2] * 16), tuple(2 + (i % 2) for i in range(16)), tuple(2 + ((i * 7) % 3) for i in range(16))]
    checks = []
    for x in samples:
        g = expand(x, E)
        exact = canonical_deck(g)
        abstract = weighted_deck(x)
        # exact deck: multiset of canonical codes; abstract: multiset of orbits.
        distinct_exact = len(set(exact))
        checks.append({"x": x, "n": g.n, "m": g.m, "exact_card_types": distinct_exact,
                       "abstract_card_types": len(abstract),
                       "exact_multiplicities": sorted(v for v in __import__("collections").Counter(exact).values()),
                       "abstract_multiplicities": sorted(c for _, c in abstract)})
    report["expansion_checks"] = checks
    # cross-check: two vectors in one orbit expand to isomorphic graphs (same canonical code)
    x = samples[2]
    inv = INVERSE_ACTIONS[3]
    y = tuple(x[s] for s in inv)
    report["orbit_mates_isomorphic"] = canonical_code(expand(x, E)) == canonical_code(expand(y, E))
    report["orbit_mates_same_canonical_weight"] = canonical_weight(x) == canonical_weight(y)
    print(json.dumps(report, indent=1, default=str))

if __name__ == "__main__":
    main()
