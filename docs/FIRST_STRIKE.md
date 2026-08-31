# First strike: parity-selector mismatch saturation

## Binding status

- Ordinary GRC counterexample: **NO**.
- Full proof: **NO**.
- Search target: exact equality of the complete vertex decks.

## Reproduced control

Sergey Ivanov's public parity-selector construction was regenerated and
verified with nauty 2.8.  The 78-vertex roots are connected and
nonisomorphic.  Their ordinary vertex decks have exact multiset intersection
51, with 16 distinct card types on each side.

The 27 unmatched deletions on each side are completely localized:

- 15 deletions from one of the two swapped port classes;
- 6 pair-vertex deletions;
- 6 selector-vertex deletions.

All 51 matched cards arise from deletion in the other three port classes.

## Extracted finite equation

The fixed auxiliary vertices are the reason that auxiliary deletion cannot
repair the odd-permutation obstruction.  Replace every vertex of the
16-vertex quotient (4 ports, 6 pair vertices, 6 selectors) by an independent
false-twin class.  A multiplicity vector is then acted on by the 12 even port
permutations.

For a vector `x`, deletion in coordinate `i` produces `x-e_i`, with
multiplicity `x_i`.  We therefore search for distinct group orbits with the
same multiset

```text
{ orbit(x-e_i), repeated x_i times }.
```

Such a collision is not automatically a GRC counterexample: it must be
expanded to ordinary graphs, the roots must be independently proved
nonisomorphic, and their complete decks must be canonicalized by nauty.

## First exact result

For all 65,536 vectors whose 16 coordinates independently take the values 2
or 3, there are 5,760 A4-orbits and **no weighted-deck collision**.  This
closes the smallest nonvanishing multiplicity box for this construction; it
does not address larger alphabets or other selector quotients.

## Local-gluing equation

Prescribe a card bijection and a concrete card isomorphism `sigma_i` for each
deleted vertex.  The identities

```text
G[u,v] = H[sigma_i(u),sigma_i(v)]  whenever u,v != i
```

partition the two parents' possible edge positions into equality classes.
Every binary assignment to these classes is hypomorphic by construction.

If the two complete graphs whose edges are colored by equality-class labels
are color-preservingly isomorphic, one global vertex permutation proves that
**every** binary assignment in that system has isomorphic parents.  This is an
exact all-assignments closure test.

Initial results:

- all 1,296 local-map systems at order 4 pass the universal gluing test;
- all 7,962,624 local-map systems at order 5 pass the universal gluing test;
  the equality-class histogram is
  `{1: 7277280, 2: 580848, 3: 83900, 4: 17130, 5: 2400, 6: 980,
  7: 40, 8: 45, 10: 1}`;
- at order 13, 4,726/4,726 sampled nontrivial systems pass;
- at order 14, 23,451/23,451 sampled nontrivial systems pass across local
  one-, two-, and three-move generators;
- an earlier direct replay of 424,292 order-14 assignments also found every
  parent pair isomorphic.

These finite results are not a proof of the universal gluing lemma or GRC.

At order 6, a seven-class system was found in which none of the six prescribed
card maps extends to a global color-preserving map.  Nevertheless, the identity
permutation globally identifies the two colored edge spaces, so all 128 binary
assignments still have isomorphic parents.  A further structured harvest found
30 such locally nongluing systems (maximum seven classes); every one retained
an external global permutation.  This refutes the stronger claim that one of
the given card maps must extend, while leaving the actual global-gluing target
open.
