#!/usr/bin/env python3
"""Exhaust local systems having one transposition on every deleted card."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from local_gluing_search import (
    edge_partition,
    parent_permutation_conditions,
    universal_edge_class_isomorphism,
)


def options(n: int, deleted: int, allow_identity: bool) -> tuple[tuple[int, ...], ...]:
    available = [v for v in range(n) if v != deleted]
    result = [tuple(range(n))] if allow_identity else []
    for u, v in itertools.combinations(available, 2):
        permutation = list(range(n))
        permutation[u], permutation[v] = permutation[v], permutation[u]
        result.append(tuple(permutation))
    return tuple(result)


def is_exact_globalizer(
    permutation: tuple[int, ...],
    n: int,
    edges,
    roots,
    classes,
) -> bool:
    slots = len(edges)
    position = {edge: i for i, edge in enumerate(edges)}
    return all(
        classes[roots[position[edge]]]
        == classes[
            roots[
                slots
                + position[tuple(sorted((permutation[edge[0]], permutation[edge[1]])))]
            ]
        ]
        for edge in edges
    )


def inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * len(permutation)
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


def relabel_system(maps, relabeling: tuple[int, ...]):
    """Simultaneously relabel the two parent copies by ``relabeling``."""

    n = len(maps)
    transformed = [[0] * n for _ in range(n)]
    for deleted, permutation in enumerate(maps):
        new_deleted = relabeling[deleted]
        for source in range(n):
            transformed[new_deleted][relabeling[source]] = relabeling[permutation[source]]
    return tuple(tuple(row) for row in transformed)


def canonical_system(maps):
    """Canonicalize under simultaneous relabeling and interchange of sides."""

    n = len(maps)
    inverse_system = tuple(inverse(permutation) for permutation in maps)
    return min(
        relabel_system(system, relabeling)
        for system in (maps, inverse_system)
        for relabeling in itertools.permutations(range(n))
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", type=int, default=6)
    parser.add_argument("--progress", type=int, default=100000)
    parser.add_argument("--representatives", type=int, default=30)
    parser.add_argument("--allow-identity", action="store_true")
    args = parser.parse_args()
    n = args.vertices
    if n != 6:
        raise SystemExit("this exact census is currently scoped and certified for n=6")
    local_options = tuple(options(n, deleted, args.allow_identity) for deleted in range(n))
    total = len(local_options[0]) ** n
    start = time.monotonic()
    class_histogram: Counter[int] = Counter()
    globalizer_histogram: Counter[int] = Counter()
    locally_nongluing = nonuniversal = 0
    representatives = []
    obstruction_orbits: Counter[tuple] = Counter()
    for count, maps in enumerate(itertools.product(*local_options), start=1):
        edges, roots, classes = edge_partition(n, maps)
        class_histogram[len(classes)] += 1
        identity = tuple(range(n))
        globalizer = (
            identity
            if is_exact_globalizer(identity, n, edges, roots, classes)
            else universal_edge_class_isomorphism(n, edges, roots, classes)
        )
        if globalizer is None:
            nonuniversal += 1
            print("ZERO_EXACT_LABEL_GLOBALIZER", repr(maps), flush=True)
            raise SystemExit(2)
        if all(not is_exact_globalizer(p, n, edges, roots, classes) for p in maps):
            locally_nongluing += 1
            conditions = parent_permutation_conditions(n, edges, roots, classes)
            globalizers = tuple(p for p, pairs in conditions if not pairs)
            globalizer_histogram[len(globalizers)] += 1
            obstruction_orbits[canonical_system(maps)] += 1
            if len(representatives) < args.representatives:
                representatives.append(
                    {
                        "index": count,
                        "maps": maps,
                        "classes": len(classes),
                        "globalizers": globalizers,
                    }
                )
        if args.progress and count % args.progress == 0:
            print(f"PROGRESS {count}/{total} elapsed={time.monotonic()-start:.1f}s", flush=True)
    payload = {
        "status": "EXHAUSTIVE_NO_ZERO_GLOBALIZER",
        "n": n,
        "domain": (
            "identity or one transposition on each deleted card"
            if args.allow_identity
            else "one transposition on each deleted card"
        ),
        "systems": total,
        "nonuniversal": nonuniversal,
        "locally_nongluing": locally_nongluing,
        "class_histogram": dict(sorted(class_histogram.items())),
        "globalizer_histogram_on_locally_nongluing": dict(sorted(globalizer_histogram.items())),
        "locally_nongluing_relabeling_inversion_orbits": len(obstruction_orbits),
        "locally_nongluing_orbit_multiplicities": sorted(obstruction_orbits.values()),
        "first_representatives": representatives,
        "elapsed_seconds": time.monotonic() - start,
    }
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
