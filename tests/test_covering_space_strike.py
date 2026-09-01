import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import covering_space_strike as strike


class CoveringSpaceStrikeTests(unittest.TestCase):
    def test_asymmetric_pseudosimilar_seed(self):
        data = strike.base_classification()
        self.assertEqual(12, data["incidence_classes"])
        self.assertEqual(4096, data["raw_assignments"])
        self.assertEqual(192, data["connected_exact_asymmetric"])
        self.assertTrue(data["all_asymmetric_are_color_discrete"])
        self.assertTrue(data["seed"]["deletion_map_valid"])
        self.assertTrue(data["seed"]["exactly_asymmetric"])

    def test_voltage_lifts_are_simple_and_legal_order(self):
        bases = strike.classified_bases({3})
        self.assertEqual(16, len(bases))
        _assignment, _base, tree, chords = bases[0]
        cases = (("C2", 16, 1), ("C3", 24, 1), ("S3", 24, 1),
                 ("S4", 32, (strike.S4[0], strike.S4[1], strike.S4[2])))
        for group, order, voltage in cases:
            graph = strike.voltage_lift(tree, chords, voltage, group)
            self.assertEqual(order, graph.n)
            sheets = {"C2": 2, "C3": 3, "S3": 3, "S4": 4}[group]
            self.assertEqual(sheets * (len(tree) + len(chords)), graph.m)

    def test_s4_rank_three_conjugacy_count(self):
        representatives = strike.simultaneous_conjugacy_representatives(strike.S4, 3)
        self.assertEqual(681, len(representatives))

    def test_complete_rank_three_c2_regression(self):
        result = strike.search("C2", (3,), progress=0)
        self.assertEqual(16, result["base_count"])
        self.assertEqual(128, result["presentations"])
        self.assertEqual(0, result["nonisomorphic_deck_collisions"])
        self.assertTrue(result["zero_counterexamples"])


if __name__ == "__main__":
    unittest.main()
