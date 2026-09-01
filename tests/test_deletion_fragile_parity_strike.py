import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import deletion_fragile_parity_strike as parity
import outer_s6_strike as outer


class DeletionFragileParityStrikeTests(unittest.TestCase):
    def test_no_nontrivial_release_code_through_dimension_four(self):
        expected_isometries = {2: 4, 3: 24, 4: 192}
        for dimension in range(2, 5):
            result = parity.classify_dimension(dimension)
            self.assertEqual(expected_isometries[dimension], result["odd_cube_isometries"])
            self.assertEqual(0, result["nontrivial_complete_release_codes"])

    def test_outer_s6_geometry(self):
        self.assertEqual(15, len(outer.DUADS))
        self.assertEqual(15, len(outer.SYNTHEMES))
        self.assertEqual(6, len(outer.TOTALS))
        result = outer.classification()
        self.assertEqual(720, result["outer_images_distinct"])
        self.assertEqual(120, result["ordinary_S5_order"])
        self.assertEqual(120, result["exotic_S5_order"])
        self.assertEqual((1, 5), result["ordinary_S5_orbits_on_points"])
        self.assertEqual((6,), result["exotic_S5_orbits_on_points"])

    def test_outer_map_sends_transpositions_to_triple_transpositions(self):
        transposition = (1, 0, 2, 3, 4, 5)
        self.assertEqual((2, 2, 2), outer.cycle_type(outer.outer_image(transposition)))


if __name__ == "__main__":
    unittest.main()
