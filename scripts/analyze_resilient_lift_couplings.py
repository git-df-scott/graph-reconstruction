#!/usr/bin/env python3
"""Targeted exact couplings of the strongest resilient all-double n=7 lift."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from exhaustive_transposition_systems import inverse, relabel_system
from local_gluing_search import (
    edge_partition,
    edge_partition_families,
    edge_class_arrays,
    instantiate,
    parent_permutation_conditions,
    separating_binary_assignment,
    universal_edge_class_isomorphism,
    verify_local_maps,
)
from grc import is_isomorphic, same_deck


N = 7
IDENTITY = tuple(range(N))
PERMUTATIONS = tuple(itertools.permutations(range(N)))

# Exact best record recovered by extension_resilience_census.py --three-count 0.
LIFT = (
    (0, 1, 3, 2, 5, 4, 6),
    (0, 1, 3, 2, 5, 4, 6),
    (3, 4, 2, 0, 1, 5, 6),
    (2, 5, 0, 3, 4, 1, 6),
    (2, 5, 0, 3, 4, 1, 6),
    (3, 4, 2, 0, 1, 5, 6),
    (0, 1, 3, 2, 5, 4, 6),
)
RESCUERS = (
    (0, 1, 3, 2, 5, 4, 6),
    (2, 5, 0, 3, 4, 1, 6),
    (3, 4, 2, 0, 1, 5, 6),
)
LIFT_R8 = (
    (0, 1, 3, 2, 5, 4, 6),
    (0, 1, 3, 2, 5, 4, 6),
    (1, 0, 2, 3, 5, 4, 6),
    (1, 0, 2, 3, 5, 4, 6),
    (2, 3, 0, 1, 4, 5, 6),
    (2, 3, 0, 1, 4, 5, 6),
    (0, 1, 2, 3, 5, 4, 6),
)
RESCUERS_R8 = (
    (0, 1, 2, 3, 5, 4, 6),
    (0, 1, 3, 2, 5, 4, 6),
    (1, 0, 2, 3, 5, 4, 6),
    (1, 0, 3, 2, 5, 4, 6),
    (2, 3, 0, 1, 4, 5, 6),
    (2, 3, 1, 0, 4, 5, 6),
    (3, 2, 0, 1, 4, 5, 6),
    (3, 2, 1, 0, 4, 5, 6),
)
LIFT_R2 = (
    (0, 2, 3, 1, 4, 5, 6),
    (2, 1, 3, 0, 4, 5, 6),
    (4, 5, 2, 3, 0, 1, 6),
    (4, 5, 2, 3, 0, 1, 6),
    (0, 1, 5, 2, 4, 3, 6),
    (0, 1, 4, 2, 3, 5, 6),
    (0, 1, 3, 2, 4, 5, 6),
)
RESCUERS_R2 = (
    (0, 1, 3, 2, 4, 5, 6),
    (4, 5, 2, 3, 0, 1, 6),
)
LIFT_R4 = (
    (0, 2, 3, 1, 4, 5, 6),
    (3, 1, 0, 2, 4, 5, 6),
    (1, 3, 2, 0, 4, 5, 6),
    (2, 0, 1, 3, 4, 5, 6),
    (1, 3, 2, 0, 4, 5, 6),
    (1, 3, 2, 0, 4, 5, 6),
    (0, 2, 3, 1, 4, 5, 6),
)
RESCUERS_R4 = (
    (0, 2, 3, 1, 4, 5, 6),
    (1, 3, 2, 0, 4, 5, 6),
    (2, 0, 1, 3, 4, 5, 6),
    (3, 1, 0, 2, 4, 5, 6),
)

LIFTS = {"r2": LIFT_R2, "r3": LIFT, "r4": LIFT_R4, "r8": LIFT_R8}
RESCUE_SETS = {
    "r2": RESCUERS_R2,
    "r3": RESCUERS,
    "r4": RESCUERS_R4,
    "r8": RESCUERS_R8,
}


def compose(left, right):
    return tuple(left[right[v]] for v in range(N))


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


def verify_candidate(edges, roots, classes, assignment, families):
    g, h = instantiate(N, edges, roots, classes, assignment)
    return {
        "assignment": assignment,
        "G_graph6": g.to_graph6(),
        "H_graph6": h.to_graph6(),
        "local_maps_verify": all(verify_local_maps(g, h, family) for family in families),
        "same_deck": same_deck(g, h),
        "parents_isomorphic": is_isomorphic(g, h),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", choices=tuple(LIFTS), default="r3")
    parser.add_argument("--second", choices=tuple(LIFTS), default="r3")
    parser.add_argument("--globalizer-min-classes", type=int, default=4)
    args = parser.parse_args()
    first_lift = LIFTS[args.first]
    first_rescuers = RESCUE_SETS[args.first]
    second_lift = LIFTS[args.second]
    second_rescuers = RESCUE_SETS[args.second]
    start = time.monotonic()
    edges, roots, classes = edge_partition(N, first_lift)
    conditions = parent_permutation_conditions(N, edges, roots, classes)
    exact_rescuers = tuple(p for p, pairs in conditions if not pairs)
    if exact_rescuers != first_rescuers:
        raise AssertionError("recovered resilient-lift certificate changed")

    rescue_group = generated_subgroup(first_rescuers)
    centralizer = tuple(
        p for p in PERMUTATIONS
        if all(compose(p, g) == compose(g, p) for g in rescue_group)
    )
    subgroup_normalizer = tuple(
        p for p in PERMUTATIONS
        if {conjugate(p, g) for g in rescue_group} == set(rescue_group)
    )
    rescue_normalizer = tuple(
        p for p in PERMUTATIONS
        if {conjugate(p, g) for g in first_rescuers} == set(first_rescuers)
    )
    second_rescue_normalizer = tuple(
        p for p in PERMUTATIONS
        if {conjugate(p, g) for g in second_rescuers} == set(second_rescuers)
    )
    unseen = set(PERMUTATIONS)
    double_cosets = []
    while unseen:
        representative = min(unseen)
        members = {
            compose(compose(left, representative), right)
            for left in rescue_normalizer for right in second_rescue_normalizer
        }
        unseen.difference_update(members)
        intersection = set(first_rescuers) & {
            conjugate(representative, g) for g in second_rescuers
        }
        double_cosets.append((representative, len(members), len(intersection)))

    total = zero = separators = 0
    class_histogram = Counter()
    witness_histogram = Counter()
    identity_histogram = Counter()
    promising_globalizer_histogram = Counter()
    intersection_outcomes = Counter()
    best = None
    for orientation, second_base, oriented_second_rescuers in (
        ("same", second_lift, second_rescuers),
        (
            "side_reversed",
            inverse_family(second_lift),
            tuple(inverse(p) for p in second_rescuers),
        ),
    ):
        for twist in PERMUTATIONS:
            second = relabel_system(second_base, twist)
            coupled = (first_lift, second)
            coupled_edges, coupled_roots, coupled_classes = edge_partition_families(N, coupled)
            total += 1
            class_count = len(coupled_classes)
            class_histogram[class_count] += 1
            old_intersection = len(
                set(first_rescuers)
                & {conjugate(twist, g) for g in oriented_second_rescuers}
            )
            witness = universal_edge_class_isomorphism(
                N, coupled_edges, coupled_roots, coupled_classes
            )
            side_classes = edge_class_arrays(
                coupled_edges, coupled_roots, coupled_classes
            )
            identity_histogram[
                (old_intersection, class_count, side_classes[0] == side_classes[1])
            ] += 1
            witness_histogram["none" if witness is None else "present"] += 1
            intersection_outcomes[(old_intersection, class_count, witness is not None)] += 1
            if witness is None:
                zero += 1
                coupled_conditions = parent_permutation_conditions(
                    N, coupled_edges, coupled_roots, coupled_classes
                )
                assignment = separating_binary_assignment(class_count, coupled_conditions)
                separators += assignment is not None
                record = {
                    "status": "ZERO_EXACT_LABEL_GLOBALIZER",
                    "orientation": orientation,
                    "twist": twist,
                    "first_family": first_lift,
                    "second_family": second,
                    "class_count": class_count,
                    "assignment": assignment,
                }
                if assignment is not None:
                    record.update(verify_candidate(
                        coupled_edges, coupled_roots, coupled_classes, assignment, coupled
                    ))
                    print(json.dumps(record, sort_keys=True), flush=True)
                    raise SystemExit(3)
                print(json.dumps(record, sort_keys=True), flush=True)
                raise SystemExit(2)
            if class_count >= args.globalizer_min_classes:
                coupled_conditions = parent_permutation_conditions(
                    N, coupled_edges, coupled_roots, coupled_classes
                )
                promising_globalizers = tuple(
                    p for p, pairs in coupled_conditions if not pairs
                )
                promising_globalizer_histogram[
                    (class_count, old_intersection, len(promising_globalizers))
                ] += 1
            score = (class_count, -old_intersection)
            if best is None or score > best[0]:
                best = (score, {
                    "orientation": orientation,
                    "twist": twist,
                    "class_count": class_count,
                    "old_rescue_intersection": old_intersection,
                    "globalizer_witness": witness,
                })

    print(json.dumps({
        "status": "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "n": N,
        "orientations": 2,
        "twists_per_orientation": len(PERMUTATIONS),
        "couplings": total,
        "first_lift_kind": args.first,
        "lift": first_lift,
        "lift_class_count": len(classes),
        "lift_rescuers": first_rescuers,
        "second_lift_kind": args.second,
        "second_lift": second_lift,
        "second_lift_rescuers": second_rescuers,
        "rescue_generated_group_order": len(rescue_group),
        "centralizer_order": len(centralizer),
        "subgroup_normalizer_order": len(subgroup_normalizer),
        "rescue_set_normalizer_order": len(rescue_normalizer),
        "second_rescue_set_normalizer_order": len(second_rescue_normalizer),
        "rescue_set_conjugates": len({
            tuple(sorted(conjugate(p, g) for g in first_rescuers)) for p in PERMUTATIONS
        }),
        "double_cosets": double_cosets,
        "class_histogram": dict(sorted(class_histogram.items())),
        "universal_witness_histogram": dict(sorted(witness_histogram.items())),
        "intersection_class_identity_outcomes": {
            str(key): value for key, value in sorted(identity_histogram.items())
        },
        "promising_globalizer_histogram": {
            str(key): value for key, value in sorted(promising_globalizer_histogram.items())
        },
        "intersection_class_witness_outcomes": {
            str(key): value for key, value in sorted(intersection_outcomes.items())
        },
        "zero_globalizer_systems": zero,
        "assignment_specific_separators": separators,
        "best": best[1],
        "elapsed_seconds": time.monotonic() - start,
        "completeness": "all 7! twists in both side orientations; exact backtracking",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
