#!/usr/bin/env python3
"""Exact two-sorted incidence strike from the exceptional-S6 Gassmann pair.

The two row carriers are S6/H and S6/K, where H and K are the unique
outer-balanced nonconjugate V4 pair.  The common column carrier is the union
of the ordinary and exceptional six-point actions.  Each side has six cross
orbitals, hence 64 invariant incidence matrices.  We add a clique on the 12
columns and no row-row edges, then compare the complete row/column deletion
decks exactly.

Matrix isomorphism is certified directly as weighted-hypergraph isomorphism:
an arbitrary column permutation must carry the multiset of row neighbourhoods
to the other multiset.  A recursive restriction-histogram test is necessary
and sufficient and does not rely on hashes.
"""

from __future__ import annotations

import itertools
import json
import resource
import time
from collections import Counter, defaultdict
from functools import lru_cache

import exceptional_s6_direct_strike as exceptional
import outer_s6_strike as outer


IDENTITY = tuple(range(6))
H_GENERATORS = ((1, 0, 3, 2, 4, 5), (2, 3, 0, 1, 4, 5))
K_GENERATORS = ((1, 0, 3, 2, 4, 5), (1, 0, 2, 3, 5, 4))


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[i]] for i in range(6))


def generated_subgroup(generators: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    seen = {IDENTITY}
    frontier = [IDENTITY]
    steps = generators + tuple(exceptional.inverse(g) for g in generators)
    while frontier:
        item = frontier.pop()
        for step in steps:
            image = compose(item, step)
            if image not in seen:
                seen.add(image)
                frontier.append(image)
    return tuple(sorted(seen))


def column_action(group_element: tuple[int, ...], column: int) -> int:
    if column < 6:
        return group_element[column]
    return 6 + exceptional.beta_table()[group_element][column - 6]


def subgroup_column_orbits(subgroup: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(12))
    result = []
    while unseen:
        seed = min(unseen)
        orbit = tuple(sorted({column_action(g, seed) for g in subgroup}))
        unseen -= set(orbit)
        result.append(orbit)
    return tuple(result)


def coset_data(subgroup: tuple[tuple[int, ...], ...]):
    position = {g: i for i, g in enumerate(outer.PERMUTATIONS)}
    unseen = set(outer.PERMUTATIONS)
    cosets = []
    owner = {}
    while unseen:
        representative = min(unseen)
        coset = frozenset(compose(representative, h) for h in subgroup)
        index = len(cosets)
        cosets.append((representative, coset))
        for element in coset:
            owner[element] = index
        unseen -= coset
    assert len(cosets) == 180 and len(owner) == 720
    identity_coset = owner[IDENTITY]
    return position, tuple(cosets), owner, identity_coset


def orbital_rows(subgroup: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    _position, cosets, owner, identity_coset = coset_data(subgroup)
    assert identity_coset == 0
    orbitals = []
    for column_orbit in subgroup_column_orbits(subgroup):
        seed = column_orbit[0]
        rows = [0] * 180
        for g in outer.PERMUTATIONS:
            row = owner[g]
            column = column_action(g, seed)
            rows[row] |= 1 << column
        assert rows[0] == sum(1 << c for c in column_orbit)
        orbitals.append(tuple(rows))
    assert len(orbitals) == 6
    return tuple(orbitals)


def matrices(subgroup: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    orbitals = orbital_rows(subgroup)
    result = []
    for mask in range(64):
        rows = tuple(
            sum(orbital[row] for bit, orbital in enumerate(orbitals) if mask & (1 << bit))
            for row in range(180)
        )
        result.append(rows)
    return tuple(result)


def delete_row(rows: tuple[int, ...], row: int = 0) -> tuple[int, ...]:
    return rows[:row] + rows[row + 1:]


def delete_column(rows: tuple[int, ...], column: int) -> tuple[int, ...]:
    low = (1 << column) - 1
    return tuple((row & low) | ((row >> 1) & ~low) for row in rows)


def column_degrees(rows: tuple[int, ...], columns: int) -> tuple[int, ...]:
    return tuple(sum((row >> column) & 1 for row in rows) for column in range(columns))


def fast_invariant(rows: tuple[int, ...], columns: int) -> tuple[object, ...]:
    degrees = column_degrees(rows, columns)
    codegrees = [[0] * columns for _ in range(columns)]
    for row in rows:
        support = [i for i in range(columns) if row & (1 << i)]
        for i in support:
            for j in support:
                codegrees[i][j] += 1
    column_signatures = tuple(sorted(
        (degrees[i], tuple(sorted(codegrees[i][j] for j in range(columns) if j != i)))
        for i in range(columns)
    ))
    return (
        len(rows),
        columns,
        tuple(sorted(Counter(row.bit_count() for row in rows).items())),
        tuple(sorted(degrees)),
        column_signatures,
        tuple(sorted(Counter(rows).values())),
    )


def isomorphic_matrices(
    left: tuple[int, ...], right: tuple[int, ...], columns: int
) -> tuple[int, ...] | None:
    """Return an exact column permutation witness, or None."""
    if fast_invariant(left, columns) != fast_invariant(right, columns):
        return None
    left_degrees = column_degrees(left, columns)
    right_degrees = column_degrees(right, columns)
    left_codegrees = [[0] * columns for _ in range(columns)]
    right_codegrees = [[0] * columns for _ in range(columns)]
    for rows, table in ((left, left_codegrees), (right, right_codegrees)):
        for row in rows:
            support = [i for i in range(columns) if row & (1 << i)]
            for i in support:
                for j in support:
                    table[i][j] += 1

    mapping = [-1] * columns
    used = [False] * columns

    @lru_cache(maxsize=None)
    def projection(rows: tuple[int, ...], chosen: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
        counts = Counter()
        for row in rows:
            pattern = 0
            for index, column in enumerate(chosen):
                pattern |= ((row >> column) & 1) << index
            counts[pattern] += 1
        return tuple(sorted(counts.items()))

    def candidates(source: int) -> list[int]:
        mapped_sources = [i for i in range(columns) if mapping[i] >= 0]
        return [
            target for target in range(columns)
            if not used[target]
            and left_degrees[source] == right_degrees[target]
            and all(
                left_codegrees[source][old] == right_codegrees[target][mapping[old]]
                for old in mapped_sources
            )
        ]

    def search() -> bool:
        remaining = [i for i in range(columns) if mapping[i] < 0]
        if not remaining:
            return True
        options = [(len(candidates(source)), source) for source in remaining]
        count, source = min(options)
        if count == 0:
            return False
        mapped_sources = tuple(i for i in range(columns) if mapping[i] >= 0)
        for target in candidates(source):
            new_sources = mapped_sources + (source,)
            new_targets = tuple(mapping[i] for i in mapped_sources) + (target,)
            if projection(left, new_sources) != projection(right, new_targets):
                continue
            mapping[source] = target
            used[target] = True
            if search():
                return True
            used[target] = False
            mapping[source] = -1
        return False

    return tuple(mapping) if search() else None


def rigid_split_graph(rows: tuple[int, ...], columns: int) -> bool:
    """Degree separation makes the column clique intrinsic in every card."""
    row_max = max((row.bit_count() for row in rows), default=0)
    return min(column_degrees(rows, columns), default=0) + columns - 1 > row_max


def card_data(rows: tuple[int, ...]) -> dict[str, tuple[int, ...]]:
    return {
        "row": delete_row(rows),
        "ordinary_column": delete_column(rows, 0),
        "exceptional_column": delete_column(rows, 6),
    }


def run() -> dict[str, object]:
    started = time.monotonic()
    h = generated_subgroup(H_GENERATORS)
    k = generated_subgroup(K_GENERATORS)
    assert len(h) == len(k) == 4
    h_matrices = matrices(h)
    k_matrices = matrices(k)

    eligible_h = [m for m, rows in enumerate(h_matrices) if rigid_split_graph(rows, 12)]
    eligible_k = [m for m, rows in enumerate(k_matrices) if rigid_split_graph(rows, 12)]
    exact_card_comparisons = 0
    deck_collisions = []
    parent_isomorphic = 0

    h_cards = {mask: card_data(h_matrices[mask]) for mask in eligible_h}
    k_cards = {mask: card_data(k_matrices[mask]) for mask in eligible_k}

    for hm in eligible_h:
        hc = h_cards[hm]
        hrow_inv = fast_invariant(hc["row"], 12)
        hcol_invs = sorted((
            fast_invariant(hc["ordinary_column"], 11),
            fast_invariant(hc["exceptional_column"], 11),
        ), key=repr)
        for km in eligible_k:
            kc = k_cards[km]
            if hrow_inv != fast_invariant(kc["row"], 12):
                continue
            if hcol_invs != sorted((
                fast_invariant(kc["ordinary_column"], 11),
                fast_invariant(kc["exceptional_column"], 11),
            ), key=repr):
                continue
            exact_card_comparisons += 1
            row_witness = isomorphic_matrices(hc["row"], kc["row"], 12)
            if row_witness is None:
                continue
            straight = (
                isomorphic_matrices(hc["ordinary_column"], kc["ordinary_column"], 11),
                isomorphic_matrices(hc["exceptional_column"], kc["exceptional_column"], 11),
            )
            if None not in straight:
                column_pairing = "straight"
                column_witnesses = straight
            else:
                crossed = (
                    isomorphic_matrices(hc["ordinary_column"], kc["exceptional_column"], 11),
                    isomorphic_matrices(hc["exceptional_column"], kc["ordinary_column"], 11),
                )
                if None in crossed:
                    continue
                column_pairing = "crossed"
                column_witnesses = crossed
            parent_witness = isomorphic_matrices(h_matrices[hm], k_matrices[km], 12)
            if parent_witness is not None:
                parent_isomorphic += 1
            deck_collisions.append({
                "h_mask": hm,
                "k_mask": km,
                "column_pairing": column_pairing,
                "parent_isomorphic": parent_witness is not None,
                "row_card_column_permutation": row_witness,
                "column_card_permutations": column_witnesses,
                "parent_column_permutation": parent_witness,
            })

    nonisomorphic = [item for item in deck_collisions if not item["parent_isomorphic"]]
    return {
        "grc_ce": "YES" if nonisomorphic else "NO",
        "carrier_order": 192,
        "row_carriers": [180, 180],
        "column_carrier": [6, 6],
        "h_column_orbits": [list(x) for x in subgroup_column_orbits(h)],
        "k_column_orbits": [list(x) for x in subgroup_column_orbits(k)],
        "invariant_matrices_each_side": 64,
        "degree_rigid_masks": {"H": eligible_h, "K": eligible_k},
        "structured_pairs": len(eligible_h) * len(eligible_k),
        "exact_card_comparisons_after_invariants": exact_card_comparisons,
        "deck_collisions": len(deck_collisions),
        "parent_isomorphic_deck_collisions": parent_isomorphic,
        "nonisomorphic_deck_collisions": nonisomorphic,
        "runtime_seconds": time.monotonic() - started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
