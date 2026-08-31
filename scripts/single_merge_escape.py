#!/usr/bin/env python3
"""Classify all fifteen one-pair old-class merges and their row CSPs."""

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

import kill_universal_rescuer as universal
from incidence_join_strike import BASE_RESCUERS, IDENTITY, OLD_N, OLD_PRIMITIVE
from local_gluing_search import edge_class_arrays, edge_partition


N = 7
CLASS_COUNT = 6
ALL_S7 = tuple(itertools.permutations(range(N)))
OLD_S6 = tuple(itertools.permutations(range(OLD_N)))
OLD_RESCUERS = tuple(row[:OLD_N] for row in BASE_RESCUERS)


def compose(left, right):
    return tuple(left[right[v]] for v in range(len(left)))


def generated_subgroup(generators, degree):
    identity = tuple(range(degree))
    group = {identity}
    frontier = list(generators)
    while frontier:
        element = frontier.pop()
        if element in group:
            continue
        previous = tuple(group)
        group.add(element)
        frontier.extend(compose(element, old) for old in previous)
        frontier.extend(compose(old, element) for old in previous)
    return tuple(sorted(group))


def cycle_type(permutation):
    seen = set()
    cycles = []
    for vertex in range(len(permutation)):
        if vertex in seen:
            continue
        current = vertex
        length = 0
        while current not in seen:
            seen.add(current)
            length += 1
            current = permutation[current]
        if length > 1:
            cycles.append(length)
    return tuple(sorted(cycles, reverse=True))


def old_data():
    edges, roots, index = edge_partition(OLD_N, OLD_PRIMITIVE)
    return edges, edge_class_arrays(edges, roots, index)


OLD_EDGES, OLD_ARRAYS = old_data()
OLD_POSITION = {edge: position for position, edge in enumerate(OLD_EDGES)}


def maps_old(classes, permutation):
    return all(
        classes[0][position]
        == classes[1][OLD_POSITION[tuple(sorted((permutation[u], permutation[v])))] ]
        for position, (u, v) in enumerate(OLD_EDGES)
    )


def coarsen_old(pair):
    return tuple(
        tuple(pair[0] if color == pair[1] else color for color in side)
        for side in OLD_ARRAYS
    )


def old_merge_analysis(pair):
    classes = coarsen_old(pair)
    globalizers = tuple(p for p in OLD_S6 if maps_old(classes, p))
    generated = generated_subgroup(globalizers, OLD_N)
    if pair[0] < 3 and pair[1] < 3:
        group_description = "S4 on {0,1,2,3}, fixing {4,5}"
    elif pair == (3, 4):
        group_description = "A4 on {0,1,2,3} times C2 swapping {4,5}"
    else:
        group_description = "no enlargement beyond the four-rescuer torsor"
    return {
        "profile": tuple(sorted(Counter(classes[0] + classes[1]).values(), reverse=True)),
        "side_classes": classes,
        "globalizer_count": len(globalizers),
        "globalizers": globalizers,
        "generated_group_order": len(generated),
        "generated_group_description": group_description,
        "old_rescuers": tuple(
            index for index, rescue in enumerate(OLD_RESCUERS)
            if maps_old(classes, rescue)
        ),
        "identity": tuple(range(OLD_N)) in globalizers,
        "side_arrays_equal": classes[0] == classes[1],
    }


def a4_class_action():
    group = generated_subgroup(OLD_RESCUERS, OLD_N)
    actions = set()
    for permutation in group:
        action = []
        for color in range(CLASS_COUNT):
            images = {
                OLD_ARRAYS[0][OLD_POSITION[tuple(sorted((permutation[u], permutation[v])))] ]
                for position, (u, v) in enumerate(OLD_EDGES)
                if OLD_ARRAYS[0][position] == color
            }
            if len(images) != 1:
                raise AssertionError("A4 does not induce a class permutation")
            action.append(images.pop())
        actions.add(tuple(action))
    pairs = set(itertools.combinations(range(CLASS_COUNT), 2))
    orbits = []
    while pairs:
        representative = min(pairs)
        orbit = {
            tuple(sorted((action[representative[0]], action[representative[1]])))
            for action in actions
        }
        pairs.difference_update(orbit)
        orbits.append(tuple(sorted(orbit)))
    return {
        "vertex_group_order": len(group),
        "vertex_group": group,
        "class_action_order": len(actions),
        "class_actions": tuple(sorted(actions)),
        "pair_orbits": tuple(orbits),
    }


def merged_seed(pair):
    seed, representatives = universal.old_seed()
    seed = seed.add_pairs(((representatives[pair[0]], representatives[pair[1]]),))
    retained = tuple(
        representative for index, representative in enumerate(representatives)
        if index != pair[1]
    )
    if not universal.old_classes_distinct(seed, retained):
        raise AssertionError("single-merge seed malformed")
    return seed, retained


def terminal_dp_with_paths(seed, representatives, vocabularies):
    states = {seed.labels: ()}
    layer_counts = [1]
    for deleted in range(OLD_N):
        next_states = {}
        for labels, rows in states.items():
            state = universal.Partition(labels)
            for row in vocabularies[deleted]["effects"]:
                merged = state.add_pairs(universal.row_pairs(deleted, row))
                if universal.old_classes_distinct(merged, representatives):
                    next_states.setdefault(merged.labels, rows + (row,))
        states = next_states
        layer_counts.append(len(states))
    return states, tuple(layer_counts)


def witness_pairs(permutation):
    return tuple(
        (
            universal.slot(0, (OLD_N, vertex)),
            universal.slot(1, (OLD_N, permutation[vertex])),
        )
        for vertex in range(OLD_N)
    )


def analyze_merge(pair, raw_replay=False):
    old = old_merge_analysis(pair)
    seed, representatives = merged_seed(pair)
    vocabularies = tuple(
        universal.row_vocabulary(deleted, seed, representatives)
        for deleted in range(OLD_N)
    )
    independent = universal.independent_row_vocabularies(seed, representatives)
    for discovery, verification in zip(vocabularies, independent):
        if (
            discovery["raw"], discovery["compatible"], discovery["distinct_effects"]
        ) != (
            verification["raw"], verification["compatible"], verification["distinct_effects"]
        ):
            raise AssertionError("row vocabularies disagree")
    terminals, layers = terminal_dp_with_paths(seed, representatives, vocabularies)
    independent_blocks, independent_layers = universal.independent_terminal_dp(
        seed, representatives, independent
    )
    independent_labels = {universal.labels_from_blocks(blocks) for blocks in independent_blocks}
    if set(terminals) != independent_labels or layers != independent_layers:
        raise AssertionError("terminal dynamic programs disagree")

    histogram = Counter()
    old_rescue_histogram = Counter()
    r1_dead = 0
    identity = 0
    records = []
    minimum = None
    for labels, rows in terminals.items():
        state = universal.Partition(labels)
        classes = state.side_classes()
        globalizers = universal.exact_globalizers(classes)
        old_survivors = tuple(
            index for index, rescue in enumerate(BASE_RESCUERS)
            if universal.maps_classes(classes, rescue)
        )
        histogram[(state.class_count(), len(globalizers))] += 1
        old_rescue_histogram[len(old_survivors)] += 1
        r1_dead += not universal.maps_classes(classes, universal.R1)
        identity += universal.maps_classes(classes, IDENTITY)
        profile = tuple(sorted(Counter(labels).values(), reverse=True))
        record = {
            "class_count": state.class_count(),
            "class_profile": profile,
            "old_rescuers": old_survivors,
            "globalizer_count": len(globalizers),
            "globalizers": globalizers,
            "globalizer_cycle_types": tuple(cycle_type(p) for p in globalizers),
            "generated_group_order": len(generated_subgroup(globalizers, N)),
            "identity": IDENTITY in globalizers,
            "rows": rows,
            "outside_row": BASE_RESCUERS[0],
            "side_classes": classes,
        }
        records.append(record)
        score = (len(globalizers), -state.class_count())
        if minimum is None or score < minimum[0]:
            minimum = (score, record)

    minimum_count = min(record["globalizer_count"] for record in records)
    raw_checked = 0
    if raw_replay:
        for record in records:
            if record["globalizer_count"] != minimum_count:
                continue
            raw = tuple(
                p for p in ALL_S7
                if universal.maps_classes(record["side_classes"], p)
            )
            if set(raw) != set(record["globalizers"]):
                raise AssertionError("raw S7 replay disagrees")
            raw_checked += 1

    level_one, csp = universal.search_level_one(seed, representatives, vocabularies)
    if (level_one is not None) != bool(r1_dead):
        raise AssertionError("witness CSP disagrees with terminal classification")

    if r1_dead:
        taxonomy = "IV_GOLDILOCKS"
    elif old["identity"] or old["side_arrays_equal"]:
        taxonomy = "II_OVERMERGED"
    elif old["globalizer_count"] > len(OLD_RESCUERS):
        taxonomy = "III_REGENERATION_PRONE"
    else:
        taxonomy = "I_USELESS"

    return {
        "pair": pair,
        "taxonomy": taxonomy,
        "old": old,
        "witnesses": {
            str(index): witness_pairs(rescue)
            for index, rescue in enumerate(BASE_RESCUERS)
        },
        "witnesses_automatic_at_seed": {
            str(index): tuple(
                vertex for vertex, endpoints in enumerate(witness_pairs(rescue))
                if seed.connected(*endpoints)
            )
            for index, rescue in enumerate(BASE_RESCUERS)
        },
        "row_vocabularies": tuple({
            "raw": vocabulary["raw"],
            "compatible": vocabulary["compatible"],
            "distinct_effects": vocabulary["distinct_effects"],
        } for vocabulary in vocabularies),
        "csp": csp,
        "layers": layers,
        "terminal_count": len(records),
        "terminal_histogram": {
            str(key): count for key, count in sorted(histogram.items())
        },
        "old_rescuer_histogram": dict(sorted(old_rescue_histogram.items())),
        "r1_dead_terminals": r1_dead,
        "identity_terminals": identity,
        "minimum_globalizer_count": minimum_count,
        "maximum_permutations_killed": len(ALL_S7) - minimum_count,
        "minimum_record": minimum[1],
        "raw_s7_minimum_replays": raw_checked,
    }


def run(raw_replay=False):
    start = time.monotonic()
    action = a4_class_action()
    results = tuple(
        analyze_merge(pair, raw_replay=raw_replay)
        for pair in itertools.combinations(range(CLASS_COUNT), 2)
    )
    taxonomy = Counter(result["taxonomy"] for result in results)
    goldilocks = tuple(result["pair"] for result in results if result["taxonomy"] == "IV_GOLDILOCKS")
    minimum = min(result["minimum_globalizer_count"] for result in results)
    zero = sum(
        result["terminal_histogram"].get(str((classes, 0)), 0)
        for result in results for classes in range(1, 19)
    )
    return {
        "status": "ZERO_GLOBALIZER_FROZEN" if zero else "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "raw_merges": len(results),
        "canonical_orbits": len(action["pair_orbits"]),
        "a4_action": action,
        "taxonomy": dict(sorted(taxonomy.items())),
        "goldilocks_merges": goldilocks,
        "minimum_globalizer_count": minimum,
        "zero_globalizer_systems": zero,
        "merge_results": results,
        "elapsed_seconds": time.monotonic() - start,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "completeness": "all 15 raw merges; all 6! rows per deletion; two terminal DPs",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--raw-s7-replay", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        run(raw_replay=args.raw_s7_replay),
        indent=2 if args.pretty else None,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
