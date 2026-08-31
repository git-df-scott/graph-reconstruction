#!/usr/bin/env python3
"""Exhaust all relabeled two-copy couplings of the frozen n=6 primitive."""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from exhaustive_transposition_systems import relabel_system
from local_gluing_search import (
    edge_class_arrays,
    edge_partition,
    edge_partition_families,
    parent_permutation_conditions,
    separating_binary_assignment,
)

N = 6
IDENTITY = tuple(range(N))
PRIMITIVE = (
    (0, 2, 3, 1, 4, 5),
    (4, 1, 2, 5, 0, 3),
    (4, 1, 2, 5, 0, 3),
    (5, 2, 1, 3, 4, 0),
    (0, 5, 1, 3, 4, 2),
    (0, 2, 1, 4, 3, 5),
)
RESCUERS = (
    (0, 2, 1, 3, 4, 5),
    (4, 1, 2, 5, 0, 3),
)
PERMUTATIONS = tuple(itertools.permutations(range(N)))


def compose(left, right):
    return tuple(left[right[v]] for v in range(N))


def inverse(permutation):
    result = [0] * N
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


def conjugate(by, permutation):
    return compose(compose(by, permutation), inverse(by))


def inverse_family(family):
    return tuple(inverse(permutation) for permutation in family)


def generated_subgroup(generators):
    result = {IDENTITY}
    frontier = list(generators)
    while frontier:
        item = frontier.pop()
        if item in result:
            continue
        old = tuple(result)
        result.add(item)
        frontier.extend(compose(item, other) for other in old)
        frontier.extend(compose(other, item) for other in old)
    return tuple(sorted(result))


def canonical_class_key(edges, side_classes):
    """Canonicalize a two-sided edge partition under vertices and side swap."""

    position = {edge: i for i, edge in enumerate(edges)}
    best = None
    for permutation in PERMUTATIONS:
        order = [
            position[tuple(sorted((permutation[u], permutation[v])))]
            for u, v in edges
        ]
        for swap in (False, True):
            raw = (
                tuple(side_classes[swap][i] for i in order)
                + tuple(side_classes[not swap][i] for i in order)
            )
            names = {}
            normalized = tuple(names.setdefault(value, len(names)) for value in raw)
            if best is None or normalized < best:
                best = normalized
    return best


def main():
    edges, roots, classes = edge_partition(N, PRIMITIVE)
    primitive_conditions = parent_permutation_conditions(N, edges, roots, classes)
    primitive_rescuers = tuple(p for p, pairs in primitive_conditions if not pairs)
    if primitive_rescuers != RESCUERS:
        raise AssertionError("frozen primitive rescue certificate changed")
    subgroup = generated_subgroup(RESCUERS)
    centralizer = tuple(
        p for p in PERMUTATIONS
        if all(compose(p, g) == compose(g, p) for g in subgroup)
    )
    subgroup_normalizer = tuple(
        p for p in PERMUTATIONS
        if {conjugate(p, g) for g in subgroup} == set(subgroup)
    )
    rescue_normalizer = tuple(
        p for p in PERMUTATIONS
        if {conjugate(p, g) for g in RESCUERS} == set(RESCUERS)
    )
    unseen = set(PERMUTATIONS)
    double_cosets = []
    while unseen:
        representative = min(unseen)
        members = {
            compose(compose(left, representative), right)
            for left in rescue_normalizer for right in rescue_normalizer
        }
        unseen.difference_update(members)
        intersection = set(RESCUERS) & {
            conjugate(representative, g) for g in RESCUERS
        }
        double_cosets.append({
            "representative": representative,
            "size": len(members),
            "old_rescue_intersection": len(intersection),
        })

    globalizer_histogram = Counter()
    class_histogram = Counter()
    intersection_outcomes = Counter()
    canonical_outcomes = Counter()
    separating_assignments = 0
    minimum = None
    orientation_histograms = {}
    for orientation, second_base in (
        ("same", PRIMITIVE),
        ("side_reversed", inverse_family(PRIMITIVE)),
    ):
        orientation_globalizers = Counter()
        orientation_classes = Counter()
        for twist in PERMUTATIONS:
            second = relabel_system(second_base, twist)
            coupled_edges, coupled_roots, coupled_classes = edge_partition_families(
                N, (PRIMITIVE, second)
            )
            conditions = parent_permutation_conditions(
                N, coupled_edges, coupled_roots, coupled_classes
            )
            globalizers = tuple(p for p, pairs in conditions if not pairs)
            if not globalizers:
                print(json.dumps({
                    "status": "ZERO_EXACT_LABEL_GLOBALIZER",
                    "orientation": orientation,
                    "twist": twist,
                    "first_family": PRIMITIVE,
                    "second_family": second,
                    "class_count": len(coupled_classes),
                }, sort_keys=True))
                raise SystemExit(2)
            assignment = separating_binary_assignment(len(coupled_classes), conditions)
            separating_assignments += assignment is not None
            old_intersection = set(RESCUERS) & {
                conjugate(twist, g) for g in RESCUERS
            }
            globalizer_histogram[len(globalizers)] += 1
            class_histogram[len(coupled_classes)] += 1
            orientation_globalizers[len(globalizers)] += 1
            orientation_classes[len(coupled_classes)] += 1
            intersection_outcomes[
                (len(old_intersection), len(coupled_classes), len(globalizers))
            ] += 1
            side_classes = edge_class_arrays(
                coupled_edges, coupled_roots, coupled_classes
            )
            canonical_outcomes[
                (
                    len(coupled_classes),
                    len(globalizers),
                    canonical_class_key(coupled_edges, side_classes),
                )
            ] += 1
            record = (len(globalizers), twist, len(coupled_classes), globalizers)
            if minimum is None or record < minimum:
                minimum = record
        orientation_histograms[orientation] = {
            "globalizers": dict(sorted(orientation_globalizers.items())),
            "classes": dict(sorted(orientation_classes.items())),
        }

    primitive_side_classes = edge_class_arrays(edges, roots, classes)
    payload = {
        "status": "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "n": N,
        "twists_per_orientation": len(PERMUTATIONS),
        "couplings": 2 * len(PERMUTATIONS),
        "orientation_histograms": orientation_histograms,
        "primitive_maps": PRIMITIVE,
        "primitive_edge_classes": primitive_side_classes,
        "primitive_rescuers": RESCUERS,
        "generated_subgroup": subgroup,
        "generated_subgroup_order": len(subgroup),
        "centralizer_order": len(centralizer),
        "subgroup_normalizer_order": len(subgroup_normalizer),
        "rescue_set_normalizer_order": len(rescue_normalizer),
        "rescue_conjugates": len({
            tuple(sorted(conjugate(p, g) for g in RESCUERS)) for p in PERMUTATIONS
        }),
        "double_cosets": double_cosets,
        "class_histogram": dict(sorted(class_histogram.items())),
        "globalizer_histogram": dict(sorted(globalizer_histogram.items())),
        "intersection_class_globalizer_outcomes": {
            str(key): value for key, value in sorted(intersection_outcomes.items())
        },
        "canonical_coupled_partition_types": len(canonical_outcomes),
        "canonical_outcome_multiplicities": sorted(canonical_outcomes.values()),
        "assignment_specific_separators": separating_assignments,
        "minimum_globalizer_record": minimum,
        "theorem": (
            "every simultaneous-relabeling two-copy coupling of the frozen "
            "primitive has an exact-label globalizer"
        ),
    }
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
