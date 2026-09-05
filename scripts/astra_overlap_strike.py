#!/usr/bin/env python3
"""Complete one-card CE construction via double-deletion root migration.

For a fixed card C, two one-vertex extensions have neighborhoods A and B.
A card map either fixes the new root (a finite SAT groupoid problem), or
moves it. A moving map restricts to an isomorphism C-{u,s} -> C-{v,t}
and leaves only three binary choices for A,B. No graph-space census,
digest equality, or unproved symmetry leader is used.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import gzip
import itertools as it
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import networkx as nx
import pynauty
import pysat
from pysat.solvers import Glucose4

Graph = tuple[int, ...]


def edge(g, u, v):
    return (g[u] >> v) & 1


def induced(g, kept):
    return tuple(sum(edge(g, u, v) << j for j, v in enumerate(kept)) for u in kept)


def ng(g):
    return pynauty.Graph(len(g), adjacency_dict={u: [v for v in range(len(g)) if edge(g, u, v)] for u in range(len(g))})


def canon(g):
    # This is a full canonical adjacency byte string, not a digest.
    return pynauty.certificate(ng(g))


def g6(g):
    h = nx.Graph()
    h.add_nodes_from(range(len(g)))
    h.add_edges_from((u, v) for u in range(len(g)) for v in range(u) if edge(g, u, v))
    return nx.to_graph6_bytes(h, header=False).decode().strip()


def from_g6(s):
    h = nx.from_graph6_bytes(s.encode())
    return tuple(sum(1 << v for v in h[u]) for u in range(len(h)))


def extend(g, mask):
    m = len(g)
    return tuple(row | (((mask >> u) & 1) << m) for u, row in enumerate(g)) + (mask,)


def explicit(g):
    return {'order': len(g), 'edges': [[u, v] for u in range(len(g)) for v in range(u + 1, len(g)) if edge(g, u, v)], 'graph6': g6(g)}


def group(g, limit=200000):
    generators, size, exponent, _, _ = pynauty.autgrp(ng(g))
    identity = tuple(range(len(g)))
    seen, todo = {identity}, [identity]
    for p in todo:
        for q in generators:
            pq = tuple(q[p[i]] for i in range(len(p)))
            if pq not in seen:
                seen.add(pq)
                todo.append(pq)
                if len(seen) > limit:
                    raise RuntimeError('automorphism limit exceeded; domain INCOMPLETE')
    if exponent == 0 and int(size) != len(seen):
        raise AssertionError('automorphism closure disagrees with nauty group order')
    return tuple(sorted(seen))


class Overlaps:
    def __init__(self, c, deleted):
        self.c = c
        self.deleted = deleted
        self.entries = {}
        self.buckets = defaultdict(list)
        self.auts = {}
        m = len(c)
        for removed in it.combinations(range(m), deleted):
            kept = tuple(v for v in range(m) if v not in removed)
            h = induced(c, kept)
            key = canon(h)
            self.entries[removed] = (kept, h, pynauty.canon_label(ng(h)), key)
            self.buckets[key].append(removed)

    def maps(self, left, right):
        kl, gl, ll, key = self.entries[left]
        kr, gr, lr, otherkey = self.entries[right]
        if key != otherkey:
            return
        if left not in self.auts:
            self.auts[left] = group(gl)
        # Canonical order is new -> old. f sends left ll[i] to right lr[i].
        f = [None] * len(kl)
        for a, b in zip(ll, lr):
            f[a] = b
        for p in self.auts[left]:
            yield {kl[a]: kr[f[p[a]]] for a in range(len(kl))}


def moving_completions(c, u, s, v, t, theta):
    """All eight extensions realizing x->t, s->y, ordinary vertices->theta."""
    aa = sum(edge(c, t, b) << a for a, b in theta.items())
    bb = sum(edge(c, s, a) << b for a, b in theta.items())
    for deleted_a, deleted_b, bridge in it.product((0, 1), repeat=3):
        a = aa | (deleted_a << u) | (bridge << s)
        b = bb | (deleted_b << v) | (bridge << t)
        yield a, b


def replay_moving(c, a, b, u, s, v, t, theta):
    g, h = extend(c, a), extend(c, b)
    f = {**theta, len(c): t, s: len(c)}
    assert set(f) == set(range(len(g))) - {u}
    assert set(f.values()) == set(range(len(h))) - {v}
    return all(edge(g, i, j) == edge(h, f[i], f[j]) for i, j in it.combinations(f, 2))


class FixedRootCNF:
    def __init__(self, c):
        self.c, self.m = c, len(c)
        self.nv, self.clauses = 0, []
        self.a = [self.new() for _ in c]
        self.b = [self.new() for _ in c]
        self.xors = {}
        self.options = []

    def new(self):
        self.nv += 1
        return self.nv

    def xor(self, i, j):
        if (i, j) not in self.xors:
            x, y, z = self.a[i], self.b[j], self.new()
            self.clauses.extend([[x, y, -z], [-x, -y, -z], [x, -y, z], [-x, y, z]])
            self.xors[i, j] = z
        return self.xors[i, j]

    def exactly_one(self, opts):
        self.clauses.append(list(opts))
        if len(opts) <= 1:
            return
        # Sequential at-most-one: p_i means some option among 0..i is true.
        prefix = [self.new() for _ in opts[:-1]]
        self.clauses.append([-opts[0], prefix[0]])
        for i in range(1, len(opts) - 1):
            self.clauses.extend([[-opts[i], prefix[i]], [-prefix[i - 1], prefix[i]], [-opts[i], -prefix[i - 1]]])
        self.clauses.append([-opts[-1], -prefix[-1]])

    def encode(self):
        ov = Overlaps(self.c, 1)
        rows, cols = defaultdict(list), defaultdict(list)
        for bucket in ov.buckets.values():
            for left, right in it.product(bucket, repeat=2):
                u, v = left[0], right[0]
                for f in ov.maps(left, right):
                    sel = self.new()
                    rows[u].append(sel)
                    cols[v].append(sel)
                    self.options.append((sel, u, v, f))
                    for i, j in f.items():
                        self.clauses.append([-sel, -self.xor(i, j)])
        # Explicit bijection of deletion occurrences; repeats are not discarded.
        for table in (rows, cols):
            for i in range(self.m):
                opts = table[i]
                self.exactly_one(opts)
        auts = group(self.c)
        for p in auts:
            self.clauses.append([self.xor(i, p[i]) for i in range(self.m)])
        return {'card_isomorphism_options': len(self.options), 'aut_C': len(auts), 'card_type_multiplicities': sorted(map(len, ov.buckets.values()), reverse=True)}


class PairGate:
    def __init__(self, c, out):
        self.c, self.out = c, out
        self.counts = Counter()
        self.seen = set()
        self.first_rejection = None
        self.records = gzip.open(out / 'nonisomorphic_pairs.jsonl.gz', 'wt')

    @lru_cache(maxsize=None)
    def parent(self, mask):
        g = extend(self.c, mask)
        return g, tuple(sorted(row.bit_count() for row in g)), canon(g)

    @lru_cache(maxsize=None)
    def deck(self, mask):
        g = extend(self.c, mask)
        return tuple(sorted(canon(induced(g, tuple(w for w in range(len(g)) if w != v))) for v in range(len(g))))

    def check(self, a, b, witness):
        self.counts['emitted_completions'] += 1
        pair = tuple(sorted((a, b)))
        if pair in self.seen:
            self.counts['duplicate_neighborhood_pairs'] += 1
            return False
        self.seen.add(pair)
        if a.bit_count() != b.bit_count():
            self.counts['edge_count_rejections'] += 1
            return False
        ga, da, ca = self.parent(a)
        gb, db, cb = self.parent(b)
        if da != db:
            self.counts['parent_degree_rejections'] += 1
            return False
        if ca == cb:
            self.counts['parent_isomorphic_rejections'] += 1
            return False
        self.counts['nonisomorphic_parent_pairs'] += 1
        ad, bd = self.deck(a), self.deck(b)
        equal = ad == bd
        self.records.write(json.dumps({'A': a, 'B': b, 'deck_equal': equal}, sort_keys=True) + '\n')
        if not equal:
            self.counts['exact_deck_rejections'] += 1
            if self.first_rejection is None:
                self.first_rejection = {'G': explicit(ga), 'H': explicit(gb), 'A': a, 'B': b, 'witness': witness,
                                        'common_cards': sum((Counter(ad) & Counter(bd)).values()),
                                        'G_canonical': ca.hex(), 'H_canonical': cb.hex(),
                                        'G_deck': [x.hex() for x in ad], 'H_deck': [x.hex() for x in bd]}
            return False
        # Stop discovery before running the independent hostile gate.
        self.records.flush()
        path = self.out / 'candidate_pair.json'
        path.write_text(json.dumps({'G': explicit(ga), 'H': explicit(gb), 'witness': witness}, indent=2) + '\n')
        print('FULL_DECK_COLLISION: discovery stopped; invoking hostile checker', flush=True)
        checker = Path(__file__).with_name('hostile_ce_checker.py')
        subprocess.run([sys.executable, str(checker), '--input', str(path), '--certificate', str(self.out / 'hostile_candidate_certificate.json'), '--pretty'], check=True)
        raise RuntimeError('FULL_DECK_COLLISION_FROZEN: independently investigate; do not resume discovery')

    def close(self):
        self.records.close()
        with gzip.open(self.out / 'neighborhood_pairs.json.gz', 'wt') as fp:
            json.dump(sorted(self.seen), fp, separators=(',', ':'))
        if self.first_rejection:
            (self.out / 'first_nonisomorphic_rejection.json').write_text(json.dumps(self.first_rejection, indent=2) + '\n')


def root_fixed(c, out, gate):
    enc = FixedRootCNF(c)
    stats = enc.encode()
    cnf = out / 'root_fixed.cnf'
    cnf.write_text(f'p cnf {enc.nv} {len(enc.clauses)}\n' + ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in enc.clauses))
    stats.update(variables=enc.nv, clauses=len(enc.clauses), sat_models=0)
    # Each SAT model outside Aut(C) orbits is still checked for an unrooted
    # parent isomorphism. Only its actual full assignment is then blocked.
    blocking = []
    with Glucose4(bootstrap_with=enc.clauses, with_proof=True) as solver:
        while solver.solve():
            vals = set(x for x in solver.get_model() if x > 0)
            a = sum((x in vals) << i for i, x in enumerate(enc.a))
            b = sum((x in vals) << i for i, x in enumerate(enc.b))
            chosen = [(u, v, f) for sel, u, v, f in enc.options if sel in vals]
            assert len(chosen) == len(c)
            assert len({v for u, v, f in chosen}) == len(c)
            for u, v, f in chosen:
                assert all(((a >> i) & 1) == ((b >> j) & 1) for i, j in f.items())
            stats['sat_models'] += 1
            ga, gb = extend(c, a), extend(c, b)
            assert gate.deck(a) == gate.deck(b)
            gate.check(a, b, {'kind': 'root_fixed', 'maps': chosen})
            assert canon(ga) == canon(gb), 'nonisomorphic full-deck pair should have stopped discovery'
            clause = [-x if x in vals else x for x in enc.a + enc.b]
            solver.add_clause(clause)
            blocking.append({'A': a, 'B': b, 'clause': clause})
        proof = solver.get_proof()
    # Glucose can find inconsistency while bootstrapping and return no proof
    # lines. The independent DRUP replay must then validate the empty clause
    # directly from the input CNF by unit propagation.
    if not proof or proof[-1].strip() != '0':
        proof.append('0')
    (out / 'root_fixed.drup').write_text('\n'.join(proof) + '\n')
    (out / 'root_fixed_blocking.json').write_text(json.dumps(blocking, indent=2) + '\n')
    # If blocking is needed, the final CNF includes exactly certified isomorphic
    # assignments. Original CNF retained; independent replay checks each block.
    allclauses = enc.clauses + [x['clause'] for x in blocking]
    (out / 'root_fixed_final.cnf').write_text(f'p cnf {enc.nv} {len(allclauses)}\n' + ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in allclauses))
    stats.update(status='UNSAT', proof_lines=len(proof))
    return stats


def root_moving(c, gate):
    ov = Overlaps(c, 2)
    stats = Counter(double_deleted_subsets=len(ov.entries), double_deleted_types=len(ov.buckets))
    # Interchanging the two parents covers the opposite order of A,B.
    for bucket in ov.buckets.values():
        for left, right in it.combinations_with_replacement(bucket, 2):
            stats['isomorphic_double_subset_pairs'] += 1
            for f in ov.maps(left, right):
                stats['double_overlap_isomorphisms'] += 1
                for u, s in (left, left[::-1]):
                    for v, t in (right, right[::-1]):
                        for a, b in moving_completions(c, u, s, v, t, f):
                            witness = {'kind': 'root_moving', 'u': u, 's': s, 'v': v, 't': t, 'theta': f}
                            gate.check(a, b, witness)
    return dict(stats)


def phase_card(steps=(1, 3), word=(0, 1, 3, 5, 8, 9), shift=1, link=0):
    """13-vertex circulant + two unequal phase terminals, no twin blow-up.

    Deletion 0 -> deletion 1 is 1->0 and i->i+shift on the ring.
    Thus N(1)=word and N(0)=word+shift.
    """
    k = 13
    rows = [0] * (k + 2)
    def add(u, v):
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    for i in range(k):
        for step in steps:
            add(2 + i, 2 + ((i + step) % k))
    for i in word:
        add(1, 2 + i)
        add(0, 2 + ((i + shift) % k))
    if link:
        add(0, 1)
    return tuple(rows)


def run(c, out):
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    (out / 'card.json').write_text(json.dumps(explicit(c), indent=2) + '\n')
    gate = PairGate(c, out)
    try:
        fixed = root_fixed(c, out, gate)
        print('ROOT_FIXED', out.name, fixed, flush=True)
        moving = root_moving(c, gate)
    finally:
        gate.close()
    report = {'status': 'COMPLETE_NO_CE_IN_THIS_SHARED_CARD_FIBRE', 'card': explicit(c),
              'root_fixed': fixed, 'root_moving': moving, 'pair_gates': dict(gate.counts),
              'unique_neighborhood_pairs': len(gate.seen), 'seconds': time.monotonic() - start,
              'versions': {'python': platform.python_version(), 'pynauty': pynauty.__version__, 'networkx': nx.__version__, 'python_sat': pysat.__version__}}
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('COMPLETE', out.name, json.dumps({k: report[k] for k in ('root_moving', 'pair_gates', 'seconds')}), flush=True)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--g6')
    ap.add_argument('--steps', default='1,3')
    ap.add_argument('--word', default='0,1,3,5,8,9')
    ap.add_argument('--shift', type=int, default=1)
    ap.add_argument('--link', type=int, choices=(0, 1), default=0)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    c = from_g6(args.g6) if args.g6 else phase_card(tuple(map(int, args.steps.split(','))), tuple(map(int, args.word.split(','))), args.shift, args.link)
    run(c, args.out)


if __name__ == '__main__':
    main()
