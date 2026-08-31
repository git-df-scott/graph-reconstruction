import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import kill_universal_rescuer as strike


class UniversalRescuerTests(unittest.TestCase):
    def test_old_seed_has_six_old_and_twelve_free_cross_classes(self):
        seed, representatives = strike.old_seed()
        self.assertEqual(6, len(representatives))
        self.assertEqual(18, seed.class_count())

    def test_r1_old_edges_are_forced_and_cross_edges_are_witnesses(self):
        seed, _representatives = strike.old_seed()
        for edge in strike.OLD_EDGES:
            self.assertTrue(seed.connected(
                strike.slot(0, edge),
                strike.slot(1, tuple(sorted((strike.R1[edge[0]], strike.R1[edge[1]])))),
            ))
        self.assertTrue(all(
            not seed.connected(left, right)
            for left, right in strike.r1_witness_pairs()
        ))
        witnesses = strike.r1_witness_pairs()
        for omitted in range(len(witnesses)):
            almost = seed.add_pairs(tuple(
                pair for index, pair in enumerate(witnesses) if index != omitted
            ))
            self.assertFalse(strike.maps_classes(almost.side_classes(), strike.R1))

    def test_every_raw_row_is_a_deletion_fixed_permutation(self):
        seed, representatives = strike.old_seed()
        vocabularies = tuple(
            strike.row_vocabulary(deleted, seed, representatives)
            for deleted in range(strike.OLD_N)
        )
        self.assertEqual([9, 9, 9, 9, 24, 24], [
            vocabulary["compatible"] for vocabulary in vocabularies
        ])
        self.assertEqual([9, 9, 9, 9, 21, 21], [
            vocabulary["distinct_effects"] for vocabulary in vocabularies
        ])
        for deleted, vocabulary in enumerate(vocabularies):
            self.assertEqual(720, vocabulary["raw"])
            for row in vocabulary["effects"]:
                self.assertEqual(list(range(strike.N)), sorted(row))
                self.assertEqual(deleted, row[deleted])

    def test_independent_dp_forces_all_old_rescuers(self):
        seed, representatives = strike.old_seed()
        vocabularies = strike.independent_row_vocabularies(seed, representatives)
        terminals, layers = strike.independent_terminal_dp(
            seed, representatives, vocabularies
        )
        self.assertEqual((1, 9, 7, 3, 3, 4, 5), layers)
        self.assertEqual(5, len(terminals))
        for blocks in terminals:
            state = strike.Partition(strike.labels_from_blocks(blocks))
            self.assertTrue(all(
                strike.maps_classes(state.side_classes(), rescuer)
                for rescuer in strike.BASE_RESCUERS
            ))


if __name__ == "__main__":
    unittest.main()
