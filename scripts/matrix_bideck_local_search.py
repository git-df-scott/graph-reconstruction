#!/usr/bin/env python3
"""Deletion-compatible 7x7 incidence search for order-14 split-graph CEs.

Columns induce a clique and rows an independent set.  For every row deletion
we prescribe independent permutations of the surviving rows and all columns;
for every column deletion we prescribe permutations of all rows and the
surviving columns.  Union-find gives binary incidence classes whose every
realization has equal row- and column-deletion decks.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck
from local_gluing_search import UnionFind


N = 7


def near_identity(rng: random.Random, fixed: int | None, moves: int):
    p = list(range(N))
    available = [x for x in range(N) if x != fixed]
    for _ in range(moves):
        a, b = rng.sample(available, 2)
        p[a], p[b] = p[b], p[a]
    return tuple(p)


def partition(row_maps, column_maps):
    uf = UnionFind(2 * N * N)
    slot = lambda side, r, c: side * N * N + r * N + c
    for deleted, (rp, cp) in enumerate(row_maps):
        for r in range(N):
            if r == deleted:
                continue
            for c in range(N):
                uf.union(slot(0, r, c), slot(1, rp[r], cp[c]))
    for deleted, (rp, cp) in enumerate(column_maps):
        for r in range(N):
            for c in range(N):
                if c == deleted:
                    continue
                uf.union(slot(0, r, c), slot(1, rp[r], cp[c]))
    roots = tuple(uf.find(i) for i in range(2 * N * N))
    names = {root: i for i, root in enumerate(sorted(set(roots)))}
    return tuple(names[x] for x in roots), len(names)


def instantiate(classes, values):
    matrices = []
    for side in range(2):
        rows = []
        for r in range(N):
            bits = 0
            for c in range(N):
                if values[classes[side * N * N + r * N + c]]:
                    bits |= 1 << c
            rows.append(bits)
        matrices.append(tuple(rows))
    return tuple(matrices)


def exact_label_globalizer(classes):
    left = tuple(tuple(classes[r * N + c] for c in range(N)) for r in range(N))
    right = tuple(tuple(classes[N * N + r * N + c] for c in range(N)) for r in range(N))
    target = tuple(sorted(right))
    for permutation in PERMS:
        if tuple(sorted(tuple(row[c] for c in permutation) for row in left)) == target:
            return permutation
    return None


PERMS = tuple(itertools.permutations(range(N)))


def permute_columns(rows, permutation):
    answer = []
    for row in rows:
        image = 0
        for old, new in enumerate(permutation):
            if row & (1 << old):
                image |= 1 << new
        answer.append(image)
    return tuple(sorted(answer))


def matrix_canon(rows):
    return min(permute_columns(rows, p) for p in PERMS)


def transpose(rows):
    return tuple(sum(((rows[r] >> c) & 1) << r for r in range(N)) for c in range(N))


def matrices_isomorphic(left, right):
    def invariant(rows):
        return (
            tuple(sorted(row.bit_count() for row in rows)),
            tuple(sorted(sum((row >> c) & 1 for row in rows) for c in range(N))),
        )
    right_invariant = invariant(right)
    direct = invariant(left) == right_invariant
    transposed = transpose(left)
    dual = invariant(transposed) == right_invariant
    if not direct and not dual:
        return False
    target = matrix_canon(right)
    return (direct and matrix_canon(left) == target) or (dual and matrix_canon(transposed) == target)


def split_graph(rows):
    adjacency = [0] * (2 * N)
    for c in range(N):
        for d in range(c + 1, N):
            adjacency[N + c] |= 1 << (N + d)
            adjacency[N + d] |= 1 << (N + c)
    for r, pattern in enumerate(rows):
        for c in range(N):
            if pattern & (1 << c):
                adjacency[r] |= 1 << (N + c)
                adjacency[N + c] |= 1 << r
    return Graph(tuple(adjacency))


def run(systems: int, assignments: int, moves: int, seed: int):
    rng = random.Random(seed)
    histogram = {}
    realized = matrix_nonisomorphic = universal = nonuniversal = 0
    for system in range(systems):
        row_maps = tuple(
            (near_identity(rng, i, moves), near_identity(rng, None, moves))
            for i in range(N)
        )
        column_maps = tuple(
            (near_identity(rng, None, moves), near_identity(rng, i, moves))
            for i in range(N)
        )
        classes, count = partition(row_maps, column_maps)
        histogram[count] = histogram.get(count, 0) + 1
        if count < 2 or count > 20:
            continue
        if exact_label_globalizer(classes) is not None:
            universal += 1
            continue
        nonuniversal += 1
        for _ in range(assignments):
            values = tuple(rng.getrandbits(1) for _ in range(count))
            if not any(values) or all(values):
                continue
            realized += 1
            left, right = instantiate(classes, values)
            if matrices_isomorphic(left, right):
                continue
            matrix_nonisomorphic += 1
            g, h = split_graph(left), split_graph(right)
            if is_isomorphic(g, h):
                continue
            if not same_deck(g, h):
                raise AssertionError("prescribed matrix card maps failed ordinary exact deck replay")
            return {
                "grc_ce": "YES",
                "order": 14,
                "G_graph6": g.to_graph6(),
                "H_graph6": h.to_graph6(),
                "left_rows": left,
                "right_rows": right,
                "row_maps": row_maps,
                "column_maps": column_maps,
                "classes": count,
                "system": system,
                "seed": seed,
            }
    return {
        "grc_ce": "NO",
        "systems": systems,
        "assignments_per_eligible_system": assignments,
        "moves": moves,
        "class_histogram": histogram,
        "realizations_checked": realized,
        "matrix_nonisomorphic_realizations": matrix_nonisomorphic,
        "exact_label_globalizer_systems": universal,
        "nonuniversal_systems": nonuniversal,
        "seed": seed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems", type=int, default=10000)
    parser.add_argument("--assignments", type=int, default=32)
    parser.add_argument("--moves", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260901)
    args = parser.parse_args()
    print(json.dumps(run(args.systems, args.assignments, args.moves, args.seed), indent=2, sort_keys=True))
