#!/usr/bin/env python3
"""Emit a complete exact certificate for the seven-class order-six system."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import is_isomorphic, same_deck
from local_gluing_search import (
    edge_class_arrays,
    edge_partition,
    instantiate,
    parent_permutation_conditions,
    separating_binary_assignment,
)


MAPS = (
    (0, 1, 2, 3, 5, 4),
    (0, 1, 3, 2, 4, 5),
    (0, 3, 2, 1, 4, 5),
    (0, 2, 1, 3, 4, 5),
    (5, 1, 2, 3, 4, 0),
    (4, 1, 2, 3, 0, 5),
)


def main() -> None:
    n = 6
    edges, roots, classes = edge_partition(n, MAPS)
    side_classes = edge_class_arrays(edges, roots, classes)
    conditions = parent_permutation_conditions(n, edges, roots, classes)
    exact_label_globalizers = [p for p, pairs in conditions if not pairs]
    prescribed_are_globalizers = [MAPS[i] in exact_label_globalizers for i in range(n)]
    separating = separating_binary_assignment(len(classes), conditions)
    deck_failures = parent_nonisomorphic = 0
    for mask in range(1 << len(classes)):
        values = tuple((mask >> bit) & 1 for bit in range(len(classes)))
        g, h = instantiate(n, edges, roots, classes, values)
        deck_failures += not same_deck(g, h)
        parent_nonisomorphic += not is_isomorphic(g, h)
    payload = {
        "n": n,
        "local_maps": MAPS,
        "edge_order": edges,
        "G_edge_classes": side_classes[0],
        "H_edge_classes": side_classes[1],
        "class_count": len(classes),
        "prescribed_maps_are_exact_label_globalizers": prescribed_are_globalizers,
        "exact_label_globalizers": exact_label_globalizers,
        "exact_label_globalizer_count": len(exact_label_globalizers),
        "separating_binary_assignment": separating,
        "binary_assignments_checked": 1 << len(classes),
        "deck_failures": deck_failures,
        "nonisomorphic_parent_assignments": parent_nonisomorphic,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
