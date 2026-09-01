# Sol 4 — Legal-order covering-space strike

Date: 2026-09-01

## Live verdict

```text
GRC CE: NO
```

This session abandoned further Goldilocks coarsening and attacked explicit
legal-order graphs through graph covers.  No counterexample was found, but
three new structured domains were closed exactly and the first explicit
asymmetric pseudosimilar base was frozen in the repository.

## New angle

Parents were built as signed or permutation-voltage lifts of an asymmetric
pseudosimilar base.  This bypasses binary realization and the old exact-label
globalizer obstruction:

```text
base order 8 -> two-lift parent order 16
base order 8 -> three-lift parent order 24
```

Every searched state is already an actual finite simple graph above order 13.

## Frozen base mechanism

The exact incidence system uses

```text
p=(0 1)(2 3)(4 5 6 7)
```

as an isomorphism from deletion 0 to deletion 1.  It has 12 edge classes and
4,096 binary assignments.  Exact backtracking found precisely 192 connected
asymmetric bases.

First seed:

```text
graph6 GQyPA_
edges 02,04,05,13,14,17,24,26,35,37
pseudosimilar vertices 0,1
automorphism 0->1: none
```

## Complete results

### Signed two-lifts (`C2`), every cycle rank

```text
bases:                           192
presentations:                84,096
parent isomorphism classes:    5,256
distinct exact decks:          5,256
repeated exact decks:         78,840
repeated decks isomorphic:    78,840
nonisomorphic equal decks:         0
```

### Cyclic three-lifts (`C3`), ranks 3–5

```text
bases:                            64
presentations:                 6,912
parent isomorphism classes:      218
distinct exact decks:            218
repeated exact decks:          6,694
repeated decks isomorphic:     6,694
nonisomorphic equal decks:         0
```

### Nonabelian three-lifts (`S3`), rank 3

```text
bases:                            16
presentations:                 3,456
parent isomorphism classes:       49
distinct exact decks:             49
repeated exact decks:          3,407
repeated decks isomorphic:     3,407
nonisomorphic equal decks:         0
```

## Strongest theorem

Within each completed domain, the ordinary vertex deck is injective on the
actual parent isomorphism classes.  Voltage presentations are massively
nonunique, but every repeated deck was explained by parent isomorphism.

The two-lift statement covers every cycle rank of every connected asymmetric
base in the fixed pseudosimilarity incidence family.

## Hostile verification

- Full decks were compared with multiplicity.
- SHA-256 was only a streaming filter.
- Every digest collision received an exact deck replay.
- Every exact collision received independent adjacency/backtracking parent
  isomorphism.
- All 78,840 two-lift, 6,694 cyclic, and 3,407 nonabelian repeated decks were
  parent-isomorphic.
- No reduced-deck or local-map inference was used.

## Artifacts

```text
scripts/covering_space_strike.py
tests/test_covering_space_strike.py
docs/COVERING_SPACE_STRIKE.md
docs/COVERING_SPACE_CERTIFICATE.json
SOL_4.md
```

## Exact next strike

Scaling voltages on the same representation is not justified.  The missing
object is a pair of locally conjugate but globally nonconjugate monodromy
representations—a deletion-adapted Gassmann/Sunada pair.  Such a pair could
make every punctured Schreier cover isomorphic while leaving the two whole
covers nonisomorphic.

That is the next genuinely new CE mechanism.  It targets the quotient
nonuniqueness exposed here rather than enlarging another closed census.
