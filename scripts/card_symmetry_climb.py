#!/usr/bin/env python3
"""Generate asymmetric graphs all of whose cards are symmetric, by local search.

Hong's condition (every card non-controllable) is necessary for a
counterexample; the cleanest way for an asymmetric graph to satisfy it is
for every card to have a nontrivial automorphism.  Such graphs exist from
order 7 on (scripts/hong_census.py).  At order 14 they cannot be
enumerated, so this script hill-climbs on

    score(G) = number of cards with a nontrivial automorphism
              - n * [G has a nontrivial automorphism]

with single edge toggles, keeps every distinct optimum (score = n, i.e.
asymmetric with all cards symmetric), and prints them as graph6 for the
deck-fixed verifier.  Each evaluation is n+1 nauty automorphism calls.

--objective hong scores non-controllable cards instead (Hong's actual
condition, weaker than card symmetry), so the optima are exactly the
asymmetric graphs with no controllable card.  --seeds FILE starts the
walks from the graphs in a graph6 file (for example symmetric graphs from
the --aut feed) instead of random graphs; annealing with --t0/--t1 lets
the walk leave a symmetric start.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402

import pynauty  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from hong_filter import controllable  # noqa: E402


def ng(rows, n, skip=None):
    idx = [x for x in range(n) if x != skip]
    pos = {x: i for i, x in enumerate(idx)}
    return pynauty.Graph(len(idx), adjacency_dict={pos[x]: [pos[y] for y in idx if rows[x] >> y & 1] for x in idx})


def symmetric(rows, n, skip=None):
    return pynauty.autgrp(ng(rows, n, skip))[1] != 1.0


def connected(rows, n):
    seen, stack = 1, [0]
    while stack:
        x = stack.pop()
        nb = rows[x] & ~seen
        seen |= nb
        stack.extend(y for y in range(n) if nb >> y & 1)
    return seen == (1 << n) - 1


def card_ok(rows, n, v, objective):
    if objective == "sym":
        return symmetric(rows, n, v)
    return not controllable(Graph(tuple(rows)).delete_vertex(v))


def score(rows, n, objective="sym"):
    if not connected(rows, n) or len({bin(r).count("1") for r in rows}) < 2:
        return -1
    s = sum(card_ok(rows, n, v, objective) for v in range(n))
    if symmetric(rows, n):
        s -= n
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--restarts", type=int, default=200)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--p", type=float, default=0.4)
    ap.add_argument("--objective", choices=["sym", "hong"], default="sym")
    ap.add_argument("--seeds", type=str, default=None, help="graph6 file of start graphs")
    ap.add_argument("--t0", type=float, default=1.0)
    ap.add_argument("--t1", type=float, default=0.05)
    a = ap.parse_args()
    import math
    rng = random.Random(a.seed)
    n = a.n
    pairs = [(x, y) for x in range(n) for y in range(x + 1, n)]
    found = set()
    seeds = [l.strip() for l in open(a.seeds) if l.strip()] if a.seeds else None
    for r in range(a.restarts):
        if seeds:
            rows = list(Graph.from_graph6(rng.choice(seeds)).adj)
        else:
            rows = [0] * n
            for x, y in pairs:
                if rng.random() < a.p:
                    rows[x] |= 1 << y; rows[y] |= 1 << x
        cur = score(rows, n, a.objective)
        best = cur
        for i in range(a.steps):
            t = a.t0 * (a.t1 / a.t0) ** (i / a.steps)
            x, y = rng.choice(pairs)
            rows[x] ^= 1 << y; rows[y] ^= 1 << x
            s = score(rows, n, a.objective)
            if s >= cur or rng.random() < math.exp((s - cur) / t):
                cur = s
                best = max(best, cur)
                if cur == n:
                    c = pynauty.certificate(ng(rows, n))
                    if c not in found:
                        found.add(c)
                        print(Graph(tuple(rows)).to_graph6(), flush=True)
            else:
                rows[x] ^= 1 << y; rows[y] ^= 1 << x
        print(f"restart {r}: best {best}, distinct optima so far {len(found)}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
