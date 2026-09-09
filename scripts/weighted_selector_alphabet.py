#!/usr/bin/env python3
"""Exhaustive weighted-deck collision search over larger multiplicity alphabets.

Extends scripts/weighted_selector_search.py, which closed the {2,3}^16 box,
to every vector in {low, ..., low+k-1}^16 with k=3.  Same orbit equation:
the 12 even port permutations act on 16 false-twin classes; a vector x has
weighted deck { orbit(x-e_i) with multiplicity x_i }.  A collision between
distinct orbits is a CANDIDATE only; it must be expanded and nauty-checked.

Two independent 64-bit multiset hashes detect candidate collisions; every
hash collision is re-verified exactly in Python before it is reported.  No
hash equality is ever accepted as a certificate.
"""
from __future__ import annotations
import argparse, itertools, json, sys, time
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from weighted_selector_search import COORDINATES, INVERSE_ACTIONS, canonical_weight, weighted_deck

N = 16
PERMS = np.array(INVERSE_ACTIONS, dtype=np.int64)  # 12 x 16, vector[perm] is the image

def encode(vals: np.ndarray, base: int) -> np.ndarray:
    pw = base ** np.arange(N - 1, -1, -1, dtype=np.int64)
    return vals.astype(np.int64) @ pw

def canonical_codes(vals: np.ndarray, base: int) -> np.ndarray:
    best = None
    for p in PERMS:
        c = encode(vals[:, p], base)
        best = c if best is None else np.minimum(best, c)
    return best

def mix(x: np.ndarray, k: np.uint64) -> np.ndarray:
    x = x.astype(np.uint64) * k
    x ^= x >> np.uint64(29)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(32)
    return x

def run(low: int, k: int, chunk: int) -> dict:
    base = low + k + 1
    total = k ** N
    seen: dict[int, tuple[int, ...]] = {}
    seen2: dict[int, tuple[int, ...]] = {}
    orbits = 0
    hash_hits = 0
    exact_hits = []
    t0 = time.perf_counter()
    digits = k ** np.arange(N, dtype=np.int64)
    for start in range(0, total, chunk):
        idx = np.arange(start, min(start + chunk, total), dtype=np.int64)
        vals = ((idx[:, None] // digits[None, :]) % k + low).astype(np.int64)
        code = encode(vals, base)
        canon = canonical_codes(vals, base)
        keep = vals[code == canon]
        orbits += len(keep)
        if len(keep) == 0:
            continue
        h1 = np.zeros(len(keep), dtype=np.uint64)
        h2 = np.zeros(len(keep), dtype=np.uint64)
        for i in range(N):
            card = keep.copy()
            card[:, i] -= 1
            cc = canonical_codes(card, base)
            m = keep[:, i].astype(np.uint64)
            h1 += m * mix(cc, np.uint64(0x9E3779B97F4A7C15))
            h2 += m * mix(cc + np.uint64(7), np.uint64(0xD6E8FEB86659FD93))
        keyvals = (h1 ^ (h2 << np.uint64(1))).tolist()
        h1l = h1.tolist(); h2l = h2.tolist()
        for row, kv, a1, a2 in zip(keep.tolist(), keyvals, h1l, h2l):
            prev = seen.get(kv)
            if prev is None:
                seen[kv] = tuple(row)
                continue
            hash_hits += 1
            if weighted_deck(prev) == weighted_deck(tuple(row)) and canonical_weight(prev) != canonical_weight(tuple(row)):
                exact_hits.append({'left': prev, 'right': row})
                print(json.dumps({'status': 'WEIGHTED_ORBIT_COLLISION_NOT_YET_A_GRC_CE', 'left': prev, 'right': row}), flush=True)
        if (start // chunk) % 8 == 0:
            print(f'progress {min(start+chunk,total)}/{total} orbits={orbits} hash_hits={hash_hits} exact={len(exact_hits)} t={time.perf_counter()-t0:.0f}s', flush=True)
    return {'alphabet': list(range(low, low + k)), 'vectors': total, 'orbits': orbits,
            'hash_collisions_checked_exactly': hash_hits, 'exact_collisions': exact_hits,
            'wall_seconds': time.perf_counter() - t0}

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--low', type=int, default=1)
    ap.add_argument('--k', type=int, default=3)
    ap.add_argument('--chunk', type=int, default=1 << 20)
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    r = run(a.low, a.k, a.chunk)
    print(json.dumps({k: v for k, v in r.items()}, indent=1))
    if a.out:
        with open(a.out, 'w') as f: json.dump(r, f, indent=1)

if __name__ == '__main__':
    main()
