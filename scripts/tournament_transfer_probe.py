#!/usr/bin/env python3
"""Probe deletion-faithful transfers of small tournament counterexamples."""

from __future__ import annotations

import itertools
import json
from collections import defaultdict


def tournament_rows(n: int, bits: int) -> tuple[int, ...]:
    rows = [0] * n
    bit = 0
    for i in range(n):
        for j in range(i + 1, n):
            if bits & (1 << bit):
                rows[i] |= 1 << j
            else:
                rows[j] |= 1 << i
            bit += 1
    return tuple(rows)


def permute_square(rows, permutation):
    n = len(rows)
    answer = [0] * n
    for old_i in range(n):
        new_i = permutation[old_i]
        for old_j in range(n):
            if rows[old_i] & (1 << old_j):
                answer[new_i] |= 1 << permutation[old_j]
    return tuple(answer)


def tournament_canon(rows):
    return min(permute_square(rows, p) for p in itertools.permutations(range(len(rows))))


def delete_square(rows, deleted):
    low = (1 << deleted) - 1
    result = []
    for i, row in enumerate(rows):
        if i == deleted:
            continue
        result.append((row & low) | ((row >> 1) & ~low))
    return tuple(result)


def tournament_deck(rows):
    return tuple(sorted(tournament_canon(delete_square(rows, i)) for i in range(len(rows))))


def permute_columns(rows, permutation):
    answer = []
    for row in rows:
        image = 0
        for old, new in enumerate(permutation):
            if row & (1 << old):
                image |= 1 << new
        answer.append(image)
    return tuple(sorted(answer))


def matrix_canon(rows, columns):
    return min(permute_columns(rows, p) for p in itertools.permutations(range(columns)))


def delete_matrix_column(rows, deleted):
    low = (1 << deleted) - 1
    return tuple((row & low) | ((row >> 1) & ~low) for row in rows)


def matrix_bideck(rows, columns):
    row_cards = [matrix_canon(rows[:i] + rows[i + 1:], columns) for i in range(len(rows))]
    column_cards = [matrix_canon(delete_matrix_column(rows, j), columns - 1) for j in range(columns)]
    return tuple(sorted(row_cards, key=repr)), tuple(sorted(column_cards, key=repr))


def run(n=5):
    representatives = {}
    for bits in range(1 << (n * (n - 1) // 2)):
        rows = tournament_rows(n, bits)
        representatives.setdefault(tournament_canon(rows), rows)
    by_deck = defaultdict(list)
    for canon, rows in representatives.items():
        by_deck[tournament_deck(rows)].append((canon, rows))
    tournament_pairs = []
    for group in by_deck.values():
        if len(group) > 1:
            for left, right in itertools.combinations(group, 2):
                left_bideck = matrix_bideck(left[1], n)
                right_bideck = matrix_bideck(right[1], n)
                tournament_pairs.append({
                    "left": left[1],
                    "right": right[1],
                    "matrix_bideck_equal": left_bideck == right_bideck,
                    "matrix_parents_isomorphic": matrix_canon(left[1], n) == matrix_canon(right[1], n),
                })
    return {
        "n": n,
        "tournament_classes": len(representatives),
        "nonreconstructible_pairs": tournament_pairs,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
