import itertools
from pathlib import Path
import random
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import astra_overlap_strike as discovery
from astra_two_root_repair import Encoder as TwoRootEncoder, all_parent_maps
from astra_drup_verify import WatchedUP, contradiction_by_up, verify
from astra_independent_overlap_verify import completions as independent_completions
import networkx as nx
from pysat.solvers import Glucose4


class OverlapControls(unittest.TestCase):
    def test_completions_against_independent_edge_equations(self):
        # Symmetric, asymmetric, and known pseudosimilar small controls.
        for text in ('Cl', 'Ch', 'GQyPA_'):
            c = discovery.from_g6(text)
            graph = nx.from_graph6_bytes(text.encode())
            ov = discovery.Overlaps(c, 2)
            for bucket in ov.buckets.values():
                for left, right in itertools.combinations_with_replacement(bucket, 2):
                    for f in ov.maps(left, right):
                        for u, s in (left, left[::-1]):
                            for v, t in (right, right[::-1]):
                                expected = set(independent_completions(graph, u, s, v, t, f))
                                actual = {tuple(sorted(p)) for p in discovery.moving_completions(c, u, s, v, t, f)}
                                self.assertEqual(actual, expected)
                                for a, b in discovery.moving_completions(c, u, s, v, t, f):
                                    self.assertTrue(discovery.replay_moving(c, a, b, u, s, v, t, f))

    def test_fixed_root_cnf_against_full_colored_decks(self):
        for text in ('Cl', 'Ch'):
            c = discovery.from_g6(text)
            enc = discovery.FixedRootCNF(c)
            enc.encode()
            m = len(c)
            auts = discovery.group(c)
            def color_key(mask, removed=None):
                kept = [u for u in range(m) if u != removed]
                g = discovery.ng(discovery.induced(c, kept))
                colors = [{i for i, u in enumerate(kept) if bool(mask >> u & 1) == b} for b in (False, True)]
                g.set_vertex_coloring([cell for cell in colors if cell])
                return discovery.pynauty.certificate(g), sum(bool(mask >> u & 1) for u in kept)
            decks = [sorted(color_key(mask, u) for u in range(m)) for mask in range(1 << m)]
            with Glucose4(bootstrap_with=enc.clauses) as solver:
                for a, b in itertools.product(range(1 << m), repeat=2):
                    globally_equal = any(all(bool(a >> i & 1) == bool(b >> p[i] & 1) for i in range(m)) for p in auts)
                    expected = decks[a] == decks[b] and not globally_equal
                    assumptions = [x if mask >> i & 1 else -x for vars_, mask in ((enc.a, a), (enc.b, b)) for i, x in enumerate(vars_)]
                    self.assertEqual(solver.solve(assumptions=assumptions), expected)

    def test_watched_up_against_simple_scan(self):
        rng = random.Random(80904)
        for _ in range(40):
            clauses = [tuple(sorted(set(rng.choice((-1, 1)) * rng.randint(1, 8) for _ in range(rng.randint(1, 5))))) for _ in range(15)]
            watched = WatchedUP(clauses)
            for _ in range(20):
                assumptions = [rng.choice((-1, 1)) * rng.randint(1, 8) for _ in range(rng.randint(0, 7))]
                self.assertEqual(watched.contradiction(assumptions), contradiction_by_up(clauses, assumptions))
            watched.delete(clauses[-1])
            self.assertEqual(watched.contradiction([]), contradiction_by_up(clauses[:-1], []))

    def test_drup_accepts_unsat_rejects_false_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            cnf, proof = Path(tmp) / 'a.cnf', Path(tmp) / 'a.drup'
            proof.write_text('0\n')
            cnf.write_text('p cnf 1 2\n1 0\n-1 0\n')
            self.assertTrue(verify(cnf, proof)['verified_unsat'])
            cnf.write_text('p cnf 1 1\n1 0\n')
            with self.assertRaises(AssertionError):
                verify(cnf, proof)

    def test_two_root_encoding_all_small_assignments(self):
        # On three vertices edge count is a complete isomorphism invariant.
        # This gives a SAT-independent full-deck oracle for parents of order 4.
        for drop in (0, 3):
            with Glucose4() as solver:
                enc = TwoRootEncoder((0, 0), solver)
                enc.encode(drop)
                pairs = [(u, v) for u, v in itertools.combinations(range(4), 2) if v >= 2]
                graphs, decks = [], []
                for bits in range(32):
                    edges = {p for i, p in enumerate(pairs) if bits >> i & 1}
                    graphs.append(edges)
                    decks.append([sum(u != removed and v != removed for u, v in edges) for removed in range(4)])
                for a, b in itertools.product(range(32), repeat=2):
                    equal = sorted(decks[a]) == sorted(decks[b]) if drop == 0 else decks[a][0] in decks[b]
                    expected = a != b and equal
                    assumptions = [enc.variables[side, u, v] * (1 if bits >> i & 1 else -1)
                                   for side, bits in ((0, a), (1, b)) for i, (u, v) in enumerate(pairs)]
                    self.assertEqual(solver.solve(assumptions=assumptions), expected)

    def test_parent_map_universe_against_all_permutations(self):
        core = (2, 5, 2)  # P3, with two or three new roots.
        for roots in (2, 3):
            n = len(core) + roots
            expected = set()
            for tau in itertools.permutations(range(n)):
                if all(discovery.edge(core, u, v) == discovery.edge(core, tau[u], tau[v])
                       for u, v in itertools.combinations(range(3), 2) if tau[u] < 3 and tau[v] < 3):
                    expected.add(tau)
            emitted = [tau for k, tau in all_parent_maps(core, roots)]
            self.assertEqual(len(emitted), len(set(emitted)))
            self.assertEqual(set(emitted), expected)


if __name__ == '__main__':
    unittest.main()
