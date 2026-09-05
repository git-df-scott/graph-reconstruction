#!/usr/bin/env python3
"""Exact core-automorphism quotient of the 15-bit moving-card construction.

Normalize the distinguished four-deletion patterns independently, then take
double orbits of residual maps under their stabilizers. Parent exchange is
also included. Every orbit move is an actual core automorphism or pair swap;
it merely permutes the bridge/deletion bits. Full coverage is checked against
the separately counted ordered raw domain before any graph-pair search.
"""
import argparse
from collections import Counter, defaultdict
import itertools as it
import json
from pathlib import Path
import time

import networkx as nx

from astra_fully_moving import domain, path_order, template, search
from astra_overlap_strike import explicit, group, induced
from ivanov_pair import build


def generators(elements):
    identity = tuple(range(len(elements[0])))
    gens, seen = [], {identity}
    for p in elements:
        if p in seen:
            continue
        gens.append(p)
        queue = list(seen)
        for a in queue:
            for b in gens:
                c = tuple(b[a[i]] for i in range(len(a)))
                if c not in seen:
                    seen.add(c)
                    queue.append(c)
    assert seen == set(elements)
    return gens


def quotient(core, include_extendable=False):
    started = time.monotonic()
    ov, choices, extensions, raw_counts = domain(core)
    auts = group(core)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(core)))
    graph.add_edges_from((u, v) for u in range(len(core)) for v in range(u + 1, len(core)) if core[u] >> v & 1)
    independently = {tuple(f[u] for u in range(len(core))) for f in nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter()}
    assert independently == set(auts)
    patterns = {(u, tuple(sorted(aa))) for selected in choices.values() for u, aa in selected}
    unseen, representatives = set(patterns), []
    while unseen:
        pattern = min(unseen)
        u, aa = pattern
        orbit = {(p[u], tuple(sorted(p[x] for x in aa))) for p in auts}
        assert orbit <= patterns
        unseen.difference_update(orbit)
        stabilizer = [p for p in auts if p[u] == u and {p[x] for x in aa} == set(aa)]
        representatives.append({'pattern': pattern, 'orbit_size': len(orbit), 'generators': generators(stabilizer)})
    buckets = defaultdict(list)
    for entry in representatives:
        u, aa = entry['pattern']
        removed = tuple(sorted((u,) + aa))
        key = ov.entries[removed][3]
        buckets[(key, core[u].bit_count())].append(entry)
    records, families, coverage, orbit_records = [], {}, 0, []
    for bucket in buckets.values():
        for source, target in it.combinations_with_replacement(bucket, 2):
            sp, tp = source['pattern'], target['pattern']
            u, aa0 = sp
            v, bb0 = tp
            left, right = tuple(sorted((u,) + aa0)), tuple(sorted((v,) + bb0))
            kept = ov.entries[left][0]
            positions = {x: i for i, x in enumerate(kept)}
            universe = {bytes(theta[x] for x in kept) for theta in ov.maps(left, right)
                        if include_extendable or tuple(theta[x] for x in kept) not in extensions[left]}
            unvisited = set(universe)
            left_actions = [tuple(positions[p[x]] for x in kept) for p in source['generators']]
            right_actions = target['generators']
            while unvisited:
                first = min(unvisited)
                orbit, queue = {first}, [first]
                for theta in queue:
                    images = [bytes(theta[i] for i in p) for p in left_actions]
                    images += [bytes(p[x] for x in theta) for p in right_actions]
                    if sp == tp:
                        inverse = dict(zip(theta, kept))
                        images.append(bytes(inverse[x] for x in kept))
                    for other in images:
                        assert other in universe
                        if other not in orbit:
                            orbit.add(other)
                            queue.append(other)
                unvisited.difference_update(orbit)
                weight = source['orbit_size'] * target['orbit_size'] * len(orbit) * (1 if sp == tp else 2)
                coverage += weight
                theta = dict(zip(kept, first))
                aa, bb = path_order(core, aa0), path_order(core, bb0)
                base, variables, f = template(core, u, aa, v, bb, theta)
                key = (base, variables)
                if key not in families:
                    families[key] = len(records)
                    records.append({'u': u, 'A': aa, 'v': v, 'B': bb, 'theta': sorted(theta.items()),
                                    'card_map': sorted(f.items()), 'base': base, 'variables': variables})
                orbit_records.append({'source_pattern': sp, 'target_pattern': tp,
                                      'residual_orbit_size': len(orbit), 'raw_templates_covered': weight,
                                      'family_index': families[key]})
    expected = raw_counts['raw_equal_degree_P3_oriented_map_templates' if include_extendable else 'nonextendable_templates']
    assert coverage == expected, ('quotient coverage mismatch', coverage, expected)
    payload = {'status': 'EXACT_CORE_AUTOMORPHISM_QUOTIENT', 'include_extendable': include_extendable,
               'core_automorphisms': len(auts), 'core_group_independent_VF2_match': True,
               'oriented_patterns': len(patterns), 'pattern_orbits': len(representatives),
               'residual_double_orbits': len(orbit_records), 'distinct_literal_families': len(records),
               'ordered_raw_templates_covered': coverage, 'raw_domain': raw_counts,
               'orbit_records': orbit_records, 'seconds': time.monotonic() - started}
    return records, payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--include-extendable', action='store_true')
    parser.add_argument('--max-templates', type=int, default=64)
    parser.add_argument('--resume', action='store_true', help='Reuse completed templates only after exact input comparison')
    parser.add_argument('--out', type=Path, default=Path('data/astra_direct/moving_quotient'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    card, _ = build((1, 1, 3, 4))
    core = induced(card.adj, tuple(u for u in range(card.n) if u not in (9, 15)))
    (args.out / 'core.json').write_text(json.dumps(explicit(core), indent=2) + '\n')
    records, certificate = quotient(core, args.include_extendable)
    (args.out / 'quotient.json').write_text(json.dumps(certificate, indent=2) + '\n')
    print('MOVING_QUOTIENT', json.dumps({k: v for k, v in certificate.items() if k != 'orbit_records'}, sort_keys=True), flush=True)
    results = []
    for index, record in enumerate(records[:args.max_templates]):
        folder = args.out / f'template_{index:03d}'
        if args.resume and (folder / 'result.json').exists():
            assert json.loads((folder / 'template.json').read_text()) == json.loads(json.dumps(record)), 'Resume input mismatch'
            result = json.loads((folder / 'result.json').read_text())
            assert result['status'] in ('SELECTED_TEMPLATE_EXHAUSTED_NO_CE_SINGLE_IMPLEMENTATION', 'FULL_DECK_PAIR_FROZEN_STOP')
        else:
            result = search(record, folder)
        results.append(result)
        print('MOVING_QUOTIENT_TEMPLATE', index, json.dumps(result, sort_keys=True), flush=True)
        if result['status'] == 'FULL_DECK_PAIR_FROZEN_STOP':
            break
    totals = Counter()
    for result in results:
        totals.update(result['counts'])
    found = any(r['status'] == 'FULL_DECK_PAIR_FROZEN_STOP' for r in results)
    payload = {'status': 'FULL_DECK_PAIR_FROZEN_STOP' if found else
               'ALL_QUOTIENT_FAMILIES_EXHAUSTED_NO_CE' if len(results) == len(records) else 'BOUNDED_QUOTIENT_PREFIX_NO_CE_REMAINDER_OPEN',
               'templates_searched': len(results), 'templates_total': len(records), 'counts': dict(totals),
               'include_extendable': args.include_extendable, 'seconds': time.monotonic() - started}
    (args.out / 'result.json').write_text(json.dumps(payload, indent=2) + '\n')
    print('MOVING_QUOTIENT_RESULT', json.dumps(payload, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
