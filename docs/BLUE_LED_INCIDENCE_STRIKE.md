# Blue-LED incidence and holonomy strike

## Binding verdict

```text
GRC CE: NO
```

No nonisomorphic finite simple graphs with equal full vertex decks were
found.  This strike did not continue the direct exceptional-`S6` orbital
graph search.  It changed the construction category to two-sorted incidence
matrices and used their incidence/split graphs as deletion-faithful ordinary
graph realizations.

## Conceptual reset

For a binary incidence matrix, deleting an incidence-graph vertex deletes
exactly one row or exactly one column.  Thus a pair of matrices with equal
complete row-deletion and column-deletion decks gives equal ordinary graph
decks, provided the two sorts are structurally recognizable.  This eliminates
the extra gadget-card problem that blocks most transfers from tournaments,
hypergraphs, and colored structures.

The target became:

```text
nonisomorphic matrices with equal row- and column-deletion decks
```

rather than another direct search over unstructured graph edges.

## Degree-180 Gassmann incidence strike

The unique outer-balanced nonconjugate pair from `SOL_6` was used as the row
carrier:

```text
H = <(0 1)(2 3), (0 2)(1 3)>
K = <(0 1)(2 3), (0 1)(4 5)>.
```

The first column carrier was the ordinary plus exceptional six-point action.
Both sides have six row-column orbitals, so all `64 x 64 = 4,096` incidence
pairs were classified.  Adding a clique on the twelve columns makes the
column sort recognizable.  There were 284 exact bideck collisions; every one
had a parent matrix isomorphism.  Nonisomorphic deck collisions: zero.

The second column carrier was the rigid 21-vertex Johnson anchor consisting
of six point vertices forming a clique and fifteen independent duad vertices,
with point-duad membership edges.  Its automorphism group is exactly `S6`:
degrees distinguish the two sorts, and each duad is uniquely determined by
its two point neighbors.  The `H` and `K` row carriers each have nine
row-anchor orbitals.  All 512 invariant matrices per side were constructed;
480 `H` masks and 476 `K` masks passed degree separation in the parent and
all three representative card types.  Across 228,480 eligible structured
pairs there were 308 exact bideck collisions, all parent-isomorphic.

### New invariant-row obstruction

Let an anchor automorphism group `Gamma` act on row-neighborhood patterns,
and let two row multisets be `Gamma`-invariant.  If deleting one row from
each yields equal row cards via an element of `Gamma`, then

```text
C_1 - delta_a = C_2 - delta_b.
```

Because `C_1-C_2` is invariant, `delta_a-delta_b` must be invariant.  On a
nontrivial transitive pattern orbit this forces `a=b` and `C_1=C_2`.
Therefore full group-invariant rigid-anchor coupling cannot produce the
required missing-row asymmetry.  The next viable incidence construction must
be non-invariant before deletion and recover symmetry only after deletion—a
design trade, not another orbital union.

## Tournament transfer closed at order eight

Stockmeyer's explicit order-eight tournament pair was reconstructed from the
published matrices and all deletion-card isomorphisms were enumerated.  There
are nine complete choices of local card-map system.  Eight choices collapse
to two undirected edge classes; the ninth has four.  Every choice has an
exact-label globalizer (the first eight by identity).  Consequently forgetting
arrow direction destroys the tournament obstruction before binary graph
realization.

At the matrix level, direct and transpose variants can have equal bidecks,
but every such collision is parent-isomorphic because row and column
permutations desynchronize.  A successful transfer must enforce the same
permutation on both indices with a deletion-fragile synchronizer.

## First legal-order matrix-bideck search

Binary `7 x 7` matrices were realized as order-14 split graphs: seven row
vertices are independent and seven column vertices form a clique.  Complete
row- and column-deletion map systems were imposed simultaneously by union-find
on the 98 parent incidence slots.

Random near-identity results:

| domain | systems | information-retaining | zero globalizer |
|---|---:|---:|---:|
| one transposition per component | 10,000 | 1,127 | 0 |
| two transpositions per component | 100,000 | 154 | 0 |

The strongest class counts were six and three respectively.  Every
information-retaining system had an exact-label matrix globalizer, so binary
realization was correctly skipped.

## Crossed holonomy strike

The certified seven-symbol `BASE_LIFT` local-map primitive was placed on both
matrix axes.  For every `q in S7`, its conjugate family `B=qAq^-1` was coupled
as

```text
row deletion i:     (A_i on rows, B_i on columns)
column deletion i:  (B_i on rows, A_i on columns).
```

All 5,040 conjugates were classified.  The systems retained as many as 19
binary incidence classes:

```text
1:576, 4:2588, 5:4, 9:1722, 10:6, 16:120, 17:22, 19:2.
```

Zero-globalizer systems: zero.  Only four rescue permutations occurred,
all acting on the primitive four-vertex core.  Targeted joins of
representatives requiring different rescues were also exact: every pair,
triple, and the four-way join regenerated a globalizer, usually identity.
A further 50,000 asymmetric two-conjugate crossed systems retained up to 17
classes but again had zero zero-globalizer systems.

## Strongest new conclusion

The new construction language is viable, but three mechanisms are now
separated cleanly:

1. invariant incidence families restore the missing row by orbit balance;
2. tournament symmetrization loses synchronization between its two indices;
3. crossed matrix holonomy retains information but the certified primitive's
   four-core rescue torsor closes under every tested join.

The live address is a **non-invariant incidence trade with deletion-dependent
symmetry recovery**, preferably imported from a nonreconstructible uniform
hypergraph and required to be balanced under both point and block deletion.
That is the first source category in this strike not reduced to an already
closed globalizer mechanism.

## Reproduction

```bash
PYTHONPATH=scripts python scripts/gassmann_incidence_bideck.py
PYTHONPATH=scripts python scripts/gassmann_johnson_anchor.py
PYTHONPATH=scripts python scripts/tournament_transfer_probe.py
PYTHONPATH=scripts python scripts/matrix_bideck_local_search.py --systems 10000 --assignments 64 --moves 1
PYTHONPATH=scripts python scripts/matrix_bideck_local_search.py --systems 100000 --assignments 64 --moves 2
PYTHONPATH=scripts python scripts/crossed_matrix_holonomy.py
```

