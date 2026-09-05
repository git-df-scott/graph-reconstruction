#!/usr/bin/env python3
"""Exact matched-vertex triangle identities implied by a full deck.

For n>=4, sum_u T(G-u)=(n-3)T(G), so equal decks imply equal T(G).
The matched card G-u ~= H-v then implies T_G(u)=T_H(v), where T_G(u)
counts triangles containing u. These are redundant propagation constraints.
"""
import itertools

from astra_degree_constraints import clause, neg, thresholds


def add_triangle_constraints(enc):
    assert enc.n >= 4
    counts = {}
    indicators = 0
    for side in (0, 1):
        fixed = [0] * enc.n
        terms = [[] for _ in range(enc.n)]
        for triple in itertools.combinations(range(enc.n), 3):
            slots = [enc.slot(side, u, v) for u, v in itertools.combinations(triple, 2)]
            if any(x is False for x in slots):
                continue
            variables = [x for x in slots if x is not True]
            if not variables:
                for u in triple:
                    fixed[u] += 1
                continue
            z = enc.new()
            indicators += 1
            for x in variables:
                enc.add([-z, x])
            enc.add([z] + [-x for x in variables])
            for u in triple:
                terms[u].append(z)
        for u in range(enc.n):
            counts[side, u] = (fixed[u], thresholds(enc, terms[u]))
    for u in range(enc.n):
        fa, ra = counts[0, u]
        for v in range(enc.n):
            fb, rb = counts[1, v]
            p = enc.matching[u][v]
            for j in range(1, max(fa + len(ra), fb + len(rb)) + 1):
                a = True if j <= fa else False if j > fa + len(ra) else ra[j - fa - 1]
                b = True if j <= fb else False if j > fb + len(rb) else rb[j - fb - 1]
                clause(enc, [-p, neg(a), b])
                clause(enc, [-p, a, neg(b)])
    return {'triangle_indicators': indicators, 'max_variable_triangles_at_vertex': max(len(row) for base, row in counts.values())}
