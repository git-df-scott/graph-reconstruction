# Asymmetric pseudosimilar covering-space strike

Date: 2026-09-01

## Verdict

```text
GRC CE: NO
```

A genuinely different legal-order construction was attacked.  Instead of
coarsening the old order-seven incidence partition, the search built explicit
simple graphs as two- and three-sheet covers of asymmetric pseudosimilar base
graphs.  The parents have orders 16 and 24, so every searched graph is already
above the independently verified `n <= 13` range.

Three exact domains were completed:

```text
C2 signed two-lifts, every cycle rank: 84,096 presentations
C3 cyclic three-lifts, ranks 3–5:       6,912 presentations
S3 nonabelian three-lifts, rank 3:      3,456 presentations
```

No nonisomorphic equal-deck pair exists in any stated domain.

## New construction principle

For a connected base graph `B`, replace every base vertex by a fiber of size
`q`.  Each base edge receives a permutation voltage and becomes a perfect
matching between its two fibers.  Vertex switches gauge away all voltages on
a spanning tree, so only the cycle-rank many chord voltages remain.

- `C2` gives ordinary signed two-lifts.
- `C3` gives regular cyclic three-lifts.
- `S3` gives arbitrary three-sheet permutation covers and can have trivial
  deck-transformation group.

This is not an abstract local-map gadget or binary realization.  Every state
is an explicit finite simple parent graph and is checked through its complete
ordinary vertex deck.

## Exact asymmetric pseudosimilar base family

Fix vertices `u=0`, `v=1` and the deletion isomorphism

```text
p = (0 1)(2 3)(4 5 6 7)
  = (1,0,3,2,5,6,7,4).
```

For every edge `{a,b}` not incident with vertex 0, impose

```text
X(a,b) = X(p(a),p(b)).
```

The resulting single-graph incidence partition has 12 binary classes and
therefore 4,096 exact assignments.  Every assignment automatically satisfies

```text
X-0 ~= X-1
```

under the displayed map.  Connectivity and asymmetry were then checked,
rather than assumed.

Exact automorphism backtracking gives:

```text
raw assignments:                    4,096
connected exactly asymmetric bases:   192
```

All 192 asymmetric bases are also certified by discrete color refinement;
an independent exact classification proved that color refinement missed no
asymmetric member of this incidence family.

Cycle-rank distribution:

| Rank | Bases |
|---:|---:|
| 3 | 16 |
| 4 | 32 |
| 5 | 16 |
| 6 | 16 |
| 7 | 32 |
| 8 | 16 |
| 9 | 16 |
| 10 | 32 |
| 11 | 16 |

## Frozen seed

The first recovered asymmetric pseudosimilar base is

```text
graph6: GQyPA_
degrees: 3,3,3,3,3,2,1,2
```

with edges

```text
02,04,05,13,14,17,24,26,35,37.
```

Its deletion-0 and deletion-1 cards both have exact canonical code

```text
(7,1171744).
```

The displayed `p` is replayed edge-by-edge as a card isomorphism.  Independent
backtracking returns no automorphism sending 0 to 1; the full graph is exactly
asymmetric.

## Complete C2 two-lift result

All switching classes of all 192 bases were enumerated.  The parents have
order 16.

```text
switching-class presentations: 84,096
exact deck digests:              5,256
actual parent isomorphism classes: 5,256
repeated exact decks:           78,840
repeated decks parent-isomorphic: 78,840
nonisomorphic equal-deck pairs:      0
```

The large collision count is real but not a counterexample signal.  A single
parent cover can admit many different base/fiber quotient descriptions.
Every digest collision was replayed as a full exact deck equality, and every
exact collision was then passed to the independent parent-isomorphism
backtracker.  All 78,840 collisions were isomorphic-parent duplicates.

Consequently the ordinary deck is injective on the 5,256 actual parent
isomorphism classes in this complete two-lift domain.

## C3 odd-voltage result

The involutive fiber symmetry of two-lifts might have caused the obstruction,
so the complete cycle-rank 3–5 cyclic three-lift domain was checked next.  The
parents have order 24.

```text
bases:                         64
voltage presentations:     6,912
parent isomorphism classes:   218
distinct exact decks:         218
repeated exact decks:       6,694
repeated decks isomorphic:  6,694
nonisomorphic equal decks:       0
```

The deck is again injective on actual parent classes.

## S3 nonabelian result

Regular cyclic covers always possess a global fiber translation.  To remove
that symmetry, every chord voltage was allowed to be an arbitrary permutation
in `S3`.  The complete rank-three domain gives:

```text
bases:                         16
voltage presentations:     3,456
parent isomorphism classes:    49
distinct exact decks:          49
repeated exact decks:       3,407
repeated decks isomorphic:  3,407
nonisomorphic equal decks:       0
```

Thus noncommuting monodromy and potentially trivial cover automorphism groups
do not by themselves create a deck collision.

## Exact verification stack

The search uses:

1. union-find discovery of the 12 base-edge incidence classes;
2. direct replay of the pseudosimilar deletion isomorphism;
3. independent exact automorphism backtracking for all 4,096 bases;
4. exact spanning-tree gauge normalization;
5. explicit adjacency-bitset construction of every cover;
6. complete multiplicity-preserving canonical vertex decks;
7. SHA-256 only as a collision filter, never as proof;
8. exact deck replay on every digest collision;
9. independent adjacency/backtracking parent isomorphism on every exact
   collision.

Any nonisomorphic exact collision would stop the search as a legal-order CE
candidate.  No candidate reached that gate.

Recorded discovery runtimes were approximately:

```text
C2 global hostile replay: 400.51 seconds
C3 ranks 3–5:             110.84 seconds
S3 rank 3:                 70.46 seconds
```

The reusable implementation streams bases and retains one representative per
deck digest.  It does not retain giant populations of Python graph objects.

## Finite theorem

**Computationally exhaustive:** In the fixed 12-class pseudosimilarity family
defined by `p=(0 1)(2 3)(4 5 6 7)`, every connected asymmetric base was found
exactly.  Across all signed two-lifts, cyclic three-lifts through rank five,
and nonabelian three-lifts at rank three, equal ordinary vertex decks occur
only between isomorphic parents.

This is a theorem about the stated finite cover domains.  It is not the Graph
Reconstruction Conjecture and does not exclude counterexamples elsewhere.

## Structural lesson and next strike

The failure is no longer an exact-label globalizer.  It is quotient
nonuniqueness:

```text
many (base, voltage) descriptions
    -> one cover isomorphism class
    -> one exact deck.
```

Increasing cycle rank merely produces more voltage descriptions unless the
local cards can change monodromy in a way unavailable to the whole parent.
The precise next object is therefore a pair of **locally conjugate but
globally nonconjugate monodromy representations**.  In group language this is
a Gassmann/Sunada-type pair adapted to vertex deletion; in graph language it
is two nonisomorphic Schreier covers whose every deleted card has conjugate
monodromy.

That is the next direct CE address.  It changes the representation, not just
the voltage values, and attacks the mechanism that survived all three cover
searches.
