# Sol 3 — Complementary Goldilocks direct CE strike

Date: 2026-09-01

## Live status

```text
GRC CE: NO
```

No ordinary Kelly–Ulam counterexample was found in this session.  The exact
two-Goldilocks architecture was exhausted and closed with a new finite
obstruction theorem.

## Starting point and recovery

This session continued the graph-reconstruction campaign and did not rerun
the closed literature audit, small-graph enumerations, 53,281,250-state
order-six census, resilient-lift census, old coupling searches, universal
rescuer strike, or complete single-merge classification.

The requested local hash `5854051` was not in the recovered remote history.
The same mathematical result was recovered at:

```text
dae7492 Classify single-merge escape obstruction
2d5f352 Update Sol 2 with single-merge strike
```

The existing `single_merge_escape.py`, its tests, and
`SINGLE_MERGE_ESCAPE.md` were used as the authoritative inputs.

## Question attacked

The session decided exactly whether two Goldilocks constraints with
complementary residual two-rescuer torsors can kill all parent permutations
without collapsing incidence information or creating replacement symmetry.

The answer is:

```text
NO on the certified resilient carrier.
```

Complementary pairs do exist, but their coupling necessarily regenerates
identity and usually a much larger symmetric group.

## Strongest new result

The nine two-globalizer minima form three residual rescue pairs:

```text
merge 01 -> {(03),(12)}
merge 02 -> {(23),(01)}
merge 12 -> {(02),(13)}
```

They are pairwise disjoint and form one orbit under the old `A4`.  Each pair
generates a four-element subgroup and has normalizer/order-48 setwise
stabilizer in `S7`.

Nevertheless, all 27 cross-merge joins regenerate identity.  Three have
exactly 24 globalizers (`S4` on the active `K4`), and 24 have exactly 120
globalizers (`S5` on the active `K4` plus vertex 6).

The separately solved true simultaneous CSP is sharper.  Two distinct
matching merges imply

```text
C0 ~ C1 ~ C2.
```

Its complete six-row domain has 54 terminals, all with identity.  The unique
best terminal has ten classes, profile

```text
12,8,8,2,2,2,2,2,2,2
```

and exactly one globalizer: identity.  Thus the constrained maximum improves
from 5,038 to 5,039 killed permutations but cannot reach 5,040.

## Exact obstruction

For identity define cross witnesses

```text
I_v: (G,{6,v}) ~ (H,{6,v}),  v=0,...,5.
```

Four minimal row cores force all six witnesses:

```text
{0,1,2}, {0,1,3}, {0,2,3}, {1,2,3}.
```

Every core has 40 compatible partial terminals, all independently replayed.
Therefore every complete system contains identity before rows 4 and 5 can
help.  This is symmetry regeneration forced by information collapse, not a
failure to find disjoint torsors.

The nominal all-three-merge relaxation is also closed: any two distinct
matching merges already have the same transitive closure as all three.

## Counts

### Minimum torsors and joins

```text
two-globalizer Goldilocks minima: 9
distinct residual rescue pairs:   3
A4 orbits of rescue pairs:         1
all terminal pair joins:          36
cross-merge joins:                27
cross joins with disjoint pairs:  27
cross joins with identity:        27
zero-globalizer joins:             0
cross-join minimum globalizers:   24
```

### Simultaneous row CSP

```text
raw row trials:          4,320
compatible rows:           432
distinct row effects:      150
DP layers:        1,17,59,40,42,48,54
terminal partitions:        54
identity terminals:          54
zero-globalizer terminals:    0
minimum globalizers:          1
maximum S7 killed:  5,039 / 5,040
```

Compatible rows/exact effects by deletion are:

```text
rows 0,1,2,3: 36 / 17 each
rows 4,5:    144 / 41 each
```

## Independent verification

The hostile run used:

1. union-find discovery;
2. independently encoded bit-set joins;
3. independent bit-set row vocabularies and terminal DP;
4. exact colored-graph backtracking;
5. raw replay over all 5,040 permutations for all 36 joins;
6. raw replay over all 5,040 permutations for all 54 simultaneous terminals;
7. deletion-fixed permutation validation;
8. canonical JSON and SHA-256 terminal certificates.

All stacks agreed.  The hostile certificate took about 6.1 seconds and
recorded peak RSS of 15,360 KiB.

Binary realization was not run because zero globalizers were not reached.

## Artifacts created

```text
scripts/double_goldilocks_strike.py
tests/test_double_goldilocks_strike.py
docs/DOUBLE_GOLDILOCKS_STRIKE.md
docs/DOUBLE_GOLDILOCKS_CERTIFICATE.json
SOL_3.md
```

The JSON certificate freezes all nine minimum terminals, all 36 pairwise
joins, every simultaneous-CSP statistic, the strongest terminal, checksums,
and the independent verification metadata.

## Exact next strike

No further coarsening of this fixed matching-class carrier can repair the
obstruction.  The next construction must break a residual transposition pair
without merging a second pair among `C0,C1,C2`.

The now-precise bridge to pseudosimilarity is:

```text
deletion-level equivalence without parent-level automorphism.
```

The next strike should couple the information-rich nine-class Goldilocks
terminal to an asymmetric pseudosimilar core on a second active carrier, then
apply the same exact globalizer criterion before any realization.  This is a
proof-driven pivot; it does not reopen generic enumeration.
