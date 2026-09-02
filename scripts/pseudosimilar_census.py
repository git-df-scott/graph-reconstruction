#!/usr/bin/env python3
"""Census of asymmetric graphs in which every vertex is pseudosimilar to another.

A counterexample needs, at every vertex, a card that does not reveal the
deleted vertex's neighbourhood.  Kimble, Schwenk and Stockmeyer (JGT 1981)
showed there are graphs with trivial automorphism group in which every
vertex is pseudosimilar to some other vertex (equal cards, no automorphism).
This script lists the smallest such graphs from geng, as structural clues
for legal-order constructions, and reports how the repeated cards are
arranged (multiplicity profile).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph  # noqa: E402

import pynauty  # noqa: E402


def ng(g: Graph):
    adj = {x: [y for y in range(g.n) if g.edge(x, y)] for x in range(g.n)}
    return pynauty.Graph(g.n, adjacency_dict=adj)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--geng", default="geng")
    a = ap.parse_args()
    out = subprocess.run([a.geng, "-q", "-c", str(a.n)], capture_output=True, text=True, check=True).stdout
    total = asym = hits = 0
    for line in out.split():
        g = Graph.from_graph6(line)
        total += 1
        if pynauty.autgrp(ng(g))[1] != 1.0:
            continue
        asym += 1
        cards = Counter(pynauty.certificate(ng(g.delete_vertex(v))) for v in range(g.n))
        if min(cards.values()) >= 2:
            hits += 1
            print("TOTALLY-PSEUDOSIMILAR", line, "degrees", sorted(g.degrees), "card multiplicities", sorted(cards.values(), reverse=True), flush=True)
    print(f"n={a.n}: connected graphs={total} asymmetric={asym} totally pseudosimilar={hits}")


if __name__ == "__main__":
    main()
