# Three best remaining CE architectures

## September-4 direct strike update

`ASTRA_DIRECT_CE_STRIKE.md` supplies an executable refinement of rank 1:
root migration through double-deletion overlaps. For a fixed shared card,
each moving card map leaves only three extension bits free; a separate SAT
branch includes every root-fixed map. Twenty-three specified fibres were
exhausted, including arbitrary nonuniform attachments to the inherited
selector card at weights `(1,1,3,4)`. This does not close other shared cards.

The strongest next direct target is the **three-root pair/selector repair at
parent order 22**. The fixed 19-vertex core is obtained by removing vertices
9 (`q01`) and 15 (the first path-selector vertex) from that selector card.
It has 120 free edge bits across both parents, and exactly 8,745,408 possible
parent maps before grouping equivalent constraints. Its exact specification
is `data/astra_direct/next_three_root/specification.json`; the constructor is
`scripts/astra_two_root_repair.py --roots 3`.

The preceding two-root instance has an independently verified UNSAT proof
with all 175,104 parent maps excluded; its entire map set was separately
recreated with VF2. Three-root SAT was **not run**. Use this concrete continuation
before returning to the broader historical menu below.

## Original hostile-audit ranking

The ranking favors logical openness, distance from closed mechanisms, direct
production of ordinary graphs, certificate simplicity, and controllable
scaling.  Recency is not a criterion.

| Rank | Architecture | Openness | Actual graph route | Certificate | Scaling |
|---:|---|---|---|---|---|
| 1 | Shared-card automorphism cocycle | high | two one-vertex extensions of one explicit card | two graph6 strings | exponential in one card order, strongly quotientable by automorphisms |
| 2 | Trace-bideck incidence trade | high | rigid split/incidence graphs | two binary matrices plus graph6 | linear trade algebra before binary realization |
| 3 | Deletion-local monodromy without a global conjugator | medium-high | explicit Schreier/cover graphs with a non-invariant anchor | group generators, voltages, two graph6 strings | double-coset variables instead of arbitrary edges |

## 1. Shared-card automorphism cocycle

### Core idea

Every CE is `C+N` versus `C+N'` for a shared card `C`.  Parent
nonisomorphism says `N,N'` are in different `Aut(C)` orbits.  Card equality
requires deletion-dependent isomorphisms of cards of `C` to carry the two
neighborhoods locally.  The missing object is therefore a nontrivial cocycle:
locally equivalent neighborhoods that do not globalize to one automorphism
of `C`.

This absorbs the useful part of pseudosimilarity without assuming one fixed
deletion map or one voltage group.  It produces ordinary graphs immediately
and a hit has the simplest possible certificate.

### First experiment

For one deliberately constructed asymmetric card `C` with several repeated
card types:

1. compute `Aut(C)` on neighborhood subsets;
2. enumerate exact isomorphisms among every pair of cards `C-u`, retaining
   their action on the remaining vertices;
3. build the induced groupoid action on pairs `(N,N')`;
4. solve for different `Aut(C)` orbits that match after every deletion;
5. construct `C+N,C+N'` and send them directly to the hostile checker.

Do not score by number of common cards.  Solve the full deletion constraints.

### Stop condition

Stop a card family only after all neighborhood-pair orbits have been decided
with collision-safe exact labels.  If every local groupoid orbit meets one
global `Aut(C)` orbit, extract that as a theorem for the stated card family.
Random failure is not a stop condition.

## 2. Trace-bideck incidence trade

### Core idea

A pair of two-sorted incidence matrices with equal row-deletion and
column-deletion decks yields a pair of ordinary split graphs.  Kocay's source
failed because induced hypergraph deletion discards incident blocks, whereas
ordinary graph deletion retains the block vertices and shrinks their traces.

The open target is a non-invariant trade whose symmetry appears only after a
row or column is deleted.  Full group-invariant row families are already
theorem-blocked; the construction must deliberately violate invariance in the
parent.

### First experiment

Form an exact linear/CSP trade kernel on two `r x c` binary matrices:

- variables are signed block swaps, not arbitrary cells;
- constraints preserve every row trace and column trace up to explicitly
  represented local permutations;
- parent matrix isomorphisms are forbidden by a rigid asymmetric anchor;
- exact-label matrix globalizers are checked before binary expansion.

Begin with a paired trade formed from two overlapping Pasch-like modules in
which each module repairs the other's shortened columns.  Exhaust the module
coefficient space, then realize only zero-globalizer survivors.

### Stop condition

Close only the exact module basis and anchor stated in the experiment.  Stop
immediately if degree separation fails, if a parent invariant distinguishes
the sides, or if the trace equations force the invariant-row theorem's
hypotheses.  Do not scale Kocay's induced-deletion lift.

## 3. Deletion-local monodromy without a global conjugator

### Core idea

The cover experiments changed voltages but retained one quotient/gauge
description.  The exceptional-`S6` experiment used a functorial outer twist,
which has an automatic semilinear parent isomorphism.  The remaining group-
theoretic possibility is a pair of representations that become conjugate
after every relevant deletion, with conjugators that cannot be chosen
globally, coupled to a non-invariant anchor that destroys the semilinear map.

### First experiment

Use the known degree-180 `S6` Gassmann `V4` pair only as a control primitive.
Replace the full invariant 6/21-column anchors by a small asymmetric two-orbit
anchor and enumerate stabilizer double-coset cross relations.  Require:

1. equal parent degree data;
2. exact row- and anchor-deletion isomorphisms with explicit conjugators;
3. failure of every global carrier permutation, including the semilinear
   outer swap;
4. an explicit graph realization before any claim of progress.

The decisive object is the inconsistent family of local conjugators, not a
larger voltage alphabet.

### Stop condition

Stop if the anchor is functorial under the outer automorphism, if carrier
types become reconstructible from degrees, or if deletion conjugators satisfy
a common global conjugacy equation.  Close only the chosen group, subgroups,
and double-coset family.

## Strong alternatives, not top three

- **Complement-closed decks at order 17.**  The self-complementary-card
  reduction is clean and direct, but it is a special case of the shared-card
  fibre architecture and the existing run is incomplete and hash-dependent.
- **Ivanov auxiliary-deletion repair.**  High overlap is real, but every
  attempted parity repair has either theorem-collapsed or retained unmatched
  auxiliary deletion types.  It needs a new graph-native synchronizer before
  more parameter scaling is justified.
- **Order-8 named-colour census.**  This is an instrument frontier, not a CE
  architecture; the measured runtime makes the current implementation a poor
  first Astra experiment.
