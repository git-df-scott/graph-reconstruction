# Single-merge escape strike

Date: 2026-08-31

## Verdict

`GRC CE: NO`

All 15 one-pair old-class merges are closed.  Three Goldilocks merges destroy
the complete old A4 rescue torsor and reduce the minimum total exact-label
globalizer count from four to two.  No merge reaches zero.

## A4 action on the six old classes

On the G side, the six old classes have the following structural supports:

```text
C0: the K4 perfect matching {03,12}
C1: the K4 perfect matching {02,13}
C2: the K4 perfect matching {01,23}
C3: all four edges from {0,1,2,3} to vertex 4
C4: all four edges from {0,1,2,3} to vertex 5
C5: edge {4,5}
```

The rescue-generated vertex group is A4 of order 12 on `{0,1,2,3}`, fixing
`{4,5}`.  Its induced class action is the cyclic quotient

```text
A4 / V4 ~= C3,
```

which cycles `C0,C1,C2` and fixes `C3,C4,C5`.  Thus the six classes are not
the natural six-edge A4 set `E(K4)`: the first three are the three perfect
matchings, while the last three are fixed attachment classes.

The 15 raw pairs split into seven proved class-action orbits:

```text
{01,02,12}
{03,13,23}
{04,14,24}
{05,15,25}
{34}
{35}
{45}
```

Raw replay of all 15 pairs remains the correctness certificate.

## Static merge classification

The three internal matching merges `01,02,12` and attachment merge `34`
increase the old six-vertex exact-globalizer count from four to eight.

- An internal matching merge generates full S4 on `{0,1,2,3}`.
- Merge `34` generates `A4 x C2`, with the extra factor swapping vertices 4
  and 5.
- The remaining eleven merges retain four old globalizers, unequal side
  arrays, and no identity globalizer.

This exposed an important correction to the proposed early taxonomy:
immediate old-side enlargement is not sufficient to prove a merge dead.  The
extension rows can later destroy that enlarged torsor.  Consequently all four
statically enlarged cases were checked rather than prematurely pruned.

Old two-sided class profiles by orbit are:

| Merge orbit | Profile after one merge |
|---|---|
| `01/02/12` | `8,8,8,4,2` |
| `03/13/23` | `12,8,4,4,2` |
| `04/14/24` | `12,8,4,4,2` |
| `05/15/25` | `8,8,6,4,4` |
| `34` | `16,4,4,4,2` |
| `35` | `10,8,4,4,4` |
| `45` | `10,8,4,4,4` |

## Final merge taxonomy

After complete row compatibility and terminal classification:

```text
Type I  — useless / r1 always survives:          11
Type II — overmerged / identity already forced:   0
Type III — unavoidable regeneration:              1
Type IV — Goldilocks / all old rescues can die:    3
```

Exact pairs:

```text
Type IV: 01, 02, 12
Type III: 34
Type I: all remaining pairs
```

The three Type IV merges are exactly the orbit of pairs among the three
perfect-matching classes.

## Witness systems

Every single merge coarsens the old partition, so every original rescue still
satisfies its old-edge equations at the seed.  For each old rescue `p`, its
survival remains equivalent to six cross-edge relations:

```text
W_v(p): (G,{6,v}) ~ (H,{6,p(v)}),  v=0,...,5.
```

No cross witness is automatic at any merged seed.  Each six-relation family
is partition-level irredundant.  For the eleven Type I merges, the old
six-class forcing cores survive unchanged under the complete row CSP.  For
the three matching-class merges, all four old forcing systems are damaged:
three of the nine terminal partitions have zero surviving old rescuers.

## Row vocabularies

Every merge was replayed against all `6! = 720` deletion-fixed permutations
for every old deletion row.

| Merge regime | Compatible rows by deletion | Exact effects by deletion |
|---|---|---|
| Matching Goldilocks `01/02/12` | `16,16,16,16,48,48` | `13,13,13,13,25,25` |
| Ordinary Type I | `9,9,9,9,24,24` | `9,9,9,9,21,21` |
| Attachment regeneration `34` | `18,18,18,18,24,24` | `12,12,12,12,21,21` |

Across all raw merges this is 64,800 raw row trials, 1,524 compatible rows,
and 1,254 exact incidence effects counted within their merge/deletion
vocabularies.  No cycle-insertion or fixed-6 restriction was used.

## Six-row CSP and terminal partitions

Each merge was solved by exact state propagation.  Independent union-find and
bit-set dynamic programs agreed on every terminal partition.

For every matching Goldilocks merge the layer counts are, up to the anchored
row-order difference for merge `02`:

```text
01/12: 1,13,15,7,7,8,9
02:    1,13,33,7,7,8,9
```

Each has exactly nine terminals with identical histogram:

| Classes | Globalizers | Terminals per merge |
|---:|---:|---:|
| 9 | 2 | 1 |
| 8 | 8 | 1 |
| 7 | 8 | 2 |
| 6 | 16 | 2 |
| 5 | 8 | 1 |
| 5 | 2 | 2 |

Exactly three terminals per Goldilocks merge kill `r1` and all other old A4
rescuers.

Goldilocks Level-1 discovery CSP metrics:

| Merge | Nodes | Old-class prunes | Witness prunes |
|---|---:|---:|---:|
| `01` | 14 | 95 | 0 |
| `02` | 105 | 1,118 | 63 |
| `12` | 27 | 237 | 22 |

Aggregate terminal distribution over all 15 merges:

```text
2 globalizers:   9 terminals
4 globalizers:  35 terminals
8 globalizers:  38 terminals
16 globalizers:  6 terminals
24 globalizers:  1 terminal
total:           89 terminals
```

## Rescue regeneration and hitting-set result

The matching merges achieve genuine net rescue progress:

```text
old A4 rescuers surviving: 4 -> 0
total exact globalizers:   4 -> 2
```

The two unavoidable replacements are disjoint single transpositions on the
four active vertices.  They generate a `V4` subgroup together with their
product.  For the `01` representative they are

```text
(0 3) and (1 2), fixing {4,5,6}.
```

The other matching merges give the A4-conjugate pairs.  These are emergent
rescues, not surviving members of the old four-rescuer torsor.

The exhaustive legitimate terminal CSP is stronger than an unconstrained set
cover.  Evaluating every terminal distinction against all `7! = 5,040`
permutations proves:

```text
maximum permutations simultaneously killed: 5,038
minimum unavoidable exact globalizers:           2
```

Thus no mutually legitimate distinction set from a single merge covers all
of S7.

## Best terminal

The strongest information-retaining minimum has merge `01`, nine classes,
two exact globalizers, and profile

```text
8,8,8,4,4,4,2,2,2.
```

One exact representative uses deletion rows

```text
(0,2,1,3,4,5,6)
(3,1,2,0,4,5,6)
(3,1,2,0,4,5,6)
(0,2,1,3,4,5,6)
(0,2,1,3,4,5,6)
(0,2,1,3,4,5,6)
```

and outside row

```text
(0,2,3,1,4,5,6).
```

Its two globalizers are

```text
(0,2,1,3,4,5,6) = (1 2)
(3,1,2,0,4,5,6) = (0 3).
```

## Zero-globalizer and realization status

```text
zero-globalizer systems: 0
binary realization:      not run
legal-order construction: not reached
```

Binary realization was correctly skipped because two exact-label
globalizers remain in every minimum terminal.

## Theorem status

- **Proved:** the A4 action on old classes factors through `C3`, cycling the
  three perfect-matching classes and fixing the attachment classes; the 15
  merges have seven class-action orbits.
- **Computationally exhaustive:** all 15 raw merges, all 64,800 raw row trials,
  all compatible effects, all 89 terminal partitions, and minimum two
  globalizers.
- **Regression-exact:** all minimum terminals were checked by both exact
  backtracking and raw S7 replay.
- **Not claimed:** inevitability after two controlled merges or for another
  primitive.

## Verification and resources

- Every row independently validated as a permutation fixing its deletion.
- Discovery union-find and independent bit-set DP agree for every merge.
- Exact backtracking classified every terminal.
- Raw enumeration of all 5,040 permutations replayed all 44 merge-minimum
  terminals and agreed exactly.
- Full repository tests pass after adding the single-merge regressions.

The full 15-merge strike with hostile minimum replay used about 4.8 seconds
wall time and 14,464 KiB peak RSS on the final verification run.

## Next strike

Couple two **different** matching-class merge constraints whose unavoidable
transposition pairs are complementary, and solve their joint incidence CSP
up to the proved A4 orbit action.  The objective is to make the two residual
`V4` rescue torsors disjoint while retaining the nine-class profile.  This is
more targeted than allowing arbitrary two-merge coarsening.
