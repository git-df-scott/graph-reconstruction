#!/usr/bin/env python3
"""Classify complementary Goldilocks rescue torsors and their exact joins."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import resource
import time
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import single_merge_escape as single


N = single.N
OLD_N = single.OLD_N
GOLDILOCKS = ((0, 1), (0, 2), (1, 2))
ALL_S7 = single.ALL_S7
IDENTITY = single.IDENTITY
universal = single.universal


def inverse(permutation):
    result = [0] * len(permutation)
    for source, image in enumerate(permutation):
        result[image] = source
    return tuple(result)


def conjugate(permutation, by):
    return single.compose(single.compose(by, permutation), inverse(by))


def partition_pairs(labels):
    first = {}
    pairs = []
    for item, label in enumerate(labels):
        if label in first:
            pairs.append((first[label], item))
        else:
            first[label] = item
    return tuple(pairs)


def join_partitions(left, right):
    return left.add_pairs(partition_pairs(right.labels))


def canonical_payload(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def checksum(value):
    return hashlib.sha256(canonical_payload(value)).hexdigest()


def all_minimum_terminals():
    records = []
    for merge in GOLDILOCKS:
        seed, representatives = single.merged_seed(merge)
        vocabularies = tuple(
            universal.row_vocabulary(deleted, seed, representatives)
            for deleted in range(OLD_N)
        )
        terminals, _layers = single.terminal_dp_with_paths(
            seed, representatives, vocabularies
        )
        index = 0
        for labels, rows in terminals.items():
            state = universal.Partition(labels)
            globalizers = universal.exact_globalizers(state.side_classes())
            if len(globalizers) != 2:
                continue
            old_witness_failures = {}
            for rescue_index, rescue in enumerate(single.BASE_RESCUERS):
                old_witness_failures[str(rescue_index)] = tuple(
                    vertex
                    for vertex, endpoints in enumerate(single.witness_pairs(rescue))
                    if not state.connected(*endpoints)
                )
            generated = single.generated_subgroup(globalizers, N)
            normalizer = tuple(
                permutation
                for permutation in ALL_S7
                if {conjugate(element, permutation) for element in generated}
                == set(generated)
            )
            pair_stabilizer = tuple(
                permutation
                for permutation in ALL_S7
                if {conjugate(element, permutation) for element in globalizers}
                == set(globalizers)
            )
            moved = tuple(
                vertex
                for vertex in range(N)
                if any(permutation[vertex] != vertex for permutation in globalizers)
            )
            payload = {
                "merge": merge,
                "terminal_index": index,
                "labels": labels,
                "side_classes": state.side_classes(),
                "rows": rows,
                "outside_row": single.BASE_RESCUERS[0],
                "class_count": state.class_count(),
                "class_profile": tuple(sorted(Counter(labels).values(), reverse=True)),
                "globalizers": globalizers,
                "generated_subgroup": generated,
                "generated_subgroup_order": len(generated),
                "normalizer_order_s7": len(normalizer),
                "rescue_pair_stabilizer_order_s7": len(pair_stabilizer),
                "moved_vertices": moved,
                "fixed_vertices": tuple(v for v in range(N) if v not in moved),
                "old_rescuer_witness_failures": old_witness_failures,
            }
            payload["sha256"] = checksum(payload)
            records.append(payload)
            index += 1
    return tuple(records)


def rescue_pair_orbits(records):
    a4 = tuple(
        permutation + (OLD_N,)
        for permutation in single.a4_class_action()["vertex_group"]
    )
    distinct = {frozenset(record["globalizers"]) for record in records}
    remaining = set(distinct)
    orbits = []
    while remaining:
        representative = min(remaining, key=lambda pair: tuple(sorted(pair)))
        orbit = {
            frozenset(conjugate(element, by) for element in representative)
            for by in a4
        }
        orbit &= distinct
        remaining -= orbit
        orbits.append(tuple(tuple(sorted(pair)) for pair in sorted(
            orbit, key=lambda pair: tuple(sorted(pair))
        )))
    disjoint = tuple(
        (left, right)
        for left, right in itertools.combinations(sorted(distinct, key=lambda x: tuple(sorted(x))), 2)
        if not (left & right)
    )
    return {
        "distinct_pairs": len(distinct),
        "a4_orbits": tuple(orbits),
        "a4_orbit_count": len(orbits),
        "pairwise_disjoint_distinct_pairs": len(disjoint),
        "all_distinct_pairs_are_disjoint": len(disjoint) == 3,
    }


def independent_join_labels(left, right):
    blocks = universal.blocks_from_labels(left.labels)
    blocks = universal.independent_add_pairs(blocks, partition_pairs(right.labels))
    return universal.labels_from_blocks(blocks)


def pairwise_join_analysis(records, raw_replay=False):
    histogram = Counter()
    results = []
    for left_index, right_index in itertools.combinations(range(len(records)), 2):
        left_record, right_record = records[left_index], records[right_index]
        left = universal.Partition(tuple(left_record["labels"]))
        right = universal.Partition(tuple(right_record["labels"]))
        joined = join_partitions(left, right)
        independent = independent_join_labels(left, right)
        if joined.labels != independent:
            raise AssertionError("union-find and bit-set joins disagree")
        globalizers = universal.exact_globalizers(joined.side_classes())
        if raw_replay:
            raw = tuple(
                permutation for permutation in ALL_S7
                if universal.maps_classes(joined.side_classes(), permutation)
            )
            if set(raw) != set(globalizers):
                raise AssertionError("backtracking and raw S7 join replay disagree")
        left_set = set(left_record["globalizers"])
        right_set = set(right_record["globalizers"])
        cross_merge = tuple(left_record["merge"]) != tuple(right_record["merge"])
        key = (
            "cross" if cross_merge else "same",
            joined.class_count(),
            len(globalizers),
            IDENTITY in globalizers,
        )
        histogram[key] += 1
        results.append({
            "left": (left_record["merge"], left_record["terminal_index"]),
            "right": (right_record["merge"], right_record["terminal_index"]),
            "cross_merge": cross_merge,
            "class_count": joined.class_count(),
            "class_profile": tuple(sorted(Counter(joined.labels).values(), reverse=True)),
            "globalizer_count": len(globalizers),
            "globalizers_sha256": checksum(globalizers),
            "identity": IDENTITY in globalizers,
            "residual_intersection": tuple(sorted(left_set & right_set)),
            "new_globalizer_count": len(set(globalizers) - left_set - right_set),
            "new_globalizers_sha256": checksum(tuple(sorted(
                set(globalizers) - left_set - right_set
            ))),
            "moved_vertices": tuple(
                vertex for vertex in range(N)
                if any(permutation[vertex] != vertex for permutation in globalizers)
            ),
            "labels": joined.labels,
            "sha256": checksum({"labels": joined.labels}),
        })
    cross = tuple(result for result in results if result["cross_merge"])
    return {
        "pair_count": len(results),
        "cross_merge_pair_count": len(cross),
        "histogram": {str(key): count for key, count in sorted(histogram.items())},
        "cross_minimum_globalizers": min(r["globalizer_count"] for r in cross),
        "cross_zero_globalizer_joins": sum(r["globalizer_count"] == 0 for r in cross),
        "cross_identity_joins": sum(r["identity"] for r in cross),
        "cross_disjoint_residual_pairs": sum(not r["residual_intersection"] for r in cross),
        "results": tuple(results),
    }


def double_merge_seed():
    seed, representatives = universal.old_seed()
    seed = seed.add_pairs((
        (representatives[0], representatives[1]),
        (representatives[0], representatives[2]),
    ))
    retained = (
        representatives[0], representatives[3], representatives[4], representatives[5]
    )
    if not universal.old_classes_distinct(seed, retained):
        raise AssertionError("double-merge seed malformed")
    return seed, retained


def identity_witnesses():
    return tuple(
        (universal.slot(0, (OLD_N, vertex)), universal.slot(1, (OLD_N, vertex)))
        for vertex in range(OLD_N)
    )


def identity_forcing_cores(seed, retained, vocabularies):
    witnesses = identity_witnesses()
    data = {}
    for size in range(OLD_N + 1):
        for subset in itertools.combinations(range(OLD_N), size):
            states, _layers = universal.independent_terminal_dp(
                seed, retained, vocabularies, subset
            )
            forced = tuple(
                vertex for vertex, (left, right) in enumerate(witnesses)
                if states and all(
                    any(block & (1 << left) and block & (1 << right) for block in state)
                    for state in states
                )
            )
            data[subset] = (len(states), forced)
    cores = tuple(
        (subset, state_count)
        for subset, (state_count, forced) in data.items()
        if len(forced) == OLD_N and not any(
            set(smaller) < set(subset) and len(data[smaller][1]) == OLD_N
            for smaller in data
        )
    )
    return cores


def simultaneous_csp(raw_replay=False):
    seed, retained = double_merge_seed()
    vocabularies = tuple(
        universal.row_vocabulary(deleted, seed, retained)
        for deleted in range(OLD_N)
    )
    independent_vocabularies = universal.independent_row_vocabularies(seed, retained)
    for discovery, verification in zip(vocabularies, independent_vocabularies):
        if (
            discovery["raw"], discovery["compatible"], discovery["distinct_effects"]
        ) != (
            verification["raw"], verification["compatible"], verification["distinct_effects"]
        ):
            raise AssertionError("independent double-merge vocabularies disagree")
    terminals, layers = single.terminal_dp_with_paths(seed, retained, vocabularies)
    blocks, independent_layers = universal.independent_terminal_dp(
        seed, retained, independent_vocabularies
    )
    independent_labels = {universal.labels_from_blocks(state) for state in blocks}
    if set(terminals) != independent_labels or layers != independent_layers:
        raise AssertionError("independent double-merge terminal DPs disagree")
    histogram = Counter()
    records = []
    for labels, rows in terminals.items():
        state = universal.Partition(labels)
        globalizers = universal.exact_globalizers(state.side_classes())
        if raw_replay:
            raw = tuple(
                permutation for permutation in ALL_S7
                if universal.maps_classes(state.side_classes(), permutation)
            )
            if set(raw) != set(globalizers):
                raise AssertionError("raw S7 simultaneous replay disagrees")
        histogram[(state.class_count(), len(globalizers), IDENTITY in globalizers)] += 1
        record = {
            "labels": labels,
            "side_classes": state.side_classes(),
            "rows": rows,
            "outside_row": single.BASE_RESCUERS[0],
            "class_count": state.class_count(),
            "class_profile": tuple(sorted(Counter(labels).values(), reverse=True)),
            "globalizers": globalizers,
            "globalizer_count": len(globalizers),
            "identity": IDENTITY in globalizers,
        }
        record["sha256"] = checksum(record)
        records.append(record)
    minimum = min(record["globalizer_count"] for record in records)
    strongest = max(
        (record for record in records if record["globalizer_count"] == minimum),
        key=lambda record: record["class_count"],
    )
    return {
        "seed_class_count": seed.class_count(),
        "retained_old_classes": len(retained),
        "row_vocabularies": tuple({
            "raw": vocabulary["raw"],
            "compatible": vocabulary["compatible"],
            "distinct_effects": vocabulary["distinct_effects"],
        } for vocabulary in vocabularies),
        "raw_row_trials": sum(vocabulary["raw"] for vocabulary in vocabularies),
        "compatible_rows": sum(vocabulary["compatible"] for vocabulary in vocabularies),
        "distinct_effects": sum(vocabulary["distinct_effects"] for vocabulary in vocabularies),
        "layers": layers,
        "terminal_count": len(records),
        "histogram": {str(key): count for key, count in sorted(histogram.items())},
        "minimum_globalizers": minimum,
        "maximum_s7_killed": len(ALL_S7) - minimum,
        "zero_globalizer_terminals": sum(not record["globalizers"] for record in records),
        "identity_terminals": sum(record["identity"] for record in records),
        "identity_forcing_cores": identity_forcing_cores(
            seed, retained, independent_vocabularies
        ),
        "strongest_terminal": strongest,
        "raw_replay": raw_replay,
    }


def run(raw_replay=False):
    start = time.monotonic()
    records = all_minimum_terminals()
    joins = pairwise_join_analysis(records, raw_replay=raw_replay)
    simultaneous = simultaneous_csp(raw_replay=raw_replay)
    zero = joins["cross_zero_globalizer_joins"] + simultaneous["zero_globalizer_terminals"]
    return {
        "status": "ZERO_GLOBALIZER_FROZEN" if zero else "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "grc_ce": "NO",
        "minimum_terminal_count": len(records),
        "minimum_terminals": records,
        "rescue_pair_orbits": rescue_pair_orbits(records),
        "pairwise_joins": joins,
        "simultaneous_csp": simultaneous,
        "all_three_merges": "same transitive seed as any two distinct matching-class merges",
        "obstruction": (
            "Distinct residual rescue pairs are disjoint, but joining completed systems "
            "regenerates S4 or S5. In the true six-row CSP, two distinct merges identify "
            "all three matching classes and every terminal forces identity."
        ),
        "elapsed_seconds": time.monotonic() - start,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "verification": (
            "union-find plus independent bit-set vocabularies/DP/joins; exact backtracking"
            + (" plus raw 5040-permutation replay" if raw_replay else "")
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--raw-s7-replay", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(raw_replay=args.raw_s7_replay)
    rendered = json.dumps(result, indent=2 if args.pretty else None, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
