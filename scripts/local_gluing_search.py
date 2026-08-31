#!/usr/bin/env python3
r"""Construct hypomorphic pairs from prescribed local card bijections.

For each deleted vertex i, a permutation sigma_i of V\{i} is chosen.  Edge
equations force `G-i` to map isomorphically to `H-i` under sigma_i.  A
union-find computes the free binary edge classes.  Random assignments then
test whether these locally compatible maps can yield globally nonisomorphic
parents.

Any hit is replayed through the independent exact deck and parent-isomorphism
checkers before it is printed.  Orders at most 13 are negative controls.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, is_isomorphic, same_deck


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left, right = self.find(left), self.find(right)
        if left == right:
            return
        if self.rank[left] < self.rank[right]:
            left, right = right, left
        self.parent[right] = left
        if self.rank[left] == self.rank[right]:
            self.rank[left] += 1


def edge_index(n: int):
    edges = tuple((u, v) for u in range(n) for v in range(u + 1, n))
    return edges, {edge: i for i, edge in enumerate(edges)}


def random_local_maps(n: int, moves: int, rng: random.Random) -> tuple[tuple[int, ...], ...]:
    maps = []
    for deleted in range(n):
        permutation = list(range(n))
        available = [v for v in range(n) if v != deleted]
        for _ in range(moves):
            u, v = rng.sample(available, 2)
            permutation[u], permutation[v] = permutation[v], permutation[u]
        maps.append(tuple(permutation))
    return tuple(maps)


def edge_partition(n: int, maps: tuple[tuple[int, ...], ...]):
    edges, index = edge_index(n)
    slots = len(edges)
    union = UnionFind(2 * slots)
    for deleted, permutation in enumerate(maps):
        for edge, position in index.items():
            if deleted in edge:
                continue
            image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
            union.union(position, slots + index[image])
    roots = tuple(union.find(i) for i in range(2 * slots))
    classes = sorted(set(roots))
    return edges, roots, {root: i for i, root in enumerate(classes)}


def instantiate(
    n: int,
    edges: tuple[tuple[int, int], ...],
    roots: tuple[int, ...],
    class_index: dict[int, int],
    values: tuple[int, ...],
) -> tuple[Graph, Graph]:
    slots = len(edges)
    masks = [0, 0]
    for side in range(2):
        for position, _edge in enumerate(edges):
            if values[class_index[roots[side * slots + position]]]:
                masks[side] |= 1 << position
    return Graph.from_edge_mask(n, masks[0]), Graph.from_edge_mask(n, masks[1])


def universal_edge_class_isomorphism(
    n: int,
    edges: tuple[tuple[int, int], ...],
    roots: tuple[int, ...],
    class_index: dict[int, int],
) -> tuple[int, ...] | None:
    """Map the two complete graphs while preserving every edge-class label."""

    slots = len(edges)
    position = {edge: i for i, edge in enumerate(edges)}
    colors = [[[None] * n for _ in range(n)] for _ in range(2)]
    signatures = [[None] * n for _ in range(2)]
    for side in range(2):
        for edge, edge_position in position.items():
            color = class_index[roots[side * slots + edge_position]]
            u, v = edge
            colors[side][u][v] = colors[side][v][u] = color
        for v in range(n):
            signatures[side][v] = tuple(sorted(colors[side][v][w] for w in range(n) if w != v))
    if sorted(signatures[0]) != sorted(signatures[1]):
        return None
    mapping = [-1] * n
    used = [False] * n

    def candidates(v: int):
        for w in range(n):
            if used[w] or signatures[0][v] != signatures[1][w]:
                continue
            if all(
                colors[0][v][u] == colors[1][w][mapping[u]]
                for u in range(n)
                if mapping[u] >= 0
            ):
                yield w

    def search(remaining: tuple[int, ...]) -> bool:
        if not remaining:
            return True
        choices = [(sum(1 for _ in candidates(v)), v) for v in remaining]
        count, v = min(choices)
        if count == 0:
            return False
        rest = tuple(u for u in remaining if u != v)
        for w in candidates(v):
            mapping[v] = w
            used[w] = True
            if search(rest):
                return True
            used[w] = False
            mapping[v] = -1
        return False

    return tuple(mapping) if search(tuple(range(n))) else None


def verify_local_maps(g: Graph, h: Graph, maps: tuple[tuple[int, ...], ...]) -> bool:
    for deleted, permutation in enumerate(maps):
        for u in range(g.n):
            if u == deleted:
                continue
            for v in range(u + 1, g.n):
                if v == deleted:
                    continue
                if g.edge(u, v) != h.edge(permutation[u], permutation[v]):
                    return False
    return True


def nauty_nonisomorphic(records, labelg: str):
    """Yield records whose two roots have distinct nauty canonical labels."""

    if not records:
        return
    lines = []
    for g, h, *_ in records:
        lines.extend((g.to_graph6(), h.to_graph6()))
    with tempfile.TemporaryDirectory(prefix="grc-gluing-") as directory:
        source = Path(directory) / "roots.g6"
        target = Path(directory) / "canonical.g6"
        source.write_text("\n".join(lines) + "\n")
        subprocess.run([labelg, "-q", "-S", str(source), str(target)], check=True)
        canonical = target.read_text().splitlines()
    for position, record in enumerate(records):
        if canonical[2 * position] != canonical[2 * position + 1]:
            yield record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", type=int, required=True)
    parser.add_argument("--systems", type=int, default=1000)
    parser.add_argument("--assignments", type=int, default=100)
    parser.add_argument("--moves", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--min-classes", type=int, default=2)
    parser.add_argument("--labelg", default=None)
    parser.add_argument("--batch-size", type=int, default=5000)
    args = parser.parse_args()
    if args.vertices < 3:
        raise SystemExit("GRC starts at three vertices")
    rng = random.Random(args.seed)
    tested = assignments = isomorphic = universal = nonuniversal = 0
    batch = []
    class_histogram: dict[int, int] = {}

    def check_batch() -> dict | None:
        nonlocal isomorphic, batch
        if not batch:
            return None
        if args.labelg:
            survivors = list(nauty_nonisomorphic(batch, args.labelg))
            isomorphic += len(batch) - len(survivors)
        else:
            survivors = []
            for record in batch:
                if is_isomorphic(record[0], record[1]):
                    isomorphic += 1
                else:
                    survivors.append(record)
        batch = []
        for g, h, maps, system, free in survivors:
            # An independent decision path is mandatory for an apparent hit.
            if is_isomorphic(g, h):
                raise AssertionError("nauty/Python parent-isomorphism disagreement")
            if not verify_local_maps(g, h, maps):
                raise AssertionError("edge equation exporter is unsound")
            if not same_deck(g, h):
                raise AssertionError("local card maps did not produce equal exact decks")
            return {
                "status": "EXACT_GRC_CE_CANDIDATE",
                "n": args.vertices,
                "free_edge_classes": free,
                "G_graph6": g.to_graph6(),
                "H_graph6": h.to_graph6(),
                "local_maps": maps,
                "seed": args.seed,
                "system": system,
            }
        return None

    for system in range(1, args.systems + 1):
        maps = random_local_maps(args.vertices, args.moves, rng)
        edges, roots, class_index = edge_partition(args.vertices, maps)
        free = len(class_index)
        class_histogram[free] = class_histogram.get(free, 0) + 1
        if free < args.min_classes:
            continue
        tested += 1
        if universal_edge_class_isomorphism(args.vertices, edges, roots, class_index) is not None:
            universal += 1
            continue
        nonuniversal += 1
        for _ in range(args.assignments):
            values = tuple(rng.getrandbits(1) for _ in range(free))
            if not any(values) or all(values):
                continue
            assignments += 1
            g, h = instantiate(args.vertices, edges, roots, class_index, values)
            batch.append((g, h, maps, system, free))
            if len(batch) >= args.batch_size:
                payload = check_batch()
                if payload:
                    print(json.dumps(payload, indent=2))
                    return
    payload = check_batch()
    if payload:
        print(json.dumps(payload, indent=2))
        return
    print(
        json.dumps(
            {
                "status": "NO_CE_IN_SEARCH",
                "n": args.vertices,
                "systems_requested": args.systems,
                "systems_with_enough_classes": tested,
                "assignments_tested": assignments,
                "isomorphic_assignments": isomorphic,
                "universally_isomorphic_systems": universal,
                "nonuniversal_systems": nonuniversal,
                "free_class_histogram": class_histogram,
                "moves": args.moves,
                "seed": args.seed,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
