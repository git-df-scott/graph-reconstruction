import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import same_deck
import local_gluing_search as search


class LocalGluingTests(unittest.TestCase):
    def test_rejects_malformed_local_maps(self):
        valid = tuple(tuple(range(4)) for _ in range(4))
        malformed = list(valid)
        malformed[1] = (1, 0, 2, 3)
        with self.assertRaisesRegex(ValueError, "does not fix"):
            search.edge_partition(4, tuple(malformed))
        g, h = search.instantiate(4, *search.edge_partition(4, valid), (0,) * 6)
        self.assertFalse(search.verify_local_maps(g, h, tuple(malformed)))

    def test_equations_imply_equal_decks(self):
        rng = random.Random(17)
        maps = search.random_local_maps(7, 1, rng)
        edges, roots, classes = search.edge_partition(7, maps)
        values = tuple(rng.getrandbits(1) for _ in classes)
        g, h = search.instantiate(7, edges, roots, classes, values)
        self.assertTrue(search.verify_local_maps(g, h, maps))
        self.assertTrue(same_deck(g, h))
        permutation = search.universal_edge_class_isomorphism(7, edges, roots, classes)
        if permutation is not None:
            self.assertTrue(
                all(
                    g.edge(u, v) == h.edge(permutation[u], permutation[v])
                    for u in range(7)
                    for v in range(u + 1, 7)
                )
            )

    def test_local_maps_can_all_fail_while_an_external_global_map_survives(self):
        maps = (
            (0, 1, 2, 3, 5, 4),
            (0, 1, 3, 2, 4, 5),
            (0, 3, 2, 1, 4, 5),
            (0, 2, 1, 3, 4, 5),
            (5, 1, 2, 3, 4, 0),
            (4, 1, 2, 3, 0, 5),
        )
        edges, roots, classes = search.edge_partition(6, maps)
        self.assertEqual(7, len(classes))
        slots = len(edges)
        positions = {edge: i for i, edge in enumerate(edges)}
        for permutation in maps:
            self.assertFalse(
                all(
                    classes[roots[positions[edge]]]
                    == classes[
                        roots[
                            slots
                            + positions[
                                tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
                            ]
                        ]
                    ]
                    for edge in edges
                )
            )
        self.assertEqual(
            tuple(range(6)),
            search.universal_edge_class_isomorphism(6, edges, roots, classes),
        )
        side_classes = search.edge_class_arrays(edges, roots, classes)
        conditions = search.parent_permutation_conditions(6, edges, roots, classes)
        exact = [permutation for permutation, pairs in conditions if not pairs]
        self.assertIn(tuple(range(6)), exact)
        self.assertTrue(all(permutation not in exact for permutation in maps))
        self.assertIsNone(search.separating_binary_assignment(len(classes), conditions))
        identity_pairs = search.permutation_class_pairs(
            6, edges, side_classes, tuple(range(6))
        )
        self.assertEqual(frozenset(), identity_pairs)

    def test_length_two_minimum_rescue_primitive(self):
        maps = (
            (0, 2, 3, 1, 4, 5),
            (4, 1, 2, 5, 0, 3),
            (4, 1, 2, 5, 0, 3),
            (5, 2, 1, 3, 4, 0),
            (0, 5, 1, 3, 4, 2),
            (0, 2, 1, 4, 3, 5),
        )
        edges, roots, classes = search.edge_partition(6, maps)
        self.assertEqual(3, len(classes))
        conditions = search.parent_permutation_conditions(6, edges, roots, classes)
        exact = tuple(permutation for permutation, pairs in conditions if not pairs)
        self.assertEqual(
            (
                (0, 2, 1, 3, 4, 5),
                (4, 1, 2, 5, 0, 3),
            ),
            exact,
        )
        self.assertIsNone(search.separating_binary_assignment(len(classes), conditions))
        for mask in range(1 << len(classes)):
            values = tuple((mask >> bit) & 1 for bit in range(len(classes)))
            g, h = search.instantiate(6, edges, roots, classes, values)
            self.assertTrue(same_deck(g, h))
            self.assertTrue(search.is_isomorphic(g, h))

    def test_multiple_card_map_families_preserve_each_family(self):
        first = (
            (0, 2, 3, 1, 4, 5),
            (4, 1, 2, 5, 0, 3),
            (4, 1, 2, 5, 0, 3),
            (5, 2, 1, 3, 4, 0),
            (0, 5, 1, 3, 4, 2),
            (0, 2, 1, 4, 3, 5),
        )
        twist = (0, 1, 2, 4, 3, 5)
        # Keep the test independent of the census helper.
        second_rows = [[0] * 6 for _ in range(6)]
        for deleted, permutation in enumerate(first):
            for source in range(6):
                second_rows[twist[deleted]][twist[source]] = twist[permutation[source]]
        second = tuple(tuple(row) for row in second_rows)
        edges, roots, classes = search.edge_partition_families(6, (first, second))
        values = tuple(index & 1 for index in range(len(classes)))
        g, h = search.instantiate(6, edges, roots, classes, values)
        self.assertTrue(search.verify_local_maps(g, h, first))
        self.assertTrue(search.verify_local_maps(g, h, second))
        self.assertTrue(same_deck(g, h))

    def test_disjoint_rescue_twist_collapses_to_one_class(self):
        primitive = (
            (0, 2, 3, 1, 4, 5),
            (4, 1, 2, 5, 0, 3),
            (4, 1, 2, 5, 0, 3),
            (5, 2, 1, 3, 4, 0),
            (0, 5, 1, 3, 4, 2),
            (0, 2, 1, 4, 3, 5),
        )
        twist = (0, 1, 3, 2, 4, 5)
        rows = [[0] * 6 for _ in range(6)]
        for deleted, permutation in enumerate(primitive):
            for source in range(6):
                rows[twist[deleted]][twist[source]] = twist[permutation[source]]
        second = tuple(tuple(row) for row in rows)
        edges, roots, classes = search.edge_partition_families(
            6, (primitive, second)
        )
        self.assertEqual(1, len(classes))
        conditions = search.parent_permutation_conditions(6, edges, roots, classes)
        self.assertEqual(720, sum(not pairs for _permutation, pairs in conditions))
        self.assertIsNone(search.separating_binary_assignment(len(classes), conditions))

    def test_five_vertex_overlap_collapses_to_one_class(self):
        primitive = (
            (0, 2, 3, 1, 4, 5),
            (4, 1, 2, 5, 0, 3),
            (4, 1, 2, 5, 0, 3),
            (5, 2, 1, 3, 4, 0),
            (0, 5, 1, 3, 4, 2),
            (0, 2, 1, 4, 3, 5),
        )
        rescuers = ((0, 2, 1, 3, 4, 5), (4, 1, 2, 5, 0, 3))

        def lift(block, outside_rescuer):
            reverse = {actual: label for label, actual in enumerate(block)}
            outside = next(vertex for vertex in range(7) if vertex not in block)
            result = []
            for deleted in range(7):
                local = outside_rescuer if deleted == outside else primitive[reverse[deleted]]
                permutation = list(range(7))
                for label, actual in enumerate(block):
                    permutation[actual] = block[local[label]]
                result.append(tuple(permutation))
            return tuple(result)

        first = lift((0, 1, 2, 3, 4, 5), rescuers[0])
        second = lift((0, 1, 2, 3, 4, 6), rescuers[1])
        _edges, _roots, classes = search.edge_partition_families(7, (first, second))
        self.assertEqual(1, len(classes))

    def test_resilient_double_transposition_lift(self):
        lift = (
            (0, 1, 3, 2, 5, 4, 6),
            (0, 1, 3, 2, 5, 4, 6),
            (3, 4, 2, 0, 1, 5, 6),
            (2, 5, 0, 3, 4, 1, 6),
            (2, 5, 0, 3, 4, 1, 6),
            (3, 4, 2, 0, 1, 5, 6),
            (0, 1, 3, 2, 5, 4, 6),
        )
        edges, roots, classes = search.edge_partition(7, lift)
        self.assertEqual(7, len(classes))
        conditions = search.parent_permutation_conditions(7, edges, roots, classes)
        exact = tuple(permutation for permutation, pairs in conditions if not pairs)
        self.assertEqual(
            (
                (0, 1, 3, 2, 5, 4, 6),
                (2, 5, 0, 3, 4, 1, 6),
                (3, 4, 2, 0, 1, 5, 6),
            ),
            exact,
        )
        self.assertIsNone(search.separating_binary_assignment(len(classes), conditions))

    def test_resilient_disjoint_rescue_twist_becomes_side_symmetric(self):
        lift = (
            (0, 1, 3, 2, 5, 4, 6),
            (0, 1, 3, 2, 5, 4, 6),
            (3, 4, 2, 0, 1, 5, 6),
            (2, 5, 0, 3, 4, 1, 6),
            (2, 5, 0, 3, 4, 1, 6),
            (3, 4, 2, 0, 1, 5, 6),
            (0, 1, 3, 2, 5, 4, 6),
        )
        twist = (0, 4, 2, 3, 5, 1, 6)
        rows = [[0] * 7 for _ in range(7)]
        for deleted, permutation in enumerate(lift):
            for source in range(7):
                rows[twist[deleted]][twist[source]] = twist[permutation[source]]
        second = tuple(tuple(row) for row in rows)
        edges, roots, classes = search.edge_partition_families(7, (lift, second))
        self.assertEqual(5, len(classes))
        side_classes = search.edge_class_arrays(edges, roots, classes)
        self.assertEqual(side_classes[0], side_classes[1])
        conditions = search.parent_permutation_conditions(7, edges, roots, classes)
        self.assertEqual(36, sum(not pairs for _permutation, pairs in conditions))
        self.assertIsNone(search.separating_binary_assignment(len(classes), conditions))

    def test_nine_class_resilient_lift(self):
        lift = (
            (0, 2, 3, 1, 4, 5, 6),
            (3, 1, 0, 2, 4, 5, 6),
            (1, 3, 2, 0, 4, 5, 6),
            (2, 0, 1, 3, 4, 5, 6),
            (1, 3, 2, 0, 4, 5, 6),
            (1, 3, 2, 0, 4, 5, 6),
            (0, 2, 3, 1, 4, 5, 6),
        )
        edges, roots, classes = search.edge_partition(7, lift)
        self.assertEqual(9, len(classes))
        conditions = search.parent_permutation_conditions(7, edges, roots, classes)
        exact = tuple(permutation for permutation, pairs in conditions if not pairs)
        self.assertEqual(
            (
                (0, 2, 3, 1, 4, 5, 6),
                (1, 3, 2, 0, 4, 5, 6),
                (2, 0, 1, 3, 4, 5, 6),
                (3, 1, 0, 2, 4, 5, 6),
            ),
            exact,
        )
        self.assertIsNone(search.separating_binary_assignment(len(classes), conditions))


if __name__ == "__main__":
    unittest.main()
