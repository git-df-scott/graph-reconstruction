#!/usr/bin/env python3
"""Search a finite orbit equation extracted from the Ivanov parity selector.

The 16 coordinates are four port cells, six pair cells, and six selector
cells.  A weight vector means that every quotient vertex is replaced by an
independent false-twin class of that size.  The even port permutations A4 act
on all 16 coordinates.

For a weight vector x, deleting one ordinary vertex in cell i changes x to
x-e_i and produces that card x_i times.  Thus a collision between the exact
weighted decks of two distinct A4-orbits is a candidate ordinary GRC
counterexample.  Any reported hit must still be expanded and checked by
nauty; this script never labels a hash collision a CE.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter
from pathlib import Path


def parity(permutation: tuple[int, ...]) -> int:
    return sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    ) % 2


def edge_image(edge: tuple[int, int], permutation: tuple[int, ...]) -> tuple[int, int]:
    return tuple(sorted((permutation[edge[0]], permutation[edge[1]])))


def path_seed_image(permutation: tuple[int, ...]) -> frozenset[tuple[int, int]]:
    seed = ((0, 1), (1, 2), (2, 3))
    return frozenset(edge_image(edge, permutation) for edge in seed)


def selector_family() -> tuple[frozenset[tuple[int, int]], ...]:
    return tuple(
        sorted(
            {path_seed_image(p) for p in itertools.permutations(range(4)) if parity(p) == 0},
            key=lambda member: sorted(member),
        )
    )


def coordinate_action() -> tuple[tuple[str, object], tuple[tuple[int, ...], ...]]:
    pairs = tuple(itertools.combinations(range(4), 2))
    family = selector_family()
    coordinates: tuple[tuple[str, object], ...] = (
        tuple(("p", i) for i in range(4))
        + tuple(("q", pair) for pair in pairs)
        + tuple(("z", member) for member in family)
    )
    index = {coordinate: i for i, coordinate in enumerate(coordinates)}
    inverse_actions = []
    for p in itertools.permutations(range(4)):
        if parity(p):
            continue
        action = []
        for kind, value in coordinates:
            if kind == "p":
                target = (kind, p[value])
            elif kind == "q":
                target = (kind, edge_image(value, p))
            else:
                target = (kind, frozenset(edge_image(edge, p) for edge in value))
            action.append(index[target])
        inverse = [0] * len(action)
        for source, target in enumerate(action):
            inverse[target] = source
        inverse_actions.append(tuple(inverse))
    assert len(coordinates) == 16
    assert len(set(inverse_actions)) == 12
    return coordinates, tuple(inverse_actions)


COORDINATES, INVERSE_ACTIONS = coordinate_action()


def canonical_weight(vector: tuple[int, ...]) -> tuple[int, ...]:
    return min(tuple(vector[source] for source in inverse) for inverse in INVERSE_ACTIONS)


def weighted_deck(vector: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], int], ...]:
    cards: Counter[tuple[int, ...]] = Counter()
    for coordinate, multiplicity in enumerate(vector):
        if multiplicity <= 0:
            continue
        card = list(vector)
        card[coordinate] -= 1
        cards[canonical_weight(tuple(card))] += multiplicity
    return tuple(sorted(cards.items()))


def exhaustive_two_values(low: int) -> tuple[int, int]:
    seen: dict[tuple[tuple[tuple[int, ...], int], ...], tuple[int, ...]] = {}
    orbit_count = 0
    for bits in range(1 << len(COORDINATES)):
        vector = tuple(low + ((bits >> i) & 1) for i in range(len(COORDINATES)))
        canonical = canonical_weight(vector)
        if vector != canonical:
            continue
        orbit_count += 1
        deck = weighted_deck(vector)
        previous = seen.get(deck)
        if previous is not None and previous != vector:
            report_hit(previous, vector, deck)
            return orbit_count, 1
        seen[deck] = vector
    return orbit_count, 0


def random_search(trials: int, low: int, high: int, seed: int) -> int:
    rng = random.Random(seed)
    seen: dict[tuple[tuple[tuple[int, ...], int], ...], tuple[int, ...]] = {}
    for trial in range(1, trials + 1):
        vector = tuple(rng.randint(low, high) for _ in COORDINATES)
        vector = canonical_weight(vector)
        deck = weighted_deck(vector)
        previous = seen.get(deck)
        if previous is not None and previous != vector:
            report_hit(previous, vector, deck)
            return trial
        seen[deck] = vector
    return 0


def report_hit(
    left: tuple[int, ...],
    right: tuple[int, ...],
    deck: tuple[tuple[tuple[int, ...], int], ...],
) -> None:
    payload = {
        "status": "WEIGHTED_ORBIT_COLLISION_NOT_YET_A_GRC_CE",
        "coordinates": [repr(coordinate) for coordinate in COORDINATES],
        "left": left,
        "right": right,
        "deck_types": len(deck),
    }
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive-binary", action="store_true")
    parser.add_argument("--trials", type=int, default=0)
    parser.add_argument("--low", type=int, default=2)
    parser.add_argument("--high", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260831)
    args = parser.parse_args()
    if args.low < 1 or args.high < args.low:
        raise SystemExit("require 1 <= low <= high")
    if not args.exhaustive_binary and not args.trials:
        raise SystemExit("choose --exhaustive-binary and/or a positive --trials")
    if args.exhaustive_binary:
        orbits, hits = exhaustive_two_values(args.low)
        print(f"EXACT_TWO_VALUE_DONE low={args.low} orbits={orbits} collisions={hits}")
    if args.trials:
        hit_at = random_search(args.trials, args.low, args.high, args.seed)
        print(
            f"RANDOM_DONE trials={args.trials} range={args.low}:{args.high} "
            f"seed={args.seed} collision_at={hit_at}"
        )


if __name__ == "__main__":
    main()

