#!/usr/bin/env python3
"""Exact declared 18-card phase-defect domain; each fibre fully decided."""
import argparse
import itertools
import json
from pathlib import Path

from astra_overlap_strike import phase_card, run
from astra_drup_verify import verify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('data/astra_direct/phase_suite'))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    for steps, shift, link in itertools.product(((1, 3), (1, 4), (1, 3, 4)), (1, 2, 3), (0, 1)):
        name = 's' + ''.join(map(str, steps)) + f'_shift{shift}_link{link}'
        out = args.out / name
        result = run(phase_card(steps=steps, shift=shift, link=link), out)
        result['construction'] = {'core_order': 13, 'steps': steps, 'word': (0, 1, 3, 5, 8, 9), 'shift': shift, 'terminal_edge': link}
        result['proof_replay'] = verify(out / 'root_fixed_final.cnf', out / 'root_fixed.drup')
        results.append(result)
        (args.out / 'summary.json').write_text(json.dumps(results, indent=2) + '\n')
    assert len(results) == 18


if __name__ == '__main__':
    main()
