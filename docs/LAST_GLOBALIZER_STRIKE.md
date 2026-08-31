# Last-globalizer strike

Date: 2026-08-31

## Verdict

`GRC CE: NO`

## Replayed certificates

- 10/10 unit tests pass.
- All 32,768 labelled six-vertex graphs give 156 decks and zero collisions
  between nonisomorphic parents.
- The 2/3 weighted-selector quotient has 5,760 orbits and zero collisions.
- Ivanov's public examples reproduce overlaps 51/78 and 155/234.
- The complete order-four local-map census reproduces 1,296/1,296 systems
  with an exact-label globalizer.
- The complete order-five census reproduces 7,962,624/7,962,624 systems with
  an exact-label globalizer.  Its class histogram is
  `{1:7277280, 2:580848, 3:83900, 4:17130, 5:2400, 6:980, 7:40, 8:45, 10:1}`.

The historical 424,292-assignment order-14 figure has no frozen command or
output certificate in commit `baae75a`; it is therefore retained only as a
reported earlier run, not silently upgraded to a replayed certificate.

## Exact construction semantics

See `CONSTRUCTION_FORMALISM.md`.  For each parent permutation `tau`, the new
instrument computes the set of class equalities required for `tau` to be an
isomorphism of a particular binary realization.  A separating assignment
must violate at least one equality for every `tau`.  An exact-label
globalizer has no nontrivial equality and makes separation impossible.

## Seven-class order-six obstruction

The complete certificate is emitted by:

```bash
python3 scripts/analyze_n6_obstruction.py
```

In lexicographic edge order its class arrays on both parents are

`[5,5,5,0,1,2,3,5,5,4,5,5,5,5,6]`.

None of the six prescribed card maps is an exact-label globalizer.  Identity
is the unique exact-label globalizer.  Consequently no binary assignment can
break it.  Independent exact replay of all `2^7=128` assignments gives zero
deck failures and zero nonisomorphic parent pairs.

SHA256 of the pretty-printed certificate produced on this strike:
`26c3563b20a8eb31c6fba898a5d7232ddfed3f8108b9d7351734a799f2c7a139`.

## New exhaustive order-six classifications

The following domains were enumerated as direct Cartesian products, without
random sampling or quotient omissions:

1. Exactly one transposition on each deleted card: `10^6 = 1,000,000`
   systems.  Zero systems have no exact-label globalizer.  Exactly 10 systems
   have none of their six prescribed maps globalize.
2. Identity or one transposition on each deleted card:
   `11^6 = 1,771,561` systems.  Zero systems have no exact-label globalizer.
   The locally nongluing set is the same 10 systems.

Those 10 systems form exactly one orbit under simultaneous parent relabeling
and interchange of the two parent sides.  Every member has exactly one
exact-label globalizer, identity.  Thus the harvested examples represent one
mechanism: their generated equivalence relation gives identical class arrays
on the two parents even though none of the prescribed local maps witnesses
that fact.

Reproduce the larger classification with:

```bash
python3 scripts/exhaustive_transposition_systems.py \
  --allow-identity --progress 500000 --representatives 0
```

Observed exact class histogram:

`{1:431064, 2:514416, 3:427920, 4:214830, 5:110820, 6:50820, 7:11740, 8:7395, 9:2240, 10:90, 11:165, 12:60, 15:1}`.

## False lemmas killed

- “One of the prescribed card maps must globalize” remains false.
- “The 30 harvested systems indicate many distinct order-six mechanisms” is
  false in the classified transposition slice: the complete locally
  nongluing set is one symmetry orbit.
- “A binary coloring may break the seven-class rescue” is false: its unique
  rescue is exact-label identity and therefore survives every coloring.

## Live CE address

The next unclosed local-map territory at order six requires at least one card
map outside `{identity, one transposition}`.  The highest-value search is a
canonical branch-and-bound over systems containing a 3-cycle, a product of
two transpositions, or a longer permutation, minimizing the number of
exact-label globalizers.  If zero occurs, solve the finite binary separation
conditions immediately; do not enumerate generic graphs.
