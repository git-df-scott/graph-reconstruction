#!/usr/bin/env python3
"""Exact dual-deck audit of Kocay's smallest nonreconstructible 3-graphs.

The source construction is the pair X^n,Y^n from W. L. Kocay,
"A family of nonreconstructible hypergraphs", JCTB 42 (1987), as restated
explicitly by Cooper--Okur (2026).  This script expands the polynomial
definition into block lists and compares both vertex/point deletion decks and
edge/block deletion decks under unrestricted point permutations.

No digest is used as an isomorphism decision.  The exact checker below is a
degree/codegree-refined backtracking search on point bijections; at a leaf it
compares the complete transported block set.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


Block = tuple[int, ...]


@dataclass(frozen=True)
class Hypergraph:
    points: tuple[int, ...]
    blocks: tuple[Block, ...]

    def __post_init__(self) -> None:
        point_set = set(self.points)
        normalized = tuple(sorted(tuple(sorted(block)) for block in self.blocks))
        if normalized != self.blocks:
            raise ValueError("blocks must be internally and lexicographically sorted")
        if any(not set(block) <= point_set for block in self.blocks):
            raise ValueError("block uses a point outside the point set")

    def delete_point(self, point: int) -> "Hypergraph":
        """Standard induced-hypergraph deletion: discard incident blocks."""
        return Hypergraph(
            tuple(x for x in self.points if x != point),
            tuple(block for block in self.blocks if point not in block),
        )

    def delete_incidence_row(self, point: int) -> "Hypergraph":
        """Two-sorted incidence deletion: retain every block column.

        Incident blocks shrink and repetitions are retained because the block
        objects remain distinct in the incidence structure.
        """
        return Hypergraph(
            tuple(x for x in self.points if x != point),
            tuple(sorted(tuple(x for x in block if x != point) for block in self.blocks)),
        )

    def delete_block(self, index: int) -> "Hypergraph":
        return Hypergraph(self.points, self.blocks[:index] + self.blocks[index + 1 :])


def make_hypergraph(points: Iterable[int], blocks: Iterable[Iterable[int]]) -> Hypergraph:
    return Hypergraph(tuple(sorted(points)), tuple(sorted(set(tuple(sorted(b)) for b in blocks))))


def _mod_vertex(value: int, modulus: int) -> int:
    residue = value % modulus
    return modulus if residue == 0 else residue


def _expand_residue_block(block: Block, n: int, r: int) -> set[Block]:
    """Expand E_r^n multiplicatively on a square-free block monomial."""
    modulus = 1 << n
    fibers = [
        tuple(x for x in range(1, modulus + 1) if (x - vertex) % (1 << r) == 0)
        for vertex in block
    ]
    return {tuple(sorted(choice)) for choice in itertools.product(*fibers) if len(set(choice)) == len(block)}


def _lift_blocks(blocks: set[Block], old_n: int, bit: int) -> set[Block]:
    modulus = 1 << (old_n + 1)
    return {
        tuple(sorted(_mod_vertex(2 * vertex - bit, modulus) for vertex in block))
        for block in blocks
    }


def kocay_pair(n: int = 3) -> tuple[Hypergraph, Hypergraph]:
    """Return Kocay's explicit hypomorphic nonisomorphic pair X^n,Y^n."""
    if n < 3:
        raise ValueError("Kocay's family starts at n=3")
    base_modulus = 8
    cycle = {
        tuple(sorted((_mod_vertex(i - 1, 8), i, _mod_vertex(i + 1, 8))))
        for i in range(1, 9)
    }
    twisted = {
        tuple(sorted((_mod_vertex(i - 3, 8), i, _mod_vertex(i + 3, 8))))
        for i in range(1, 9)
    }
    g_diag = cycle | twisted
    g_two = {
        tuple(sorted((i, _mod_vertex(i + 2, base_modulus), _mod_vertex(i + 4, base_modulus))))
        for i in range(1, 5)
    }

    components: dict[int, set[Block]] = {2: g_two, 3: g_diag}
    for level in range(4, n + 1):
        for key in tuple(components):
            components[key] = _lift_blocks(components[key], level - 1, 0) | _lift_blocks(
                components[key], level - 1, 1
            )
        # G_level^level is expanded directly from G_3^3.
        components[level] = set().union(*(_expand_residue_block(block, level, 3) for block in g_diag))
    gamma = set().union(*(components[k] for k in range(2, n + 1)))

    e1 = tuple(x for x in range(1, (1 << n) + 1) if (x - 1) % 4 == 0)
    e2 = tuple(x for x in range(1, (1 << n) + 1) if (x - 2) % 4 == 0)
    e3 = tuple(x for x in range(1, (1 << n) + 1) if (x - 3) % 4 == 0)
    e4 = tuple(x for x in range(1, (1 << n) + 1) if (x - 4) % 4 == 0)
    m0 = {(0, min(a, b), max(a, b)) for left, right in ((e1, e2), (e3, e4)) for a in left for b in right}
    m1 = {(0, min(a, b), max(a, b)) for left, right in ((e1, e4), (e2, e3)) for a in left for b in right}
    points = range(0, (1 << n) + 1)
    return make_hypergraph(points, gamma | m0), make_hypergraph(points, gamma | m1)


def complete_uniform_complement(h: Hypergraph, rank: int = 3) -> Hypergraph:
    universe = set(itertools.combinations(h.points, rank))
    return make_hypergraph(h.points, universe - set(h.blocks))


def degree_data(h: Hypergraph) -> tuple[dict[int, int], dict[tuple[int, int], int]]:
    degrees = {point: 0 for point in h.points}
    codegrees = {(a, b): 0 for a in h.points for b in h.points if a < b}
    for block in h.blocks:
        for point in block:
            degrees[point] += 1
        for pair in itertools.combinations(block, 2):
            codegrees[pair] += 1
    return degrees, codegrees


def invariant(h: Hypergraph) -> tuple[object, ...]:
    degrees, codegrees = degree_data(h)
    signatures = []
    for point in h.points:
        local = [codegrees[tuple(sorted((point, other)))] for other in h.points if other != point]
        signatures.append((degrees[point], tuple(sorted(local))))
    return (
        len(h.points),
        len(h.blocks),
        tuple(sorted(Counter(map(len, h.blocks)).items())),
        tuple(sorted(degrees.values())),
        tuple(sorted(signatures)),
    )


def find_isomorphism(left: Hypergraph, right: Hypergraph) -> dict[int, int] | None:
    """Exact sort-preserving hypergraph isomorphism, independent of hashes."""
    if invariant(left) != invariant(right):
        return None
    ld, lc = degree_data(left)
    rd, rc = degree_data(right)
    lblocks = Counter(left.blocks)
    rblocks = Counter(right.blocks)
    mapping: dict[int, int] = {}
    used: set[int] = set()

    def pair_code(table: dict[tuple[int, int], int], a: int, b: int) -> int:
        return table[tuple(sorted((a, b)))]

    right_by_degree: dict[int, tuple[int, ...]] = defaultdict(tuple)
    for degree in set(rd.values()):
        right_by_degree[degree] = tuple(x for x in right.points if rd[x] == degree)

    def partial_blocks_ok() -> bool:
        mapped_left = set(mapping)
        for block in lblocks:
            if set(block) <= mapped_left and tuple(sorted(mapping[x] for x in block)) not in rblocks:
                return False
        return True

    def candidates(point: int) -> list[int]:
        return [
            target
            for target in right_by_degree[ld[point]]
            if target not in used
            and all(pair_code(lc, point, old) == pair_code(rc, target, mapping[old]) for old in mapping)
        ]

    def search() -> bool:
        if len(mapping) == len(left.points):
            transported = Counter(
                {tuple(sorted(mapping[x] for x in block)): multiplicity for block, multiplicity in lblocks.items()}
            )
            return transported == rblocks
        choices = [(len(candidates(point)), -ld[point], point) for point in left.points if point not in mapping]
        count, _negative_degree, point = min(choices)
        if count == 0:
            return False
        for target in candidates(point):
            mapping[point] = target
            used.add(target)
            if partial_blocks_ok() and search():
                return True
            used.remove(target)
            del mapping[point]
        return False

    return dict(mapping) if search() else None


def exact_deck_types(cards: Iterable[Hypergraph]) -> list[dict[str, object]]:
    """Classify cards exactly by pairwise isomorphism against representatives."""
    classes: list[dict[str, object]] = []
    buckets: dict[tuple[object, ...], list[int]] = defaultdict(list)
    for card in cards:
        inv = invariant(card)
        found = None
        for index in buckets[inv]:
            if find_isomorphism(card, classes[index]["representative"]) is not None:
                found = index
                break
        if found is None:
            found = len(classes)
            classes.append({"representative": card, "multiplicity": 0})
            buckets[inv].append(found)
        classes[found]["multiplicity"] += 1
    return classes


class ExactTypeRegistry:
    """Assign stable-in-this-run exact isomorphism class IDs."""

    def __init__(self) -> None:
        self.representatives: list[Hypergraph] = []
        self.buckets: dict[tuple[object, ...], list[int]] = defaultdict(list)

    def identify(self, h: Hypergraph) -> int:
        inv = invariant(h)
        for index in self.buckets[inv]:
            if find_isomorphism(h, self.representatives[index]) is not None:
                return index
        index = len(self.representatives)
        self.representatives.append(h)
        self.buckets[inv].append(index)
        return index


def _deck_signature(cards: Iterable[Hypergraph], registry: ExactTypeRegistry) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(Counter(registry.identify(card) for card in cards).items()))


def kocay_module_family() -> tuple[Hypergraph, ...]:
    """The six-dimensional complete-residue-pair trade space at n=3.

    The fixed core is Gamma_3.  Each generator adds every 0ab block between
    one pair of the four mod-4 residue classes.  Kocay's X and Y are masks
    001001 and 100010 in the lexicographic pair ordering.
    """
    x, _y = kocay_pair(3)
    fixed = {block for block in x.blocks if 0 not in block}
    residue_classes = {
        residue: tuple(point for point in range(1, 9) if (point - residue) % 4 == 0)
        for residue in range(1, 5)
    }
    class_pairs = tuple(itertools.combinations(range(1, 5), 2))
    modules = []
    for first, second in class_pairs:
        modules.append(
            {(0, min(a, b), max(a, b)) for a in residue_classes[first] for b in residue_classes[second]}
        )
    family = []
    for mask in range(1 << len(modules)):
        blocks = set(fixed)
        for bit, module in enumerate(modules):
            if mask & (1 << bit):
                blocks |= module
        family.append(make_hypergraph(range(9), blocks))
    return tuple(family)


def structured_trade_search() -> dict[str, object]:
    family = kocay_module_family()
    induced_registry = ExactTypeRegistry()
    row_registry = ExactTypeRegistry()
    block_registry = ExactTypeRegistry()
    parent_registry = ExactTypeRegistry()
    induced_signatures = []
    row_signatures = []
    block_signatures = []
    parent_types = []
    for h in family:
        induced_signatures.append(
            _deck_signature((h.delete_point(p) for p in h.points), induced_registry)
        )
        row_signatures.append(
            _deck_signature((h.delete_incidence_row(p) for p in h.points), row_registry)
        )
        block_signatures.append(
            _deck_signature((h.delete_block(i) for i in range(len(h.blocks))), block_registry)
        )
        parent_types.append(parent_registry.identify(h))

    induced_groups: dict[tuple[tuple[int, int], ...], list[int]] = defaultdict(list)
    row_groups: dict[tuple[tuple[int, int], ...], list[int]] = defaultdict(list)
    block_groups: dict[tuple[tuple[int, int], ...], list[int]] = defaultdict(list)
    bideck_groups: dict[tuple[object, ...], list[int]] = defaultdict(list)
    for mask in range(len(family)):
        induced_groups[induced_signatures[mask]].append(mask)
        row_groups[row_signatures[mask]].append(mask)
        block_groups[block_signatures[mask]].append(mask)
        bideck_groups[(row_signatures[mask], block_signatures[mask])].append(mask)

    induced_collisions = []
    row_collisions = []
    block_collisions = []
    dual_collisions = []
    for group in induced_groups.values():
        if len(group) < 2:
            continue
        for left, right in itertools.combinations(group, 2):
            if parent_types[left] != parent_types[right]:
                induced_collisions.append((left, right))
    for group in row_groups.values():
        if len(group) < 2:
            continue
        for left, right in itertools.combinations(group, 2):
            if parent_types[left] != parent_types[right]:
                row_collisions.append((left, right))
                if block_signatures[left] == block_signatures[right]:
                    dual_collisions.append((left, right))
    for group in block_groups.values():
        if len(group) < 2:
            continue
        for left, right in itertools.combinations(group, 2):
            if parent_types[left] != parent_types[right]:
                block_collisions.append((left, right))
    return {
        "family_size": len(family),
        "module_count": 6,
        "parent_isomorphism_types": len(set(parent_types)),
        "induced_point_card_isomorphism_types": len(induced_registry.representatives),
        "incidence_row_card_isomorphism_types": len(row_registry.representatives),
        "block_card_isomorphism_types": len(block_registry.representatives),
        "induced_point_deck_classes": len(induced_groups),
        "incidence_row_deck_classes": len(row_groups),
        "block_deck_classes": len(block_groups),
        "bideck_classes": len(bideck_groups),
        "nonisomorphic_induced_point_deck_collision_pairs": induced_collisions,
        "nonisomorphic_induced_point_deck_collision_count": len(induced_collisions),
        "nonisomorphic_incidence_row_deck_collision_pairs": row_collisions,
        "nonisomorphic_incidence_row_deck_collision_count": len(row_collisions),
        "nonisomorphic_block_deck_collision_pairs": block_collisions,
        "nonisomorphic_block_deck_collision_count": len(block_collisions),
        "nonisomorphic_dual_deck_collision_pairs": dual_collisions,
        "nonisomorphic_dual_deck_collision_count": len(dual_collisions),
    }


def compare_decks(left_cards: Iterable[Hypergraph], right_cards: Iterable[Hypergraph]) -> dict[str, object]:
    left_types = exact_deck_types(left_cards)
    right_types = exact_deck_types(right_cards)
    matched_right: set[int] = set()
    matched = []
    left_only = []
    for left_type in left_types:
        target = None
        for index, right_type in enumerate(right_types):
            if index in matched_right:
                continue
            if find_isomorphism(left_type["representative"], right_type["representative"]) is not None:
                target = index
                break
        if target is None:
            left_only.append(left_type)
        else:
            matched_right.add(target)
            matched.append((left_type, right_types[target]))
    right_only = [item for index, item in enumerate(right_types) if index not in matched_right]
    equal = not left_only and not right_only and all(a["multiplicity"] == b["multiplicity"] for a, b in matched)
    return {
        "equal": equal,
        "left_type_multiplicities": sorted(item["multiplicity"] for item in left_types),
        "right_type_multiplicities": sorted(item["multiplicity"] for item in right_types),
        "matched_multiplicity_pairs": sorted((a["multiplicity"], b["multiplicity"]) for a, b in matched),
        "left_only_multiplicities": sorted(item["multiplicity"] for item in left_only),
        "right_only_multiplicities": sorted(item["multiplicity"] for item in right_only),
        "left_type_count": len(left_types),
        "right_type_count": len(right_types),
    }


def serialize(h: Hypergraph) -> str:
    return ";".join(",".join(map(str, block)) for block in h.blocks)


def audit(n: int) -> dict[str, object]:
    x, y = kocay_pair(n)
    parent_witness = find_isomorphism(x, y)
    induced_point = compare_decks(
        (x.delete_point(p) for p in x.points), (y.delete_point(p) for p in y.points)
    )
    incidence_row = compare_decks(
        (x.delete_incidence_row(p) for p in x.points),
        (y.delete_incidence_row(p) for p in y.points),
    )
    block = compare_decks(
        (x.delete_block(i) for i in range(len(x.blocks))),
        (y.delete_block(i) for i in range(len(y.blocks))),
    )
    xc, yc = complete_uniform_complement(x), complete_uniform_complement(y)
    complement_induced_point = compare_decks(
        (xc.delete_point(p) for p in xc.points), (yc.delete_point(p) for p in yc.points)
    )
    complement_incidence_row = compare_decks(
        (xc.delete_incidence_row(p) for p in xc.points),
        (yc.delete_incidence_row(p) for p in yc.points),
    )
    complement_block = compare_decks(
        (xc.delete_block(i) for i in range(len(xc.blocks))),
        (yc.delete_block(i) for i in range(len(yc.blocks))),
    )
    return {
        "grc_ce": "NO",
        "family": "Kocay X^n,Y^n",
        "n_parameter": n,
        "points": len(x.points),
        "rank": 3,
        "x_blocks": len(x.blocks),
        "y_blocks": len(y.blocks),
        "parents_isomorphic": parent_witness is not None,
        "induced_hypergraph_point_decks": induced_point,
        "incidence_matrix_row_decks": incidence_row,
        "block_decks": block,
        "complement_blocks": len(xc.blocks),
        "complement_parents_isomorphic": find_isomorphism(xc, yc) is not None,
        "complement_induced_hypergraph_point_decks": complement_induced_point,
        "complement_incidence_matrix_row_decks": complement_incidence_row,
        "complement_block_decks": complement_block,
        "x_sha256": hashlib.sha256(serialize(x).encode()).hexdigest(),
        "y_sha256": hashlib.sha256(serialize(y).encode()).hexdigest(),
        "x_blocks_explicit": x.blocks,
        "y_blocks_explicit": y.blocks,
    }


def run(n: int, include_structured_search: bool = True) -> dict[str, object]:
    result = audit(n)
    if include_structured_search:
        if n != 3:
            raise ValueError("the structured module search is currently the exact n=3 source space")
        result["structured_trade_search"] = structured_trade_search()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--output")
    parser.add_argument("--skip-structured-search", action="store_true")
    args = parser.parse_args()
    result = run(args.n, not args.skip_structured_search)
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    print(payload)
