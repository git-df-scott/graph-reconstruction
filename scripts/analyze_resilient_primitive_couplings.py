#!/usr/bin/env python3
"""Couple the strongest extension-resilient n=7 primitive exactly."""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from exhaustive_transposition_systems import is_exact_globalizer, relabel_system
from local_gluing_search import (
    edge_partition_families,
    parent_permutation_conditions,
    separating_binary_assignment,
    universal_edge_class_isomorphism,
)

N = 7
IDENTITY = tuple(range(N))
BASE = (
    (0, 2, 3, 1, 4, 5),
    (3, 1, 0, 2, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (2, 0, 1, 3, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (1, 3, 2, 0, 4, 5),
)
BASE_ALT = (
    (0, 2, 3, 1, 4, 5),
    (3, 1, 0, 2, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (2, 0, 1, 3, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (2, 0, 1, 3, 4, 5),
)
RESCUERS = (
    (0, 2, 3, 1, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (2, 0, 1, 3, 4, 5),
    (3, 1, 0, 2, 4, 5),
)
RIGID_TWO_RESCUER = (
    (0, 2, 3, 1, 4, 5, 6),
    (4, 1, 2, 5, 0, 3, 6),
    (4, 1, 2, 5, 0, 3, 6),
    (5, 2, 1, 3, 4, 0, 6),
    (0, 5, 1, 3, 4, 2, 6),
    (0, 2, 1, 4, 3, 5, 6),
    (0, 2, 1, 3, 4, 5, 6),
)
SEVEN_CLASS_THREE_RESCUER = (
    (0, 1, 3, 2, 5, 4, 6),
    (0, 1, 3, 2, 5, 4, 6),
    (3, 4, 2, 0, 1, 5, 6),
    (2, 5, 0, 3, 4, 1, 6),
    (2, 5, 0, 3, 4, 1, 6),
    (3, 4, 2, 0, 1, 5, 6),
    (0, 1, 3, 2, 5, 4, 6),
)
PERMUTATIONS = tuple(itertools.permutations(range(N)))


def compose(left, right):
    return tuple(left[right[vertex]] for vertex in range(N))


def inverse(permutation):
    result = [0] * N
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


def conjugate(by, permutation):
    return compose(compose(by, permutation), inverse(by))


def lift(outside_globalizer, base=BASE):
    return tuple(tuple(permutation) + (6,) for permutation in base) + (
        tuple(outside_globalizer) + (6,),
    )


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


def search_pair_domain(first_families, second_families, reverse_second):
    class_histogram = Counter()
    witness_histogram = Counter()
    informative_globalizer_histogram = Counter()
    tested = separators = 0
    for first in first_families:
        for raw_second in second_families:
            orientations = (
                (("same", raw_second), ("side_reversed", tuple(inverse(p) for p in raw_second)))
                if reverse_second else (("same", raw_second),)
            )
            for _orientation, second_base in orientations:
                for twist in PERMUTATIONS:
                    tested += 1
                    second = relabel_system(second_base, twist)
                    edges, roots, classes = edge_partition_families(
                        N, (first, second)
                    )
                    if is_exact_globalizer(IDENTITY, N, edges, roots, classes):
                        witness = IDENTITY
                    else:
                        witness = universal_edge_class_isomorphism(
                            N, edges, roots, classes
                        )
                    if witness is None:
                        conditions = parent_permutation_conditions(
                            N, edges, roots, classes
                        )
                        assignment = separating_binary_assignment(
                            len(classes), conditions
                        )
                        print(json.dumps({
                            "status": "ZERO_EXACT_LABEL_GLOBALIZER",
                            "twist": twist,
                            "first_family": first,
                            "second_family": second,
                            "class_count": len(classes),
                            "separating_assignment": assignment,
                        }, sort_keys=True))
                        raise SystemExit(2)
                    class_histogram[len(classes)] += 1
                    witness_histogram[witness] += 1
                    if len(classes) >= 7:
                        conditions = parent_permutation_conditions(
                            N, edges, roots, classes
                        )
                        exact_globalizers = sum(
                            not pairs for _permutation, pairs in conditions
                        )
                        informative_globalizer_histogram[
                            (len(classes), exact_globalizers)
                        ] += 1
                    # An exact-label witness makes assignment separation
                    # impossible without enumerating binary colorings.
    return {
        "tested": tested,
        "class_histogram": dict(sorted(class_histogram.items())),
        "witness_histogram": {str(key): value for key, value in witness_histogram.items()},
        "informative_class_globalizer_histogram": {
            str(key): value for key, value in sorted(informative_globalizer_histogram.items())
        },
        "assignment_specific_separators": separators,
    }


def main():
    lifted = tuple(lift(rescuer) for rescuer in RESCUERS)
    lifted_alt = tuple(lift(rescuer, BASE_ALT) for rescuer in RESCUERS)
    lifted_rescuers = tuple(tuple(rescuer) + (6,) for rescuer in RESCUERS)
    subgroup = generated_subgroup(lifted_rescuers)
    centralizer = tuple(
        permutation for permutation in PERMUTATIONS
        if all(compose(permutation, g) == compose(g, permutation) for g in subgroup)
    )
    rescue_normalizer = tuple(
        permutation for permutation in PERMUTATIONS
        if {conjugate(permutation, g) for g in lifted_rescuers} == set(lifted_rescuers)
    )
    self_domain = search_pair_domain(lifted, lifted, reverse_second=True)
    cross_orbit_domain = search_pair_domain(
        lifted, lifted_alt, reverse_second=True
    )
    heterogeneous_seven = search_pair_domain(
        (lifted[0],), (SEVEN_CLASS_THREE_RESCUER,), reverse_second=True
    )
    heterogeneous_two = search_pair_domain(
        (lifted[0],), (RIGID_TWO_RESCUER,), reverse_second=True
    )
    print(json.dumps({
        "status": "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "rescue_generated_subgroup_order": len(subgroup),
        "rescue_generated_subgroup": subgroup,
        "rescue_centralizer_order": len(centralizer),
        "rescue_set_normalizer_order": len(rescue_normalizer),
        "rescue_set_conjugates": len(PERMUTATIONS) // len(rescue_normalizer),
        "self_all_lift_choices": self_domain,
        "cross_primitive_orbits_all_lift_choices": cross_orbit_domain,
        "heterogeneous_seven_class_three_rescuer": heterogeneous_seven,
        "heterogeneous_four_class_two_rescuer": heterogeneous_two,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
