#!/usr/bin/env python3
"""Canonical exact n=6 search for 3-cycle and double-transposition maps.

For a homogeneous conjugacy family, simultaneous relabeling lets us anchor
the map on deleted vertex 0 to one fixed representative.  A canonical-prefix
test under that anchor's centralizer removes the remaining guaranteed
duplicates.  Thus every full system in the requested family has at least one
visited representative.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from exhaustive_transposition_systems import canonical_system, is_exact_globalizer, relabel_system
from local_gluing_search import (
    edge_partition,
    parent_permutation_conditions,
    universal_edge_class_isomorphism,
)


N = 6
IDENTITY = tuple(range(N))


def three_cycles(deleted: int):
    available = [v for v in range(N) if v != deleted]
    result = []
    for a, b, c in itertools.combinations(available, 3):
        for cycle in ((a, b, c), (a, c, b)):
            permutation = list(range(N))
            permutation[cycle[0]] = cycle[1]
            permutation[cycle[1]] = cycle[2]
            permutation[cycle[2]] = cycle[0]
            result.append(tuple(permutation))
    return tuple(result)


def double_transpositions(deleted: int):
    available = [v for v in range(N) if v != deleted]
    result = set()
    for fixed in available:
        moved = [v for v in available if v != fixed]
        a = moved[0]
        for b in moved[1:]:
            remainder = [v for v in moved if v not in (a, b)]
            permutation = list(range(N))
            permutation[a], permutation[b] = b, a
            permutation[remainder[0]], permutation[remainder[1]] = remainder[1], remainder[0]
            result.add(tuple(permutation))
    return tuple(sorted(result))


def compose(left, right):
    return tuple(left[right[v]] for v in range(N))


def inverse(permutation):
    result = [0] * N
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


def centralizer(anchor):
    result = []
    for permutation in itertools.permutations(range(N)):
        if permutation[0] != 0:
            continue
        if compose(permutation, anchor) == compose(anchor, permutation):
            result.append(tuple(permutation))
    return tuple(result)


def canonical_partial(maps, assigned, group):
    """Canonical representative under anchor-preserving relabelings."""

    assigned = frozenset(assigned)
    key = tuple(maps[i] for i in sorted(assigned))
    for relabeling in group:
        if {relabeling[i] for i in assigned} != assigned:
            continue
        transformed = relabel_system(maps, relabeling)
        candidate = tuple(transformed[i] for i in sorted(assigned))
        if candidate < key:
            return False
    return True


def cycle_type(permutation):
    seen = set()
    lengths = []
    for start in range(N):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            length += 1
            current = permutation[current]
        if length > 1:
            lengths.append(length)
    return tuple(sorted(lengths, reverse=True)) or (1,)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=("3cycle", "double", "mixed"), required=True)
    parser.add_argument("--three-count", type=int, default=None)
    parser.add_argument("--progress", type=int, default=100000)
    args = parser.parse_args()
    if args.family == "mixed" and args.three_count not in range(1, N):
        raise SystemExit("mixed search requires --three-count in {1,2,3,4,5}")
    three_options = tuple(three_cycles(deleted) for deleted in range(N))
    double_options = tuple(double_transpositions(deleted) for deleted in range(N))
    if args.family == "3cycle":
        target_three = N
    elif args.family == "double":
        target_three = 0
    else:
        target_three = args.three_count
    anchor = (three_options if target_three else double_options)[0][0]
    group = centralizer(anchor)
    maps = [IDENTITY] * N
    maps[0] = anchor
    nodes = leaves = zero = identity_rescues = 0
    class_histogram = Counter()
    rescue_types = Counter()
    exceptional_orbits = Counter()
    exceptional_globalizer_counts = Counter()
    exceptional_globalizer_profiles = Counter()
    minimum_globalizer_count = None
    minimum_example = None
    start = time.monotonic()

    def visit(depth, used_three):
        nonlocal nodes, leaves, zero, identity_rescues, minimum_globalizer_count, minimum_example
        if depth == N:
            leaves += 1
            edges, roots, classes = edge_partition(N, tuple(maps))
            class_histogram[len(classes)] += 1
            if is_exact_globalizer(IDENTITY, N, edges, roots, classes):
                globalizer = IDENTITY
                identity_rescues += 1
            else:
                globalizer = universal_edge_class_isomorphism(N, edges, roots, classes)
            if globalizer is None:
                zero += 1
                print(json.dumps({
                    "status": "ZERO_EXACT_LABEL_GLOBALIZER",
                    "family": args.family,
                    "maps": maps,
                    "classes": len(classes),
                    "canonical_leaves_before_hit": leaves,
                }, sort_keys=True), flush=True)
                raise SystemExit(2)
            rescue_types[cycle_type(globalizer)] += 1
            if globalizer != IDENTITY or len(classes) >= 4:
                conditions = parent_permutation_conditions(N, edges, roots, classes)
                exact_globalizers = tuple(p for p, pairs in conditions if not pairs)
                if minimum_globalizer_count is None or len(exact_globalizers) < minimum_globalizer_count:
                    minimum_globalizer_count = len(exact_globalizers)
                    minimum_example = {
                        "maps": tuple(maps),
                        "class_count": len(classes),
                        "G_to_H_globalizers": exact_globalizers,
                    }
                if globalizer != IDENTITY:
                    exceptional_globalizer_counts[len(exact_globalizers)] += 1
                    profile = tuple(sorted(cycle_type(p) for p in exact_globalizers))
                    exceptional_globalizer_profiles[str(profile)] += 1
                    exceptional_orbits[canonical_system(tuple(maps))] += 1
            if args.progress and leaves % args.progress == 0:
                print(f"PROGRESS leaves={leaves} nodes={nodes} elapsed={time.monotonic()-start:.1f}s", flush=True)
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
                nodes += 1
                if canonical_partial(tuple(maps), range(depth + 1), group):
                    visit(depth + 1, next_three)
        maps[depth] = IDENTITY

    visit(1, 1 if target_three else 0)
    raw_domain = (
        len(three_options[1]) ** (target_three - (1 if target_three else 0))
        * len(double_options[1]) ** (N - target_three - (0 if target_three else 1))
        * (1 if target_three in (0, N) else math.comb(5, target_three - 1))
    )
    print(json.dumps({
        "status": "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "family": args.family,
        "three_cycle_card_count": target_three,
        "anchor": anchor,
        "anchor_centralizer_order": len(group),
        "raw_anchored_domain": raw_domain,
        "canonical_leaves": leaves,
        "branch_nodes": nodes,
        "zero_globalizers": zero,
        "identity_rescues": identity_rescues,
        "rescue_witness_cycle_types": {str(key): value for key, value in sorted(rescue_types.items())},
        "nonidentity_exception_full_orbits": len(exceptional_orbits),
        "nonidentity_exception_orbit_multiplicities": sorted(exceptional_orbits.values()),
        "nonidentity_exception_globalizer_counts": dict(sorted(exceptional_globalizer_counts.items())),
        "nonidentity_exception_globalizer_profiles": dict(sorted(exceptional_globalizer_profiles.items())),
        "minimum_globalizer_count_among_class_ge4_or_nonidentity": minimum_globalizer_count,
        "minimum_example_among_class_ge4_or_nonidentity": minimum_example,
        "class_histogram": dict(sorted(class_histogram.items())),
        "elapsed_seconds": time.monotonic() - start,
        "completeness": "anchor conjugacy plus exact residual-centralizer canonical prefixes",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
