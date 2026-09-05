#!/usr/bin/env python3
"""Independent complete VF2 replay of three-root parent maps.

No nauty, discovery, native blocker, or campaign graph modules are imported.
Comparison sorts full fixed-width permutation records; hashes are not used.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import itertools
import json
from pathlib import Path
import time

import networkx as nx
import numpy as np


def signature(graph):
    degree = dict(graph.degree())
    return tuple(sorted((degree[v], tuple(sorted(degree[u] for u in graph[v]))) for v in graph))


def verify(folder):
    started = time.monotonic()
    record = json.loads((folder / 'core.json').read_text())
    graph = nx.Graph()
    graph.add_nodes_from(range(record['order']))
    graph.add_edges_from(record['edges'])
    d, n = len(graph), len(graph) + 3
    roots = tuple(range(d, n))
    if (folder / 'parent_maps.bin.gz').exists():
        with gzip.open(folder / 'parent_maps.bin.gz', 'rb') as fp:
            stored_raw = bytearray(fp.read())
    else:
        from astra_archive_run import chunks
        stored_raw = bytearray()
        for block in chunks(folder, 'parent_maps.bin'):
            stored_raw.extend(block)
    assert len(stored_raw) % n == 0
    stored = np.frombuffer(stored_raw, dtype=f'V{n}')
    stored.sort()
    assert not np.any(stored[1:] == stored[:-1]), 'duplicate discovery maps'
    actual_raw, counts = bytearray(), Counter()
    for k in range(4):
        buckets, graphs = defaultdict(list), {}
        for removed in itertools.combinations(range(d), k):
            g = graph.copy()
            g.remove_nodes_from(removed)
            graphs[removed] = g
            buckets[signature(g)].append(removed)
        # Enumerate all (k+3)! completions, retaining exactly those sending
        # each omitted source core vertex into a target root.
        completions = [p for p in itertools.permutations(range(k + 3))
                       if all(p[i] >= k for i in range(k))]
        for bucket in buckets.values():
            for left, right in itertools.product(bucket, repeat=2):
                source, target = tuple(left) + roots, tuple(right) + roots
                for f in nx.algorithms.isomorphism.GraphMatcher(graphs[left], graphs[right]).isomorphisms_iter():
                    partial = bytearray(n)
                    for u, v in f.items():
                        partial[u] = v
                    for completion in completions:
                        for i, u in enumerate(source):
                            partial[u] = target[completion[i]]
                        actual_raw.extend(partial)
                        counts[k] += 1
        print('INDEPENDENT_MAP_LAYER', k, counts[k], round(time.monotonic() - started, 3), flush=True)
    actual = np.frombuffer(actual_raw, dtype=f'V{n}')
    actual.sort()
    assert not np.any(actual[1:] == actual[:-1]), 'duplicate independent maps'
    assert np.array_equal(actual, stored), ('complete map sets differ', len(actual), len(stored))
    payload = {'status': 'INDEPENDENT_PARENT_MAP_UNIVERSE_PASS', 'map_count': len(actual),
               'migration_counts': dict(counts), 'comparison': 'sorted full permutation bytes, no hashes',
               'backend': 'NetworkX VF2', 'networkx_version': nx.__version__, 'numpy_version': np.__version__,
               'seconds': time.monotonic() - started}
    (folder / 'independent_parent_maps.json').write_text(json.dumps(payload, indent=2) + '\n')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.folder), sort_keys=True))
