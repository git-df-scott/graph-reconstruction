#!/usr/bin/env python3
"""Independent finite overlap replay: NetworkX VF2 + edge-slot equations.

Imports neither discovery code, nauty nor any campaign graph class. Rebuilds
ALL double-deletion maps using VF2 under a degree-based necessary filter;
derives completions from full edge equalities, rather than the three-bit
formula; compares full sets of generated pairs and independently rejects
each pair. Deck comparisons preserve multiplicity.
"""
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import itertools
import json
from pathlib import Path
import time

import networkx as nx


def invariant(g):
    deg = dict(g.degree())
    return tuple(sorted((deg[u], tuple(sorted(deg[v] for v in g[u]))) for u in g))


def completions(c, u, s, v, t, theta):
    m = len(c)
    f = dict(theta)
    f[m], f[s] = t, m
    assert set(f) == set(range(m + 1)) - {u}
    assert set(f.values()) == set(range(m + 1)) - {v}
    parent = list(range(2 * m + 2))
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    def slot(i, j, side):
        if i == m or j == m:
            return side * m + (j if i == m else i)
        return 2 * m + int(c.has_edge(i, j))
    for i, j in itertools.combinations(f, 2):
        x, y = find(slot(i, j, 0)), find(slot(f[i], f[j], 1))
        parent[x] = y
    zero, one = find(2 * m), find(2 * m + 1)
    assert zero != one
    free = sorted({find(i) for i in range(2 * m)} - {zero, one})
    assert len(free) == 3
    for values in itertools.product((0, 1), repeat=len(free)):
        assignment = dict(zip(free, values))
        assignment.update({zero: 0, one: 1})
        a = sum(assignment[find(i)] << i for i in range(m))
        b = sum(assignment[find(m + i)] << i for i in range(m))
        yield tuple(sorted((a, b)))


def replay(folder):
    started = time.monotonic()
    raw = json.loads((folder / 'card.json').read_text())
    c = nx.Graph()
    c.add_nodes_from(range(raw['order']))
    c.add_edges_from(raw['edges'])
    m = len(c)
    buckets = defaultdict(list)
    graphs = {}
    for removed in itertools.combinations(range(m), 2):
        h = c.copy()
        h.remove_nodes_from(removed)
        graphs[removed] = h
        buckets[invariant(h)].append(removed)
    pairs, maps = set(), 0
    tested_subset_pairs = 0
    for bucket in buckets.values():
        for left, right in itertools.combinations_with_replacement(bucket, 2):
            tested_subset_pairs += 1
            matcher = nx.algorithms.isomorphism.GraphMatcher(graphs[left], graphs[right])
            for theta in matcher.isomorphisms_iter():
                maps += 1
                for u, s in (left, left[::-1]):
                    for v, t in (right, right[::-1]):
                        pairs.update(completions(c, u, s, v, t, theta))
    with gzip.open(folder / 'neighborhood_pairs.json.gz', 'rt') as fp:
        stored = {tuple(p) for p in json.load(fp)}
    assert pairs == stored, (folder, 'pair-set mismatch', len(pairs), len(stored))
    result = json.loads((folder / 'result.json').read_text())
    assert result['root_fixed']['sat_models'] == 0, 'this replay requires moving-only pair manifest'
    assert maps == result['root_moving']['double_overlap_isomorphisms']

    @lru_cache(None)
    def extended(mask):
        g = c.copy()
        g.add_node(m)
        g.add_edges_from((m, i) for i in range(m) if mask >> i & 1)
        return g

    @lru_cache(None)
    def cards(mask):
        g = extended(mask)
        answer = []
        for u in g:
            h = g.copy()
            h.remove_node(u)
            answer.append(h)
        return answer

    counts = Counter()
    for a, b in sorted(pairs):
        g, h = extended(a), extended(b)
        if sorted(dict(g.degree()).values()) != sorted(dict(h.degree()).values()):
            counts['parent_degree_mismatch'] += 1
            continue
        if nx.is_isomorphic(g, h):
            counts['parent_isomorphic'] += 1
            continue
        ga, hb = cards(a), cards(b)
        ia, ib = list(map(invariant, ga)), list(map(invariant, hb))
        if Counter(ia) != Counter(ib):
            counts['deck_invariant_multiplicity_mismatch'] += 1
            continue
        # Equal necessary invariants: match card occurrences exactly by VF2.
        available = list(range(m + 1))
        for i, left in enumerate(ga):
            j = next((j for j in available if ia[i] == ib[j] and nx.is_isomorphic(left, hb[j])), None)
            if j is None:
                counts['exact_deck_mismatch'] += 1
                break
            available.remove(j)
        else:
            raise AssertionError(('UNRESOLVED_FULL_DECK_PAIR', a, b))
    payload = {'status': 'INDEPENDENT_COMPLETE_MOVING_DOMAIN_PASS', 'graph6': raw['graph6'], 'double_subset_pairs_tried': tested_subset_pairs,
               'overlap_isomorphisms': maps, 'exact_neighborhood_pair_set': len(pairs), 'pair_rejections': dict(counts),
               'backend': 'NetworkX VF2', 'networkx_version': nx.__version__, 'seconds': time.monotonic() - started}
    (folder / 'independent_overlap_replay.json').write_text(json.dumps(payload, indent=2) + '\n')
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folders', type=Path, nargs='+')
    args = ap.parse_args()
    for folder in args.folders:
        print(json.dumps(replay(folder), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
