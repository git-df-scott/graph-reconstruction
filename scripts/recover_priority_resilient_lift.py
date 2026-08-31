#!/usr/bin/env python3
"""Recover exact tiny-rescuer/high-class lifts from one saved frontier stratum."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from extension_resilience_census import collect_exception_orbits, lift_family
from local_gluing_search import edge_partition, parent_permutation_conditions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--three-count", type=int, required=True, choices=range(7))
    parser.add_argument("--progress", type=int, default=500000)
    parser.add_argument("--min-classes", type=int, default=6)
    parser.add_argument("--max-globalizers", type=int, default=2)
    args = parser.parse_args()
    leaves, exceptions, representatives = collect_exception_orbits(
        args.three_count, args.progress
    )
    priority = []
    pareto = []
    for maps in representatives.values():
        edges, roots, classes = edge_partition(6, maps)
        globalizers = tuple(
            p for p, pairs in parent_permutation_conditions(6, edges, roots, classes)
            if not pairs
        )
        for outside in globalizers:
            lift = lift_family(maps, outside)
            edges7, roots7, classes7 = edge_partition(7, lift)
            globalizers7 = tuple(
                p for p, pairs in parent_permutation_conditions(
                    7, edges7, roots7, classes7
                ) if not pairs
            )
            record = {
                "primitive_maps": maps,
                "primitive_class_count": len(classes),
                "primitive_globalizers": globalizers,
                "outside_globalizer": outside,
                "lifted_maps": lift,
                "lifted_class_count": len(classes7),
                "lifted_globalizers": globalizers7,
            }
            if (
                len(globalizers7) <= args.max_globalizers
                and len(classes7) >= args.min_classes
            ):
                priority.append(record)
            if not any(
                other[0] >= len(classes7) and other[1] <= len(globalizers7)
                and (other[0], other[1]) != (len(classes7), len(globalizers7))
                for other in pareto
            ):
                pareto = [
                    other for other in pareto
                    if not (
                        len(classes7) >= other[0] and len(globalizers7) <= other[1]
                        and (len(classes7), len(globalizers7)) != (other[0], other[1])
                    )
                ]
                pareto.append((len(classes7), len(globalizers7), record))
    print(json.dumps({
        "status": "PRIORITY_LIFT_RECOVERY_COMPLETE",
        "three_count": args.three_count,
        "source_canonical_leaves": leaves,
        "source_nonidentity_exceptions": exceptions,
        "full_orbits": len(representatives),
        "priority_filter": {
            "minimum_classes": args.min_classes,
            "maximum_globalizers": args.max_globalizers,
        },
        "priority_record_count": len(priority),
        "priority_records": priority[:20],
        "pareto_record_count": len(pareto),
        "pareto_records": [record for _classes, _rescues, record in pareto[:20]],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
