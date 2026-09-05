#!/usr/bin/env python3
"""Exact bounded two-root repair over one fixed double card.

By default only edges touching two distinguished vertices vary on either
parent: 2*(2*d+1) binary edge variables. --roots 3 enables the specified
three-root continuation. Full deletion-occurrence matching and all
card maps are existential. No fixed deleted-vertex matching, degree-class
assumption, or prescribed local map is imposed. Optional --root-leaders
uses the proved S3 x S3 and parent-exchange representatives. Every actual
parent isomorphism is blocked as an equality system (CEGAR), or the complete
possible permutation universe is preblocked.
"""
import argparse
import itertools
import json
from pathlib import Path
import threading
import time

import pynauty
from pysat.solvers import Glucose4

from astra_overlap_strike import canon, explicit, induced, ng, Overlaps
from ivanov_pair import build


class Encoder:
    def __init__(self, core, solver, roots=2, trace=None):
        self.core, self.d, self.n = core, len(core), len(core) + roots
        self.trace = trace
        self.solver = solver
        self.nv = self.nc = 0
        self.variables = {}
        self.xors = {}
        for side in (0, 1):
            for u, v in itertools.combinations(range(self.n), 2):
                if v >= self.d:
                    self.variables[side, u, v] = self.new()
        self.edge_variables = len(self.variables)

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, clause):
        self.solver.add_clause(clause)
        self.nc += 1
        if self.trace is not None:
            self.trace.write(' '.join(map(str, clause)) + ' 0\n')

    def slot(self, side, u, v):
        u, v = sorted((u, v))
        if v < self.d:
            return bool(self.core[u] >> v & 1)
        return self.variables[side, u, v]

    def exactly_one(self, opts):
        self.add(opts)
        if len(opts) <= 1:
            return
        prefix = [self.new() for _ in opts[:-1]]
        self.add([-opts[0], prefix[0]])
        for i in range(1, len(opts) - 1):
            self.add([-opts[i], prefix[i]])
            self.add([-prefix[i - 1], prefix[i]])
            self.add([-opts[i], -prefix[i - 1]])
        self.add([-opts[-1], -prefix[-1]])

    def conditional_equal(self, p, q, a, b):
        if isinstance(a, bool) and isinstance(b, bool):
            if a != b:
                self.add([-p, -q])
        elif isinstance(a, bool):
            self.add([-p, -q, b if a else -b])
        elif isinstance(b, bool):
            self.add([-p, -q, a if b else -a])
        else:
            self.add([-p, -q, -a, b])
            self.add([-p, -q, a, -b])

    def encode(self, drop=0):
        n = self.n
        matching = [[self.new() for _ in range(n)] for _ in range(n)]
        self.matching = matching
        for row in matching:
            self.exactly_one(row)
        for col in zip(*matching):
            self.exactly_one(list(col))
        for removed in range(n - drop):
            source = [u for u in range(n) if u != removed]
            p = {(u, v): self.new() for u in source for v in range(n)}
            for u in source:
                self.exactly_one([p[u, v] for v in range(n)])
            for v in range(n):
                self.exactly_one([p[u, v] for u in source] + [matching[removed][v]])
            for a, b in itertools.combinations(source, 2):
                ga = self.slot(0, a, b)
                for x in range(n):
                    for y in range(n):
                        if x != y:
                            self.conditional_equal(p[a, x], p[b, y], ga, self.slot(1, x, y))
        self.block_isomorphism(tuple(range(n)))

    def difference(self, a, b):
        if isinstance(a, bool) and isinstance(b, bool):
            return a != b
        if isinstance(a, bool):
            return -b if a else b
        if isinstance(b, bool):
            return -a if b else a
        if a == b:
            return False
        key = tuple(sorted((a, b)))
        if key not in self.xors:
            z = self.new()
            self.add([a, b, -z])
            self.add([-a, -b, -z])
            self.add([a, -b, z])
            self.add([-a, b, z])
            self.xors[key] = z
        return self.xors[key]

    def block_isomorphism(self, tau):
        lits = []
        for u, v in itertools.combinations(range(self.n), 2):
            x = self.difference(self.slot(0, u, v), self.slot(1, tau[u], tau[v]))
            if x is True:
                return
            if x is not False:
                lits.append(x)
        self.add(list(set(lits)))

    def decode(self, model):
        vals = set(x for x in model if x > 0)
        output = []
        for side in (0, 1):
            rows = [0] * self.n
            for u, v in itertools.combinations(range(self.n), 2):
                x = self.slot(side, u, v)
                present = x if isinstance(x, bool) else x in vals
                if present:
                    rows[u] |= 1 << v
                    rows[v] |= 1 << u
            output.append(tuple(rows))
        return output


def exact_deck(g):
    return sorted(canon(induced(g, tuple(v for v in range(len(g)) if v != u))) for u in range(len(g)))


def all_parent_maps(core, roots_count=2):
    """Complete isomorphism universe for r-root extensions of fixed D.

    Exactly k=0,...,r core vertices map to target roots. Restriction to the
    remaining core is D-A -> D-B, |A|=|B|=k. Enumerate that isomorphism,
    the injection A into target roots, and the remaining r root images.
    """
    d = len(core)
    roots = tuple(range(d, d + roots_count))
    for k in range(roots_count + 1):
        ov = Overlaps(core, k)
        for bucket in ov.buckets.values():
            for left, right in itertools.product(bucket, repeat=2):
                for theta in ov.maps(left, right):
                    for images in itertools.permutations(roots, k):
                        remainder = tuple(right) + tuple(v for v in roots if v not in images)
                        for root_images in itertools.permutations(remainder):
                            f = dict(theta)
                            f.update(zip(left, images))
                            f.update(zip(roots, root_images))
                            tau = tuple(f[u] for u in range(d + roots_count))
                            assert sorted(tau) == list(range(d + roots_count))
                            yield k, tau


def run(core, out, seconds=60, drop=0, preblock=False, resume=None, roots=2, certify=False, fast_preblock=False, degree_constraints=False, near_miss_phases=False, triangle_constraints=False, root_leaders=False, root_case=None):
    out.mkdir(parents=True, exist_ok=True)
    (out / 'core.json').write_text(json.dumps(explicit(core), indent=2) + '\n')
    start = time.monotonic()
    report = {'core': explicit(core), 'parent_order': len(core) + roots, 'edge_bits': 2 * (roots * len(core) + roots * (roots - 1) // 2), 'roots': roots, 'dropped_cards': drop,
              'solver_seconds_budget': seconds, 'isomorphic_models_blocked': 0, 'status': 'BUILDING', 'preblock_all_parent_isomorphisms': preblock,
              'fast_preblock': fast_preblock, 'redundant_degree_constraints': degree_constraints,
              'near_miss_phase_preferences': near_miss_phases, 'redundant_triangle_constraints': triangle_constraints,
              'proved_root_type_leaders': root_leaders, 'root_edge_count_case': root_case}
    blockers = []
    trace = (out / 'formula.cnf').open('w+') if certify else None
    if trace:
        trace.write(f'p cnf {0:10d} {0:10d}\n')
    with Glucose4(with_proof=certify) as solver:
        enc = Encoder(core, solver, roots=roots, trace=trace)
        enc.encode(drop)
        if root_leaders:
            assert drop == 0, 'root-type representatives require the full deck'
            from astra_root_leaders import add_root_leaders
            add_root_leaders(enc)
        if root_case is not None:
            assert root_leaders and len(root_case) == 2 and 0 <= root_case[0] <= root_case[1] <= 3
            pairs = list(itertools.combinations(range(enc.d, enc.n), 2))
            for side, edge_count in enumerate(root_case):
                for i, (u, v) in enumerate(pairs):
                    x = enc.slot(side, u, v)
                    enc.add([x if i >= 3 - edge_count else -x])
        if degree_constraints:
            assert drop == 0, 'degree identities require the full deck'
            from astra_degree_constraints import add_degree_constraints
            add_degree_constraints(enc)
        if triangle_constraints:
            assert drop == 0, 'triangle identities require the full deck'
            from astra_triangle_constraints import add_triangle_constraints
            report['triangle_circuit'] = add_triangle_constraints(enc)
        report.update(base_encode_seconds=time.monotonic() - start, base_variables=enc.nv, base_clauses=enc.nc)
        if preblock:
            from collections import Counter
            if fast_preblock:
                from astra_fast_preblock import preblock as native_preblock
                counts = native_preblock(enc, out)
            else:
                counts = Counter()
                for k, tau in all_parent_maps(core, roots):
                    enc.block_isomorphism(tau)
                    counts[k] += 1
            report['parent_isomorphism_maps_by_migration_count'] = dict(counts)
        if resume:
            saved = json.loads(Path(resume).read_text())
            assert saved['core'] == explicit(core), 'checkpoint core mismatch'
            for record in saved['blockers']:
                tau = tuple(record['tau'])
                assert sorted(tau) == list(range(enc.n))
                enc.block_isomorphism(tau)
                blockers.append(record)
            report['resumed_blockers'] = len(blockers)
        report.update(build_seconds=time.monotonic() - start, initial_variables=enc.nv, initial_clauses=enc.nc)
        if near_miss_phases:
            from astra_three_root_seed import phases
            solver.set_phases(phases(enc, root_leaders=root_leaders))
        print('TWO_ROOT_ENCODED', json.dumps(report, sort_keys=True), flush=True)
        timer = threading.Timer(seconds, solver.interrupt)
        timer.start()
        try:
            while True:
                answer = solver.solve_limited(expect_interrupt=True)
                if answer is None:
                    report['status'] = 'TIMEOUT_UNRESOLVED'
                    break
                if not answer:
                    report['status'] = 'UNSAT_SINGLE_SOLVER_NO_PROOF'
                    if certify:
                        # python-sat get_proof() materializes the complete trace
                        # twice. Stream its exact ASCII records instead.
                        solver.prfile.seek(0)
                        proof_lines, last = 0, b''
                        with (out / 'unsat.drup').open('wb') as target:
                            for line in solver.prfile:
                                last = line.strip()
                                target.write(line.rstrip() + b'\n')
                                proof_lines += 1
                            if last != b'0':
                                target.write(b'0\n')
                                proof_lines += 1
                        report['status'] = 'UNSAT_PROOF_PENDING_INDEPENDENT_CHECK'
                        report['proof_lines'] = proof_lines
                    break
                g, h = enc.decode(solver.get_model())
                if canon(g) != canon(h):
                    if drop:
                        report['status'] = 'PARTIAL_DECK_POSITIVE_CONTROL'
                        # Check existence of a size n-drop occurrence matching.
                        from collections import Counter
                        overlap = sum((Counter(exact_deck(g)) & Counter(exact_deck(h))).values())
                        assert overlap >= len(g) - drop
                        report['common_cards'] = overlap
                        (out / 'partial_control_pair.json').write_text(json.dumps({'G': explicit(g), 'H': explicit(h)}, indent=2) + '\n')
                        break
                    assert exact_deck(g) == exact_deck(h), 'SAT encoding or model replay defect'
                    path = out / 'candidate_pair.json'
                    path.write_text(json.dumps({'G': explicit(g), 'H': explicit(h)}, indent=2) + '\n')
                    import subprocess, sys
                    subprocess.run([sys.executable, str(Path(__file__).with_name('hostile_ce_checker.py')), '--input', str(path), '--certificate', str(out / 'hostile_candidate_certificate.json'), '--pretty'], check=True)
                    report['status'] = 'FULL_DECK_PAIR_FROZEN_STOP'
                    break
                assert not preblock, 'full parent-map preblocking missed an isomorphism'
                lg, lh = pynauty.canon_label(ng(g)), pynauty.canon_label(ng(h))
                tau = [None] * len(g)
                for i, j in zip(lg, lh):
                    tau[i] = j
                assert all(bool(g[u] >> v & 1) == bool(h[tau[u]] >> tau[v] & 1) for u, v in itertools.combinations(range(len(g)), 2))
                enc.block_isomorphism(tau)
                report['isomorphic_models_blocked'] += 1
                blockers.append({'tau': tau, 'G': explicit(g)['graph6'], 'H': explicit(h)['graph6']})
        finally:
            timer.cancel()
        report.update(total_seconds=time.monotonic() - start, final_variables=enc.nv, final_clauses=enc.nc, solver_stats=solver.accum_stats())
    if trace:
        trace.seek(0)
        trace.write(f'p cnf {enc.nv:10d} {enc.nc:10d}\n')
        trace.close()
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    (out / 'blocker_checkpoint.json').write_text(json.dumps({'core': explicit(core), 'blockers': blockers}, indent=2) + '\n')
    print('TWO_ROOT_RESULT', json.dumps(report, sort_keys=True), flush=True)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=Path('data/astra_direct/two_root_repair'))
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--control', choices=('full', 'partial'))
    ap.add_argument('--preblock', action='store_true')
    ap.add_argument('--resume', type=Path)
    ap.add_argument('--roots', type=int, choices=(2, 3), default=2)
    ap.add_argument('--certify', action='store_true')
    ap.add_argument('--fast-preblock', action='store_true', help='native exact three-root parent-map expansion')
    ap.add_argument('--degree-constraints', action='store_true', help='redundant parent edge-count and matched-degree identities')
    ap.add_argument('--near-miss-phases', action='store_true', help='prefer inherited near-miss edges; no extra constraints')
    ap.add_argument('--triangle-constraints', action='store_true', help='redundant matched-vertex triangle identities')
    ap.add_argument('--root-leaders', action='store_true', help='proved ten root-type pair representatives')
    ap.add_argument('--root-case', type=int, nargs=2, metavar=('G_EDGES', 'H_EDGES'), help='one of ten ordered root-type cases, each count in 0..3')
    args = ap.parse_args()
    if args.fast_preblock:
        assert args.preblock and args.roots == 3, '--fast-preblock requires --preblock --roots 3'
    if args.control:
        run((0, 0), args.out, args.seconds, drop=3 if args.control == 'partial' else 0, preblock=args.preblock, resume=args.resume, roots=args.roots, certify=args.certify, fast_preblock=args.fast_preblock, degree_constraints=args.degree_constraints, near_miss_phases=args.near_miss_phases, triangle_constraints=args.triangle_constraints, root_leaders=args.root_leaders, root_case=args.root_case)
    else:
        card, _ = build((1, 1, 3, 4))
        # q_{01} is first pair vertex, at index sum(port weights)=9.
        removed = (9,) if args.roots == 2 else (9, 15)
        core = induced(card.adj, tuple(v for v in range(card.n) if v not in removed))
        run(core, args.out, args.seconds, preblock=args.preblock, resume=args.resume, roots=args.roots, certify=args.certify, fast_preblock=args.fast_preblock, degree_constraints=args.degree_constraints, near_miss_phases=args.near_miss_phases, triangle_constraints=args.triangle_constraints, root_leaders=args.root_leaders, root_case=args.root_case)


if __name__ == '__main__':
    main()
