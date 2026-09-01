import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import double_goldilocks_strike as strike


class DoubleGoldilocksStrikeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = strike.run(raw_replay=True)

    def test_nine_minima_form_three_disjoint_pairs_in_one_a4_orbit(self):
        self.assertEqual(9, self.result["minimum_terminal_count"])
        orbits = self.result["rescue_pair_orbits"]
        self.assertEqual(3, orbits["distinct_pairs"])
        self.assertEqual(1, orbits["a4_orbit_count"])
        self.assertTrue(orbits["all_distinct_pairs_are_disjoint"])
        for record in self.result["minimum_terminals"]:
            self.assertEqual(4, record["generated_subgroup_order"])
            self.assertEqual(48, record["normalizer_order_s7"])
            self.assertEqual(48, record["rescue_pair_stabilizer_order_s7"])
            self.assertEqual((4, 5, 6), record["fixed_vertices"])
            self.assertTrue(all(record["old_rescuer_witness_failures"].values()))

    def test_all_cross_terminal_joins_regenerate(self):
        joins = self.result["pairwise_joins"]
        self.assertEqual(36, joins["pair_count"])
        self.assertEqual(27, joins["cross_merge_pair_count"])
        self.assertEqual(27, joins["cross_disjoint_residual_pairs"])
        self.assertEqual(24, joins["cross_minimum_globalizers"])
        self.assertEqual(0, joins["cross_zero_globalizer_joins"])
        self.assertEqual(27, joins["cross_identity_joins"])

    def test_simultaneous_csp_forces_identity(self):
        csp = self.result["simultaneous_csp"]
        self.assertEqual((1, 17, 59, 40, 42, 48, 54), csp["layers"])
        self.assertEqual(54, csp["terminal_count"])
        self.assertEqual(1, csp["minimum_globalizers"])
        self.assertEqual(0, csp["zero_globalizer_terminals"])
        self.assertEqual(54, csp["identity_terminals"])
        self.assertEqual(5039, csp["maximum_s7_killed"])
        self.assertEqual(
            (((0, 1, 2), 40), ((0, 1, 3), 40),
             ((0, 2, 3), 40), ((1, 2, 3), 40)),
            csp["identity_forcing_cores"],
        )
        strongest = csp["strongest_terminal"]
        self.assertEqual(10, strongest["class_count"])
        self.assertEqual((strike.IDENTITY,), strongest["globalizers"])

    def test_no_binary_realization_trigger(self):
        self.assertEqual("EXHAUSTIVE_NO_ZERO_GLOBALIZER", self.result["status"])
        self.assertEqual("NO", self.result["grc_ce"])


if __name__ == "__main__":
    unittest.main()
