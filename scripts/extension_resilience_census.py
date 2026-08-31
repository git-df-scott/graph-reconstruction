#!/usr/bin/env python3
"""Mine nonidentity-rescued n=6 leaves for legitimate n=7 resilience."""

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

from exhaustive_length2_frontier import (
    IDENTITY,
    N,
    canonical_partial,
    centralizer,
    cycle_type,
    double_transpositions,
    three_cycles,
)
from exhaustive_transposition_systems import canonical_system, is_exact_globalizer
from local_gluing_search import (
    edge_class_arrays,
    edge_partition,
    instantiate,
    parent_permutation_conditions,
    separating_binary_assignment,
    universal_edge_class_isomorphism,
    verify_local_maps,
)
from grc import is_isomorphic, same_deck


def compose(left, right):
    return tuple(left[right[v]] for v in range(len(left)))


def generated_subgroup(generators, degree):
    identity = tuple(range(degree))
    result = {identity}
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


def class_profile(roots):
    return tuple(sorted(Counter(roots).values(), reverse=True))


def lift_family(maps, outside_globalizer):
    """Add vertex 6, fix it on old deletions, and use a globalizer on G-6."""

    family = []
    for deleted in range(7):
        permutation = list(range(7))
        local = outside_globalizer if deleted == 6 else maps[deleted]
        for vertex in range(6):
            permutation[vertex] = local[vertex]
        family.append(tuple(permutation))
    return tuple(family)


def retained_old_classes(old_edges, old_side_classes, lifted_edges, lifted_roots):
    lifted_position = {edge: i for i, edge in enumerate(lifted_edges)}
    lifted_slots = len(lifted_edges)
    groups = {}
    for side in range(2):
        for position, edge in enumerate(old_edges):
            old_class = old_side_classes[side][position]
            lifted_root = lifted_roots[
                side * lifted_slots + lifted_position[edge]
            ]
            groups.setdefault(old_class, set()).add(lifted_root)
    # Every old class remains internally equal; distinct roots measure classes
    # retained after extension-induced merging.
    return len({next(iter(roots)) for roots in groups.values()})


def collect_exception_orbits(target_three, progress):
    three_options = tuple(three_cycles(deleted) for deleted in range(N))
    double_options = tuple(double_transpositions(deleted) for deleted in range(N))
    anchor = (three_options if target_three else double_options)[0][0]
    group = centralizer(anchor)
    maps = [IDENTITY] * N
    maps[0] = anchor
    leaves = exceptions = 0
    orbit_representatives = {}
    start = time.monotonic()

    def visit(depth, used_three):
        nonlocal leaves, exceptions
        if depth == N:
            leaves += 1
            frozen = tuple(maps)
            edges, roots, classes = edge_partition(N, frozen)
            if not is_exact_globalizer(IDENTITY, N, edges, roots, classes):
                globalizer = universal_edge_class_isomorphism(N, edges, roots, classes)
                if globalizer is None:
                    raise AssertionError("closed frontier unexpectedly contains zero globalizer")
                exceptions += 1
                key = canonical_system(frozen)
                orbit_representatives.setdefault(key, frozen)
            if progress and leaves % progress == 0:
                print(json.dumps({
                    "status": "SOURCE_PROGRESS",
                    "three_count": target_three,
                    "leaves": leaves,
                    "exceptions": exceptions,
                    "full_orbits": len(orbit_representatives),
                    "elapsed_seconds": round(time.monotonic() - start, 1),
                }), flush=True)
            return
        remaining_after = N - depth - 1
        choices = []
        if used_three < target_three and used_three + 1 + remaining_after >= target_three:
            choices.append((three_options[depth], used_three + 1))
        used_double = depth - used_three
        target_double = N - target_three
        if used_double < target_double and used_double + 1 + remaining_after >= target_double:
            choices.append((double_options[depth], used_three))
        for option_set, next_three in choices:
            for option in option_set:
                maps[depth] = option
                if canonical_partial(tuple(maps), range(depth + 1), group):
                    visit(depth + 1, next_three)
        maps[depth] = IDENTITY

    visit(1, 1 if target_three else 0)
    return leaves, exceptions, orbit_representatives


def analyze_orbits(target_three, representatives):
    primitive_class_histogram = Counter()
    primitive_globalizer_histogram = Counter()
    local_group_histogram = Counter()
    rescue_group_histogram = Counter()
    lift_class_histogram = Counter()
    lift_globalizer_histogram = Counter()
    retained_old_histogram = Counter()
    lift_profile_histogram = Counter()
    lifts = zero_lifts = separators = 0
    best = None

    for orbit_key, maps in sorted(representatives.items()):
        old_edges, old_roots, old_classes = edge_partition(6, maps)
        old_side_classes = edge_class_arrays(old_edges, old_roots, old_classes)
        conditions = parent_permutation_conditions(6, old_edges, old_roots, old_classes)
        globalizers = tuple(permutation for permutation, pairs in conditions if not pairs)
        if not globalizers or IDENTITY in globalizers:
            raise AssertionError("exception filter/globalizer census mismatch")
        local_group = generated_subgroup(maps, 6)
        rescue_group = generated_subgroup(globalizers, 6)
        primitive_class_histogram[len(old_classes)] += 1
        primitive_globalizer_histogram[len(globalizers)] += 1
        local_group_histogram[len(local_group)] += 1
        rescue_group_histogram[len(rescue_group)] += 1

        for outside_globalizer in globalizers:
            lifts += 1
            family = lift_family(maps, outside_globalizer)
            lifted_edges, lifted_roots, lifted_classes = edge_partition(7, family)
            retained = retained_old_classes(
                old_edges, old_side_classes, lifted_edges, lifted_roots
            )
            profile = class_profile(lifted_roots)
            lift_class_histogram[len(lifted_classes)] += 1
            retained_old_histogram[retained] += 1
            lift_profile_histogram[profile] += 1
            lifted_conditions = parent_permutation_conditions(
                7, lifted_edges, lifted_roots, lifted_classes
            )
            lifted_globalizers = tuple(
                permutation for permutation, pairs in lifted_conditions if not pairs
            )
            lift_globalizer_histogram[len(lifted_globalizers)] += 1
            assignment = None
            if not lifted_globalizers:
                zero_lifts += 1
                assignment = separating_binary_assignment(
                    len(lifted_classes), lifted_conditions
                )
                separators += assignment is not None
                if assignment is not None:
                    g, h = instantiate(
                        7, lifted_edges, lifted_roots, lifted_classes, assignment
                    )
                    candidate = {
                        "status": "EXACT_GRC_CE_CANDIDATE",
                        "three_count": target_three,
                        "primitive_maps": maps,
                        "outside_globalizer": outside_globalizer,
                        "lifted_maps": family,
                        "lifted_class_count": len(lifted_classes),
                        "assignment": assignment,
                        "G_graph6": g.to_graph6(),
                        "H_graph6": h.to_graph6(),
                        "local_maps_verify": verify_local_maps(g, h, family),
                        "same_deck": same_deck(g, h),
                        "parents_isomorphic": is_isomorphic(g, h),
                    }
                    print(json.dumps(candidate, sort_keys=True), flush=True)
                    raise SystemExit(3)
            score = (
                len(lifted_classes),
                retained,
                -len(lifted_globalizers),
                len(old_classes),
                -len(globalizers),
            )
            if best is None or score > best[0]:
                best = (score, {
                    "primitive_maps": maps,
                    "primitive_edge_classes": old_side_classes,
                    "primitive_class_profile": class_profile(old_roots),
                    "primitive_globalizers": globalizers,
                    "primitive_globalizer_cycle_types": tuple(
                        cycle_type(permutation) for permutation in globalizers
                    ),
                    "local_generated_group_order": len(local_group),
                    "rescue_generated_group_order": len(rescue_group),
                    "outside_globalizer": outside_globalizer,
                    "lifted_maps": family,
                    "lifted_class_count": len(lifted_classes),
                    "lifted_class_profile": profile,
                    "retained_old_classes": retained,
                    "lifted_globalizers": lifted_globalizers,
                })

    return {
        "primitive_class_histogram": dict(sorted(primitive_class_histogram.items())),
        "primitive_globalizer_histogram": dict(sorted(primitive_globalizer_histogram.items())),
        "local_generated_group_histogram": dict(sorted(local_group_histogram.items())),
        "rescue_generated_group_histogram": dict(sorted(rescue_group_histogram.items())),
        "admissible_lifts": lifts,
        "lift_class_histogram": dict(sorted(lift_class_histogram.items())),
        "lift_globalizer_histogram": dict(sorted(lift_globalizer_histogram.items())),
        "retained_old_class_histogram": dict(sorted(retained_old_histogram.items())),
        "lift_class_profile_histogram": {
            str(key): value for key, value in sorted(lift_profile_histogram.items())
        },
        "zero_globalizer_lifts": zero_lifts,
        "assignment_specific_separators": separators,
        "best": best[1] if best else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--three-count", type=int, choices=range(7), required=True)
    parser.add_argument("--progress", type=int, default=500000)
    args = parser.parse_args()
    start = time.monotonic()
    leaves, exceptions, representatives = collect_exception_orbits(
        args.three_count, args.progress
    )
    analysis = analyze_orbits(args.three_count, representatives)
    payload = {
        "status": "EXTENSION_RESILIENCE_CENSUS_COMPLETE",
        "three_count": args.three_count,
        "source_canonical_leaves": leaves,
        "source_nonidentity_exceptions": exceptions,
        "full_relabeling_side_reversal_orbits": len(representatives),
        **analysis,
        "elapsed_seconds": time.monotonic() - start,
    }
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
