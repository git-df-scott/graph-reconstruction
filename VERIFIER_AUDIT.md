# Verifier audit and canonical CE protocol

## Bottom line

Before this audit, the repository had several good exact components but no
single independent gate that enforced the full definition of a CE.  The new
standalone gate is:

```bash
python3 scripts/hostile_ce_checker.py --g6 'GRAPH6_G' 'GRAPH6_H' \
  --certificate ce-certificate.json --pretty
```

or:

```bash
python3 scripts/hostile_ce_checker.py --input pair.json \
  --certificate ce-certificate.json --pretty
```

It imports no campaign modules.  A graph is serialized as graph6 plus an
explicit edge list.  No hash decides any mathematical property.

## Checks performed from scratch

1. adjacency is finite, simple, loopless, symmetric, and duplicate-free;
2. both graphs have the same order and the order is at least three;
3. parent canonical labels differ;
4. an independent adjacency backtracker fails to find a parent isomorphism;
5. every vertex-deleted card is constructed explicitly;
6. exact canonical card labels are sorted with occurrences retained;
7. the canonical deck multisets agree;
8. independently, deletion occurrences are matched by a perfect matching
   whose edges are exact card isomorphisms;
9. the two parent routes and two deck routes must agree;
10. the JSON certificate receives a SHA-256 integrity checksum only after all
    decisions are complete.

Only status `VERIFIED_COUNTEREXAMPLE` passes.  `CEC` is not emitted by this
checker: CEC is a workflow label for explicit `G,H` that already have equal
decks and await exactly one independent check.

## Hostile controls

Run:

```bash
python3 scripts/hostile_ce_checker.py --self-test --pretty
python3 -m unittest tests.test_hostile_ce_checker -v
```

| Control | Purpose | Required result |
|---|---|---|
| Relabeled cycle | genuinely equal decks and an actual parent isomorphism | reject as parent-isomorphic |
| Empty vs one-edge graph at order 2 | known equal decks outside the conjecture's order range | reject order below three |
| graph6 `B_` vs `Bo` | same card-type support but multiplicities `2+1` and `1+2` | reject deck mismatch |
| `C6` vs two disjoint triangles | nonisomorphic parents with the same degree sequence | reject deck mismatch |
| One altered card label | deliberately corrupted deck | reject exact multiset equality |
| All labeled graphs through order 5 | compare the independent canonical form with brute force inside canonical degree cells | exact agreement |

The full repository suite also retains local-map, incidence, CFI, covering,
and `S6` regressions.

## Existing verifier inventory

| Verifier | Equal decks seen? | Nonisomorphic parents seen? | Corruption control? | Multiplicity control? | Hostile finding |
|---|---|---|---|---|---|
| `src/grc/canon.py`, `iso.py`, `deck.py` | yes, relabelings and local-map realizations | yes, same-degree `C6` / `2C3` | no direct deck corruption | yes | exact small/structured backend; not independent of scripts importing it |
| `local_gluing_search.py` | yes, by explicit local maps | only ordinary unequal-deck controls; no simple-graph CE exists | malformed maps rejected | equations give one matched occurrence per deletion | logic is sound; globalizer absence remains only a gate |
| `covering_space_strike.py` | many equal decks from duplicate presentations | yes, candidate parents before deck grouping | no | canonical deck tuples retain occurrences | historical runs stored one representative per SHA bucket and are not logically exact; reported collisions were replayed exactly; this audit repaired future buckets to retain every exact deck but did not rerun them |
| `exceptional_s6_direct_strike.py` | yes after explicit parent swaps | every quotient-bucket pair is rescued | orbital coverage controls | orbit multiplicities `6,6,15,15` included | negative conclusion sound in its invariant domain; “independent verifier” is not independent |
| Gassmann matrix verifiers | yes, 284 and 308 bideck collisions | source row carriers are nonconjugate; collided parents all isomorphic | no | row-pattern `Counter`s preserve repetitions | exact only because degree/anchor rigidity is proved for eligible masks |
| Kocay trade verifier | yes for induced hypergraph decks | yes, Kocay source pair | category-change regression | repeated shrunken columns retained | correctly detects that induced deletion is not trace deletion |
| `deck_fixed_sat.py` | dropped-card positive control; SAT hits replay decks | yes in partial-card control | cards deliberately dropped | full replay uses exact deck | earlier unsound degree-group symmetry was caught; custom row lex-leader still lacks a proof or DRAT certificate |
| `card_fibre.c` | tournament counterexamples at orders 5 and 6 | yes, tournament controls | no | multiset hash is order-independent | not exact: 64-bit hash equality suppresses distinct parent hashes and deduplicates distinct card types on collision |
| `sigma_dfs.c` | local-map equalities are implicit | zero-globalizer colored objects sought | n=5 control | one row per deletion | completeness normalization and persistent-globalizer prune are sound; large outputs not frozen or independently rerun |

## Local-map to graph realization, re-derived

Let the parent copies be `X` and `Y`, and after relabeling the deck matching
pair deletion `x_i` with deletion `y_i`.  A row `sigma_i` must be a genuine
bijection `X-{x_i} -> Y-{y_i}`.  Extending it by `sigma_i(x_i)=y_i` is only a
notation convenience.

For every edge avoiding `i`, impose

```text
A_uv = B_sigma_i(u),sigma_i(v).
```

The transitive closure partitions all `G` and `H` edge slots.  Assign one bit
to each class.  Row `i` then maps `G-x_i` to `H-y_i` edge by edge.  Since the
deletion matching is a bijection over all `i`, the complete decks agree with
multiplicity.  No consistency between different card maps is additionally
required.

A parent permutation `tau` is an exact-label globalizer precisely when every
`G` edge slot and its `H` image lie in the same equality class.  It is then an
isomorphism for every binary assignment.  Discarding that local-map object is
sound.  If no exact-label globalizer exists, a binary assignment must still
hit at least one unequal class pair for every `tau`; otherwise coarsening the
class labels to bits creates an assignment-specific isomorphism.

Consequences of the audit:

- **A, overstrong globalizer:** not found.  Exact-label globalizers are a
  valid universal obstruction; class-permuting symmetries are not treated as
  universal by the core formalism.
- **B, unrealizable survivor:** possible for abstract variants, but the core
  row validator correctly requires one deletion-fixed permutation per card;
  binary edge-class assignments then always realize actual graphs.
- **C, exact-label vs unlabeled:** earlier prose sometimes said “globalizer”
  without the qualifier, but the implemented predicate is exact-label.
- **D, multiplicity loss:** not found in the normalized complete map family;
  pairing deletion `i` to deletion `i` retains all `n` occurrences.  Several
  auxiliary searches use support hashes or stable quotients only as filters;
  they must not be promoted to deck equality without final replay.

## Required future replay

For a plausible hit, keep the discovery process alive but freeze its explicit
graphs immediately.  Run the standalone checker, then use nauty/Traces or a
second mature package on the serialized graphs.  Store:

- the exact input JSON;
- the checker certificate;
- canonical graph6/sparse6 records from the external backend;
- the external parent's nonisomorphism result;
- all external card canonical labels, sorted without deduplication;
- tool versions and command lines.

No local maps, SAT model, stable quotient, digest, common-card count, or
zero-globalizer object can substitute for that package.
