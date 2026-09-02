#!/usr/bin/env python3
"""Census of graphs with no controllable card (Hong's necessary condition).

Hong (1982): a graph with a controllable card is reconstructible.  So every
counterexample has all cards non-controllable, i.e. every card has an
eigenvector orthogonal to the all-ones vector.  Random graphs fail this at
once (at order 14 the chance that all 14 cards are non-controllable is
astronomically small), so counterexamples live in a thin, highly
structured set.  Symmetric graphs are in it trivially (an automorphism of
a card gives a non-main eigenvalue).  The interesting members are the
ASYMMETRIC graphs with no controllable card: the only place an asymmetric
counterexample could live.  This script lists them at small order from
geng, with the mechanism (which cards are symmetric, which have twins,
which are non-controllable for a subtler reason).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from grc import Graph  # noqa: E402

from hong_filter import controllable  # noqa: E402

import pynauty  # noqa: E402


def autsize(g: Graph) -> float:
    return pynauty.autgrp(pynauty.Graph(g.n, adjacency_dict={x: [y for y in range(g.n) if g.edge(x, y)] for x in range(g.n)}))[1]


def has_twins(g: Graph) -> bool:
    return any((g.adj[x] | (1 << x)) == (g.adj[y] | (1 << y)) or g.adj[x] == g.adj[y] for x in range(g.n) for y in range(x + 1, g.n))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--geng", default="geng")
    a = ap.parse_args()
    out = subprocess.run([a.geng, "-q", "-c", str(a.n)], capture_output=True, text=True, check=True).stdout.split()
    total = nocontrol = asym_nocontrol = 0
    for line in out:
        g = Graph.from_graph6(line)
        total += 1
        cards = [g.delete_vertex(v) for v in range(g.n)]
        if any(controllable(c) for c in cards):
            continue
        nocontrol += 1
        if autsize(g) != 1.0:
            continue
        asym_nocontrol += 1
        mech = []
        for c in cards:
            if autsize(c) != 1.0:
                mech.append("sym")
            elif has_twins(c):
                mech.append("twin")
            else:
                mech.append("subtle")
        print("ASYMMETRIC-NO-CONTROLLABLE-CARD", line, "degrees", sorted(g.degrees), "card mechanisms", " ".join(mech), flush=True)
    print(f"n={a.n}: connected={total} no-controllable-card={nocontrol} of which asymmetric={asym_nocontrol}", flush=True)


if __name__ == "__main__":
    main()
