#!/usr/bin/env python3
"""Small standalone exact DRUP checker. No SAT/discovery imports.

Each addition must be reverse-unit-propagation redundant. Deletions remove
one occurrence of the exact clause. Success requires a verified empty clause.
This is deliberately simple, intended for the small root-fixed certificates.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from collections import defaultdict


def read_cnf(path):
    clauses, pending, declared = [], [], None
    for line in Path(path).read_text().splitlines():
        if not line or line[0] == 'c':
            continue
        if line[0] == 'p':
            _, fmt, nv, nc = line.split()
            assert fmt == 'cnf'
            declared = int(nv), int(nc)
            continue
        for token in line.split():
            literal = int(token)
            if literal:
                pending.append(literal)
            else:
                clauses.append(tuple(sorted(set(pending))))
                pending = []
    assert not pending and declared is not None
    assert len(clauses) == declared[1]
    assert all(abs(x) <= declared[0] for c in clauses for x in c)
    return clauses


def contradiction_by_up(clauses, assumptions):
    values = {}
    for x in assumptions:
        if abs(x) in values and values[abs(x)] != (x > 0):
            return True
        values[abs(x)] = x > 0
    while True:
        changed = False
        for c in clauses:
            unknown, satisfied = [], False
            for x in c:
                val = values.get(abs(x))
                if val is None:
                    unknown.append(x)
                elif val == (x > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unknown:
                return True
            if len(unknown) == 1:
                x = unknown[0]
                values[abs(x)] = x > 0
                changed = True
        if not changed:
            return False


class WatchedUP:
    """Reusable two-watch propagation; assignments are fresh for every RUP."""
    def __init__(self, clauses):
        self.clauses = []
        self.positions = []
        self.alive = []
        self.index = defaultdict(list)
        self.watch = defaultdict(set)
        self.units = set()
        self.empty = set()
        for c in clauses:
            self.add(c)

    def add(self, c):
        i = len(self.clauses)
        self.clauses.append(c)
        self.alive.append(True)
        self.index[c].append(i)
        self.positions.append([0, min(1, len(c) - 1)])
        if not c:
            self.empty.add(i)
        elif len(c) == 1:
            self.units.add(i)
        else:
            self.watch[c[0]].add(i)
            self.watch[c[1]].add(i)

    def delete(self, c):
        assert self.index[c], 'deletion absent'
        i = self.index[c].pop()
        self.alive[i] = False
        self.empty.discard(i)
        self.units.discard(i)
        if len(c) >= 2:
            for pos in self.positions[i]:
                self.watch[c[pos]].discard(i)

    def contradiction(self, assumptions):
        if self.empty:
            return True
        values, queue = {}, []

        def enqueue(x):
            old = values.get(abs(x))
            if old is not None:
                return old == (x > 0)
            values[abs(x)] = x > 0
            queue.append(x)
            return True

        def value(x):
            old = values.get(abs(x))
            return None if old is None else old == (x > 0)

        for i in self.units:
            if not enqueue(self.clauses[i][0]):
                return True
        for x in assumptions:
            if not enqueue(x):
                return True
        for true in queue:
            false = -true
            for i in list(self.watch[false]):
                c, p = self.clauses[i], self.positions[i]
                slot = 0 if c[p[0]] == false else 1
                otherpos = p[1 - slot]
                other = c[otherpos]
                if value(other) is True:
                    continue
                replacement = next((k for k, x in enumerate(c) if k != otherpos and k != p[slot] and value(x) is not False), None)
                if replacement is not None:
                    self.watch[false].remove(i)
                    p[slot] = replacement
                    self.watch[c[replacement]].add(i)
                elif value(other) is False or not enqueue(other):
                    return True
        return False


def verify(cnf, proof):
    database = WatchedUP(read_cnf(cnf))
    additions = deletions = 0
    empty = False
    for lineno, line in enumerate(Path(proof).read_text().splitlines(), 1):
        tokens = line.split()
        if not tokens or tokens[0] == 'c':
            continue
        deletion = tokens[0] == 'd'
        if deletion:
            tokens = tokens[1:]
        literals = list(map(int, tokens))
        assert literals[-1] == 0 and 0 not in literals[:-1], (lineno, 'invalid clause')
        c = tuple(sorted(set(literals[:-1])))
        if deletion:
            database.delete(c)
            deletions += 1
        else:
            assert database.contradiction([-x for x in c]), (lineno, 'not RUP')
            database.add(c)
            additions += 1
            empty |= not c
    assert empty, 'no verified empty clause'
    return {'verified_unsat': True, 'rup_additions': additions, 'deletions': deletions}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cnf')
    ap.add_argument('proof')
    args = ap.parse_args()
    print(json.dumps(verify(args.cnf, args.proof), sort_keys=True))


if __name__ == '__main__':
    main()
