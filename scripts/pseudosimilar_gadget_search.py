#!/usr/bin/env python3
"""Attach every small one-anchor gadget at pseudo-similar vertex pairs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from grc import Graph, canonical_deck, is_isomorphic
from pseudosimilar_leaf_search import pseudosimilar_pairs


def overlap(left: tuple, right: tuple) -> int:
    return sum((Counter(left) & Counter(right)).values())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-vertices", type=int, default=8)
    parser.add_argument("--gadget-vertices", type=int, required=True)
    parser.add_argument("--geng", default="geng")
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()
    k = args.gadget_vertices
    if not 1 <= k <= 4:
        raise SystemExit("gadget size is capped at four for the exact dependency-free search")
    process = subprocess.Popen(
        [args.geng, "-q", "-c", str(args.base_vertices)], stdout=subprocess.PIPE, text=True
    )
    assert process.stdout is not None
    records = []
    bases = pairs = candidates = 0
    for line in process.stdout:
        base = Graph.from_graph6(line)
        pseudo = list(pseudosimilar_pairs(base))
        if not pseudo:
            continue
        bases += 1
        pairs += len(pseudo)
        for internal_mask in range(1 << (k * (k - 1) // 2)):
            gadget = Graph.from_edge_mask(k, internal_mask)
            for attachment_mask in range(1, 1 << k):
                for u, v in pseudo:
                    left = base.attach_gadget(u, gadget, attachment_mask)
                    right = base.attach_gadget(v, gadget, attachment_mask)
                    if is_isomorphic(left, right):
                        continue
                    candidates += 1
                    common = overlap(canonical_deck(left), canonical_deck(right))
                    records.append(
                        (
                            common,
                            left.n,
                            line.strip(),
                            u,
                            v,
                            internal_mask,
                            attachment_mask,
                        )
                    )
                    if common == left.n:
                        print(
                            "EXACT_CE_CANDIDATE "
                            f"base={line.strip()} vertices={u},{v} internal={internal_mask} "
                            f"attachment={attachment_mask}"
                        )
                        raise SystemExit(2)
    if process.wait():
        raise SystemExit(process.returncode)
    records.sort(reverse=True)
    print(
        f"DONE base_n={args.base_vertices} gadget_n={k} bases={bases} "
        f"pseudo_pairs={pairs} candidates={candidates} exact_ce_candidates=0"
    )
    for common, order, code, u, v, internal, attachment in records[: args.top]:
        print(
            f"OVERLAP {common}/{order} base={code} vertices={u},{v} "
            f"internal={internal} attachment={attachment}"
        )


if __name__ == "__main__":
    main()
