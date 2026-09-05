#!/usr/bin/env python3
"""Define/count the next three-root domain without running its SAT search."""
import argparse
import json
import math
from pathlib import Path

import pynauty

from astra_overlap_strike import Overlaps, explicit, induced, ng
from astra_two_root_repair import Encoder
from ivanov_pair import build


class CountOnly:
    def add_clause(self, clause):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('data/astra_direct/next_three_root/specification.json'))
    args = parser.parse_args()
    card, _ = build((1, 1, 3, 4))
    core = induced(card.adj, tuple(v for v in range(card.n) if v not in (9, 15)))
    counts = {}
    for k in range(4):
        overlaps = Overlaps(core, k)
        total = 0
        for bucket in overlaps.buckets.values():
            sample = overlaps.entries[bucket[0]][1]
            _, size, exponent, _, _ = pynauty.autgrp(ng(sample))
            assert exponent == 0 and size == int(size)
            total += len(bucket) ** 2 * int(size) * math.perm(3, k) * math.factorial(3)
        counts[k] = total
    enc = Encoder(core, CountOnly(), roots=3)
    enc.encode()
    payload = {'status': 'DEFINED_NOT_SEARCHED', 'parent_order': 22, 'core': explicit(core), 'removed_from_shared_card': [9, 15],
               'roles': ['pair q01', 'first even-path selector z0'], 'roots': 3, 'edge_bits': 120,
               'base_variables': enc.nv, 'base_clauses': enc.nc, 'exact_parent_map_counts_by_migration_count': counts,
               'total_parent_maps': sum(counts.values()), 'domain': 'all pairs of three-vertex extensions of the fixed 19-vertex core'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({k: v for k, v in payload.items() if k != 'core'}, sort_keys=True))


if __name__ == '__main__':
    main()
