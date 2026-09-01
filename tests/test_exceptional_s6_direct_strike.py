import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import exceptional_s6_direct_strike as strike
import verify_exceptional_s6_direct as verifier


class ExceptionalS6DirectStrikeTests(unittest.TestCase):
    def test_outer_group_laws(self):
        result = strike.verify_outer_group_laws()
        self.assertEqual(518400, result["pairs_replayed"])
        self.assertTrue(result["homomorphism"])
        self.assertTrue(result["involution"])
        self.assertEqual(720, result["images_distinct"])

    def test_direct_fifteen_orbitals(self):
        result = strike.direct_fifteen_classification()
        self.assertEqual(2, result["unordered_pair_orbitals"])
        self.assertEqual([45, 60], result["orbital_sizes"])
        self.assertEqual(4, result["invariant_graphs"])
        self.assertEqual(0, result["counterexamples"])

    def test_complete_combined_domain(self):
        result = strike.classify_combined_domain()
        self.assertEqual(15, result["unordered_pair_orbitals"])
        self.assertEqual(32768, result["raw_invariant_graphs"])
        self.assertEqual(14912, result["stable_deck_quotient_classes"])
        self.assertEqual(0, result["nonisomorphic_deck_collisions"])

    def test_s6_subgroup_and_gassmann_classification(self):
        result = strike.subgroup_classification()
        self.assertEqual(56, result["subgroup_conjugacy_classes"])
        self.assertEqual(2, result["outer_balanced_nonconjugate_directed_classes"])
        self.assertEqual(1, result["outer_balanced_unordered_pairs"])
        self.assertEqual(4, result["unique_pair_order"])
        self.assertEqual(180, result["coset_degree"])

    def test_independent_raw_replay(self):
        result = verifier.raw_replay()
        self.assertTrue(result["all_actions_are_bijections"])
        self.assertTrue(result["orbitals_disjoint"])
        self.assertTrue(result["orbitals_cover_all_unordered_pairs"])
        self.assertEqual(861, result["orbital_edge_total"])
        self.assertEqual(0, result["unrescued_pairs"])


if __name__ == "__main__":
    unittest.main()
