#!/usr/bin/env python3
"""Independent symbolic verification of frozen 15-bit card-map certificates.

No discovery module or canonicalizer is imported. Equality of affine Boolean
edge expressions verifies every one of the 2**15 assignments at once.
This verifies the built-in card equality, not the negative full-deck search.
"""
import argparse
import itertools
import json
from pathlib import Path


def verify(record):
    base = record['base']
    n = len(base[0])
    assert n == len(base[1]) == 22
    assert len(record['variables']) == 15
    edges = []
    for rows in base:
        assert all(not (rows[u] >> u & 1) for u in range(n))
        assert all((rows[u] >> v & 1) == (rows[v] >> u & 1)
                   for u in range(n) for v in range(n))
        edges.append({(u, v): rows[u] >> v & 1
                      for u, v in itertools.combinations(range(n), 2)})
    for bit, changes in enumerate(record['variables'], 1):
        for side, u, v in changes:
            edges[side][tuple(sorted((u, v)))] ^= 1 << bit
    mapping = dict(record['card_map'])
    assert set(mapping) == set(range(n)) - {record['u']}
    assert set(mapping.values()) == set(range(n)) - {record['v']}
    for u, v in itertools.combinations(sorted(mapping), 2):
        assert edges[0][u, v] == edges[1][tuple(sorted((mapping[u], mapping[v])))], (u, v)
    return 210


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    paths = sorted(args.folder.glob('template_*/template.json'))
    assert paths
    comparisons = sum(verify(json.loads(p.read_text())) for p in paths)
    print(json.dumps({'status': 'PASS', 'templates': len(paths),
                      'symbolic_card_edge_equalities': comparisons,
                      'assignments_per_template': 32768,
                      'scope': 'single-card identity only; not independent negative search verification'}, indent=2))


if __name__ == '__main__':
    main()
