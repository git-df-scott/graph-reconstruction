import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import hostile_ce_checker as checker


class HostileCeCheckerTests(unittest.TestCase):
    def test_self_test_controls(self):
        self.assertTrue(checker.self_test()["passed"])

    def test_canonical_label_agrees_with_brute_force_through_order_five(self):
        for order in range(1, 6):
            edge_count = order * (order - 1) // 2
            for mask in range(1 << edge_count):
                edges = []
                bit = 0
                for left in range(order):
                    for right in range(left + 1, order):
                        if mask & (1 << bit):
                            edges.append((left, right))
                        bit += 1
                graph = checker.ExactGraph.from_edges(order, edges)
                # The exact normal form canonically orders degree cells first,
                # then minimizes inside them.  It need not be the unrestricted
                # minimum adjacency integer, but this restricted minimum is
                # still a complete isomorphism invariant.
                brute = min(
                    graph.edge_mask(new_to_old)
                    for new_to_old in itertools.permutations(range(order))
                    if tuple(graph.degrees[v] for v in new_to_old)
                    == tuple(sorted(graph.degrees))
                )
                self.assertEqual(
                    int(checker.canonical_label(graph).split(":")[1], 16), brute
                )

    def test_multiplicity_is_not_reduced_to_support(self):
        one_edge = checker.ExactGraph.from_graph6("B_")
        two_edge_path = checker.ExactGraph.from_graph6("Bo")
        result = checker.verify_pair(one_edge, two_edge_path)
        self.assertTrue(result["deck_verification"]["support_sets_equal"])
        self.assertFalse(result["deck_verification"]["canonical_multisets_equal"])
        self.assertEqual("REJECTED_DECK_MISMATCH", result["status"])

    def test_two_deck_routes_and_two_parent_routes_agree(self):
        cycle = checker.ExactGraph.from_edges(
            5, ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0))
        )
        relabelled = cycle.permute((3, 1, 4, 0, 2))
        result = checker.verify_pair(cycle, relabelled)
        self.assertTrue(result["parent_verification"]["routes_agree"])
        self.assertTrue(result["deck_verification"]["routes_agree"])
        self.assertEqual(5, len(result["deck_verification"]["matching"]))

    def test_invalid_graphs_are_rejected_at_parse_time(self):
        with self.assertRaisesRegex(ValueError, "loops"):
            checker.ExactGraph.from_edges(3, ((0, 0),))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            checker.ExactGraph.from_edges(3, ((0, 1), (1, 0)))
        with self.assertRaisesRegex(ValueError, "encoded length"):
            checker.ExactGraph.from_graph6("B__")
        with self.assertRaisesRegex(ValueError, "padding"):
            checker.ExactGraph.from_graph6("B`")


if __name__ == "__main__":
    unittest.main()
