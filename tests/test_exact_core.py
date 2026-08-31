import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, canonical_code, canonical_deck, is_isomorphic, same_deck


class ExactCoreTests(unittest.TestCase):
    def test_permutation_invariance(self):
        g = Graph.from_edge_mask(6, 0b101101001011001)
        base = canonical_code(g)
        for order in itertools.islice(itertools.permutations(range(6)), 100):
            h = g.permute(order)
            self.assertEqual(base, canonical_code(h))
            self.assertTrue(is_isomorphic(g, h))

    def test_nonisomorphic_same_degree_sequence(self):
        cycle6 = Graph.from_edge_mask(6, sum(1 << k for k in [0, 5, 9, 12, 14, 4]))
        triangles = Graph.from_edge_mask(6, sum(1 << k for k in [0, 1, 5, 12, 13, 14]))
        self.assertEqual(sorted(cycle6.degrees), sorted(triangles.degrees))
        self.assertFalse(is_isomorphic(cycle6, triangles))
        self.assertNotEqual(canonical_code(cycle6), canonical_code(triangles))

    def test_deck_multiplicity_and_complement(self):
        g = Graph.from_edge_mask(5, 0b1011010111)
        h = g.permute((4, 2, 0, 3, 1))
        self.assertEqual(5, len(canonical_deck(g)))
        self.assertTrue(same_deck(g, h))
        self.assertTrue(same_deck(g.complement(), h.complement()))

    def test_two_vertex_exception(self):
        empty = Graph.from_edge_mask(2, 0)
        edge = Graph.from_edge_mask(2, 1)
        self.assertFalse(is_isomorphic(empty, edge))
        self.assertTrue(same_deck(empty, edge))

    def test_graph6_and_fixed_isomorphism(self):
        # Dhc is the six-vertex path under graph6's upper-triangle order.
        g = Graph.from_graph6("EhCG")
        self.assertEqual(6, g.n)
        self.assertEqual(g, Graph.from_graph6(g.to_graph6()))
        from grc import find_isomorphism

        self.assertIsNotNone(find_isomorphism(g, g, {0: 0}))



if __name__ == "__main__":
    unittest.main()
