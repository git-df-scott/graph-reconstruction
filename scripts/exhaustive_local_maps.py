#!/usr/bin/env python3
"""Exhaust every prescribed local-bijection system at very small order."""

from __future__ import annotations

import argparse
import itertools
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from local_gluing_search import edge_partition, universal_edge_class_isomorphism


def local_options(n: int, deleted: int):
    domain = [v for v in range(n) if v != deleted]
    for image in itertools.permutations(domain):
        permutation = list(range(n))
        for source, target in zip(domain, image):
            permutation[source] = target
        yield tuple(permutation)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", type=int, required=True)
    parser.add_argument("--progress", type=int, default=500000)
    args = parser.parse_args()
    n = args.vertices
    if not 3 <= n <= 5:
        raise SystemExit("exact product census is intentionally capped at n=5")
    options = [tuple(local_options(n, deleted)) for deleted in range(n)]
    total = len(options[0]) ** n
    histogram: Counter[int] = Counter()
    start = time.monotonic()
    for count, maps in enumerate(itertools.product(*options), start=1):
        edges, roots, classes = edge_partition(n, maps)
        histogram[len(classes)] += 1
        if universal_edge_class_isomorphism(n, edges, roots, classes) is None:
            print(f"NONUNIVERSAL_LOCAL_SYSTEM n={n} index={count} classes={len(classes)}")
            print(repr(maps))
            raise SystemExit(2)
        if args.progress and count % args.progress == 0:
            elapsed = time.monotonic() - start
            print(f"PROGRESS {count}/{total} elapsed={elapsed:.1f}s", flush=True)
    elapsed = time.monotonic() - start
    print(
        f"EXHAUSTIVE_DONE n={n} systems={total} nonuniversal=0 "
        f"class_histogram={dict(sorted(histogram.items()))} elapsed={elapsed:.1f}s"
    )


if __name__ == "__main__":
    main()
