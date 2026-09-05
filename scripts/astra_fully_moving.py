#!/usr/bin/env python3
"""Construct three-root graph pairs from one fully migrating card map.

For core deletions u,v, all three roots moving into the opposite core
leave nine shared bridge bits and six unseen deletion bits: exactly 15.
The P3/P3 root case normalizes root labels by its center and sorted leaves.
"""
import argparse
from collections import Counter
import itertools as it
import json
from pathlib import Path
import subprocess
import sys
import time

import pynauty

from astra_overlap_strike import Overlaps, canon, explicit, group, induced, ng
from astra_two_root_repair import exact_deck
from ivanov_pair import build


def path_order(core, vertices):
    degree = {u: sum((core[u] >> v) & 1 for v in vertices if v != u) for u in vertices}
    if sorted(degree.values()) != [1, 1, 2]:
        return None
    return tuple(sorted(u for u in vertices if degree[u] == 1)) + tuple(u for u in vertices if degree[u] == 2)


def template(core, u, aa, v, bb, theta):
    d, n = len(core), len(core) + 3
    roots = tuple(range(d, n))
    rows = [list(core) + [0] * 3 for _ in range(2)]
    def edge(side, a, b):
        rows[side][a] |= 1 << b
        rows[side][b] |= 1 << a
    for i, r in enumerate(roots):
        for x, y in theta.items():
            if core[bb[i]] >> y & 1:
                edge(0, r, x)
            if core[aa[i]] >> x & 1:
                edge(1, r, y)
    for i, j in it.combinations(range(3), 2):
        if core[bb[i]] >> bb[j] & 1:
            edge(0, roots[i], roots[j])
        if core[aa[i]] >> aa[j] & 1:
            edge(1, roots[i], roots[j])
    variables = [((0, roots[i], aa[j]), (1, roots[j], bb[i])) for i in range(3) for j in range(3)]
    variables += [((0, roots[i], u),) for i in range(3)]
    variables += [((1, roots[j], v),) for j in range(3)]
    f = dict(theta)
    f.update(zip(roots, bb))
    f.update(zip(aa, roots))
    # Verify the card identity as an identity of Boolean expressions, so it
    # holds simultaneously for all 2^15 assignments, not just test graphs.
    symbols = {}
    for bit, changes in enumerate(variables):
        for side, a, b in changes:
            key = (side, *sorted((a, b)))
            assert key not in symbols
            assert not (rows[side][a] >> b & 1)
            symbols[key] = ('variable', bit)
    def expression(side, a, b):
        return symbols.get((side, *sorted((a, b))), ('constant', (rows[side][a] >> b) & 1))
    assert set(f) == set(range(n)) - {u}
    assert set(f.values()) == set(range(n)) - {v}
    assert all(expression(0, a, b) == expression(1, f[a], f[b]) for a, b in it.combinations(f, 2))
    return tuple(map(tuple, rows)), tuple(variables), f


def domain(core):
    ov = Overlaps(core, 4)
    auts = group(core)
    choices, degree_profiles, extensions = {}, {}, {}
    for removed in ov.entries:
        choices[removed] = [(u, order) for u in removed
                            if (order := path_order(core, tuple(x for x in removed if x != u))) is not None]
        degree_profiles[removed] = Counter(core[u].bit_count() for u, aa in choices[removed])
    total = 0
    for bucket in ov.buckets.values():
        profile = Counter()
        for removed in bucket:
            profile.update(degree_profiles[removed])
        _, size, exponent, _, _ = pynauty.autgrp(ng(ov.entries[bucket[0]][1]))
        assert exponent == 0 and int(size) == size
        total += int(size) * sum(value * value for value in profile.values())
    extendable = 0
    for removed, profile in degree_profiles.items():
        if not profile:
            continue
        kept = ov.entries[removed][0]
        restrictions = {tuple(p[x] for x in kept) for p in auts}
        extensions[removed] = restrictions
        extendable += len(restrictions) * sum(value * value for value in profile.values())
    counts = {'core_four_deletion_subsets': len(ov.entries), 'residual_types': len(ov.buckets),
              'raw_equal_degree_P3_oriented_map_templates': total,
              'extendable_templates': extendable, 'nonextendable_templates': total - extendable,
              'independent_bits_per_template': 15, 'edge_count_equal_assignments_per_template': 10240}
    return ov, choices, extensions, counts


def selected_templates(core, ov, choices, extensions, limit):
    seen = set()
    for bucket in ov.buckets.values():
        for left, right in it.product(bucket, repeat=2):
            if not choices[left] or not choices[right]:
                continue
            kept = ov.entries[left][0]
            for theta in ov.maps(left, right):
                if tuple(theta[x] for x in kept) in extensions[left]:
                    continue
                for (u, aa), (v, bb) in it.product(choices[left], choices[right]):
                    if core[u].bit_count() != core[v].bit_count():
                        continue
                    base, variables, f = template(core, u, aa, v, bb, theta)
                    key = (base, variables)
                    if key in seen:
                        continue
                    seen.add(key)
                    yield {'u': u, 'A': aa, 'v': v, 'B': bb, 'theta': sorted(theta.items()),
                           'card_map': sorted(f.items()), 'base': base, 'variables': variables}
                    if len(seen) >= limit:
                        return


def search(record, folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'template.json').write_text(json.dumps(record, indent=2) + '\n')
    rows = [list(g) for g in record['base']]
    degree = [[row.bit_count() for row in g] for g in rows]
    m = [sum(row) // 2 for row in degree]
    counts = Counter()
    first_rejection = None
    n = len(rows[0])
    for index in range(1 << 15):
        if index:
            bit = (index & -index).bit_length() - 1
            for side, a, b in record['variables'][bit]:
                delta = -1 if rows[side][a] >> b & 1 else 1
                rows[side][a] ^= 1 << b
                rows[side][b] ^= 1 << a
                degree[side][a] += delta
                degree[side][b] += delta
                m[side] += delta
        counts['assignments'] += 1
        if m[0] != m[1]:
            counts['edge_count_rejections'] += 1
            continue
        if sorted(degree[0]) != sorted(degree[1]):
            counts['degree_rejections'] += 1
            continue
        g, h = tuple(rows[0]), tuple(rows[1])
        if canon(g) == canon(h):
            counts['parent_isomorphic'] += 1
            continue
        counts['nonisomorphic_parent_pairs'] += 1
        if first_rejection is None:
            first_rejection = {'G': explicit(g), 'H': explicit(h), 'gray_assignment': index ^ (index >> 1)}
        multiplicities = Counter(degree[1])
        probe = min((u for u in range(n) if u != record['u']), key=lambda u: (multiplicities[degree[0][u]], -degree[0][u], u))
        probe_card = canon(induced(g, tuple(x for x in range(n) if x != probe)))
        if not any(probe_card == canon(induced(h, tuple(x for x in range(n) if x != v)))
                   for v in range(n) if degree[1][v] == degree[0][probe]):
            counts['missing_probe_card'] += 1
            continue
        if exact_deck(g) != exact_deck(h):
            counts['full_deck_mismatch'] += 1
            continue
        path = folder / 'candidate_pair.json'
        path.write_text(json.dumps({'G': explicit(g), 'H': explicit(h)}, indent=2) + '\n')
        subprocess.run([sys.executable, str(Path(__file__).with_name('hostile_ce_checker.py')), '--input', str(path),
                        '--certificate', str(folder / 'hostile_candidate.json'), '--pretty'], check=True)
        return {'status': 'FULL_DECK_PAIR_FROZEN_STOP', 'counts': dict(counts)}
    assert counts['assignments'] - counts['edge_count_rejections'] == 10240
    if first_rejection is not None:
        (folder / 'first_nonisomorphic_rejection.json').write_text(json.dumps(first_rejection, indent=2) + '\n')
    result = {'status': 'SELECTED_TEMPLATE_EXHAUSTED_NO_CE_SINGLE_IMPLEMENTATION', 'counts': dict(counts)}
    (folder / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--templates', type=int, default=16)
    parser.add_argument('--out', type=Path, default=Path('data/astra_direct/fully_moving'))
    args = parser.parse_args()
    assert args.templates > 0
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    card, _ = build((1, 1, 3, 4))
    core = induced(card.adj, tuple(v for v in range(card.n) if v not in (9, 15)))
    (args.out / 'core.json').write_text(json.dumps(explicit(core), indent=2) + '\n')
    ov, choices, extensions, counts = domain(core)
    (args.out / 'domain.json').write_text(json.dumps(counts, indent=2) + '\n')
    print('FULLY_MOVING_DOMAIN', json.dumps(counts, sort_keys=True), flush=True)
    results = []
    for i, record in enumerate(selected_templates(core, ov, choices, extensions, args.templates)):
        result = search(record, args.out / f'template_{i:03d}')
        results.append(result)
        print('FULLY_MOVING_TEMPLATE', i, json.dumps(result, sort_keys=True), flush=True)
        if result['status'] == 'FULL_DECK_PAIR_FROZEN_STOP':
            break
    totals = Counter()
    for result in results:
        totals.update(result['counts'])
    payload = {'status': 'FULL_DECK_PAIR_FROZEN_STOP' if any(r['status'] == 'FULL_DECK_PAIR_FROZEN_STOP' for r in results)
               else 'BOUNDED_TEMPLATE_PREFIX_COMPLETE_NO_CE', 'templates_requested': args.templates,
               'templates_searched': len(results), 'counts': dict(totals), 'domain': counts,
               'selection': 'first distinct templates in deterministic overlap iteration, nonextendable residual maps, equal core deletion degrees; root triples P3',
               'seconds': time.monotonic() - started}
    (args.out / 'result.json').write_text(json.dumps(payload, indent=2) + '\n')
    print('FULLY_MOVING_RESULT', json.dumps(payload, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
