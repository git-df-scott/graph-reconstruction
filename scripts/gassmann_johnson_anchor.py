#!/usr/bin/env python3
"""Exact Gassmann incidence strike with a rigid Johnson anchor.

The 21 anchor vertices are six points P and their fifteen duads D.  P induces
a clique, D an independent set, and P-D adjacency is membership.  Degrees in
the anchor distinguish P from D and every duad has its unique two-point
neighbourhood, so Aut(anchor)=S6 exactly.

Rows are S6/H on one side and S6/K on the other.  H and K are the exceptional
outer-balanced V4 Gassmann pair.  Their orbits on P+D give nine incidence
orbitals on each side, hence 512 matrices and 262,144 structured pairs.
Exact canonical codes enumerate all permitted S6 anchor maps (or the relevant
point/duad stabilizer after an anchor deletion).
"""

from __future__ import annotations

import json
import resource
import time
from collections import Counter

import gassmann_incidence_bideck as base
import outer_s6_strike as outer


def anchor_action(g: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(g) + tuple(
        6 + outer.DUAD_INDEX[outer.act_duad(g, duad)] for duad in outer.DUADS
    )


ACTIONS = tuple(anchor_action(g) for g in outer.PERMUTATIONS)
POINT_STABILIZER = tuple(a for a in ACTIONS if a[0] == 0)
DUAD_STABILIZER = tuple(a for a in ACTIONS if a[6] == 6)


def subgroup_anchor_orbits(subgroup):
    unseen = set(range(21))
    answer = []
    actions = tuple(anchor_action(g) for g in subgroup)
    while unseen:
        seed = min(unseen)
        orbit = tuple(sorted({a[seed] for a in actions}))
        unseen -= set(orbit)
        answer.append(orbit)
    return tuple(answer)


def orbital_rows(subgroup):
    _position, _cosets, owner, identity_coset = base.coset_data(subgroup)
    assert identity_coset == 0
    orbitals = []
    for orbit in subgroup_anchor_orbits(subgroup):
        seed = orbit[0]
        rows = [0] * 180
        for g, action in zip(outer.PERMUTATIONS, ACTIONS):
            rows[owner[g]] |= 1 << action[seed]
        assert rows[0] == sum(1 << c for c in orbit)
        orbitals.append(tuple(rows))
    assert len(orbitals) == 9
    return tuple(orbitals)


def matrices(subgroup):
    orbitals = orbital_rows(subgroup)
    return tuple(
        tuple(
            sum(orbital[r] for bit, orbital in enumerate(orbitals) if mask & (1 << bit))
            for r in range(180)
        )
        for mask in range(512)
    )


def permute_bits(pattern: int, action: tuple[int, ...]) -> int:
    answer = 0
    while pattern:
        low = pattern & -pattern
        answer |= 1 << action[low.bit_length() - 1]
        pattern -= low
    return answer


def canonical_code(rows: tuple[int, ...], actions: tuple[tuple[int, ...], ...]):
    counts = Counter(rows)
    best = None
    for action in actions:
        code = tuple(sorted((permute_bits(pattern, action), count) for pattern, count in counts.items()))
        if best is None or code < best:
            best = code
    return best


def anchor_internal_degrees(deleted: int | None = None) -> tuple[int, ...]:
    degrees = []
    for vertex in range(21):
        if vertex == deleted:
            continue
        if vertex < 6:
            neighbors = {x for x in range(6) if x != vertex}
            neighbors |= {6 + i for i, duad in enumerate(outer.DUADS) if vertex in duad}
        else:
            neighbors = set(outer.DUADS[vertex - 6])
        if deleted is not None:
            neighbors.discard(deleted)
        degrees.append(len(neighbors))
    return tuple(degrees)


def degree_separated(rows: tuple[int, ...], deleted_row: bool = False, deleted_column: int | None = None) -> bool:
    active_rows = rows[1:] if deleted_row else rows
    if deleted_column is not None:
        active_rows = tuple(row & ~(1 << deleted_column) for row in active_rows)
    row_max = max((row.bit_count() for row in active_rows), default=0)
    internal = anchor_internal_degrees(deleted_column)
    active_columns = [c for c in range(21) if c != deleted_column]
    column_totals = []
    for internal_degree, column in zip(internal, active_columns):
        incidence = sum((row >> column) & 1 for row in active_rows)
        column_totals.append(internal_degree + incidence)
    return min(column_totals, default=row_max + 1) > row_max


def eligible(rows: tuple[int, ...]) -> bool:
    return all((
        degree_separated(rows),
        degree_separated(rows, deleted_row=True),
        degree_separated(rows, deleted_column=0),
        degree_separated(rows, deleted_column=6),
    ))


def codes(rows: tuple[int, ...]):
    return {
        "parent": canonical_code(rows, ACTIONS),
        "row": canonical_code(rows[1:], ACTIONS),
        "point": canonical_code(tuple(r & ~(1 << 0) for r in rows), POINT_STABILIZER),
        "duad": canonical_code(tuple(r & ~(1 << 6) for r in rows), DUAD_STABILIZER),
    }


def run():
    started = time.monotonic()
    h = base.generated_subgroup(base.H_GENERATORS)
    k = base.generated_subgroup(base.K_GENERATORS)
    hmats, kmats = matrices(h), matrices(k)
    eligible_h = [m for m, rows in enumerate(hmats) if eligible(rows)]
    eligible_k = [m for m, rows in enumerate(kmats) if eligible(rows)]
    hcodes = {m: codes(hmats[m]) for m in eligible_h}
    kcodes = {m: codes(kmats[m]) for m in eligible_k}

    k_by_deck = {}
    for mask, item in kcodes.items():
        key = (item["row"], item["point"], item["duad"])
        k_by_deck.setdefault(key, []).append(mask)

    collisions = []
    for hmask, item in hcodes.items():
        key = (item["row"], item["point"], item["duad"])
        for kmask in k_by_deck.get(key, ()):
            collisions.append({
                "h_mask": hmask,
                "k_mask": kmask,
                "parent_isomorphic": item["parent"] == kcodes[kmask]["parent"],
            })
    nonisomorphic = [x for x in collisions if not x["parent_isomorphic"]]
    return {
        "grc_ce": "YES" if nonisomorphic else "NO",
        "carrier_order": 201,
        "anchor": "K6 point clique plus point-duad incidence",
        "anchor_automorphism_group": "S6 (structural proof)",
        "h_orbit_sizes": [len(x) for x in subgroup_anchor_orbits(h)],
        "k_orbit_sizes": [len(x) for x in subgroup_anchor_orbits(k)],
        "matrices_each_side": 512,
        "eligible_degree_separated": {"H": len(eligible_h), "K": len(eligible_k)},
        "structured_pairs": len(eligible_h) * len(eligible_k),
        "deck_collisions": len(collisions),
        "parent_isomorphic_deck_collisions": sum(x["parent_isomorphic"] for x in collisions),
        "nonisomorphic_deck_collisions": nonisomorphic,
        "runtime_seconds": time.monotonic() - started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
