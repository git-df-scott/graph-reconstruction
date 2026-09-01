# Complementary Goldilocks direct strike

Date: 2026-09-01

## Verdict

`GRC CE: NO`

Two complementary Goldilocks constraints do **not** kill the final two
exact-label globalizers.  Complementary residual pairs do occur, and their
set intersection is empty, but coupling them regenerates a larger symmetry.
The exact obstruction has two forms:

1. joining two completed Goldilocks terminals regenerates `S4` or `S5` and
   always introduces identity;
2. in the genuine simultaneous six-row CSP, two distinct matching-class
   merges transitively merge all three matching classes, after which identity
   is forced in every one of the 54 legitimate terminals.

The strongest simultaneous terminal retains ten incidence classes and has
exactly one globalizer, identity.  Thus this strike improves the constrained
minimum from two to one, but cannot reach zero.

## Recovery

The requested local campaign hash `5854051` was not on the recovered remote
history.  The same single-merge result is present as:

```text
dae7492 Classify single-merge escape obstruction
2d5f352 Update Sol 2 with single-merge strike
```

Those artifacts were used directly.  No old census or generic graph
enumeration was rerun.

## The nine minimum terminals

Each of the three Goldilocks merges has exactly three two-globalizer
terminals: one information-rich nine-class terminal and two five-class
terminals.

| Merge | Terminals | Class profiles | Residual rescue pair |
|---|---:|---|---|
| `01` | 3 | one `8,8,8,4,4,4,2,2,2`; two `12,10,10,8,2` | `(03)`, `(12)` |
| `02` | 3 | one `8,8,8,4,4,4,2,2,2`; two `12,10,10,8,2` | `(23)`, `(01)` |
| `12` | 3 | one `8,8,8,4,4,4,2,2,2`; two `12,10,10,8,2` | `(02)`, `(13)` |

Every rescue fixes vertices `4,5,6`.  The two transpositions in each pair are
disjoint and generate a four-element subgroup

```text
{1, a, b, ab} ~= V4.
```

This is not the usual transitive `V4` on four vertices: it has two two-point
orbits and three fixed points.  Its normalizer in `S7` has order 48.  The
setwise stabilizer of the two-element rescue pair also has order 48; it is
`(S2 wr S2) x S3`, preserving the two active pairs and permuting the three
fixed vertices.

Under the proved old `A4` action, all three rescue pairs form one orbit.  The
stabilizer of one pair inside `A4` is the old order-four kernel.  The three
distinct rescue pairs are pairwise disjoint as sets of `G -> H`
globalizers.  Thus the proposed complementary pairs genuinely exist.

## Exact old-rescuer witness failures

For each old rescue `p`, survival requires all six cross witnesses

```text
W_v(p): (G,{6,v}) ~ (H,{6,p(v)}).
```

Every minimum terminal kills every old rescue.  The failed witness vertices
are constant within each merge:

| Merge | Old rescue 0 | Old rescue 1 | Old rescue 2 | Old rescue 3 |
|---|---|---|---|---|
| `01` | `2,3` | `0,1` | `0,1` | `2,3` |
| `02` | `1,3` | `1,3` | `0,2` | `0,2` |
| `12` | `1,2` | `0,3` | `1,2` | `0,3` |

The frozen JSON certificate records the complete rows, labels, side arrays,
profiles, rescue sets, generated subgroups, and SHA-256 checksums of all nine
terminals.

## Pairwise joins of completed terminals

All `C(9,2) = 36` terminal pairs were joined exactly.  Of these, 27 pair
different Goldilocks merges and therefore have disjoint residual rescue
pairs.

| Pair type | Joined classes | Globalizers | Identity | Count |
|---|---:|---:|---|---:|
| Cross-merge | 7 | 24 | yes | 3 |
| Cross-merge | 4 | 120 | yes | 24 |
| Same-merge | 5 | 2 | no | 6 |
| Same-merge | 4 | 120 | yes | 3 |

The three best cross-merge joins regenerate full `S4` on active vertices
`{0,1,2,3}`, fixing `{4,5,6}`.  The other 24 regenerate full `S5` on
`{0,1,2,3,6}`, fixing `{4,5}`.  Consequently:

```text
residual intersection:          empty in 27/27 cross joins
new replacement globalizers:    present in 27/27 cross joins
identity regenerated:           27/27 cross joins
zero-globalizer joins:           0/27
minimum cross-join globalizers: 24
```

This proves that disjoint rescue torsors are not sufficient: their joint
incidence coarsening destroys the distinctions that selected the two
transpositions and restores a full symmetric action.

## Genuine simultaneous six-row CSP

Intersecting completed-terminal output could have missed legitimate
row-level states, so the actual simultaneous problem was solved separately.
Any two distinct pairs among `01,02,12` generate the same transitive old-class
relation:

```text
C0 ~ C1 ~ C2.
```

Thus all three choices of two constraints, and the nominal three-merge
relaxation, have exactly the same seed.  The four retained old classes are

```text
C012, C3, C4, C5.
```

Every deletion row was an actual permutation fixing the deleted vertex.

| Deleted row | Raw permutations | Compatible rows | Exact effects |
|---:|---:|---:|---:|
| 0 | 720 | 36 | 17 |
| 1 | 720 | 36 | 17 |
| 2 | 720 | 36 | 17 |
| 3 | 720 | 36 | 17 |
| 4 | 720 | 144 | 41 |
| 5 | 720 | 144 | 41 |
| **Total** | **4,320** | **432** | **150** |

The exact terminal DP layer counts are:

```text
1, 17, 59, 40, 42, 48, 54.
```

The complete terminal distribution is:

| Classes | Globalizers | Identity | Terminals |
|---:|---:|---|---:|
| 10 | 1 | yes | 1 |
| 9 | 2 | yes | 6 |
| 8 | 4 | yes | 3 |
| 8 | 6 | yes | 4 |
| 7 | 24 | yes | 1 |
| 6 | 2 | yes | 6 |
| 6 | 6 | yes | 16 |
| 6 | 24 | yes | 2 |
| 5 | 4 | yes | 6 |
| 5 | 12 | yes | 4 |
| 5 | 24 | yes | 2 |
| 5 | 48 | yes | 2 |
| 4 | 120 | yes | 1 |

Therefore the constrained hitting-set maximum is exactly

```text
5,039 / 5,040 parent permutations killed.
```

The unique forced survivor is identity.  No deletion-compatible selection
of one effect per row covers all of `S7`.

## Identity-forcing obstruction

Let

```text
I_v: (G,{6,v}) ~ (H,{6,v}),  v=0,...,5
```

be the six cross witnesses for identity.  Independent subset DPs give four
minimal forcing cores:

```text
rows {0,1,2}
rows {0,1,3}
rows {0,2,3}
rows {1,2,3}
```

Each core has 40 legitimate partial terminal partitions, and every one of
those partitions contains all six `I_v`.  No proper subset of any displayed
core forces all six.  Since every complete system contains all four active
deletion rows, identity is unavoidable before rows 4 and 5 are even needed.

This is the human-readable constrained-cover obstruction:

```text
two distinct Goldilocks merges
    => all three matching classes coalesce
    => any three active deletion rows force all identity witnesses
    => identity is an exact-label globalizer in every completion.
```

The failure mode is **C: symmetry regeneration**, caused by a specific
information collapse (**B**) in the perfect-matching quotient.  It is not
residual-pair intersection or row incompatibility.

## Strongest terminal

The strongest simultaneous terminal has profile

```text
12,8,8,2,2,2,2,2,2,2
```

and ten classes.  Both side arrays are exactly

```text
0,0,0,1,2,3,0,0,1,2,4,0,1,2,5,1,2,6,7,8,9
```

Its six old deletion rows are identity, its outside row is

```text
(0,2,3,1,4,5,6),
```

and its complete exact globalizer set is

```text
{(0,1,2,3,4,5,6)}.
```

Certificate SHA-256:

```text
382482492de0ae0218c810ffc723b7b664a7009a0c5c631810222d59f73fc80a
```

## Verification

Discovery and hostile verification share only the frozen slot convention.
The following checks agree:

- immutable union-find partition discovery;
- independent bit-set partition joins;
- independent bit-set row vocabularies and terminal DP;
- exact colored-complete-graph backtracking;
- raw replay of all 5,040 permutations for all 36 joined terminals;
- raw replay of all 5,040 permutations for all 54 simultaneous terminals;
- exact legitimacy checks for every deletion-fixed row;
- SHA-256 canonical serialization of terminals and joins.

No zero-globalizer gadget was found, so binary realization and legal-order
transport were correctly not run.

Runtime for the frozen hostile certificate was approximately 6.1 seconds.
Peak RSS was 15,360 KiB on the recorded run.

## Theorem status

**Computationally exhaustive finite theorem.**  Within the complete
deletion-fixed compatible-row domain over the certified resilient primitive,
coupling any two distinct Goldilocks matching-class merges cannot produce a
zero-globalizer system.  Completed-terminal joins have at least 24
globalizers.  The full simultaneous six-row CSP has at least one, with
identity forced by each of four minimal three-row cores.

The nominal all-three-merge extension is already covered because any two
distinct matching merges generate the same equivalence closure as all three.

This is not the Graph Reconstruction Conjecture and not a counterexample.

## Exact next strike

Further coarsening on this carrier is closed: it cannot undo an equivalence
and can only discard more information.  A successful next construction must
break the residual pair without transitively identifying all three matching
classes.  The precise missing ingredient is a deletion-level equivalence
that is not induced by a parent-level automorphism and does not coarsen the
perfect-matching quotient.

That identifies the useful bridge to pseudosimilarity:

```text
X-u ~= X-v without an automorphism sending u to v
```

supplies exactly deletion-level equivalence without parent symmetry.  The
next strike should import a certified asymmetric pseudosimilar core as a
second active carrier and couple it to the information-rich nine-class
Goldilocks terminal.  The acceptance test remains the empty exact-label
globalizer set; no binary realization should occur before that test passes.
