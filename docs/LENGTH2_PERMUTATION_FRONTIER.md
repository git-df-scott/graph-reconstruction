# Exact order-six permutation-length-two frontier

Date: 2026-08-31

## Verdict

`GRC CE: NO`

## Domain and completeness

For every deleted vertex `i`, this search restricts `sigma_i` to one of the
35 permutations of the other five vertices having cycle type either `3` or
`2+2`.  Every mixture of these two types is included.

The seven strata are indexed by the number `r` of 3-cycle cards.  When `r>0`,
simultaneous parent relabeling sends a chosen 3-cycle card to deleted vertex 0
and conjugates it to one fixed 3-cycle.  When `r=0`, the same normalization is
performed with a fixed double transposition.  Canonical-prefix rejection under
the anchor centralizer (order 6 or 8) cannot delete an entire orbit: the least
member of every residual orbit has a least prefix at every depth.  Therefore
the visited leaves cover the full stated domain, although systems with several
possible anchors may still occur more than once.

## Exhaustive result

| `r` | Raw anchored domain | Canonical leaves | Identity rescues | Nonidentity rescues |
|---:|---:|---:|---:|---:|
| 0 | 759,375 | 95,280 | 95,275 | 5 |
| 1 | 759,375 | 126,630 | 126,623 | 7 |
| 2 | 5,062,500 | 843,885 | 843,822 | 63 |
| 3 | 13,500,000 | 2,250,202 | 2,249,956 | 246 |
| 4 | 18,000,000 | 3,000,200 | 2,999,558 | 642 |
| 5 | 12,000,000 | 2,000,120 | 1,998,869 | 1,251 |
| 6 | 3,200,000 | 533,388 | 532,421 | 967 |
| **Total** | **53,281,250** | **8,849,705** | **8,846,524** | **3,181** |

No visited system has zero exact-label globalizers.  Hence no binary class
assignment in this entire domain can give nonisomorphic parents.

This is a computationally exhaustive finite theorem, not a proof of GRC and
not a theorem about local maps of other cycle types.

## Rescue classification

Most systems are rescued by identity.  For all 3,181 nonidentity cases, every
one of the 720 parent permutations was checked and the complete exact-label
globalizer set was counted.  The possible counts across the seven strata are

`2, 3, 4, 6, 8, 10, 16, 72`.

Among the nonidentity-rescued exceptions, the minimum two occurs in the `r=2`
and `r=4` strata.  This does not assert that two is the minimum over systems
short-circuited after finding identity.  A frozen `r=2` representative has
three edge classes and local maps

```text
(0,2,3,1,4,5)
(4,1,2,5,0,3)
(4,1,2,5,0,3)
(5,2,1,3,4,0)
(0,5,1,3,4,2)
(0,2,1,4,3,5)
```

Its only exact-label globalizers are

```text
(0,2,1,3,4,5)
(4,1,2,5,0,3)
```

Both preserve every binary assignment, so its eight realizations are all
isomorphic parent pairs with exactly equal decks.  It is not a CE.  This
primitive is the sharp coupling target: two blocks must force incompatible
choices between their two rescue permutations while retaining all deletion
maps.

## Finite theorem extracted

**Order-six length-two gluing theorem (computationally exhaustive).**  If all
six normalized deletion maps fix their deleted vertex and each restricts to a
3-cycle or a double transposition on the other five vertices, then the induced
two edge-class-labelled complete graphs admit a label-preserving parent
permutation.  Consequently every binary realization has isomorphic parents.

Reproduce a stratum with, for example:

```bash
python3 scripts/exhaustive_length2_frontier.py \
  --family mixed --three-count 2 --progress 250000
```

The homogeneous endpoints use `--family double` and `--family 3cycle`.
