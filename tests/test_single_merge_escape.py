import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import single_merge_escape as strike


class SingleMergeEscapeTests(unittest.TestCase):
    def test_a4_action_and_merge_orbits(self):
        action = strike.a4_class_action()
        self.assertEqual(12, action["vertex_group_order"])
        self.assertEqual(3, action["class_action_order"])
        self.assertEqual(7, len(action["pair_orbits"]))
        self.assertIn(((0, 1), (0, 2), (1, 2)), action["pair_orbits"])

    def test_old_merge_taxonomy_controls(self):
        matching = strike.old_merge_analysis((0, 1))
        attachment = strike.old_merge_analysis((0, 3))
        enlarged = strike.old_merge_analysis((3, 4))
        self.assertEqual(8, matching["globalizer_count"])
        self.assertEqual(24, matching["generated_group_order"])
        self.assertEqual(4, attachment["globalizer_count"])
        self.assertEqual(8, enlarged["globalizer_count"])
        self.assertEqual(24, enlarged["generated_group_order"])
        self.assertFalse(any(
            record["identity"] or record["side_arrays_equal"]
            for record in (matching, attachment, enlarged)
        ))

    def test_goldilocks_merge_reaches_two_not_zero(self):
        result = strike.analyze_merge((0, 1), raw_replay=True)
        self.assertEqual("IV_GOLDILOCKS", result["taxonomy"])
        self.assertEqual(3, result["r1_dead_terminals"])
        self.assertEqual(2, result["minimum_globalizer_count"])
        self.assertEqual(5038, result["maximum_permutations_killed"])
        self.assertEqual(3, result["raw_s7_minimum_replays"])

    def test_useless_and_regeneration_controls(self):
        useless = strike.analyze_merge((0, 3))
        regeneration = strike.analyze_merge((3, 4))
        self.assertEqual("I_USELESS", useless["taxonomy"])
        self.assertEqual(0, useless["r1_dead_terminals"])
        self.assertEqual("III_REGENERATION_PRONE", regeneration["taxonomy"])
        self.assertEqual(0, regeneration["r1_dead_terminals"])


if __name__ == "__main__":
    unittest.main()
