import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import same_deck
import local_gluing_search as search


class LocalGluingTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
