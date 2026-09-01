#!/usr/bin/env python3
"""Crossed row/column holonomy strike on the 7x7 incidence carrier."""

from __future__ import annotations

import itertools
import json
from collections import Counter

from incidence_join_strike import BASE_LIFT
from matrix_bideck_local_search import (
    N,
    exact_label_globalizer,
    instantiate,
    matrices_isomorphic,
    partition,
    split_graph,
)
from grc import is_isomorphic, same_deck


def inverse(p):
    answer = [0] * N
    for i, j in enumerate(p):
        answer[j] = i
    return tuple(answer)


def compose(a, b):
    return tuple(a[b[i]] for i in range(N))


def conjugate_family(family, q):
    qi = inverse(q)
    return tuple(compose(compose(q, family[qi[i]]), qi) for i in range(N))


def run():
    histogram = Counter()
    globalizer_histogram = Counter()
    zero = []
    for q in itertools.permutations(range(N)):
        second = conjugate_family(BASE_LIFT, q)
        row_maps = tuple((BASE_LIFT[i], second[i]) for i in range(N))
        column_maps = tuple((second[i], BASE_LIFT[i]) for i in range(N))
        classes, count = partition(row_maps, column_maps)
        histogram[count] += 1
        witness = exact_label_globalizer(classes)
        if witness is None:
            zero.append((q, classes, count, row_maps, column_maps))
        else:
            globalizer_histogram[witness] += 1

    candidates = []
    for q, classes, count, row_maps, column_maps in zero:
        if count > 22:
            candidates.append({"q": q, "classes": count, "status": "binary_search_skipped_over_22"})
            continue
        for values in itertools.product((0, 1), repeat=count):
            left, right = instantiate(classes, values)
            if matrices_isomorphic(left, right):
                continue
            g, h = split_graph(left), split_graph(right)
            if is_isomorphic(g, h):
                continue
            if not same_deck(g, h):
                raise AssertionError("crossed local maps failed exact deck replay")
            candidates.append({
                "q": q,
                "classes": count,
                "G_graph6": g.to_graph6(),
                "H_graph6": h.to_graph6(),
                "values": values,
                "status": "EXACT_GRC_CE",
            })
            return {
                "grc_ce": "YES",
                "conjugates": 5040,
                "class_histogram": dict(sorted(histogram.items())),
                "zero_globalizer_systems": len(zero),
                "candidate": candidates[-1],
            }
    return {
        "grc_ce": "NO",
        "conjugates": 5040,
        "class_histogram": dict(sorted(histogram.items())),
        "zero_globalizer_systems": len(zero),
        "distinct_globalizers": len(globalizer_histogram),
        "candidate_records": candidates,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
