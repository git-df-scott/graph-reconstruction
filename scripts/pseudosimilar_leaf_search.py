#!/usr/bin/env python3
"""Find pseudo-similar vertices and audit the two competing leaf extensions."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, canonical_code, canonical_deck, find_isomorphism, is_isomorphic


def overlap(left: tuple, right: tuple) -> int:
    return sum((Counter(left) & Counter(right)).values())


def pseudosimilar_pairs(g: Graph):
    card_codes = [canonical_code(g.delete_vertex(v)) for v in range(g.n)]
    for u in range(g.n):
        for v in range(u + 1, g.n):
            if card_codes[u] != card_codes[v]:
                continue
            if find_isomorphism(g, g, {u: v}) is None:
                yield u, v


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", type=int, required=True)
    parser.add_argument("--geng", default="geng")
    parser.add_argument("--connected", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()
    if not 3 <= args.vertices <= 10:
        raise SystemExit("the dependency-free pseudo-similarity census is capped at 10 vertices")
    command = [args.geng, "-q"]
    if args.connected:
        command.append("-c")
    command.append(str(args.vertices))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
    assert process.stdout is not None
    graphs = pairs = noniso_extensions = 0
    records = []
    for line in process.stdout:
        graphs += 1
        g = Graph.from_graph6(line)
        for u, v in pseudosimilar_pairs(g):
            pairs += 1
            left, right = g.add_leaf(u), g.add_leaf(v)
            if is_isomorphic(left, right):
                continue
            noniso_extensions += 1
            left_deck, right_deck = canonical_deck(left), canonical_deck(right)
            common = overlap(left_deck, right_deck)
            records.append((common, line.strip(), u, v, left.n))
            if common == left.n:
                print(f"EXACT_CE_CANDIDATE graph6={line.strip()} u={u} v={v}")
                raise SystemExit(2)
    returncode = process.wait()
    if returncode:
        raise SystemExit(returncode)
    records.sort(reverse=True)
    print(
        f"DONE n={args.vertices} graphs={graphs} pseudo_pairs={pairs} "
        f"noniso_leaf_pairs={noniso_extensions} exact_ce_candidates=0"
    )
    for common, code, u, v, order in records[: args.top]:
        print(f"OVERLAP {common}/{order} base={code} vertices={u},{v}")


if __name__ == "__main__":
    main()
