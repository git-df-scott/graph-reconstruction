#!/usr/bin/env python3
"""Standalone hostile verifier for an explicit graph-reconstruction claim.

The checker deliberately imports no campaign modules.  It accepts two graph6
records or a JSON pair, validates the parents, tests parent isomorphism by two
independent routes, constructs every vertex-deleted card, and compares the
decks both by exact canonical labels and by an independent bipartite matching
of card isomorphisms.  Multiplicity is never discarded.

JSON input format:

    {"G": {"order": 4, "edges": [[0, 1], [1, 2]]},
     "H": "C?"}

A graph value can be a graph6 string or an object with ``order`` and ``edges``.
The emitted JSON is the machine-readable certificate.  No hash is used to
decide isomorphism or deck equality; SHA-256 is only an integrity checksum of
the finished certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class ExactGraph:
    adjacency: tuple[int, ...]

    def __post_init__(self) -> None:
        n = len(self.adjacency)
        allowed = (1 << n) - 1
        for vertex, row in enumerate(self.adjacency):
            if not isinstance(row, int) or row < 0:
                raise ValueError("adjacency rows must be nonnegative integers")
            if row & ~allowed:
                raise ValueError("adjacency outside the vertex set")
            if row & (1 << vertex):
                raise ValueError("loops are not allowed")
            for other in range(vertex):
                if bool(row & (1 << other)) != bool(
                    self.adjacency[other] & (1 << vertex)
                ):
                    raise ValueError("adjacency must be symmetric")

    @property
    def n(self) -> int:
        return len(self.adjacency)

    @property
    def degrees(self) -> tuple[int, ...]:
        return tuple(row.bit_count() for row in self.adjacency)

    @property
    def edge_count(self) -> int:
        return sum(self.degrees) // 2

    def edge(self, left: int, right: int) -> bool:
        return bool(self.adjacency[left] & (1 << right))

    def edges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (left, right)
            for left in range(self.n)
            for right in range(left + 1, self.n)
            if self.edge(left, right)
        )

    def delete_vertex(self, removed: int) -> "ExactGraph":
        if not 0 <= removed < self.n:
            raise IndexError(removed)
        kept = tuple(vertex for vertex in range(self.n) if vertex != removed)
        position = {old: new for new, old in enumerate(kept)}
        rows = [0] * len(kept)
        for left_index, old_left in enumerate(kept):
            for old_right in kept:
                if old_left < old_right and self.edge(old_left, old_right):
                    right_index = position[old_right]
                    rows[left_index] |= 1 << right_index
                    rows[right_index] |= 1 << left_index
        return ExactGraph(tuple(rows))

    def permute(self, old_to_new: Iterable[int]) -> "ExactGraph":
        permutation = tuple(old_to_new)
        if sorted(permutation) != list(range(self.n)):
            raise ValueError("not a vertex permutation")
        rows = [0] * self.n
        for left, right in self.edges():
            image_left, image_right = permutation[left], permutation[right]
            rows[image_left] |= 1 << image_right
            rows[image_right] |= 1 << image_left
        return ExactGraph(tuple(rows))

    def edge_mask(self, new_to_old: Iterable[int] | None = None) -> int:
        order = tuple(new_to_old) if new_to_old is not None else tuple(range(self.n))
        if sorted(order) != list(range(self.n)):
            raise ValueError("not a vertex order")
        value = 0
        bit = 0
        for left in range(self.n):
            for right in range(left + 1, self.n):
                if self.edge(order[left], order[right]):
                    value |= 1 << bit
                bit += 1
        return value

    def to_graph6(self) -> str | None:
        if self.n > 62:
            return None
        output = [chr(self.n + 63)]
        value = width = 0
        for right in range(1, self.n):
            for left in range(right):
                value = (value << 1) | int(self.edge(left, right))
                width += 1
                if width == 6:
                    output.append(chr(value + 63))
                    value = width = 0
        if width:
            output.append(chr((value << (6 - width)) + 63))
        return "".join(output)

    def explicit_record(self) -> dict[str, Any]:
        return {
            "order": self.n,
            "edge_count": self.edge_count,
            "edges": [list(edge) for edge in self.edges()],
            "graph6": self.to_graph6(),
        }

    @classmethod
    def from_edges(cls, order: int, edges: Iterable[Iterable[int]]) -> "ExactGraph":
        if not isinstance(order, int) or order < 0:
            raise ValueError("order must be a nonnegative integer")
        rows = [0] * order
        seen: set[tuple[int, int]] = set()
        for raw in edges:
            pair = tuple(raw)
            if len(pair) != 2 or not all(isinstance(value, int) for value in pair):
                raise ValueError("every edge must contain two integer vertices")
            left, right = pair
            if not (0 <= left < order and 0 <= right < order):
                raise ValueError("edge endpoint outside the vertex set")
            if left == right:
                raise ValueError("loops are not allowed")
            edge = tuple(sorted((left, right)))
            if edge in seen:
                raise ValueError("duplicate edge")
            seen.add(edge)
            rows[left] |= 1 << right
            rows[right] |= 1 << left
        return cls(tuple(rows))

    @classmethod
    def from_graph6(cls, record: str) -> "ExactGraph":
        text = record.strip()
        if text.startswith(">>graph6<<"):
            text = text[len(">>graph6<<") :]
        if not text:
            raise ValueError("empty graph6 record")
        order = ord(text[0]) - 63
        if not 0 <= order <= 62:
            raise ValueError("only ordinary graph6 orders 0 through 62 are supported")
        required = order * (order - 1) // 2
        encoded_characters = (required + 5) // 6
        if len(text) - 1 != encoded_characters:
            raise ValueError("graph6 record has the wrong encoded length")
        bits: list[int] = []
        for character in text[1:]:
            value = ord(character) - 63
            if not 0 <= value < 64:
                raise ValueError("invalid graph6 character")
            bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
        if any(bits[required:]):
            raise ValueError("graph6 padding bits must be zero")
        rows = [0] * order
        cursor = 0
        for right in range(1, order):
            for left in range(right):
                if bits[cursor]:
                    rows[left] |= 1 << right
                    rows[right] |= 1 << left
                cursor += 1
        return cls(tuple(rows))


Partition = tuple[tuple[int, ...], ...]


def _initial_partition(graph: ExactGraph) -> Partition:
    cells: dict[int, list[int]] = {}
    for vertex, degree in enumerate(graph.degrees):
        cells.setdefault(degree, []).append(vertex)
    return tuple(tuple(cells[degree]) for degree in sorted(cells))


def _refine(graph: ExactGraph, partition: Partition) -> Partition:
    while True:
        masks = tuple(sum(1 << vertex for vertex in cell) for cell in partition)
        refined: list[tuple[int, ...]] = []
        changed = False
        for cell in partition:
            buckets: dict[tuple[int, ...], list[int]] = {}
            for vertex in cell:
                signature = tuple(
                    (graph.adjacency[vertex] & mask).bit_count() for mask in masks
                )
                buckets.setdefault(signature, []).append(vertex)
            changed |= len(buckets) > 1
            refined.extend(tuple(buckets[key]) for key in sorted(buckets))
        result = tuple(refined)
        if not changed:
            return result
        partition = result


def canonical_label(graph: ExactGraph) -> str:
    """Exact individualization/refinement canonical label."""

    if graph.n == 0:
        return "0:0"
    best: int | None = None

    def visit(partition: Partition) -> None:
        nonlocal best
        partition = _refine(graph, partition)
        target = next(
            (index for index, cell in enumerate(partition) if len(cell) > 1), None
        )
        if target is None:
            order = tuple(cell[0] for cell in partition)
            code = graph.edge_mask(order)
            if best is None or code < best:
                best = code
            return
        cell = partition[target]
        for vertex in cell:
            remainder = tuple(item for item in cell if item != vertex)
            visit(partition[:target] + ((vertex,), remainder) + partition[target + 1 :])

    visit(_initial_partition(graph))
    assert best is not None
    width = max(1, (graph.n * (graph.n - 1) // 2 + 3) // 4)
    return f"{graph.n}:{best:0{width}x}"


def find_isomorphism(
    left: ExactGraph, right: ExactGraph
) -> tuple[int, ...] | None:
    """Exact adjacency backtracker independent of ``canonical_label``."""

    if (
        left.n != right.n
        or left.edge_count != right.edge_count
        or sorted(left.degrees) != sorted(right.degrees)
    ):
        return None
    order = left.n
    by_degree: dict[int, list[int]] = {}
    for vertex, degree in enumerate(right.degrees):
        by_degree.setdefault(degree, []).append(vertex)
    mapping = [-1] * order
    used = [False] * order

    def candidates(source: int) -> list[int]:
        return [
            target
            for target in by_degree[left.degrees[source]]
            if not used[target]
            and all(
                left.edge(source, old_source)
                == right.edge(target, mapping[old_source])
                for old_source in range(order)
                if mapping[old_source] >= 0
            )
        ]

    def search(remaining: tuple[int, ...]) -> bool:
        if not remaining:
            return True
        ranked = [(len(candidates(vertex)), -left.degrees[vertex], vertex) for vertex in remaining]
        count, _negative_degree, source = min(ranked)
        if count == 0:
            return False
        rest = tuple(vertex for vertex in remaining if vertex != source)
        for target in candidates(source):
            mapping[source] = target
            used[target] = True
            if search(rest):
                return True
            used[target] = False
            mapping[source] = -1
        return False

    return tuple(mapping) if search(tuple(range(order))) else None


def canonical_deck(graph: ExactGraph) -> tuple[str, ...]:
    return tuple(sorted(canonical_label(graph.delete_vertex(v)) for v in range(graph.n)))


def compare_label_multisets(left: Iterable[str], right: Iterable[str]) -> bool:
    return Counter(left) == Counter(right)


def independent_deck_matching(
    left: ExactGraph, right: ExactGraph
) -> tuple[tuple[int, int, tuple[int, ...]], ...] | None:
    """Match all deletion occurrences using the adjacency backtracker.

    This route does not inspect canonical labels.  Separate deletion
    occurrences remain separate, so the resulting perfect matching is
    multiplicity-sensitive.
    """

    if left.n != right.n:
        return None
    left_cards = tuple(left.delete_vertex(vertex) for vertex in range(left.n))
    right_cards = tuple(right.delete_vertex(vertex) for vertex in range(right.n))
    witnesses: dict[tuple[int, int], tuple[int, ...]] = {}
    options: dict[int, list[int]] = {}
    for source, card in enumerate(left_cards):
        options[source] = []
        for target, other in enumerate(right_cards):
            witness = find_isomorphism(card, other)
            if witness is not None:
                witnesses[source, target] = witness
                options[source].append(target)
        if not options[source]:
            return None
    matched_right = [-1] * right.n

    def augment(source: int, seen: set[int]) -> bool:
        for target in options[source]:
            if target in seen:
                continue
            seen.add(target)
            if matched_right[target] < 0 or augment(matched_right[target], seen):
                matched_right[target] = source
                return True
        return False

    for source in sorted(range(left.n), key=lambda vertex: len(options[vertex])):
        if not augment(source, set()):
            return None
    pairs = sorted((source, target) for target, source in enumerate(matched_right))
    return tuple((source, target, witnesses[source, target]) for source, target in pairs)


def _counter_record(values: Iterable[str]) -> list[dict[str, Any]]:
    return [
        {"label": label, "multiplicity": multiplicity}
        for label, multiplicity in sorted(Counter(values).items())
    ]


def verify_pair(left: ExactGraph, right: ExactGraph) -> dict[str, Any]:
    same_order = left.n == right.n
    order_valid = same_order and left.n >= 3
    left_label = canonical_label(left)
    right_label = canonical_label(right)
    parent_canonical_equal = left_label == right_label
    parent_mapping = find_isomorphism(left, right)
    parent_backtracking_equal = parent_mapping is not None
    parent_routes_agree = parent_canonical_equal == parent_backtracking_equal

    left_deck = canonical_deck(left)
    right_deck = canonical_deck(right)
    deck_canonical_equal = same_order and left_deck == right_deck
    deck_matching = independent_deck_matching(left, right) if same_order else None
    deck_backtracking_equal = deck_matching is not None
    deck_routes_agree = deck_canonical_equal == deck_backtracking_equal

    if not same_order:
        status = "REJECTED_DIFFERENT_ORDERS"
    elif not order_valid:
        status = "REJECTED_ORDER_BELOW_THREE"
    elif not parent_routes_agree or not deck_routes_agree:
        status = "INTERNAL_VERIFIER_DISAGREEMENT"
    elif parent_backtracking_equal:
        status = "REJECTED_PARENT_ISOMORPHIC"
    elif not deck_canonical_equal:
        status = "REJECTED_DECK_MISMATCH"
    else:
        status = "VERIFIED_COUNTEREXAMPLE"

    left_counter = Counter(left_deck)
    right_counter = Counter(right_deck)
    all_labels = sorted(set(left_counter) | set(right_counter))
    multiplicity_delta = [
        {
            "label": label,
            "G": left_counter[label],
            "H": right_counter[label],
            "delta_G_minus_H": left_counter[label] - right_counter[label],
        }
        for label in all_labels
        if left_counter[label] != right_counter[label]
    ]
    report: dict[str, Any] = {
        "schema": "grc-hostile-ce-certificate-v1",
        "status": status,
        "claim_accepted": status == "VERIFIED_COUNTEREXAMPLE",
        "definition": {
            "simple_undirected": True,
            "same_order": same_order,
            "order_at_least_three": order_valid,
            "nonisomorphic_parents": parent_routes_agree and not parent_backtracking_equal,
            "equal_vertex_decks_with_multiplicity": deck_routes_agree and deck_canonical_equal,
        },
        "graphs": {"G": left.explicit_record(), "H": right.explicit_record()},
        "parent_verification": {
            "route_1": "exact individualization/refinement canonical label",
            "G_label": left_label,
            "H_label": right_label,
            "canonical_labels_equal": parent_canonical_equal,
            "route_2": "independent adjacency-preserving backtracking",
            "isomorphism_mapping_G_to_H": list(parent_mapping) if parent_mapping else None,
            "isomorphic": parent_backtracking_equal,
            "routes_agree": parent_routes_agree,
        },
        "deck_verification": {
            "card_count_G": len(left_deck),
            "card_count_H": len(right_deck),
            "route_1": "sorted exact canonical labels, occurrences retained",
            "G_multiset": _counter_record(left_deck),
            "H_multiset": _counter_record(right_deck),
            "canonical_multisets_equal": deck_canonical_equal,
            "support_sets_equal": set(left_deck) == set(right_deck),
            "multiplicity_delta": multiplicity_delta,
            "route_2": "perfect matching of deletion occurrences using exact card backtracking",
            "backtracking_decks_equal": deck_backtracking_equal,
            "matching": [
                {
                    "G_deleted": source,
                    "H_deleted": target,
                    "card_mapping": list(mapping),
                }
                for source, target, mapping in (deck_matching or ())
            ],
            "routes_agree": deck_routes_agree,
        },
        "hash_role": "integrity only; no hash participates in a mathematical decision",
    }
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    report["certificate_sha256"] = hashlib.sha256(encoded).hexdigest()
    return report


def parse_graph(value: Any) -> ExactGraph:
    if isinstance(value, str):
        return ExactGraph.from_graph6(value)
    if isinstance(value, dict) and "order" in value and "edges" in value:
        return ExactGraph.from_edges(value["order"], value["edges"])
    raise ValueError("graph must be a graph6 string or an {order, edges} object")


def self_test() -> dict[str, Any]:
    cycle4 = ExactGraph.from_edges(4, ((0, 1), (1, 2), (2, 3), (3, 0)))
    cycle4_relabelled = cycle4.permute((2, 0, 3, 1))
    one_edge = ExactGraph.from_graph6("B_")
    two_edge_path = ExactGraph.from_graph6("Bo")
    empty2 = ExactGraph.from_edges(2, ())
    edge2 = ExactGraph.from_edges(2, ((0, 1),))
    cycle6 = ExactGraph.from_edges(6, tuple((i, (i + 1) % 6) for i in range(6)))
    triangles = ExactGraph.from_edges(
        6, ((0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5))
    )
    controls = {
        "isomorphic_equal_decks": verify_pair(cycle4, cycle4_relabelled)["status"],
        "order_two_equal_decks_rejected": verify_pair(empty2, edge2)["status"],
        "same_support_different_multiplicity": verify_pair(one_edge, two_edge_path)["status"],
        "nonisomorphic_same_degree_sequence": verify_pair(cycle6, triangles)["status"],
        "corrupted_deck_rejected": not compare_label_multisets(
            canonical_deck(cycle4), canonical_deck(cycle4)[:-1] + ("CORRUPTED",)
        ),
    }
    expected = {
        "isomorphic_equal_decks": "REJECTED_PARENT_ISOMORPHIC",
        "order_two_equal_decks_rejected": "REJECTED_ORDER_BELOW_THREE",
        "same_support_different_multiplicity": "REJECTED_DECK_MISMATCH",
        "nonisomorphic_same_degree_sequence": "REJECTED_DECK_MISMATCH",
        "corrupted_deck_rejected": True,
    }
    return {"passed": controls == expected, "controls": controls, "expected": expected}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="JSON file containing G and H")
    source.add_argument("--g6", nargs=2, metavar=("G", "H"), help="two graph6 records")
    source.add_argument("--self-test", action="store_true")
    parser.add_argument("--certificate", type=Path, help="write certificate JSON here")
    parser.add_argument("--pretty", action="store_true")
    arguments = parser.parse_args()

    if arguments.self_test:
        report = self_test()
    elif arguments.input:
        payload = json.loads(arguments.input.read_text())
        report = verify_pair(parse_graph(payload["G"]), parse_graph(payload["H"]))
    else:
        report = verify_pair(
            ExactGraph.from_graph6(arguments.g6[0]),
            ExactGraph.from_graph6(arguments.g6[1]),
        )
    rendered = json.dumps(report, indent=2 if arguments.pretty else None, sort_keys=True) + "\n"
    if arguments.certificate:
        arguments.certificate.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
