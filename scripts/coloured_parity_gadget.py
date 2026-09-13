"""Deletion-fragile parity on the COLOURED carrier (SOL_5's mechanism, new carrier).

SOL_5 closed the binary-CFI-code version of this mechanism: a global parity
obstruction that dissolves after every single deletion, which is the exact
logical form of a Kelly-Ulam counterexample.  The same form lives in
port-coloured graphs and is NOT covered by that theorem.  It is also the
condition Ivanov's family (scripts/ivanov_selector.py) must meet to reach
deficit zero.

A gadget is (S, sigma) with sigma : V(S) -> {0, +, -}; tau0 flips + and -.
Write sigma_bar = tau0 . sigma.  The two conditions are

  (a) (S, sigma) is NOT isomorphic to (S, sigma_bar)     -- parents differ
  (b) deck(S, sigma) == deck(S, sigma_bar) as multisets  -- every gadget card matches

(b) matches card v of one side to card w of the other for ANY w, not w = v.
An earlier version of this search wrongly demanded w = v and was strictly too
narrow; its negative was weaker than it looked.  See SOL_9.md.

Coloured canonical forms go through nauty by a faithful encoding: attach to
each vertex a pendant path whose length encodes its colour, with all lengths
above the gadget order so no pendant can be confused with gadget structure.
Coloured isomorphism holds iff the encodings are isomorphic.

Result: 216,507 gadgets through m = 7, zero hits.
"""
import nauty_deck as deck
from itertools import product

COLOURS = (0, 1, 2)          # 0 neutral, 1 = '+', 2 = '-'
FLIP = {0: 0, 1: 2, 2: 1}


def encode(m, edges, sigma):
    """Faithful uncoloured encoding of a coloured graph, for nauty."""
    L = m + 2                                    # pendant lengths exceed the order
    n, out = m, list(edges)
    for v in range(m):
        prev = v
        for _ in range(L + sigma[v]):
            out.append((prev, n))
            prev = n
            n += 1
    return deck.g6_encode(n, out)


def coloured_deck_keys(m, edges, sigma):
    """Encodings of the gadget itself and of each of its coloured cards."""
    keys = [encode(m, edges, sigma)]
    for v in range(m):
        r = {u: (u if u < v else u - 1) for u in range(m) if u != v}
        e2 = [(r[a], r[b]) for a, b in edges if a != v and b != v]
        s2 = [sigma[u] for u in range(m) if u != v]
        keys.append(encode(m - 1, e2, s2))
    return keys


def search(mmax=6, progress=None):
    """Enumerate gadgets on 2..mmax vertices; report those meeting (a) and (b)."""
    hits, tested = [], 0
    for m in range(2, mmax + 1):
        for g6 in deck.geng(m):
            mm, es = deck.g6_decode(g6)
            edges = sorted(es)
            batch = []
            for sigma in product(COLOURS, repeat=m):
                if all(c == 0 for c in sigma):
                    continue                     # sigma_bar == sigma, (a) impossible
                # PROVED PRUNE: every vertex lies in exactly m-1 cards, so summing
                # colour counts over the deck gives (m-1) times the parent's colour
                # count -- the coloured multiset is deck-reconstructible.  X has
                # (p,q,z) and Y has (q,p,z), so equal decks force p == q.
                if sigma.count(1) != sigma.count(2):
                    continue
                bar = tuple(FLIP[c] for c in sigma)
                if bar < sigma:
                    continue                     # each unordered pair once
                batch.append((sigma, bar))
                tested += 1
            flat = []
            for sigma, bar in batch:
                flat += coloured_deck_keys(m, edges, sigma)
                flat += coloured_deck_keys(m, edges, bar)
            if not flat:
                continue
            canon = deck.canon_many(flat)
            k = m + 1
            for i, (sigma, bar) in enumerate(batch):
                a = canon[2 * i * k: 2 * i * k + k]
                b = canon[2 * i * k + k: 2 * i * k + 2 * k]
                if a[0] == b[0]:
                    continue                     # fails (a): coloured-isomorphic
                if sorted(a[1:]) == sorted(b[1:]):
                    hits.append((g6, sigma, bar))
                    print('   HIT m=%d %s sigma=%s bar=%s' % (m, g6, sigma, bar),
                          flush=True)
        if progress:
            progress(m, tested, len(hits))
    return tested, hits
