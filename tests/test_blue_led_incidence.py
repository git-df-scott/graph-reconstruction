import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import crossed_matrix_holonomy as crossed
import gassmann_incidence_bideck as gassmann
import gassmann_johnson_anchor as johnson
import matrix_bideck_local_search as matrix_search
import tournament_transfer_probe as tournament


class BlueLedIncidenceTests(unittest.TestCase):
    def test_gassmann_orbit_counts(self):
        h = gassmann.generated_subgroup(gassmann.H_GENERATORS)
        k = gassmann.generated_subgroup(gassmann.K_GENERATORS)
        self.assertEqual((len(h), len(k)), (4, 4))
        self.assertEqual(len(gassmann.orbital_rows(h)), 6)
        self.assertEqual(len(gassmann.orbital_rows(k)), 6)

    def test_johnson_anchor_has_six_and_fifteen_types(self):
        degrees = johnson.anchor_internal_degrees()
        self.assertEqual(degrees[:6], (10,) * 6)
        self.assertEqual(degrees[6:], (2,) * 15)
        self.assertEqual(len(set(johnson.ACTIONS)), 720)

    def test_tournament_control_does_not_transfer_directly(self):
        result = tournament.run(5)
        self.assertEqual(result["tournament_classes"], 12)
        self.assertEqual(len(result["nonreconstructible_pairs"]), 1)
        self.assertFalse(result["nonreconstructible_pairs"][0]["matrix_bideck_equal"])

    def test_crossed_holonomy_complete_domain(self):
        result = crossed.run()
        self.assertEqual(result["conjugates"], 5040)
        self.assertEqual(result["zero_globalizer_systems"], 0)
        self.assertEqual(result["class_histogram"][19], 2)

    def test_split_graph_order(self):
        graph = matrix_search.split_graph((0,) * 7)
        self.assertEqual(graph.n, 14)
        self.assertEqual(graph.m, 21)


if __name__ == "__main__":
    unittest.main()
