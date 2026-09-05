#!/usr/bin/env python3
"""Independent VF2 enumeration of the complete two-root isomorphism universe.

Compare full sets of permutation bytes, not digests or counts alone.
No discovery, nauty, or campaign graph modules are imported.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import itertools
import json
from pathlib import Path
import time

import networkx as nx


def signature(g):
    d = dict(g.degree())
    return tuple(sorted((d[v], tuple(sorted(d[u] for u in g[v]))) for v in g))


def verify(folder):
    start = time.monotonic()
    record = json.loads((folder / 'core.json').read_text())
    graph = nx.Graph()
    graph.add_nodes_from(range(record['order']))
    graph.add_edges_from(record['edges'])
    d = len(graph)
    roots, n = (d, d + 1), d + 2
    with gzip.open(folder / 'parent_maps.bin.gz', 'rb') as fp:
        raw = fp.read()
    assert len(raw) % n == 0
    stored = {raw[i:i + n] for i in range(0, len(raw), n)}
    assert len(stored) * n == len(raw), 'duplicate maps in stored universe'
    actual, counts = set(), Counter()
    for k in range(3):
        buckets, graphs = defaultdict(list), {}
        for removed in itertools.combinations(range(d), k):
            g = graph.copy()
            g.remove_nodes_from(removed)
            graphs[removed] = g
            buckets[signature(g)].append(removed)
        for bucket in buckets.values():
            for left, right in itertools.product(bucket, repeat=2):
                for f in nx.algorithms.isomorphism.GraphMatcher(graphs[left], graphs[right]).isomorphisms_iter():
                    source = tuple(left) + roots
                    target = tuple(right) + roots
                    # Deliberately enumerate the whole small completion and
                    # test its condition, independently of discovery's injection formula.
                    for images in itertools.permutations(target):
                        if any(images[i] < d for i in range(k)):
                            continue
                        completed = dict(f)
                        completed.update(zip(source, images))
                        permutation = bytes(completed[u] for u in range(n))
                        assert permutation not in actual
                        actual.add(permutation)
                        counts[k] += 1
    assert actual == stored, ('permutation-universe mismatch', len(actual), len(stored))
    payload = {'status': 'INDEPENDENT_PARENT_MAP_UNIVERSE_PASS', 'map_count': len(actual), 'migration_counts': dict(counts),
               'comparison': 'full exact permutation sets', 'backend': 'NetworkX VF2', 'networkx_version': nx.__version__, 'seconds': time.monotonic() - start}
    (folder / 'independent_parent_maps.json').write_text(json.dumps(payload, indent=2) + '\n')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.folder), sort_keys=True))
