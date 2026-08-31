#!/usr/bin/env python3
"""Exact row-vocabulary/CSP strike against the universal order-seven rescuer."""

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

from incidence_join_strike import (
    BASE_RESCUERS,
    EDGES,
    EDGE_POSITION,
    IDENTITY,
    N,
    OLD_N,
    OLD_PRIMITIVE,
    exact_globalizers,
    maps_classes,
)
from local_gluing_search import (
    edge_class_arrays,
    edge_partition,
    instantiate,
    parent_permutation_conditions,
    separating_binary_assignment,
    validate_local_maps,
    verify_local_maps,
)
from grc import is_isomorphic, same_deck


SLOTS = len(EDGES)
R1 = BASE_RESCUERS[1]
OUTSIDE_ROW = BASE_RESCUERS[0]
OLD_EDGES = tuple((u, v) for u in range(OLD_N) for v in range(u + 1, OLD_N))


class Partition:
    """Small immutable union-find state represented by canonical class labels."""

    def __init__(self, labels: tuple[int, ...]):
        self.labels = labels

    @classmethod
    def discrete(cls):
        return cls(tuple(range(2 * SLOTS)))

    def add_pairs(self, pairs: tuple[tuple[int, int], ...]):
        parent = list(range(2 * SLOTS))

        def find(item: int) -> int:
            while parent[item] != item:
                parent[item] = parent[parent[item]]
                item = parent[item]
            return item

        def union(left: int, right: int) -> None:
            left, right = find(left), find(right)
            if left != right:
                parent[right] = left

        first: dict[int, int] = {}
        for slot, label in enumerate(self.labels):
            if label in first:
                union(first[label], slot)
            else:
                first[label] = slot
        for left, right in pairs:
            union(left, right)
        names: dict[int, int] = {}
        labels = []
        for slot in range(2 * SLOTS):
            root = find(slot)
            if root not in names:
                names[root] = len(names)
            labels.append(names[root])
        return Partition(tuple(labels))

    def connected(self, left: int, right: int) -> bool:
        return self.labels[left] == self.labels[right]

    def side_classes(self):
        return self.labels[:SLOTS], self.labels[SLOTS:]

    def class_count(self) -> int:
        return len(set(self.labels))


def slot(side: int, edge: tuple[int, int]) -> int:
    return side * SLOTS + EDGE_POSITION[tuple(sorted(edge))]


def old_seed() -> tuple[Partition, tuple[int, ...]]:
    """Embed the certified six-class old partition, leaving cross slots free."""

    old_edges, old_roots, old_index = edge_partition(OLD_N, OLD_PRIMITIVE)
    old_arrays = edge_class_arrays(old_edges, old_roots, old_index)
    pairs = []
    representatives: dict[int, int] = {}
    for side in range(2):
        for position, edge in enumerate(old_edges):
            old_class = old_arrays[side][position]
            current = slot(side, edge)
            if old_class in representatives:
                pairs.append((representatives[old_class], current))
            else:
                representatives[old_class] = current
    return Partition.discrete().add_pairs(tuple(pairs)), tuple(
        representatives[index] for index in sorted(representatives)
    )


def row_pairs(deleted: int, permutation: tuple[int, ...]):
    pairs = []
    for edge in EDGES:
        if deleted in edge:
            continue
        image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
        pairs.append((slot(0, edge), slot(1, image)))
    return tuple(pairs)


def old_classes_distinct(state: Partition, representatives: tuple[int, ...]) -> bool:
    return len({state.labels[item] for item in representatives}) == len(representatives)


def row_vocabulary(deleted: int, seed: Partition, representatives: tuple[int, ...]):
    raw = compatible = 0
    effects: dict[tuple[int, ...], tuple[int, ...]] = {}
    witness_direct = Counter()
    vertices = tuple(vertex for vertex in range(N) if vertex != deleted)
    for images in itertools.permutations(vertices):
        raw += 1
        permutation = list(range(N))
        for source, image in zip(vertices, images):
            permutation[source] = image
        row = tuple(permutation)
        validate_local_maps(N, tuple(
            row if index == deleted else IDENTITY for index in range(N)
        ))
        state = seed.add_pairs(row_pairs(deleted, row))
        if not old_classes_distinct(state, representatives):
            continue
        compatible += 1
        effects.setdefault(state.labels, row)
        for vertex in range(OLD_N):
            target = (slot(0, (OLD_N, vertex)), slot(1, (OLD_N, R1[vertex])))
            if state.connected(*target):
                witness_direct[vertex] += 1
    return {
        "raw": raw,
        "compatible": compatible,
        "effects": tuple(effects.values()),
        "distinct_effects": len(effects),
        "direct_witness_repairs": dict(sorted(witness_direct.items())),
    }


def r1_witness_pairs():
    return tuple(
        (slot(0, (OLD_N, vertex)), slot(1, (OLD_N, R1[vertex])))
        for vertex in range(OLD_N)
    )


def search_level_one(seed, representatives, vocabularies):
    """Find the first complete family keeping one r1 witness disconnected."""

    nodes = pruned_old = pruned_witness = 0
    witnesses = r1_witness_pairs()
    order = tuple(sorted(range(OLD_N), key=lambda i: len(vocabularies[i]["effects"])))

    for witness_index, forbidden in enumerate(witnesses):
        chosen: dict[int, tuple[int, ...]] = {}

        def dfs(depth: int, state: Partition):
            nonlocal nodes, pruned_old, pruned_witness
            nodes += 1
            if state.connected(*forbidden):
                pruned_witness += 1
                return None
            if depth == len(order):
                rows = tuple(chosen[index] for index in range(OLD_N)) + (OUTSIDE_ROW,)
                validate_local_maps(N, rows)
                return rows, state, witness_index
            deleted = order[depth]
            for row in vocabularies[deleted]["effects"]:
                next_state = state.add_pairs(row_pairs(deleted, row))
                if not old_classes_distinct(next_state, representatives):
                    pruned_old += 1
                    continue
                if next_state.connected(*forbidden):
                    pruned_witness += 1
                    continue
                chosen[deleted] = row
                answer = dfs(depth + 1, next_state)
                if answer is not None:
                    return answer
            chosen.pop(deleted, None)
            return None

        answer = dfs(0, seed)
        if answer is not None:
            return answer, {
                "nodes": nodes,
                "pruned_old_class_merges": pruned_old,
                "pruned_witness_repairs": pruned_witness,
                "variable_order": order,
            }
    return None, {
        "nodes": nodes,
        "pruned_old_class_merges": pruned_old,
        "pruned_witness_repairs": pruned_witness,
        "variable_order": order,
    }


def blocks_from_labels(labels: tuple[int, ...]) -> tuple[int, ...]:
    """Independent partition encoding used by the hostile DP verifier."""

    blocks: dict[int, int] = {}
    for item, label in enumerate(labels):
        blocks[label] = blocks.get(label, 0) | (1 << item)
    return tuple(sorted(blocks.values(), key=lambda block: (block & -block).bit_length()))


def independent_add_pairs(
    blocks: tuple[int, ...], pairs: tuple[tuple[int, int], ...]
) -> tuple[int, ...]:
    """Merge bit-set blocks without using the discovery union-find logic."""

    current = list(blocks)
    for left, right in pairs:
        left_bit, right_bit = 1 << left, 1 << right
        left_index = next(i for i, block in enumerate(current) if block & left_bit)
        right_index = next(i for i, block in enumerate(current) if block & right_bit)
        if left_index == right_index:
            continue
        merged = current[left_index] | current[right_index]
        for index in sorted((left_index, right_index), reverse=True):
            current.pop(index)
        current.append(merged)
    return tuple(sorted(current, key=lambda block: (block & -block).bit_length()))


def independent_old_classes_distinct(
    blocks: tuple[int, ...], representatives: tuple[int, ...]
) -> bool:
    owners = []
    for representative in representatives:
        owners.append(next(i for i, block in enumerate(blocks) if block & (1 << representative)))
    return len(set(owners)) == len(owners)


def labels_from_blocks(blocks: tuple[int, ...]) -> tuple[int, ...]:
    labels = [-1] * (2 * SLOTS)
    for label, block in enumerate(blocks):
        for item in range(2 * SLOTS):
            if block & (1 << item):
                labels[item] = label
    if any(label < 0 for label in labels):
        raise AssertionError("incomplete independent partition")
    return tuple(labels)


def independent_row_vocabularies(seed: Partition, representatives: tuple[int, ...]):
    seed_blocks = blocks_from_labels(seed.labels)
    result = []
    for deleted in range(OLD_N):
        compatible = 0
        effects: dict[tuple[int, ...], tuple[int, ...]] = {}
        vertices = tuple(vertex for vertex in range(N) if vertex != deleted)
        for images in itertools.permutations(vertices):
            row = list(range(N))
            for source, image in zip(vertices, images):
                row[source] = image
            row = tuple(row)
            blocks = independent_add_pairs(seed_blocks, row_pairs(deleted, row))
            if not independent_old_classes_distinct(blocks, representatives):
                continue
            compatible += 1
            effects.setdefault(blocks, row)
        result.append({
            "raw": 720,
            "compatible": compatible,
            "effects": tuple(effects.values()),
            "distinct_effects": len(effects),
        })
    return tuple(result)


def independent_terminal_dp(seed, representatives, vocabularies, row_subset=tuple(range(OLD_N))):
    states = {blocks_from_labels(seed.labels)}
    layer_counts = [len(states)]
    for deleted in row_subset:
        next_states = set()
        for blocks in states:
            for row in vocabularies[deleted]["effects"]:
                merged = independent_add_pairs(blocks, row_pairs(deleted, row))
                if independent_old_classes_distinct(merged, representatives):
                    next_states.add(merged)
        states = next_states
        layer_counts.append(len(states))
    return states, tuple(layer_counts)


def minimal_forcing_cores(seed, representatives, vocabularies):
    witnesses = r1_witness_pairs()
    data = {}
    for size in range(OLD_N + 1):
        for subset in itertools.combinations(range(OLD_N), size):
            states, _layers = independent_terminal_dp(
                seed, representatives, vocabularies, subset
            )
            forced = tuple(
                vertex for vertex, (left, right) in enumerate(witnesses)
                if states and all(
                    any(block & (1 << left) and block & (1 << right) for block in state)
                    for state in states
                )
            )
            data[subset] = (len(states), forced)
    cores = []
    for subset, (state_count, forced) in data.items():
        if len(forced) != OLD_N:
            continue
        if any(
            set(smaller) < set(subset) and len(data[smaller][1]) == OLD_N
            for smaller in data
        ):
            continue
        cores.append((subset, state_count))
    return tuple(cores)


def analyze_system(rows, state, killed_witness):
    classes = state.side_classes()
    globalizers = exact_globalizers(classes)
    old_survivors = tuple(p for p in BASE_RESCUERS if maps_classes(classes, p))
    profile = Counter(state.labels)
    return {
        "rows": rows,
        "killed_r1_witness_vertex": killed_witness,
        "class_count": state.class_count(),
        "class_profile": tuple(sorted(profile.values(), reverse=True)),
        "side_classes": classes,
        "r1_survives": maps_classes(classes, R1),
        "old_rescuers": old_survivors,
        "globalizers": globalizers,
        "globalizer_count": len(globalizers),
    }


def binary_replay(rows, state):
    """Run only after a zero-globalizer system is reached."""

    roots = state.labels
    class_names = sorted(set(roots))
    class_index = {name: index for index, name in enumerate(class_names)}
    conditions = parent_permutation_conditions(N, EDGES, roots, class_index)
    assignment = separating_binary_assignment(len(class_names), conditions)
    if assignment is None:
        return {"assignment": None}
    g, h = instantiate(N, EDGES, roots, class_index, assignment)
    return {
        "assignment": assignment,
        "G_graph6": g.to_graph6(),
        "H_graph6": h.to_graph6(),
        "local_maps": verify_local_maps(g, h, rows),
        "same_deck": same_deck(g, h),
        "parents_isomorphic": is_isomorphic(g, h),
    }


def run(raw_s7_replay: bool = False):
    start = time.monotonic()
    seed, representatives = old_seed()
    vocabularies = tuple(
        row_vocabulary(deleted, seed, representatives) for deleted in range(OLD_N)
    )
    answer, csp = search_level_one(seed, representatives, vocabularies)
    independent_vocabularies = independent_row_vocabularies(seed, representatives)
    for discovery, verification in zip(vocabularies, independent_vocabularies):
        if (
            discovery["raw"], discovery["compatible"], discovery["distinct_effects"]
        ) != (
            verification["raw"], verification["compatible"], verification["distinct_effects"]
        ):
            raise AssertionError("independent row vocabulary disagrees")
    terminal_blocks, layer_counts = independent_terminal_dp(
        seed, representatives, independent_vocabularies
    )
    terminal_states = tuple(Partition(labels_from_blocks(blocks)) for blocks in terminal_blocks)
    terminal_summary = Counter()
    terminal_old_rescuers = Counter()
    for terminal in terminal_states:
        globalizers = exact_globalizers(terminal.side_classes())
        old_survivors = sum(
            maps_classes(terminal.side_classes(), rescue) for rescue in BASE_RESCUERS
        )
        terminal_summary[(terminal.class_count(), len(globalizers))] += 1
        terminal_old_rescuers[old_survivors] += 1
    independent_level_one_sat = any(
        not maps_classes(terminal.side_classes(), R1) for terminal in terminal_states
    )
    if independent_level_one_sat != (answer is not None):
        raise AssertionError("independent DP disagrees with discovery CSP")
    result = None
    binary = None
    raw_checked = False
    if answer is not None:
        rows, state, killed_witness = answer
        result = analyze_system(rows, state, killed_witness)
        if raw_s7_replay:
            raw = tuple(
                p for p in itertools.permutations(range(N))
                if maps_classes(state.side_classes(), p)
            )
            if set(raw) != set(result["globalizers"]):
                raise AssertionError("raw S7 replay disagrees")
            raw_checked = True
        if result["globalizer_count"] == 0:
            binary = binary_replay(rows, state)
    elif raw_s7_replay:
        for terminal in terminal_states:
            backtracking = exact_globalizers(terminal.side_classes())
            raw = tuple(
                p for p in itertools.permutations(range(N))
                if maps_classes(terminal.side_classes(), p)
            )
            if set(raw) != set(backtracking):
                raise AssertionError("raw S7 terminal replay disagrees")
        raw_checked = True
    return {
        "status": "LEVEL_1_SAT" if answer is not None else "LEVEL_1_UNSAT",
        "old_class_count": len(representatives),
        "seed_class_count": seed.class_count(),
        "r1": R1,
        "r1_minimal_witness_vertices": tuple(range(OLD_N)),
        "row_vocabularies": tuple({
            key: value for key, value in vocabulary.items() if key != "effects"
        } for vocabulary in vocabularies),
        "csp": csp,
        "independent_dp_layer_counts": layer_counts,
        "independent_terminal_states": len(terminal_states),
        "terminal_class_globalizer_histogram": {
            str(key): count for key, count in sorted(terminal_summary.items())
        },
        "terminal_old_rescuer_count_histogram": dict(sorted(terminal_old_rescuers.items())),
        "minimal_unsat_row_cores": minimal_forcing_cores(
            seed, representatives, independent_vocabularies
        ),
        "first_system": result,
        "binary_replay": binary,
        "raw_s7_replay": raw_checked,
        "elapsed_seconds": time.monotonic() - start,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def main():
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
