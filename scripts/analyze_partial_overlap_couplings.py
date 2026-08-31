#!/usr/bin/env python3
"""Exhaust minimal n=7 five-vertex-overlap couplings of the primitive."""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from analyze_primitive_couplings import PRIMITIVE, RESCUERS, inverse_family
from local_gluing_search import (
    edge_partition,
    edge_partition_families,
    parent_permutation_conditions,
    separating_binary_assignment,
)

N = 7
FIRST_BLOCK = (0, 1, 2, 3, 4, 5)
SECOND_BLOCK_VERTICES = (0, 1, 2, 3, 4, 6)


def lift_family(base, block, outside_rescuer):
    """Promote a six-card family to seven complete deletion maps."""

    actual_to_label = {actual: label for label, actual in enumerate(block)}
    outside = next(vertex for vertex in range(N) if vertex not in block)
    family = []
    for deleted in range(N):
        local = (
            outside_rescuer
            if deleted == outside
            else base[actual_to_label[deleted]]
        )
        permutation = list(range(N))
        for label, actual in enumerate(block):
            permutation[actual] = block[local[label]]
        family.append(tuple(permutation))
    return tuple(family)


def main():
    single_lift_classes = {}
    for choice, rescuer in enumerate(RESCUERS):
        family = lift_family(PRIMITIVE, FIRST_BLOCK, rescuer)
        _edges, _roots, classes = edge_partition(N, family)
        single_lift_classes[choice] = len(classes)

    class_histogram = Counter()
    globalizer_histogram = Counter()
    separating_assignments = 0
    tested = 0
    for orientation, base in (
        ("same", PRIMITIVE),
        ("side_reversed", inverse_family(PRIMITIVE)),
    ):
        for second_block in itertools.permutations(SECOND_BLOCK_VERTICES):
            for first_rescuer in RESCUERS:
                first = lift_family(PRIMITIVE, FIRST_BLOCK, first_rescuer)
                for second_rescuer in RESCUERS:
                    second = lift_family(base, second_block, second_rescuer)
                    tested += 1
                    edges, roots, classes = edge_partition_families(
                        N, (first, second)
                    )
                    class_histogram[len(classes)] += 1
                    if len(classes) == 1:
                        globalizer_histogram[5040] += 1
                        continue
                    conditions = parent_permutation_conditions(N, edges, roots, classes)
                    globalizers = tuple(p for p, pairs in conditions if not pairs)
                    if not globalizers:
                        print(json.dumps({
                            "status": "ZERO_EXACT_LABEL_GLOBALIZER",
                            "orientation": orientation,
                            "second_block": second_block,
                            "first_rescuer": first_rescuer,
                            "second_rescuer": second_rescuer,
                            "first_family": first,
                            "second_family": second,
                            "class_count": len(classes),
                        }, sort_keys=True))
                        raise SystemExit(2)
                    globalizer_histogram[len(globalizers)] += 1
                    separating_assignments += (
                        separating_binary_assignment(len(classes), conditions) is not None
                    )
    print(json.dumps({
        "status": "EXHAUSTIVE_ALL_COUPLINGS_INDISCRETE",
        "n": N,
        "overlap_vertices": 5,
        "orientations": 2,
        "second_block_embeddings": 720,
        "outside_rescuer_choices": 4,
        "couplings": tested,
        "single_lift_class_counts": single_lift_classes,
        "class_histogram": dict(sorted(class_histogram.items())),
        "globalizer_histogram": dict(sorted(globalizer_histogram.items())),
        "assignment_specific_separators": separating_assignments,
        "theorem": (
            "every minimal five-vertex-overlap coupling collapses all parent "
            "edge slots to one equality class"
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
