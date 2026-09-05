#!/usr/bin/env python3
"""Put the inherited selector near-miss into the three-root coordinates.

Used only for preferred SAT phases, never for additional constraints.
This is an existing 9/22-card near-miss, not a CEC.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

from astra_overlap_strike import canon, extend, explicit, induced
from astra_two_root_repair import exact_deck
from ivanov_pair import build


def seed():
    card, _ = build((1, 1, 3, 4))
    order = tuple(u for u in range(card.n) if u not in (9, 15)) + (21, 9, 15)
    return tuple(induced(extend(card.adj, card.adj[i]), order) for i in (0, 1))


def phases(enc, root_leaders=False):
    pair = seed()
    if root_leaders:
        from astra_root_leaders import normalize_pair
        pair = normalize_pair(pair)
    assert enc.n == 22 and enc.d == 19
    assert all(induced(g, tuple(range(enc.d))) == enc.core for g in pair)
    return [value if pair[side][u] >> v & 1 else -value
            for (side, u, v), value in enc.variables.items()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('data/astra_direct/three_root_seed'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    g, h = seed()
    path = args.out / 'pair.json'
    path.write_text(json.dumps({'G': explicit(g), 'H': explicit(h)}, indent=2) + '\n')
    result = {'purpose': 'inherited near-miss phase preference, no edge constraints',
              'nonisomorphic_nauty': canon(g) != canon(h),
              'common_cards': sum((Counter(exact_deck(g)) & Counter(exact_deck(h))).values()),
              'order': len(g)}
    (args.out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    checked = subprocess.run([sys.executable, str(Path(__file__).with_name('hostile_ce_checker.py')),
                              '--input', str(path), '--certificate', str(args.out / 'hostile_certificate.json'), '--pretty'],
                             text=True, capture_output=True)
    (args.out / 'hostile.log').write_text(checked.stdout + checked.stderr)
    assert result['nonisomorphic_nauty'] and result['common_cards'] == 9
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
