import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import weighted_selector_search as search


class WeightedSelectorTests(unittest.TestCase):
    def test_a4_action(self):
        self.assertEqual(16, len(search.COORDINATES))
        self.assertEqual(12, len(search.INVERSE_ACTIONS))

    def test_orbit_invariance(self):
        vector = tuple(range(2, 18))
        canonical = search.canonical_weight(vector)
        for inverse in search.INVERSE_ACTIONS:
            image = tuple(vector[source] for source in inverse)
            self.assertEqual(canonical, search.canonical_weight(image))
            self.assertEqual(search.weighted_deck(vector), search.weighted_deck(image))

    def test_deck_multiplicity(self):
        vector = (2,) * 16
        self.assertEqual(sum(vector), sum(count for _, count in search.weighted_deck(vector)))


if __name__ == "__main__":
    unittest.main()
