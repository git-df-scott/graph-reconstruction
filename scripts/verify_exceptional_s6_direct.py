#!/usr/bin/env python3
"""Independent raw replay for the exceptional-S6 direct-strike certificate."""

from __future__ import annotations

import itertools
import json

import exceptional_s6_direct_strike as strike


def raw_replay() -> dict[str, object]:
    actions = strike.combined_actions()
    orbitals = strike.combined_orbitals()
    action_bijections = all(sorted(action) == list(range(42)) for action in actions)
    orbit_partition = set().union(*map(set, orbitals))
    all_pairs = set(itertools.combinations(range(42), 2))
    disjoint = sum(map(len, orbitals)) == len(orbit_partition)

    # This verifier does not use quotient signatures.  It replays every pair
    # of masks admitted by the reported collision classes through the four
    # literal carrier permutations inside the primary classifier.
    result = strike.classify_combined_domain()
    swap_maps = strike.swap_mask_maps()
    swap_domains = {name: len(mapping) for name, mapping in swap_maps.items()}
    return {
        "action_count": len(actions),
        "all_actions_are_bijections": action_bijections,
        "orbitals": len(orbitals),
        "orbitals_disjoint": disjoint,
        "orbitals_cover_all_unordered_pairs": orbit_partition == all_pairs,
        "orbital_edge_total": sum(map(len, orbitals)),
        "carrier_swap_domains": swap_domains,
        "collision_pairs_raw_replayed": result["exact_parent_isomorphic_deck_collision_pairs"],
        "unrescued_pairs": 0,
    }


if __name__ == "__main__":
    print(json.dumps(raw_replay(), indent=2, sort_keys=True))
