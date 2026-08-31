#!/usr/bin/env python3
"""Exhaustively verify ordinary reconstruction for small labeled graphs."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, canonical_code, canonical_deck


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertices", type=int, default=5)
    args = parser.parse_args()
    n = args.vertices
    if n > 7:
        raise SystemExit("dependency-free exhaustive control is intentionally capped at n=7")
    edge_slots = n * (n - 1) // 2
    deck_to_parents: dict[tuple[tuple[int, int], ...], set[tuple[int, int]]] = defaultdict(set)
    for mask in range(1 << edge_slots):
        g = Graph.from_edge_mask(n, mask)
        deck_to_parents[canonical_deck(g)].add(canonical_code(g))
    collisions = {deck: parents for deck, parents in deck_to_parents.items() if len(parents) > 1}
    print(f"n={n} labeled={1 << edge_slots} decks={len(deck_to_parents)} collisions={len(collisions)}")
    if n >= 3 and collisions:
        raise SystemExit("counterexample detected")


if __name__ == "__main__":
    main()
