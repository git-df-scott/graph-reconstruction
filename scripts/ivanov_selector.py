"""Ivanov's selector construction (arXiv:2608.11930, 12 Aug 2026), r = 4.

Ports P_1..P_4 are false-twin classes of sizes (a1,a2,a3,a4).  Six pair
vertices q_ij, each joined to every vertex of P_i and P_j.  Six selector
vertices z_1..z_6 forming K_6, each joined to three q's along the six labelled
paths below.  Lemma 2.1: the port permutations extending to automorphisms of
the selector are exactly the EVEN ones, so swapping two class sizes (an odd
permutation) gives a non-isomorphic partner.

The paper proves b(G,H) >= 51 for sizes (15,16,17,18) on n = 78.  It does not
compute b exactly.  This module does: b = 51, so the bound is tight, and
deleting a selector vertex does NOT restore the odd port permutation.  Over
port-class sizes 1..6 the minimum deficit n - b is 13, never 0.  See SOL_9.md.
"""
import nauty_deck as deck

Z_TO_Q = {                       # the six labelled paths of Lemma 2.1
    0: [(1, 2), (1, 3), (2, 4)],
    1: [(1, 2), (1, 4), (3, 4)],
    2: [(1, 2), (2, 3), (3, 4)],
    3: [(1, 3), (1, 4), (2, 3)],
    4: [(1, 3), (2, 4), (3, 4)],
    5: [(1, 4), (2, 3), (2, 4)],
}
PAIRS = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]


def build(sizes):
    """Graph6 string for the selector graph with port classes of given sizes."""
    assert len(sizes) == 4
    idx, edges = {}, []

    def node(k):
        if k not in idx:
            idx[k] = len(idx)
        return idx[k]

    for i, s in enumerate(sizes, start=1):        # port classes (false twins)
        for c in range(s):
            node(('p', i, c))
    for pr in PAIRS:
        node(('q', pr))
    for t in range(6):
        node(('z', t))
    for pr in PAIRS:                              # ports -> their pair vertices
        for i in pr:
            for c in range(sizes[i - 1]):
                edges.append((node(('p', i, c)), node(('q', pr))))
    for t in range(6):                            # K6 among selector vertices
        for u in range(t + 1, 6):
            edges.append((node(('z', t)), node(('z', u))))
        for pr in Z_TO_Q[t]:                      # selector -> pair vertices
            edges.append((node(('z', t)), node(('q', pr))))
    return deck.g6_encode(len(idx), edges)


def pair_graphs(sizes):
    """G = S(sizes), H = S(sizes with the first two swapped)."""
    sw = [sizes[1], sizes[0]] + list(sizes[2:])
    return build(sizes), build(sw)
