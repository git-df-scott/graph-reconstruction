#!/usr/bin/env python3
"""Nonuniform neighborhood split of the inherited selector near-miss.

The fixed shared card has port weights (1,1,3,4). Both (1,2,3,4) and
(2,1,3,4) parents extend it. All 2^21 neighborhoods are allowed, including
nonuniform attachment inside every twin cell; no weighted-vector condition
is imposed. The overlap engine decides the complete pair fibre.
"""
import argparse
import json
from pathlib import Path

from ivanov_pair import build
from astra_overlap_strike import canon, explicit, extend, run
from astra_drup_verify import verify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('data/astra_direct/selector_split'))
    args = ap.parse_args()
    c, types = build((1, 1, 3, 4))
    args.out.mkdir(parents=True, exist_ok=True)
    # Add a duplicate of the unique vertex in port 0 or port 1.
    a, b = c.adj[0], c.adj[1]
    g, h = extend(c.adj, a), extend(c.adj, b)
    assert canon(g) != canon(h)
    (args.out / 'inherited_near_pair.json').write_text(json.dumps({'G': explicit(g), 'H': explicit(h), 'A': a, 'B': b, 'port_weights': [1, 1, 3, 4]}, indent=2) + '\n')
    result = run(c.adj, args.out)
    result['construction'] = {'port_weights': [1, 1, 3, 4], 'types': types, 'neighborhoods_allowed': 1 << len(c.adj), 'uniformity_constraint': False}
    result['proof_replay'] = verify(args.out / 'root_fixed_final.cnf', args.out / 'root_fixed.drup')
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
