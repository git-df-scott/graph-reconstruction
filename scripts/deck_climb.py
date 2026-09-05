#!/usr/bin/env python3
"""Hill-climb over graphs G on the deck-fixed MaxSAT objective.

f(G) = maximum number of cards of G shared with a non-isomorphic graph H
having the same labelled degree sequence (scripts/deck_fixed_sat.py,
--maxsat).  A counterexample is exactly a graph with f(G) = n.  Unlike the
annealer in scripts/mutation_anneal.py, which co-evolves one specific H,
this objective is maximised over every possible mate by the solver, so the
climb over G sees the true distance to non-reconstructibility.

Moves: toggle one edge of G (connected, non-regular graphs only, since
disconnected and regular graphs are reconstructible).  First-improvement
with plateau moves allowed; restarts from structured seeds (twin blow-ups
with cells of size 1 and 2, bi-circulants) or random graphs.  Every f(G)
evaluation is cached by nauty certificate.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from grc import Graph  # noqa: E402

from deck_fixed_sat import nauty_cert, run_maxsat  # noqa: E402
from mutation_anneal import bicirc_start, blowup_start, random_start  # noqa: E402


def connected(rows, n):
    seen, stack = 1, [0]
    while stack:
        x = stack.pop()
        nb = rows[x] & ~seen
        seen |= nb
        stack.extend(y for y in range(n) if nb >> y & 1)
    return seen == (1 << n) - 1


def admissible(rows, n):
    degs = [bin(r).count("1") for r in rows]
    return len(set(degs)) >= 2 and connected(rows, n)


class Climber:
    def __init__(self, n, rng, tau_limit, timeout):
        self.n, self.rng, self.tau_limit = n, rng, tau_limit
        self.cache = {}
        self.evals = 0
        self.timeout = timeout

    def f(self, rows):
        G = Graph(tuple(rows))
        c = nauty_cert(G)
        if c in self.cache:
            return self.cache[c]
        r = run_maxsat(G, self.tau_limit)
        self.evals += 1
        val = r.get("matched_cards", 0) if r["status"] == "OPT" else 0
        self.cache[c] = (val, r)
        return self.cache[c]

    def climb(self, rows, steps):
        n = self.n
        cur, info = self.f(rows)
        best, best_rows, best_info = cur, list(rows), info
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
        stale = 0
        for _ in range(steps):
            a, b = self.rng.choice(pairs)
            rows[a] ^= 1 << b; rows[b] ^= 1 << a
            if not admissible(rows, n):
                rows[a] ^= 1 << b; rows[b] ^= 1 << a
                continue
            val, inf = self.f(rows)
            if val >= cur:
                if val > cur:
                    stale = 0
                cur, info = val, inf
                if val > best:
                    best, best_rows, best_info = val, list(rows), inf
                    if best == n:
                        return best, best_rows, best_info
            else:
                rows[a] ^= 1 << b; rows[b] ^= 1 << a
                stale += 1
        return best, best_rows, best_info


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--restarts", type=int, default=10)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--start", choices=["random", "bicirc", "blowup"], default="blowup")
    ap.add_argument("--p", type=float, default=0.5)
    ap.add_argument("--tau-limit", type=int, default=200000)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    cl = Climber(a.n, rng, a.tau_limit, None)
    t0 = time.time()
    overall = 0
    for r in range(a.restarts):
        while True:
            st = {"random": lambda: random_start(a.n, rng, a.p), "bicirc": lambda: bicirc_start(a.n, rng), "blowup": lambda: blowup_start(a.n, rng, a.p)}[a.start]()
            if admissible(st.g, a.n):
                break
        best, rows, info = cl.climb(list(st.g), a.steps)
        G = Graph(tuple(rows))
        overall = max(overall, best)
        tag = " COUNTEREXAMPLE-CANDIDATE" if best == a.n else ""
        print(f"n={a.n} start={a.start} restart={r} best_f={best}{tag} G={G.to_graph6()} H={info.get('H')} deg={sorted(G.degrees)} evals={cl.evals} ({time.time()-t0:.0f}s)", flush=True)
        if best == a.n:
            break
    print(f"n={a.n}: max f over {a.restarts} restarts = {overall}, evaluations {cl.evals}, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
