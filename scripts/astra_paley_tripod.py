#!/usr/bin/env python3
"""Three deletion-equivalent terminals on an exact quadratic-residue core.

Vertices 0..16 form the Paley graph over F_17. Three terminals at 17..19
encode open/closed neighborhoods of the clique {0,1,2}; terminals are either
independent or a clique. This introduces a triangle of local card maps,
while the intact terminal action need not be transitive. Each of the four
specific shared-card fibres is passed to the complete overlap constructor.
"""
import argparse
import itertools
import json
from pathlib import Path

from astra_overlap_strike import canon, group, induced, run
from astra_drup_verify import verify


def build(closed, terminal_clique):
    q = 17
    residues = {x * x % q for x in range(1, q)}
    rows = [0] * (q + 3)
    def add(u, v):
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    for u, v in itertools.combinations(range(q), 2):
        if (v - u) % q in residues:
            add(u, v)
    for terminal, port in enumerate((0, 1, 2), q):
        for x in range(q):
            if (x - port) % q in residues or (closed and x == port):
                add(terminal, x)
    if terminal_clique:
        for u, v in itertools.combinations(range(q, q + 3), 2):
            add(u, v)
    return tuple(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('data/astra_direct/paley_tripod'))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    for closed, link in itertools.product((0, 1), repeat=2):
        c = build(closed, link)
        auts = group(c)
        # Actual graph checks, rather than an assumed faithful gadget action.
        cards = [canon(induced(c, tuple(v for v in range(20) if v != t))) for t in (17, 18, 19)]
        assert len(set(cards)) == 1
        assert all(p[17] != 18 for p in auts)
        out = args.out / f'closed{closed}_clique{link}'
        result = run(c, out)
        result['construction'] = {'core': 'quadratic residues mod 17', 'terminal_ports': [0, 1, 2], 'closed_neighborhoods': closed, 'terminal_clique': link}
        result['terminal_orbits'] = [sorted({p[t] for p in auts}) for t in (17, 18, 19)]
        result['proof_replay'] = verify(out / 'root_fixed_final.cnf', out / 'root_fixed.drup')
        results.append(result)
        (args.out / 'summary.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
