import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from grc import Graph, is_isomorphic

import dual_deck_trade_strike as strike


def split_incidence_graph(h: strike.Hypergraph) -> Graph:
    """Independent ordinary-graph encoding: points independent, blocks clique."""
    point_position = {point: index for index, point in enumerate(h.points)}
    offset = len(h.points)
    rows = [0] * (len(h.points) + len(h.blocks))
    for first in range(len(h.blocks)):
        for second in range(first + 1, len(h.blocks)):
            u, v = offset + first, offset + second
            rows[u] |= 1 << v
            rows[v] |= 1 << u
    for block_index, block in enumerate(h.blocks):
        block_vertex = offset + block_index
        for point in block:
            point_vertex = point_position[point]
            rows[point_vertex] |= 1 << block_vertex
            rows[block_vertex] |= 1 << point_vertex
    return Graph(tuple(rows))


class DualDeckTradeStrikeTests(unittest.TestCase):
    def test_kocay_n3_source_and_category_mismatch(self):
        x, y = strike.kocay_pair(3)
        self.assertEqual((len(x.points), len(x.blocks), len(y.blocks)), (9, 28, 28))
        self.assertIsNone(strike.find_isomorphism(x, y))
        induced = strike.compare_decks(
            (x.delete_point(p) for p in x.points),
            (y.delete_point(p) for p in y.points),
        )
        trace = strike.compare_decks(
            (x.delete_incidence_row(p) for p in x.points),
            (y.delete_incidence_row(p) for p in y.points),
        )
        self.assertTrue(induced["equal"])
        self.assertFalse(trace["equal"])
        self.assertEqual(trace["matched_multiplicity_pairs"], [])

    def test_independent_split_graph_replay_of_row_failure(self):
        x, y = strike.kocay_pair(3)
        self.assertFalse(is_isomorphic(split_incidence_graph(x), split_incidence_graph(y)))
        x_cards = [split_incidence_graph(x.delete_incidence_row(p)) for p in x.points]
        y_cards = [split_incidence_graph(y.delete_incidence_row(p)) for p in y.points]
        self.assertFalse(any(is_isomorphic(left, right) for left in x_cards for right in y_cards))

    def test_complete_six_module_trade_space(self):
        result = strike.structured_trade_search()
        self.assertEqual(result["family_size"], 64)
        self.assertEqual(result["parent_isomorphism_types"], 40)
        self.assertEqual(result["nonisomorphic_induced_point_deck_collision_count"], 6)
        self.assertEqual(result["nonisomorphic_incidence_row_deck_collision_count"], 0)
        self.assertEqual(result["nonisomorphic_block_deck_collision_count"], 0)
        self.assertEqual(result["nonisomorphic_dual_deck_collision_count"], 0)


if __name__ == "__main__":
    unittest.main()
