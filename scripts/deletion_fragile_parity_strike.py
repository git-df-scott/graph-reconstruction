#!/usr/bin/env python3
"""Exact tests for a deletion-fragile CFI parity lock.

The local code C is a subset of F_2^d.  An odd cube isometry is a
coordinate permutation followed by translation by an odd vector.  It is a
punctured odd symmetry at c when it maps C-{c} onto C-{d} for some d in C,
despite no odd isometry stabilizing C itself.

This is a structured code search, not graph enumeration.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter


def coordinate_map(dimension: int, permutation: tuple[int, ...]) -> tuple[int, ...]:
    image = []
    for vector in range(1 << dimension):
        value = 0
        for coordinate in range(dimension):
            value |= ((vector >> coordinate) & 1) << permutation[coordinate]
        image.append(value)
    return tuple(image)


def odd_cube_isometries(dimension: int) -> tuple[tuple[int, ...], ...]:
    result = []
    for permutation in itertools.permutations(range(dimension)):
        linear = coordinate_map(dimension, permutation)
        for translation in range(1 << dimension):
            if translation.bit_count() & 1:
                result.append(tuple(value ^ translation for value in linear))
    return tuple(result)


def image_mask(mask: int, mapping: tuple[int, ...]) -> int:
    result = 0
    while mask:
        low = mask & -mask
        result |= 1 << mapping[low.bit_length() - 1]
        mask -= low
    return result


def punctured_sources(mask: int, mappings: tuple[tuple[int, ...], ...]) -> tuple[set[int], bool]:
    """Return released source words and whether an intact odd symmetry exists."""
    words = tuple(index for index in range(len(mappings[0])) if mask & (1 << index))
    sources: set[int] = set()
    for mapping in mappings:
        transformed = image_mask(mask, mapping)
        difference = mask ^ transformed
        if difference == 0:
            return set(), True
        if difference.bit_count() != 2:
            continue
        inside = difference & mask
        outside = difference & transformed
        if not inside or not outside:
            continue
        outside_word = outside.bit_length() - 1
        source = next((word for word in words if mapping[word] == outside_word), None)
        if source is not None:
            sources.add(source)
    return sources, False


def classify_dimension(dimension: int) -> dict[str, object]:
    mappings = odd_cube_isometries(dimension)
    universe = 1 << dimension
    complete = 0
    by_size: Counter[int] = Counter()
    intact_odd_symmetric = 0
    for mask in range(1, (1 << universe) - 1):
        if mask.bit_count() < 2:
            continue
        sources, intact = punctured_sources(mask, mappings)
        if intact:
            intact_odd_symmetric += 1
            continue
        if len(sources) == mask.bit_count():
            complete += 1
            by_size[mask.bit_count()] += 1
    return {
        "dimension": dimension,
        "subsets_checked": (1 << universe) - 2 - universe,
        "odd_cube_isometries": len(mappings),
        "intact_odd_symmetric": intact_odd_symmetric,
        "nontrivial_complete_release_codes": complete,
        "complete_release_codes_by_size": dict(sorted(by_size.items())),
    }


def translation_release_theorem() -> dict[str, object]:
    return {
        "statement": "Every full odd-translation release code is a singleton.",
        "proof_kernel": [
            "A witness translation has exactly one cut pair, incident with its deleted codeword.",
            "Two witness cut pairs lie in a four-cycle and must share their outside endpoint.",
            "Thus every codeword has parity opposite one common outside endpoint.",
            "An odd witness pairs every remaining codeword across parity, so none can remain.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-dimension", type=int, default=4)
    args = parser.parse_args()
    if not 2 <= args.max_dimension <= 4:
        raise SystemExit("the exhaustive implementation is certified for dimensions 2 through 4")
    result = {
        "translation_obstruction": translation_release_theorem(),
        "cube_isometry_classification": [
            classify_dimension(dimension)
            for dimension in range(2, args.max_dimension + 1)
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
