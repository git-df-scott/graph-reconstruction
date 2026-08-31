#!/usr/bin/env python3
"""Exact incidence-signature strike on heterogeneous order-seven extensions.

The finite domain inserts the new vertex into each cycle decomposition of the
six certified primitive rows.  Deleting the new symbol from the lifted cycle
recovers the old row.  This changes the cross-edge incidence and is not a
carrier twist of an already-complete lift.
"""

from __future__ import annotations

import argparse
import itertools
import json
import resource
import time
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from local_gluing_search import edge_partition, edge_class_arrays, validate_local_maps


N = 7
OLD_N = 6
IDENTITY = tuple(range(N))
EDGES = tuple((u, v) for u in range(N) for v in range(u + 1, N))
EDGE_POSITION = {edge: position for position, edge in enumerate(EDGES)}

OLD_PRIMITIVE = (
    (0, 2, 3, 1, 4, 5),
    (3, 1, 0, 2, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (2, 0, 1, 3, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (1, 3, 2, 0, 4, 5),
)
OLD_RESCUERS = (
    (0, 2, 3, 1, 4, 5),
    (1, 3, 2, 0, 4, 5),
    (2, 0, 1, 3, 4, 5),
    (3, 1, 0, 2, 4, 5),
)


def extend_fixed(permutation: tuple[int, ...]) -> tuple[int, ...]:
    return permutation + (OLD_N,)


BASE_LIFT = tuple(extend_fixed(row) for row in OLD_PRIMITIVE) + (
    extend_fixed(OLD_RESCUERS[0]),
)
BASE_RESCUERS = tuple(extend_fixed(row) for row in OLD_RESCUERS)


def insert_new_vertex(
    permutation: tuple[int, ...], deleted: int, after: int | None
) -> tuple[int, ...]:
    """Insert vertex 6 after one old cycle symbol, or leave it fixed.

    Removing 6 from the resulting cycle notation recovers ``permutation``.
    The deleted vertex cannot be an insertion point, so its fixed-point row
    condition is preserved.
    """

    if after == deleted:
        raise ValueError("cannot insert after the deleted fixed point")
    result = list(extend_fixed(permutation))
    if after is not None:
        result[after], result[OLD_N] = OLD_N, permutation[after]
    lifted = tuple(result)
    validate_local_maps(N, tuple(
        lifted if index == deleted else IDENTITY for index in range(N)
    ))
    return lifted


def heterogeneous_family(
    insertion_choices: tuple[int | None, ...], outside_rescuer: int
) -> tuple[tuple[int, ...], ...]:
    if len(insertion_choices) != OLD_N:
        raise ValueError("one insertion choice is required for each old row")
    rows = tuple(
        insert_new_vertex(OLD_PRIMITIVE[deleted], deleted, choice)
        for deleted, choice in enumerate(insertion_choices)
    ) + (extend_fixed(OLD_RESCUERS[outside_rescuer]),)
    validate_local_maps(N, rows)
    return rows


def side_classes(family: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return edge_class_arrays(*edge_partition(N, family))


def normalized_incidence_signature(
    first: tuple[tuple[int, ...], tuple[int, ...]],
    second: tuple[tuple[int, ...], tuple[int, ...]],
) -> tuple[tuple[int, int], ...]:
    """Fixed-carrier colored incidence signature, invariant to class names.

    Slot order is ``(side, lexicographic unordered edge)``.  Each entry gives
    its canonically renamed first- and second-system class.  Retaining every
    colored slot, rather than only intersection multiplicities, preserves the
    complete parent-side information.
    """

    pairs = tuple(
        (first[side][position], second[side][position])
        for side in range(2) for position in range(len(EDGES))
    )
    left_sets: dict[int, list[int]] = {}
    right_sets: dict[int, list[int]] = {}
    for slot, (left, right) in enumerate(pairs):
        left_sets.setdefault(left, []).append(slot)
        right_sets.setdefault(right, []).append(slot)
    left_order = {
        old: new for new, (old, _slots) in enumerate(
            sorted(left_sets.items(), key=lambda item: tuple(item[1]))
        )
    }
    right_order = {
        old: new for new, (old, _slots) in enumerate(
            sorted(right_sets.items(), key=lambda item: tuple(item[1]))
        )
    }
    return tuple((left_order[left], right_order[right]) for left, right in pairs)


def joined_side_classes(
    signature: tuple[tuple[int, int], ...]
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], int]:
    """Return component colors; incidence components equal partition joins."""

    left_count = 1 + max(left for left, _right in signature)
    right_count = 1 + max(right for _left, right in signature)
    parent = list(range(left_count + right_count))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for left, right in signature:
        union(left, left_count + right)
    roots = tuple(find(left) for left, _right in signature)
    names: dict[int, int] = {}
    colors = []
    for root in roots:
        if root not in names:
            names[root] = len(names)
        colors.append(names[root])
    slots = len(EDGES)
    return (tuple(colors[:slots]), tuple(colors[slots:])), len(names)


def maps_classes(
    classes: tuple[tuple[int, ...], tuple[int, ...]],
    permutation: tuple[int, ...],
) -> bool:
    for position, edge in enumerate(EDGES):
        image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
        if classes[0][position] != classes[1][EDGE_POSITION[image]]:
            return False
    return True


def exact_globalizers(
    classes: tuple[tuple[int, ...], tuple[int, ...]],
) -> tuple[tuple[int, ...], ...]:
    """Enumerate all colored-complete-graph isomorphisms by exact backtracking."""

    colors = [[[None] * N for _ in range(N)] for _ in range(2)]
    signatures = [[None] * N for _ in range(2)]
    for side in range(2):
        for position, (u, v) in enumerate(EDGES):
            color = classes[side][position]
            colors[side][u][v] = colors[side][v][u] = color
        for vertex in range(N):
            signatures[side][vertex] = tuple(sorted(
                colors[side][vertex][other] for other in range(N) if other != vertex
            ))
    if sorted(signatures[0]) != sorted(signatures[1]):
        return ()
    mapping = [-1] * N
    used = [False] * N
    answers: list[tuple[int, ...]] = []

    def candidates(vertex: int):
        for image in range(N):
            if used[image] or signatures[0][vertex] != signatures[1][image]:
                continue
            if all(
                colors[0][vertex][old] == colors[1][image][mapping[old]]
                for old in range(N) if mapping[old] >= 0
            ):
                yield image

    def search(remaining: tuple[int, ...]) -> None:
        if not remaining:
            answers.append(tuple(mapping))
            return
        counts = [(sum(1 for _ in candidates(vertex)), vertex) for vertex in remaining]
        count, vertex = min(counts)
        if count == 0:
            return
        rest = tuple(old for old in remaining if old != vertex)
        for image in candidates(vertex):
            mapping[vertex] = image
            used[image] = True
            search(rest)
            used[image] = False
            mapping[vertex] = -1

    search(tuple(range(N)))
    return tuple(answers)


def regression_examples() -> dict[str, object]:
    """Classify three fixed representatives solely through incidence data."""

    base = side_classes(BASE_LIFT)
    examples: dict[str, object] = {}
    # These twists are fixed certificates recovered once from the closed domain.
    twists = {
        "compatible": IDENTITY,
        "partial": (0, 1, 3, 2, 4, 5, 6),
        "strong": (0, 1, 2, 4, 3, 5, 6),
    }
    for name, twist in twists.items():
        rows = [[0] * N for _ in range(N)]
        for deleted, permutation in enumerate(BASE_LIFT):
            for source in range(N):
                rows[twist[deleted]][twist[source]] = twist[permutation[source]]
        second = side_classes(tuple(tuple(row) for row in rows))
        signature = normalized_incidence_signature(base, second)
        joined, class_count = joined_side_classes(signature)
        globalizers = exact_globalizers(joined)
        examples[name] = {
            "twist": twist,
            "classes": class_count,
            "globalizers": len(globalizers),
            "identity": IDENTITY in globalizers,
        }
    return examples


def run(raw_s7_replay: bool = False) -> dict[str, object]:
    start = time.monotonic()
    base = side_classes(BASE_LIFT)
    choices_by_row = tuple(
        (None,) + tuple(vertex for vertex in range(OLD_N) if vertex != deleted)
        for deleted in range(OLD_N)
    )
    totals = Counter()
    class_histogram = Counter()
    intersection_histogram = Counter()
    rescue_subset_histogram = Counter()
    class_intersection_histogram = Counter()
    emergent_histogram = Counter()
    signature_keys = set()
    globalizer_cache: dict[
        tuple[tuple[int, ...], tuple[int, ...]], tuple[tuple[int, ...], ...]
    ] = {}
    best: dict[str, object] | None = None
    zero_record: dict[str, object] | None = None

    for insertion_choices in itertools.product(*choices_by_row):
        for outside_rescuer in range(len(OLD_RESCUERS)):
            family = heterogeneous_family(insertion_choices, outside_rescuer)
            second = side_classes(family)
            signature = normalized_incidence_signature(base, second)
            signature_keys.add(signature)
            joined, class_count = joined_side_classes(signature)
            class_histogram[class_count] += 1
            totals["systems"] += 1
            if joined not in globalizer_cache:
                globalizer_cache[joined] = exact_globalizers(joined)
            all_globalizers = globalizer_cache[joined]

            rescue_subset = tuple(
                index for index, rescue in enumerate(BASE_RESCUERS)
                if maps_classes(second, rescue)
            )
            if 1 not in rescue_subset:
                raise AssertionError("the certified universal survivor disappeared")
            old_intersection = len(rescue_subset)
            intersection_histogram[old_intersection] += 1
            rescue_subset_histogram[rescue_subset] += 1
            class_intersection_histogram[(class_count, old_intersection)] += 1
            emergent_histogram[
                (class_count, old_intersection, len(all_globalizers))
            ] += 1
            if old_intersection:
                totals["old_rescue_rejects"] += 1
                continue
            totals["empty_old_intersection"] += 1
            if maps_classes(joined, IDENTITY):
                totals["identity_rejects"] += 1
                continue
            totals["parent_side_asymmetric"] += 1
            globalizers = all_globalizers
            score = (class_count, -len(globalizers))
            if best is None or score > tuple(best["score"]):
                best = {
                    "score": score,
                    "insertion_choices": insertion_choices,
                    "outside_rescuer": outside_rescuer,
                    "family": family,
                    "classes": class_count,
                    "globalizers": globalizers,
                    "signature": signature,
                    "joined_side_classes": joined,
                }
            if not globalizers:
                zero_record = best
                totals["zero_globalizers"] += 1
                break
        if zero_record is not None:
            break

    raw_replay_checked = 0
    if raw_s7_replay:
        permutations = tuple(itertools.permutations(range(N)))
        for joined, backtracking_globalizers in globalizer_cache.items():
            raw = tuple(p for p in permutations if maps_classes(joined, p))
            if set(raw) != set(backtracking_globalizers):
                raise AssertionError("raw S7 replay disagrees with backtracking")
            raw_replay_checked += 1

    return {
        "status": "ZERO_GLOBALIZER_FROZEN" if zero_record else "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "n": N,
        "domain": "cycle-insertion lifts of all six old rows x four outside rescuers",
        "row_choices": [len(choices) for choices in choices_by_row],
        "expected_systems": (6 ** 6) * len(OLD_RESCUERS),
        "totals": dict(totals),
        "fixed_carrier_incidence_signatures": len(signature_keys),
        "distinct_joined_side_arrays": len(globalizer_cache),
        "class_histogram": dict(sorted(class_histogram.items())),
        "old_rescue_intersection_histogram": dict(sorted(intersection_histogram.items())),
        "old_rescue_subset_histogram": {
            str(key): count for key, count in sorted(rescue_subset_histogram.items())
        },
        "class_intersection_histogram": {
            str(key): count for key, count in sorted(class_intersection_histogram.items())
        },
        "class_old_intersection_total_globalizer_histogram": {
            str(key): count for key, count in sorted(emergent_histogram.items(), key=str)
        },
        "best": best,
        "zero_record": zero_record,
        "trichotomy_regression": regression_examples(),
        "elapsed_seconds": time.monotonic() - start,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "raw_s7_replay_joined_arrays": raw_replay_checked,
        "completeness": "raw enumeration; every row validated; exact colored-graph backtracking",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--raw-s7-replay", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        run(raw_s7_replay=args.raw_s7_replay),
        indent=2 if args.pretty else None,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
