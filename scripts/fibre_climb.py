#!/usr/bin/env python3
"""Anneal over cards C of order m on the exact near-miss objective of
card_fibre -m: the largest number of common cards over all pairs of
non-isomorphic extensions of C (out of m + 1; m + 1 is a counterexample).

Single edge toggles; a persistent card_fibre -m process evaluates each
candidate.  Distinct cards reaching --report or more common cards are
printed as "score C G1 G2" with the best pair.  --start FILE seeds the
restarts from graph6 lines (for example symmetric cards); otherwise random
G(m, p) starts.
"""
from __future__ import annotations

import argparse
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from grc import Graph  # noqa: E402


class Evaluator:
    def __init__(self, tool):
        self.p = subprocess.Popen([tool, "-m"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.cache = {}

    def __call__(self, g6):
        if g6 in self.cache:
            return self.cache[g6]
        self.p.stdin.write(g6 + "\n")
        self.p.stdin.flush()
        line = self.p.stdout.readline().split()
        # MAX <C> common=<c>/<n> pairs=<k> [G1 G2]
        c = int(line[2].split("=")[1].split("/")[0])
        k = int(line[3].split("=")[1])
        pair = tuple(line[4:6]) if len(line) >= 6 else ()
        r = (c, k, pair)
        self.cache[g6] = r
        return r


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--m", type=int, default=13)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--p", type=float, default=0.5)
    ap.add_argument("--t0", type=float, default=0.8)
    ap.add_argument("--t1", type=float, default=0.05)
    ap.add_argument("--report", type=int, default=5)
    ap.add_argument("--start", type=str, default=None)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ev = Evaluator(a.tool)
    m = a.m
    starts = [l.strip() for l in open(a.start) if l.strip()] if a.start else None
    reported = set()
    overall = 0
    for r in range(a.restarts):
        if starts:
            rows = list(Graph.from_graph6(rng.choice(starts)).adj)
        else:
            rows = [0] * m
            for x in range(m):
                for y in range(x + 1, m):
                    if rng.random() < a.p:
                        rows[x] |= 1 << y
                        rows[y] |= 1 << x
        g6 = Graph(tuple(rows)).to_graph6()
        cur = ev(g6)
        best = cur
        t0 = time.time()
        for step in range(a.steps):
            T = a.t0 * (a.t1 / a.t0) ** (step / max(1, a.steps - 1))
            x, y = rng.sample(range(m), 2)
            rows[x] ^= 1 << y
            rows[y] ^= 1 << x
            g6n = Graph(tuple(rows)).to_graph6()
            new = ev(g6n)
            # objective: common cards first, then number of pairs at the maximum
            f_old = cur[0] + 0.01 * min(cur[1], 50)
            f_new = new[0] + 0.01 * min(new[1], 50)
            if f_new >= f_old or rng.random() < pow(2.718281828, (f_new - f_old) / T):
                cur = new
                g6 = g6n
                if new[0] >= a.report and g6n not in reported:
                    reported.add(g6n)
                    print(f"{new[0]}/{m+1} pairs={new[1]} {g6n} {' '.join(new[2])}", flush=True)
                if new[0] > best[0]:
                    best = new
            else:
                rows[x] ^= 1 << y
                rows[y] ^= 1 << x
        overall = max(overall, best[0])
        print(f"restart {r}: best {best[0]}/{m+1} pairs={best[1]} ({time.time()-t0:.0f} s, {len(ev.cache)} evals) overall best {overall}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
