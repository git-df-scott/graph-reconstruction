#!/usr/bin/env python3
"""Exact signed/voltage-cover strike from an asymmetric pseudosimilar core.

This is a structured legal-order search, not generic graph enumeration.  The
base incidence equations force deletion 0 to be isomorphic to deletion 1 by
the fixed permutation P.  Exact asymmetry is then checked before any lift is
constructed.  Tree gauge fixes a spanning tree to identity; chord voltages
enumerate the remaining switching classes.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import resource
import time
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from grc import Graph, canonical_deck, find_isomorphism, is_isomorphic


BASE_N = 8
PSEUDO_MAP = (1, 0, 3, 2, 5, 6, 7, 4)
SEED_GRAPH6 = "GQyPA_"
BASE_EDGES = tuple(itertools.combinations(range(BASE_N), 2))
S3 = tuple(itertools.permutations(range(3)))
S4 = tuple(itertools.permutations(range(4)))


def incidence_classes():
    position = {edge: index for index, edge in enumerate(BASE_EDGES)}
    parent = list(range(len(BASE_EDGES)))

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for u, v in BASE_EDGES:
        if u == 0:
            continue
        image = tuple(sorted((PSEUDO_MAP[u], PSEUDO_MAP[v])))
        union(position[(u, v)], position[image])
    names = {}
    labels = []
    for item in range(len(BASE_EDGES)):
        root = find(item)
        names.setdefault(root, len(names))
        labels.append(names[root])
    return tuple(labels), len(names)


INCIDENCE_LABELS, INCIDENCE_CLASS_COUNT = incidence_classes()


def base_graph(assignment):
    rows = [0] * BASE_N
    edges = []
    for (u, v), color in zip(BASE_EDGES, INCIDENCE_LABELS):
        if assignment & (1 << color):
            rows[u] |= 1 << v
            rows[v] |= 1 << u
            edges.append((u, v))
    return Graph(tuple(rows)), tuple(edges)


def connected(graph):
    seen = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        for image in range(graph.n):
            if graph.edge(vertex, image) and image not in seen:
                seen.add(image)
                frontier.append(image)
    return len(seen) == graph.n


def exactly_asymmetric(graph):
    for source in range(graph.n):
        for image in range(source + 1, graph.n):
            if graph.degrees[source] != graph.degrees[image]:
                continue
            if find_isomorphism(graph, graph, {source: image}) is not None:
                return False
    return True


def discrete_color_refinement(graph):
    colors = list(graph.degrees)
    while True:
        signatures = [
            (
                colors[vertex],
                tuple(sorted(
                    colors[other]
                    for other in range(graph.n)
                    if graph.edge(vertex, other)
                )),
            )
            for vertex in range(graph.n)
        ]
        names = {value: index for index, value in enumerate(sorted(set(signatures)))}
        refined = [names[value] for value in signatures]
        if len(set(refined)) == graph.n:
            return True
        if refined == colors:
            return False
        colors = refined


def spanning_tree(edges):
    parent = list(range(BASE_N))
    tree = []
    chords = []

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for edge in edges:
        left, right = map(find, edge)
        if left != right:
            parent[right] = left
            tree.append(edge)
        else:
            chords.append(edge)
    return tuple(tree), tuple(chords)


def integer_digits(value, base, count):
    result = []
    for _ in range(count):
        result.append(value % base)
        value //= base
    return tuple(result)


def compose(left, right):
    return tuple(left[right[index]] for index in range(len(left)))


def inverse(permutation):
    result = [0] * len(permutation)
    for source, image in enumerate(permutation):
        result[image] = source
    return tuple(result)


def simultaneous_conjugacy_representatives(permutations, rank):
    def conjugate(permutation, by):
        return compose(compose(by, permutation), inverse(by))

    return tuple(sorted({
        min(
            tuple(conjugate(permutation, by) for permutation in voltage_tuple)
            for by in permutations
        )
        for voltage_tuple in itertools.product(permutations, repeat=rank)
    }))


def voltage_lift(tree, chords, code, voltage_group):
    if voltage_group == "C2":
        sheets = 2
        permutations = ((0, 1), (1, 0))
    elif voltage_group == "C3":
        sheets = 3
        permutations = ((0, 1, 2), (1, 2, 0), (2, 0, 1))
    elif voltage_group == "S3":
        sheets = 3
        permutations = S3
    elif voltage_group == "S4":
        sheets = 4
        permutations = S4
    else:
        raise ValueError(voltage_group)
    if voltage_group == "S4":
        if len(code) != len(chords):
            raise ValueError("one S4 permutation is required per chord")
        chord_voltage = dict(zip(chords, code))
    else:
        digits = integer_digits(code, len(permutations), len(chords))
        chord_voltage = {
            edge: permutations[digits[index]] for index, edge in enumerate(chords)
        }
    identity = tuple(range(sheets))
    rows = [0] * (sheets * BASE_N)
    for u, v in tree + chords:
        permutation = chord_voltage.get((u, v), identity)
        for fiber in range(sheets):
            left = sheets * u + fiber
            right = sheets * v + permutation[fiber]
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return Graph(tuple(rows))


def exact_deck_digest(deck):
    digest = hashlib.sha256()
    for order, code in deck:
        encoded = code.to_bytes((code.bit_length() + 7) // 8 or 1, "big")
        digest.update(bytes((order, len(encoded))))
        digest.update(encoded)
    return digest.hexdigest()


def classified_bases(ranks=None):
    result = []
    for assignment in range(1 << INCIDENCE_CLASS_COUNT):
        graph, edges = base_graph(assignment)
        if not connected(graph) or not exactly_asymmetric(graph):
            continue
        tree, chords = spanning_tree(edges)
        if ranks is not None and len(chords) not in ranks:
            continue
        result.append((assignment, graph, tree, chords))
    return tuple(result)


def reconstruct(assignment, voltage_code, voltage_group):
    _graph, edges = base_graph(assignment)
    tree, chords = spanning_tree(edges)
    return voltage_lift(tree, chords, voltage_code, voltage_group)


def search(voltage_group, ranks, hostile=True, progress=16):
    started = time.monotonic()
    group_order = {"C2": 2, "C3": 3, "S3": 6, "S4": 24}[voltage_group]
    bases = classified_bases(set(ranks))
    # SHA-256 is only a first-level index.  Keep every distinct exact deck in
    # a digest bucket: storing a single representative here can turn a digest
    # collision into a false negative on a later equal deck.
    deck_table = {}
    presentations = digest_collisions = exact_collisions = 0
    isomorphic_collisions = candidate_count = 0
    rank_histogram = Counter()
    for base_index, (assignment, graph, tree, chords) in enumerate(bases, 1):
        rank_histogram[len(chords)] += 1
        if voltage_group == "S4":
            voltage_codes = simultaneous_conjugacy_representatives(S4, len(chords))
        else:
            voltage_codes = range(group_order ** len(chords))
        for voltage_code in voltage_codes:
            parent = voltage_lift(tree, chords, voltage_code, voltage_group)
            deck = canonical_deck(parent)
            digest = exact_deck_digest(deck)
            presentations += 1
            bucket = deck_table.setdefault(digest, {})
            previous = bucket.get(deck)
            if previous is None:
                if bucket:
                    digest_collisions += 1
                bucket[deck] = (assignment, voltage_code)
                continue
            digest_collisions += 1
            old_assignment, old_voltage = previous
            old_parent = reconstruct(old_assignment, old_voltage, voltage_group)
            old_deck = canonical_deck(old_parent)
            if old_deck != deck:
                continue
            exact_collisions += 1
            if is_isomorphic(old_parent, parent):
                isomorphic_collisions += 1
                continue
            candidate_count += 1
            if hostile:
                raise AssertionError(
                    "LEGAL_ORDER_CE_CANDIDATE requires immediate frozen hostile replay: "
                    f"{old_parent.to_graph6()} {parent.to_graph6()}"
                )
        if progress and base_index % progress == 0:
            print(
                f"progress group={voltage_group} bases={base_index}/{len(bases)} "
                f"presentations={presentations}",
                file=sys.stderr,
            )
    return {
        "voltage_group": voltage_group,
        "ranks": tuple(ranks),
        "base_count": len(bases),
        "rank_histogram": dict(sorted(rank_histogram.items())),
        "presentations": presentations,
        "parent_deck_classes": sum(len(bucket) for bucket in deck_table.values()),
        "digest_collisions": digest_collisions,
        "exact_deck_collisions": exact_collisions,
        "isomorphic_deck_collisions": isomorphic_collisions,
        "nonisomorphic_deck_collisions": candidate_count,
        "zero_counterexamples": candidate_count == 0,
        "elapsed_seconds": time.monotonic() - started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def base_classification():
    started = time.monotonic()
    histogram = Counter()
    asymmetric = []
    for assignment in range(1 << INCIDENCE_CLASS_COUNT):
        graph, edges = base_graph(assignment)
        if not connected(graph):
            continue
        exact = exactly_asymmetric(graph)
        discrete = discrete_color_refinement(graph)
        tree, chords = spanning_tree(edges)
        histogram[(len(chords), exact, discrete)] += 1
        if exact:
            asymmetric.append((assignment, graph.to_graph6(), len(chords)))
    seed = Graph.from_graph6(SEED_GRAPH6)
    deletion_map_valid = all(
        seed.edge(u, v) == seed.edge(PSEUDO_MAP[u], PSEUDO_MAP[v])
        for u in range(1, BASE_N)
        for v in range(u + 1, BASE_N)
    )
    return {
        "incidence_classes": INCIDENCE_CLASS_COUNT,
        "raw_assignments": 1 << INCIDENCE_CLASS_COUNT,
        "connected_exact_asymmetric": len(asymmetric),
        "all_asymmetric_are_color_discrete": all(
            histogram[(rank, True, False)] == 0
            for rank in range(len(BASE_EDGES) - BASE_N + 2)
        ),
        "rank_histogram": dict(sorted(Counter(x[2] for x in asymmetric).items())),
        "seed": {
            "graph6": SEED_GRAPH6,
            "pseudosimilar_vertices": (0, 1),
            "deletion_map": PSEUDO_MAP,
            "deletion_map_valid": deletion_map_valid,
            "exactly_asymmetric": exactly_asymmetric(seed),
        },
        "elapsed_seconds": time.monotonic() - started,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("C2", "C3", "S3", "S4"))
    parser.add_argument("--ranks", default="")
    parser.add_argument("--classify-bases", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--progress", type=int, default=16)
    args = parser.parse_args()
    result = {"grc_ce": "NO", "base_classification": base_classification()}
    if args.group:
        if not args.ranks:
            raise SystemExit("--ranks is required with --group")
        ranks = tuple(int(value) for value in args.ranks.split(","))
        result["search"] = search(args.group, ranks, progress=args.progress)
    elif not args.classify_bases:
        raise SystemExit("choose --classify-bases or --group with --ranks")
    rendered = json.dumps(result, indent=2 if args.pretty else None, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
