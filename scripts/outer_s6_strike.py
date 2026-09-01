#!/usr/bin/env python3
"""Construct and certify the exceptional outer action of S6.

The 15 duads are the pairs of six points.  A syntheme is a partition into
three duads.  A total is a partition of all 15 duads into five synthemes.
There are six totals, and the action of S6 on them is the exceptional outer
six-point action.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter


POINTS = tuple(range(6))
PERMUTATIONS = tuple(itertools.permutations(POINTS))
DUADS = tuple(itertools.combinations(POINTS, 2))
DUAD_INDEX = {duad: index for index, duad in enumerate(DUADS)}


def perfect_matchings(vertices: tuple[int, ...]) -> tuple[tuple[tuple[int, int], ...], ...]:
    if not vertices:
        return ((),)
    first = vertices[0]
    result = []
    for index in range(1, len(vertices)):
        second = vertices[index]
        rest = vertices[1:index] + vertices[index + 1:]
        for matching in perfect_matchings(rest):
            result.append(tuple(sorted(((first, second),) + matching)))
    return tuple(sorted(set(result)))


SYNTHEMES = perfect_matchings(POINTS)
SYNTHEME_MASKS = tuple(sum(1 << DUAD_INDEX[duad] for duad in syntheme) for syntheme in SYNTHEMES)


def totals() -> tuple[tuple[int, ...], ...]:
    target = (1 << len(DUADS)) - 1
    result = []
    for choice in itertools.combinations(range(len(SYNTHEMES)), 5):
        mask = 0
        for index in choice:
            if mask & SYNTHEME_MASKS[index]:
                break
            mask |= SYNTHEME_MASKS[index]
        else:
            if mask == target:
                result.append(choice)
    return tuple(result)


TOTALS = totals()
TOTAL_INDEX = {total: index for index, total in enumerate(TOTALS)}
SYNTHEME_INDEX = {syntheme: index for index, syntheme in enumerate(SYNTHEMES)}


def act_duad(permutation: tuple[int, ...], duad: tuple[int, int]) -> tuple[int, int]:
    return tuple(sorted((permutation[duad[0]], permutation[duad[1]])))


def act_syntheme(permutation: tuple[int, ...], index: int) -> int:
    image = tuple(sorted(act_duad(permutation, duad) for duad in SYNTHEMES[index]))
    return SYNTHEME_INDEX[image]


def outer_image(permutation: tuple[int, ...]) -> tuple[int, ...]:
    image = []
    for total in TOTALS:
        transformed = tuple(sorted(act_syntheme(permutation, index) for index in total))
        image.append(TOTAL_INDEX[transformed])
    return tuple(image)


def cycle_type(permutation: tuple[int, ...]) -> tuple[int, ...]:
    seen = set()
    lengths = []
    for point in POINTS:
        if point in seen:
            continue
        length = 0
        current = point
        while current not in seen:
            seen.add(current)
            length += 1
            current = permutation[current]
        lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def subgroup_orbits(subgroup: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    unseen = set(POINTS)
    sizes = []
    while unseen:
        point = min(unseen)
        orbit = {permutation[point] for permutation in subgroup}
        unseen -= orbit
        sizes.append(len(orbit))
    return tuple(sorted(sizes))


def classification() -> dict[str, object]:
    images = {permutation: outer_image(permutation) for permutation in PERMUTATIONS}
    class_map: dict[tuple[int, ...], Counter[tuple[int, ...]]] = {}
    for permutation, image in images.items():
        class_map.setdefault(cycle_type(permutation), Counter())[cycle_type(image)] += 1
    ordinary = tuple(permutation for permutation in PERMUTATIONS if permutation[0] == 0)
    exotic = tuple(permutation for permutation in PERMUTATIONS if images[permutation][0] == 0)
    intersections = Counter()
    for point in POINTS:
        point_stabilizer = {p for p in PERMUTATIONS if p[point] == point}
        for total in POINTS:
            total_stabilizer = {p for p in PERMUTATIONS if images[p][total] == total}
            intersections[len(point_stabilizer & total_stabilizer)] += 1
    return {
        "duads": len(DUADS),
        "synthemes": len(SYNTHEMES),
        "totals": len(TOTALS),
        "outer_images_distinct": len(set(images.values())),
        "cycle_class_map": {
            str(source): {str(target): count for target, count in targets.items()}
            for source, targets in sorted(class_map.items())
        },
        "ordinary_S5_order": len(ordinary),
        "exotic_S5_order": len(exotic),
        "ordinary_S5_orbits_on_points": subgroup_orbits(ordinary),
        "exotic_S5_orbits_on_points": subgroup_orbits(exotic),
        "point_total_stabilizer_intersections": dict(sorted(intersections.items())),
        "nonconjugacy_certificate": "ordinary S5 has point orbits 1+5; exotic S5 is transitive on six points",
    }


if __name__ == "__main__":
    print(json.dumps(classification(), indent=2, sort_keys=True))
