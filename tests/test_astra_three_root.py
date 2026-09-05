import ctypes as ct
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from astra_fast_preblock import Native
from astra_degree_constraints import add_degree_constraints, thresholds
from astra_triangle_constraints import add_triangle_constraints
from astra_root_leaders import add_root_leaders, normalize_pair
from astra_three_root_seed import seed, phases
from astra_overlap_strike import Overlaps, induced
from astra_two_root_repair import Encoder, all_parent_maps
from ivanov_pair import build
from pysat.solvers import Glucose4


class Collector:
    def __init__(self):
        self.clauses = []

    def add_clause(self, clause):
        self.clauses.append(tuple(sorted(clause)))


class ThreeRootControls(unittest.TestCase):
    def test_native_nonisomorphism_all_order_four_pairs(self):
        pairs = list(itertools.combinations(range(4), 2))
        edge_index = {edge: i for i, edge in enumerate(pairs)}
        labels = []
        for bits in range(64):
            orbit = []
            for p in itertools.permutations(range(4)):
                orbit.append(sum(1 << edge_index[tuple(sorted((p[u], p[v])))]
                                 for i, (u, v) in enumerate(pairs) if bits >> i & 1))
            labels.append(min(orbit))
        with Glucose4() as solver:
            enc = Encoder((0,), solver, roots=3)
            native = Native(enc)
            try:
                for k in (0, 1):
                    ov = Overlaps((0,), k)
                    for bucket in ov.buckets.values():
                        for left, right in itertools.product(bucket, repeat=2):
                            for theta in ov.maps(left, right):
                                count = native.expand(theta)
                                for i in range(count):
                                    offset = i * native.width
                                    enc.add(native.clauses[offset + 1:offset + 1 + native.clauses[offset]])
                for a, b in itertools.product(range(64), repeat=2):
                    assumptions = [enc.variables[side, u, v] * (1 if bits >> i & 1 else -1)
                                   for side, bits in ((0, a), (1, b)) for i, (u, v) in enumerate(pairs)]
                    self.assertEqual(solver.solve(assumptions=assumptions), labels[a] != labels[b])
            finally:
                native.close()

    def test_root_type_leaders_cover_all_64_patterns(self):
        edges = list(itertools.combinations(range(1, 4), 2))
        def graph(bits):
            rows = [0] * 4
            for i, (u, v) in enumerate(edges):
                if bits >> i & 1:
                    rows[u] |= 1 << v
                    rows[v] |= 1 << u
            return tuple(rows)
        representatives = set()
        with Glucose4() as solver:
            enc = Encoder((0,), solver, roots=3)
            add_root_leaders(enc)
            for a, b in itertools.product(range(8), repeat=2):
                pair = normalize_pair((graph(a), graph(b)))
                bits = tuple(tuple((g[u] >> v) & 1 for u, v in edges) for g in pair)
                self.assertEqual(sorted((a.bit_count(), b.bit_count())), [sum(row) for row in bits])
                self.assertTrue(all(tuple(sorted(row)) == row for row in bits))
                assumptions = [enc.variables[side, u, v] * (1 if pair[side][u] >> v & 1 else -1)
                               for side in (0, 1) for u, v in edges]
                self.assertTrue(solver.solve(assumptions=assumptions))
                representatives.add(bits)
            self.assertEqual(len(representatives), 10)

    def test_seed_phases_respect_proved_leaders(self):
        g, h = seed()
        core = induced(g, tuple(range(19)))
        with Glucose4() as solver:
            enc = Encoder(core, solver, roots=3)
            add_root_leaders(enc)
            self.assertTrue(solver.solve(assumptions=phases(enc, root_leaders=True)))
            self.assertEqual(enc.decode(solver.get_model()), list(normalize_pair((g, h))))

    def test_triangle_matching_all_small_assignments(self):
        pairs = list(itertools.combinations(range(4), 2))
        counts = []
        for bits in range(64):
            edges = {edge for i, edge in enumerate(pairs) if bits >> i & 1}
            triangles = [set(t) for t in itertools.combinations(range(4), 3)
                         if all(edge in edges for edge in itertools.combinations(t, 2))]
            counts.append([sum(u in t for t in triangles) for u in range(4)])
        with Glucose4() as solver:
            enc = Encoder((0,), solver, roots=3)
            enc.matching = [[enc.new() for _ in range(4)] for _ in range(4)]
            add_triangle_constraints(enc)
            for permutation in ((0, 1, 2, 3), (1, 2, 3, 0)):
                matching = [enc.matching[u][v] * (1 if permutation[u] == v else -1)
                            for u in range(4) for v in range(4)]
                for a, b in itertools.product(range(64), repeat=2):
                    assumptions = [enc.variables[side, u, v] * (1 if bits >> i & 1 else -1)
                                   for side, bits in ((0, a), (1, b)) for i, (u, v) in enumerate(pairs)]
                    expected = all(counts[a][u] == counts[b][permutation[u]] for u in range(4))
                    self.assertEqual(solver.solve(assumptions=assumptions + matching), expected)

    def test_unary_thresholds_both_directions(self):
        with Glucose4() as solver:
            enc = Encoder((0,), solver, roots=3)
            inputs = list(enc.variables.values())[:6]
            row = thresholds(enc, inputs)
            for bits in range(64):
                assumptions = [x if bits >> i & 1 else -x for i, x in enumerate(inputs)]
                count = bits.bit_count()
                for j, x in enumerate(row, 1):
                    self.assertTrue(solver.solve(assumptions=assumptions + [x if count >= j else -x]))
                    self.assertFalse(solver.solve(assumptions=assumptions + [-x if count >= j else x]))

    def test_degree_matching_all_small_assignments(self):
        pairs = list(itertools.combinations(range(4), 2))
        degrees = [[sum(u in edge for i, edge in enumerate(pairs) if bits >> i & 1) for u in range(4)]
                   for bits in range(64)]
        with Glucose4() as solver:
            enc = Encoder((0,), solver, roots=3)
            enc.matching = [[enc.new() for _ in range(4)] for _ in range(4)]
            add_degree_constraints(enc)
            for permutation in ((0, 1, 2, 3), (1, 2, 3, 0)):
                matching = [enc.matching[u][v] * (1 if permutation[u] == v else -1)
                            for u in range(4) for v in range(4)]
                for a, b in itertools.product(range(64), repeat=2):
                    assumptions = [enc.variables[side, u, v] * (1 if bits >> i & 1 else -1)
                                   for side, bits in ((0, a), (1, b)) for i, (u, v) in enumerate(pairs)]
                    expected = all(degrees[a][u] == degrees[b][permutation[u]] for u in range(4))
                    self.assertEqual(solver.solve(assumptions=assumptions + matching), expected)

    def test_native_complete_small_universe_and_each_clause(self):
        core = (2, 5, 2)
        sink = Collector()
        enc = Encoder(core, sink, roots=3)
        native = Native(enc)
        actual = set()
        try:
            for k in range(4):
                ov = Overlaps(core, k)
                for bucket in ov.buckets.values():
                    for left, right in itertools.product(bucket, repeat=2):
                        for theta in ov.maps(left, right):
                            count = native.expand(theta)
                            raw = ct.string_at(native.maps, count * enc.n)
                            for i in range(count):
                                tau = tuple(raw[i * enc.n:(i + 1) * enc.n])
                                self.assertNotIn(tau, actual)
                                actual.add(tau)
                                offset = i * native.width
                                got = tuple(native.clauses[offset + 1:offset + 1 + native.clauses[offset]])
                                sink.clauses.clear()
                                enc.block_isomorphism(tau)
                                self.assertEqual([got], sink.clauses)
            self.assertEqual(actual, {tau for k, tau in all_parent_maps(core, 3)})
        finally:
            native.close()

    def test_full_core_native_clause_samples_all_layers(self):
        card, _ = build((1, 1, 3, 4))
        core = induced(card.adj, tuple(v for v in range(card.n) if v not in (9, 15)))
        sink = Collector()
        enc = Encoder(core, sink, roots=3)
        native = Native(enc)
        try:
            for k in range(4):
                ov = Overlaps(core, k)
                for bucket in ov.buckets.values():
                    # Both ends exercise different deleted sets and core maps.
                    for left, right in ((bucket[0], bucket[-1]), (bucket[-1], bucket[0])):
                        theta = next(ov.maps(left, right))
                        count = native.expand(theta)
                        raw = ct.string_at(native.maps, count * enc.n)
                        for i in range(count):
                            tau = tuple(raw[i * enc.n:(i + 1) * enc.n])
                            offset = i * native.width
                            got = tuple(native.clauses[offset + 1:offset + 1 + native.clauses[offset]])
                            sink.clauses.clear()
                            enc.block_isomorphism(tau)
                            self.assertEqual([got], sink.clauses)
        finally:
            native.close()

    def test_three_root_deck_encoding_all_order_four_assignments(self):
        pairs = list(itertools.combinations(range(4), 2))
        decks = []
        for bits in range(64):
            edges = [edge for i, edge in enumerate(pairs) if bits >> i & 1]
            decks.append(sorted(sum(u != removed and v != removed for u, v in edges) for removed in range(4)))
        with Glucose4() as solver:
            enc = Encoder((0,), solver, roots=3)
            enc.encode()
            for a, b in itertools.product(range(64), repeat=2):
                assumptions = [enc.variables[side, u, v] * (1 if bits >> i & 1 else -1)
                               for side, bits in ((0, a), (1, b)) for i, (u, v) in enumerate(pairs)]
                self.assertEqual(solver.solve(assumptions=assumptions), a != b and decks[a] == decks[b])


if __name__ == '__main__':
    unittest.main()
