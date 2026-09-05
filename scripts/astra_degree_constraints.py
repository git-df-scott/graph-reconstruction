#!/usr/bin/env python3
"""Redundant exact consequences of equal full vertex-deleted decks.

Sum of card edge counts is (n-2)|E|. Thus equal decks imply equal parent
edge counts and deg_G(u)=deg_H(v) for each matched deletion occurrence.
These constraints add propagation, not a restriction on counterexamples.
"""


def clause(enc, literals):
    if any(x is True for x in literals):
        return
    enc.add([x for x in literals if x is not False])


def neg(x):
    return not x if isinstance(x, bool) else -x


def thresholds(enc, inputs):
    """Exact literals for sum(inputs)>=1, >=2, ... (both directions)."""
    row = []
    for x in inputs:
        updated = []
        for j in range(len(row) + 1):
            a = row[j] if j < len(row) else False
            b = row[j - 1] if j else True
            z = enc.new()
            # z iff a OR (x AND b).
            clause(enc, [neg(a), z])
            clause(enc, [-x, neg(b), z])
            clause(enc, [-z, a, x])
            clause(enc, [-z, a, b])
            updated.append(z)
        row = updated
    return row


def add_degree_constraints(enc):
    assert enc.n >= 3
    edge_rows, degrees = [], {}
    for side in (0, 1):
        edge_rows.append(thresholds(enc, [value for (s, u, v), value in enc.variables.items() if s == side]))
        for u in range(enc.n):
            slots = [enc.slot(side, u, v) for v in range(enc.n) if v != u]
            fixed = sum(x is True for x in slots)
            row = thresholds(enc, [x for x in slots if not isinstance(x, bool)])
            degrees[side, u] = [True if j <= fixed else False if j > fixed + len(row) else row[j - fixed - 1]
                                for j in range(1, enc.n)]
    for a, b in zip(*edge_rows):
        enc.add([-a, b])
        enc.add([a, -b])
    for u in range(enc.n):
        for v in range(enc.n):
            p = enc.matching[u][v]
            for a, b in zip(degrees[0, u], degrees[1, v]):
                clause(enc, [-p, neg(a), b])
                clause(enc, [-p, a, neg(b)])
