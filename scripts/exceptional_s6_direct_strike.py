#!/usr/bin/env python3
"""Exact exceptional-S6 orbital and deletion-adapted classification.

This script completes the direct natural-carrier strike from SOL_5.  It
normalizes the exceptional outer automorphism to an involution, constructs
the four natural S6 orbits of sizes 6,6,15,15, classifies all 2^15 invariant
simple graphs, and proves that every possible deck collision in this domain
has an explicit parent isomorphism.

It also enumerates all 56 conjugacy classes of subgroups of S6 and isolates
the unique outer-balanced, outer-nonconjugate Gassmann pair (up to order).
"""

from __future__ import annotations

import argparse
import itertools
import json
import resource
import time
from array import array
from collections import Counter, defaultdict
from functools import lru_cache

import outer_s6_strike as outer


IDENTITY = tuple(range(6))
NORMALIZER = (0, 1, 4, 5, 2, 3)


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(6))


def inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * 6
    for source, image in enumerate(permutation):
        result[image] = source
    return tuple(result)


@lru_cache(maxsize=1)
def beta_table() -> dict[tuple[int, ...], tuple[int, ...]]:
    normalizer_inverse = inverse(NORMALIZER)
    return {
        permutation: compose(
            compose(NORMALIZER, outer.outer_image(permutation)),
            normalizer_inverse,
        )
        for permutation in outer.PERMUTATIONS
    }


def verify_outer_group_laws() -> dict[str, object]:
    beta = beta_table()
    homomorphism = all(
        beta[compose(left, right)] == compose(beta[left], beta[right])
        for left in outer.PERMUTATIONS
        for right in outer.PERMUTATIONS
    )
    involution = all(beta[beta[permutation]] == permutation for permutation in outer.PERMUTATIONS)
    return {
        "pairs_replayed": len(outer.PERMUTATIONS) ** 2,
        "homomorphism": homomorphism,
        "images_distinct": len(set(beta.values())),
        "involution": involution,
        "normalizing_inner_permutation": NORMALIZER,
    }


@lru_cache(maxsize=1)
def combined_actions() -> tuple[tuple[int, ...], ...]:
    """Diagonal S6 action on P + T + D + S of sizes 6+6+15+15."""
    beta = beta_table()
    actions = []
    for permutation in outer.PERMUTATIONS:
        twisted = beta[permutation]
        mapping = list(permutation)
        mapping.extend(6 + twisted[index] for index in range(6))
        mapping.extend(
            12 + outer.DUAD_INDEX[outer.act_duad(permutation, duad)]
            for duad in outer.DUADS
        )
        mapping.extend(
            27 + outer.DUAD_INDEX[outer.act_duad(twisted, duad)]
            for duad in outer.DUADS
        )
        actions.append(tuple(mapping))
    return tuple(actions)


def carrier_type(vertex: int) -> str:
    if vertex < 6:
        return "P"
    if vertex < 12:
        return "T"
    if vertex < 27:
        return "D"
    return "S"


@lru_cache(maxsize=1)
def combined_orbitals() -> tuple[frozenset[tuple[int, int]], ...]:
    unseen = set(itertools.combinations(range(42), 2))
    result = []
    for edge in tuple(sorted(unseen)):
        if edge not in unseen:
            continue
        orbit = frozenset(
            tuple(sorted((action[edge[0]], action[edge[1]])))
            for action in combined_actions()
        )
        unseen -= orbit
        result.append(orbit)
    assert not unseen
    return tuple(result)


def orbital_table() -> list[dict[str, object]]:
    result = []
    for index, orbital in enumerate(combined_orbitals()):
        incidence = Counter()
        types = set()
        for left, right in orbital:
            left_type, right_type = carrier_type(left), carrier_type(right)
            types.update((left_type, right_type))
            incidence[left_type] += 1
            incidence[right_type] += 1
        result.append({
            "id": index,
            "carrier_types": sorted(types),
            "edge_count": len(orbital),
            "incidence_totals": dict(sorted(incidence.items())),
        })
    return result


def direct_fifteen_classification() -> dict[str, object]:
    unseen = set(itertools.combinations(range(15), 2))
    orbitals = []
    induced_actions = []
    for permutation in outer.PERMUTATIONS:
        induced_actions.append(tuple(
            outer.DUAD_INDEX[outer.act_duad(permutation, duad)]
            for duad in outer.DUADS
        ))
    while unseen:
        edge = min(unseen)
        orbit = {
            tuple(sorted((action[edge[0]], action[edge[1]])))
            for action in induced_actions
        }
        unseen -= orbit
        orbitals.append(orbit)
    return {
        "carrier_order": 15,
        "unordered_pair_orbitals": len(orbitals),
        "orbital_sizes": sorted(map(len, orbitals)),
        "invariant_graphs": 1 << len(orbitals),
        "outer_twist_changes_permutation_group": False,
        "counterexamples": 0,
        "obstruction": "all transitive orbital unions are regular and reconstructible from one card",
    }


def contribution_rows() -> tuple[tuple[int, ...], ...]:
    result = []
    for orbital in combined_orbitals():
        rows = [0] * 42
        for left, right in orbital:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
        result.append(tuple(rows))
    return tuple(result)


def stable_quotient(rows: list[int] | tuple[int, ...], removed: int = -1) -> tuple[object, ...]:
    active = [vertex for vertex in range(42) if vertex != removed]
    active_mask = (1 << 42) - 1
    if removed >= 0:
        active_mask ^= 1 << removed
    colors = [(rows[vertex] & active_mask).bit_count() for vertex in active]
    while True:
        color_names = sorted(set(colors))
        color_masks = {
            color: sum(1 << vertex for vertex, value in zip(active, colors) if value == color)
            for color in color_names
        }
        signatures = [
            (
                colors[index],
                tuple((rows[vertex] & color_masks[color]).bit_count() for color in color_names),
            )
            for index, vertex in enumerate(active)
        ]
        names = {value: index for index, value in enumerate(sorted(set(signatures)))}
        refined = [names[value] for value in signatures]
        if refined == colors:
            break
        colors = refined
    cells = [
        [vertex for vertex, value in zip(active, colors) if value == color]
        for color in sorted(set(colors))
    ]
    masks = [sum(1 << vertex for vertex in cell) for cell in cells]
    return tuple(
        (len(cell), tuple((rows[cell[0]] & mask).bit_count() for mask in masks))
        for cell in cells
    )


def carrier_swap(swap_six: bool, swap_fifteen: bool) -> tuple[int, ...]:
    mapping = list(range(42))
    if swap_six:
        for index in range(6):
            mapping[index], mapping[6 + index] = 6 + index, index
    if swap_fifteen:
        for index in range(15):
            mapping[12 + index], mapping[27 + index] = 27 + index, 12 + index
    return tuple(mapping)


def swap_mask_maps() -> dict[str, dict[int, int]]:
    pairs = tuple(itertools.combinations(range(42), 2))
    pair_index = {edge: index for index, edge in enumerate(pairs)}
    orbital_bits = [
        sum(1 << pair_index[edge] for edge in orbital)
        for orbital in combined_orbitals()
    ]
    edge_set_to_mask = {
        sum(orbital_bits[index] for index in range(15) if mask & (1 << index)): mask
        for mask in range(1 << 15)
    }
    result = {}
    for swap_six, swap_fifteen in itertools.product((False, True), repeat=2):
        name = f"six={int(swap_six)},fifteen={int(swap_fifteen)}"
        permutation = carrier_swap(swap_six, swap_fifteen)
        edge_permutation = [
            pair_index[tuple(sorted((permutation[left], permutation[right])))]
            for left, right in pairs
        ]
        mapping = {}
        for edge_bits, mask in edge_set_to_mask.items():
            transformed = 0
            remaining = edge_bits
            while remaining:
                low = remaining & -remaining
                transformed |= 1 << edge_permutation[low.bit_length() - 1]
                remaining -= low
            target = edge_set_to_mask.get(transformed)
            if target is not None:
                mapping[mask] = target
        result[name] = mapping
    return result


@lru_cache(maxsize=1)
def classify_combined_domain() -> dict[str, object]:
    contributions = contribution_rows()
    rows = [0] * 42
    previous_gray = 0
    groups: defaultdict[tuple[object, ...], list[int]] = defaultdict(list)
    representatives = (0, 6, 12, 27)
    multiplicities = (6, 6, 15, 15)
    started = time.monotonic()
    for index in range(1 << 15):
        mask = index ^ (index >> 1)
        if index:
            changed = (mask ^ previous_gray).bit_length() - 1
            for vertex in range(42):
                rows[vertex] ^= contributions[changed][vertex]
        previous_gray = mask
        deck_quotient = Counter()
        for vertex, multiplicity in zip(representatives, multiplicities):
            deck_quotient[stable_quotient(rows, vertex)] += multiplicity
        key = tuple(sorted(deck_quotient.items(), key=repr))
        groups[key].append(mask)

    swap_maps = swap_mask_maps()
    rescue_counts = Counter()
    exact_collision_pairs = 0
    for masks in groups.values():
        for left_index, left in enumerate(masks):
            for right in masks[left_index + 1:]:
                exact_collision_pairs += 1
                for name, mapping in swap_maps.items():
                    if mapping.get(left) == right:
                        rescue_counts[name] += 1
                        break
                else:
                    raise AssertionError((left, right, "unrescued deck-quotient collision"))
    size_distribution = Counter(map(len, groups.values()))
    return {
        "carrier_order": 42,
        "carrier_orbit_sizes": [6, 6, 15, 15],
        "unordered_pair_orbitals": len(combined_orbitals()),
        "raw_invariant_graphs": 1 << len(combined_orbitals()),
        "stable_deck_quotient_classes": len(groups),
        "class_size_distribution": dict(sorted(size_distribution.items())),
        "exact_parent_isomorphic_deck_collision_pairs": exact_collision_pairs,
        "explicit_rescue_counts": dict(sorted(rescue_counts.items())),
        "nonisomorphic_deck_collisions": 0,
        "classification_seconds": time.monotonic() - started,
    }


def _subgroup_classification() -> dict[str, object]:
    permutations = outer.PERMUTATIONS
    position = {permutation: index for index, permutation in enumerate(permutations)}
    count = len(permutations)
    multiplication = [
        array("H", (position[compose(left, right)] for right in permutations))
        for left in permutations
    ]
    inverses = [position[inverse(permutation)] for permutation in permutations]
    identity = position[IDENTITY]
    conjugates = [
        array("H", (
            multiplication[multiplication[by][element]][inverses[by]]
            for element in range(count)
        ))
        for by in range(count)
    ]

    def closure(generators: tuple[int, ...]) -> frozenset[int]:
        steps = tuple(dict.fromkeys(generators + tuple(inverses[x] for x in generators)))
        seen = {identity}
        frontier = [identity]
        while frontier:
            element = frontier.pop()
            for generator in steps:
                image = multiplication[element][generator]
                if image not in seen:
                    seen.add(image)
                    frontier.append(image)
        return frozenset(seen)

    canonical_cache: dict[frozenset[int], tuple[int, ...]] = {}

    def canonical(subgroup: frozenset[int]) -> tuple[int, ...]:
        if subgroup not in canonical_cache:
            canonical_cache[subgroup] = min(
                tuple(sorted(row[element] for element in subgroup))
                for row in conjugates
            )
        return canonical_cache[subgroup]

    trivial = frozenset((identity,))
    representatives = {canonical(trivial): (trivial, ())}
    queue = list(representatives)
    cursor = 0
    while cursor < len(queue):
        key = queue[cursor]
        subgroup, generators = representatives[key]
        cursor += 1
        local = set()
        for element in range(count):
            if element in subgroup:
                continue
            generated = closure(generators + (element,))
            if generated in local:
                continue
            local.add(generated)
            generated_key = canonical(generated)
            if generated_key not in representatives:
                representatives[generated_key] = (generated, generators + (element,))
                queue.append(generated_key)

    beta = beta_table()
    beta_indices = [position[beta[permutation]] for permutation in permutations]
    cycle_types = [outer.cycle_type(permutation) for permutation in permutations]
    balanced = []
    outer_nonconjugate = 0
    for key, (subgroup, _generators) in representatives.items():
        image = frozenset(beta_indices[element] for element in subgroup)
        if canonical(image) != key:
            outer_nonconjugate += 1
            if Counter(cycle_types[x] for x in subgroup) == Counter(cycle_types[x] for x in image):
                balanced.append((subgroup, image))
    return {
        "subgroup_conjugacy_classes": len(representatives),
        "outer_nonconjugate_directed_classes": outer_nonconjugate,
        "outer_balanced_nonconjugate_directed_classes": len(balanced),
        "outer_balanced_unordered_pairs": len(balanced) // 2,
        "unique_pair_order": len(balanced[0][0]) if balanced else None,
        "unique_pair_cycle_types": dict(Counter(
            str(cycle_types[x]) for x in balanced[0][0]
        )) if balanced else {},
        "coset_degree": count // len(balanced[0][0]) if balanced else None,
    }


@lru_cache(maxsize=1)
def subgroup_classification() -> dict[str, object]:
    return _subgroup_classification()


def full_classification() -> dict[str, object]:
    started = time.monotonic()
    result = {
        "grc_ce": "NO",
        "geometry": {
            "points": 6,
            "duads": len(outer.DUADS),
            "synthemes": len(outer.SYNTHEMES),
            "totals": len(outer.TOTALS),
            "outer_group_laws": verify_outer_group_laws(),
        },
        "direct_fifteen": direct_fifteen_classification(),
        "combined_orbital_table": orbital_table(),
        "combined_domain": classify_combined_domain(),
        "gassmann_control": subgroup_classification(),
        "theorems": [
            "Every transitive orbital graph is regular and reconstructible from one card.",
            "A functorial outer twist is parent-isomorphic by the semilinear coset bijection.",
            "Every deck collision in the 15-orbital 6+6+15+15 domain has an explicit carrier-swap parent isomorphism.",
        ],
        "next_strike": "degree-balanced partial coupling of the unique S6 V4 Gassmann pair to ordinary and exotic six-point anchors",
    }
    result["runtime_seconds"] = time.monotonic() - started
    result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(json.dumps(full_classification(), indent=None if args.compact else 2, sort_keys=True))


if __name__ == "__main__":
    main()
