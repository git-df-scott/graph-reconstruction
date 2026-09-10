import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import numpy as np

import weighted_selector_alphabet as alphabet
import weighted_selector_search as search


class WeightedSelectorAlphabetTests(unittest.TestCase):
    def test_vectorized_canonical_matches_reference(self):
        rng = random.Random(20260909)
        rows = [[rng.randint(0, 4) for _ in range(16)] for _ in range(500)]
        base = 6
        expected = [
            alphabet.encode(np.array([search.canonical_weight(tuple(row))]), base)[0]
            for row in rows
        ]
        actual = alphabet.canonical_codes(np.array(rows), base)
        self.assertEqual(expected, actual.tolist())

    def test_replays_closed_two_value_box(self):
        result = alphabet.run(2, 2, 1 << 16)
        self.assertEqual(65536, result["vectors"])
        self.assertEqual(5760, result["orbits"])
        self.assertEqual([], result["exact_collisions"])

    def test_detects_planted_collision(self):
        # Any two vectors in one orbit share a deck; the exact re-check must
        # reject them as the SAME orbit rather than report a collision.
        vector = tuple(range(1, 17))
        image = tuple(vector[s] for s in search.INVERSE_ACTIONS[1])
        self.assertEqual(search.weighted_deck(vector), search.weighted_deck(image))
        self.assertEqual(search.canonical_weight(vector), search.canonical_weight(image))


if __name__ == "__main__":
    unittest.main()
