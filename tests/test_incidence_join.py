import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import incidence_join_strike as strike
from local_gluing_search import edge_partition_families, edge_class_arrays


class IncidenceJoinTests(unittest.TestCase):
    def test_cycle_insertion_rows_are_legitimate(self):
        choices = (1, 2, 3, 4, 5, 0)
        family = strike.heterogeneous_family(choices, 3)
        for deleted, row in enumerate(family):
            self.assertEqual(list(range(strike.N)), sorted(row))
            self.assertEqual(deleted, row[deleted])

    def test_incidence_components_equal_direct_partition_join(self):
        first = strike.side_classes(strike.BASE_LIFT)
        family = strike.heterogeneous_family((None, 2, None, 4, None, 0), 2)
        second = strike.side_classes(family)
        signature = strike.normalized_incidence_signature(first, second)
        joined, count = strike.joined_side_classes(signature)
        direct = edge_class_arrays(*edge_partition_families(
            strike.N, (strike.BASE_LIFT, family)
        ))
        self.assertGreater(count, 0)
        # Compare equality relations, independent of arbitrary class names.
        for system in (joined, direct):
            for left in range(2 * len(strike.EDGES)):
                side_left, pos_left = divmod(left, len(strike.EDGES))
                for right in range(2 * len(strike.EDGES)):
                    side_right, pos_right = divmod(right, len(strike.EDGES))
                    self.assertEqual(
                        joined[side_left][pos_left] == joined[side_right][pos_right],
                        direct[side_left][pos_left] == direct[side_right][pos_right],
                    )

    def test_globalizer_criterion_agrees_with_enumerator(self):
        classes = strike.side_classes(strike.BASE_LIFT)
        exact = strike.exact_globalizers(classes)
        self.assertEqual(strike.BASE_RESCUERS, exact)
        self.assertTrue(all(strike.maps_classes(classes, p) for p in exact))

    def test_trichotomy_regression_is_incidence_only(self):
        regression = strike.regression_examples()
        self.assertEqual((9, 4, False), tuple(
            regression["compatible"][key] for key in ("classes", "globalizers", "identity")
        ))
        self.assertEqual((7, 24, True), tuple(
            regression["partial"][key] for key in ("classes", "globalizers", "identity")
        ))
        self.assertEqual((4, 120, True), tuple(
            regression["strong"][key] for key in ("classes", "globalizers", "identity")
        ))


if __name__ == "__main__":
    unittest.main()
