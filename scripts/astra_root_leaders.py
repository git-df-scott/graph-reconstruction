#!/usr/bin/env python3
"""Proved symmetry representatives for a pair of three-root extensions.

S3 induces all six permutations of the three root-pair edge positions.
Thus each parent can have nondecreasing root-edge bits (000,001,011,111).
Exchanging G,H then orders their edge counts. Exactly ten root-type pairs
remain. These operations fix the core, preserve full-deck equality and
parent nonisomorphism, and do not prescribe any local card map.
"""
import itertools

from astra_overlap_strike import induced


def add_root_leaders(enc):
    assert enc.n - enc.d == 3
    pairs = tuple(itertools.combinations(range(enc.d, enc.n), 2))
    rows = [[enc.slot(side, u, v) for u, v in pairs] for side in (0, 1)]
    for a, b, c in rows:
        enc.add([-a, b])
        enc.add([-b, c])
    for a, b in zip(*rows):
        enc.add([-a, b])


def normalize_pair(pair):
    n = len(pair[0])
    d = n - 3
    pairs = tuple(itertools.combinations(range(d, n), 2))
    normalized = []
    for graph in pair:
        images = [induced(graph, tuple(range(d)) + order)
                  for order in itertools.permutations(range(d, n))]
        best = min(images, key=lambda g: (tuple((g[u] >> v) & 1 for u, v in pairs), g))
        normalized.append(best)
    return tuple(sorted(normalized, key=lambda g: (sum((g[u] >> v) & 1 for u, v in pairs), g)))
