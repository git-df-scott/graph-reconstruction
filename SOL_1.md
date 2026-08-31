# Sol 1

Date: 2026-08-31

Final mathematics tip: `ab55889`

Publication base after the literature-audit merge: `f089ccf`

Final verdict: **`GRC CE: NO`**

This is the complete ledger for the first cloud research session.  It records
the work performed, replayed, inherited from the shared campaign worktree,
verified, committed, and pushed.  No abstract nongluing system or partial deck
match is reported as a counterexample.

## Starting point

The session resumed after

```text
7e4339c — Classify frozen primitive rescue couplings
```

with the two-copy frozen primitive domain closed.  The immediate objective was
to mine the 3,181 nonidentity-rescued leaves of the completed order-six
3-cycle/double-transposition frontier, identify an extension-resilient
primitive, and frustrate its remaining parent permutations.

## Certificate replay

The existing repository was inspected before extension.  The following
certificates were replayed:

- full Python unit-test suite;
- same-carrier frozen primitive coupling: 1,440 exact systems;
- five-vertex-overlap order-seven coupling: 5,760 exact systems;
- strict separation of local maps, edge-class constraints, and binary graph
  realization;
- exact-label globalizer checks over all parent permutations.

The initial 14 tests passed.  The resilient-lift checkpoint reached 18 tests;
the final incidence-join and universal-rescuer repository has 26 passing
tests.

## Complete exceptional-leaf census

`scripts/extension_resilience_census.py` regenerated the complete source
frontier rather than trusting saved counts.

| 3-cycle rows | Canonical leaves | Nonidentity exceptions | Full relabel/side-reversal orbits | Legitimate lifts |
|---:|---:|---:|---:|---:|
| 0 | 95,280 | 5 | 3 | 19 |
| 1 | 126,630 | 7 | 6 | 238 |
| 2 | 843,885 | 63 | 34 | 1,628 |
| 3 | 2,250,202 | 246 | 62 | 2,994 |
| 4 | 3,000,200 | 642 | 117 | 3,074 |
| 5 | 2,000,120 | 1,251 | 142 | 2,142 |
| 6 | 533,388 | 967 | 103 | 1,315 |
| **Total** | **8,849,705** | **3,181** | **467** | **11,410** |

Every primitive globalizer was used as the outside-deletion row of a genuine
order-seven family.  Every resulting family passed deletion-map validation.

Primitive class distribution:

```text
2: 324, 3: 96, 4: 39, 5: 6, 6: 2
```

Lift class distribution:

```text
3: 10,056, 4: 186, 5: 640, 6: 482, 7: 38, 9: 8
```

Lift exact-globalizer distribution:

```text
2: 6, 3: 6, 4: 16, 6: 66, 8: 504,
10: 340, 16: 4,208, 72: 6,264
```

Result:

```text
zero-globalizer lifts:             0
assignment-specific separators:   0
```

## Joint Pareto recovery

Marginal histograms can falsely suggest that a low-rescuer count and a high
class count occur in the same lift.  `scripts/recover_priority_resilient_lift.py`
was therefore used to recover exact joint records.

Exact recoveries performed:

```bash
python3 scripts/recover_priority_resilient_lift.py --three-count 2 --progress 250000
python3 scripts/recover_priority_resilient_lift.py --three-count 4 --progress 500000
python3 scripts/recover_priority_resilient_lift.py --three-count 6 \
  --min-classes 9 --max-globalizers 4 --progress 250000
```

Results:

- `r=2`: 843,885 source leaves, 63 exceptions, 34 full orbits; no lift
  simultaneously has at most two globalizers and at least six classes;
- `r=4`: 3,000,200 source leaves, 642 exceptions, 117 full orbits; again no
  such joint Pareto lift;
- `r=6`: 533,388 source leaves, 967 exceptions, 103 full orbits; exactly eight
  nine-class/four-globalizer lifts, arising from four outside-map choices over
  each of two primitive orbits.

This killed the tempting inference obtained by combining unrelated marginal
histogram bins.

## Strongest recovered primitive

One strongest order-six primitive is

```text
(0,2,3,1,4,5)
(3,1,0,2,4,5)
(1,3,2,0,4,5)
(2,0,1,3,4,5)
(1,3,2,0,4,5)
(1,3,2,0,4,5)
```

Its legitimate order-seven lift is

```text
(0,2,3,1,4,5,6)
(3,1,0,2,4,5,6)
(1,3,2,0,4,5,6)
(2,0,1,3,4,5,6)
(1,3,2,0,4,5,6)
(1,3,2,0,4,5,6)
(0,2,3,1,4,5,6)
```

It retains all six old classes and has nine lifted classes with profile

```text
8,8,8,4,4,4,2,2,2.
```

Its four exact-label rescuers generate `A4` on vertices `0,1,2,3` and fix
`4,5,6`.  The rescue-set centralizer has order 6, its normalizer order 72,
and it has 70 conjugates in `S7`.

## Coupling searches

### Strongest same-orbit and cross-orbit families

`scripts/analyze_resilient_primitive_couplings.py` checked all four outside
rows on both sides, both relative side orientations, and every one of the
5,040 carrier twists.

| Domain | Systems | Zero globalizers | Binary separators |
|---|---:|---:|---:|
| Same primitive orbit | 161,280 | 0 | 0 |
| Two distinct primitive orbits | 161,280 | 0 | 0 |

Both domains produced the identical class histogram:

```text
1 class: 18,432
2 classes: 82,944
4 classes: 55,296
7 classes:  2,304, each with 24 globalizers
9 classes:  2,304, each with 4 globalizers
```

Thus changing primitive orbit did not change the rescue mechanism.

### Representative heterogeneous families

Additional exact seven-vertex coupling domains included:

- nine-class/four-rescuer versus seven-class/three-rescuer: 10,080 systems,
  all identity-rescued;
- nine-class/four-rescuer versus four-class/two-rescuer: 10,080 systems, all
  identity-rescued in this representative domain;
- seven-class/three-rescuer self coupling: 10,080 systems, no zero;
- seven-class/three-rescuer versus eight-rescuer lift: 10,080 systems, no
  zero;
- tiny two-rescuer Pareto self and mixed domains, all globally rescued.

The structural outcome was a trichotomy:

1. aligned joins retain the four `A4` rescuers;
2. partial frustration enlarges rescue to `S4`, producing 24 globalizers;
3. stronger frustration coarsens the partition until both sides become
   identical and identity globalizes every binary assignment.

## Heterogeneous incidence-join strike

The shared worktree then advanced through

```text
930f41c — Classify heterogeneous incidence joins
```

`scripts/incidence_join_strike.py` classified 186,624 legitimate
cycle-insertion extension systems and 128 fixed-carrier incidence signatures.
All remained rescued.  This domain is closed and was preserved in the final
push; its full certificate is `docs/INCIDENCE_JOIN_STRIKE.md`.

## Universal-rescuer strike

The campaign next reached

```text
ab55889 — Prove universal rescuer forcing obstruction
```

`scripts/kill_universal_rescuer.py` removed the cycle-insertion restriction.
For every old deletion it admitted every permutation in `S7` fixing the
deleted vertex, subject only to retaining all six old primitive classes.

Exact domain:

```text
raw deletion-fixed rows:                4,320
compatible rows:                           84
distinct exact row effects:                78
complete terminal partitions:               5
minimum terminal globalizers:                4
zero-globalizer terminals:                   0
```

The universal rescuer

```text
r1 = (1,3,2,0,4,5,6)
```

survives exactly when six cross-edge witnesses hold.  Minimal row subsets
forcing all six are

```text
{0,2}, {1,2}, {2,3}, {2,4}, {2,5}, {0,1,3}.
```

This proved that rescue persistence is not merely a cycle-insertion artifact.
The full result is `docs/UNIVERSAL_RESCUER_STRIKE.md`.

## Source files added

```text
docs/RESILIENT_LIFT_COUPLING_STRIKE.md
docs/INCIDENCE_JOIN_STRIKE.md
docs/UNIVERSAL_RESCUER_STRIKE.md
scripts/analyze_resilient_lift_couplings.py
scripts/analyze_resilient_primitive_couplings.py
scripts/extension_resilience_census.py
scripts/recover_priority_resilient_lift.py
scripts/incidence_join_strike.py
scripts/kill_universal_rescuer.py
tests/test_incidence_join.py
tests/test_universal_rescuer.py
```

## Existing files strengthened

```text
README.md
scripts/local_gluing_search.py
tests/test_local_gluing.py
```

`scripts/local_gluing_search.py` gained strict validation requiring exactly
one genuine permutation row per deletion and requiring every row to fix its
deleted vertex.  Verification now rejects malformed maps and parent-size
mismatches.

Frozen regressions were added for:

- malformed deletion rows;
- seven-class double-transposition lift;
- disjoint-rescue side-symmetric coupling;
- nine-class `A4` lift;
- heterogeneous incidence joins;
- universal-rescuer terminal classification.

## Commands and checks run

Core verification:

```bash
python3 -m unittest discover -s tests -v
find scripts src -type f -name '*.py' -print0 | xargs -0 python3 -m py_compile
git diff --check
```

The final suite result was:

```text
26 tests, 26 passed
```

Targeted discovery/replay commands included:

```bash
python3 scripts/analyze_primitive_couplings.py
python3 scripts/analyze_partial_overlap_couplings.py
python3 scripts/extension_resilience_census.py --three-count R
python3 scripts/recover_priority_resilient_lift.py --three-count R
python3 scripts/analyze_resilient_primitive_couplings.py
python3 scripts/analyze_resilient_lift_couplings.py --first TYPE --second TYPE
python3 scripts/incidence_join_strike.py
python3 scripts/kill_universal_rescuer.py
```

Here `R` was instantiated over the required strata `0,...,6`, and `TYPE` over
the documented Pareto representatives.  Temporary JSONL outputs were used for
long source recoveries; they were scratch artifacts and were not committed.

## Resource discipline

- no generic graph enumeration beyond existing six-vertex controls;
- no blind increase of graph order;
- all large source spaces streamed rather than stored as giant tables;
- the seven source strata took about 19 minutes total wall time on the cloud
  host;
- joint `r=2`, `r=4`, and `r=6` recoveries were bounded finite jobs;
- the 322,560 strongest coupling systems were streamed with exact `S7`
  checks;
- the final universal-rescuer CSP took about 0.81 seconds and 13,184 KiB peak
  RSS.

## Commits and GitHub publication

Work was preserved in this sequence:

```text
7919b80  Classify resilient lift rescue couplings
d1c04e3  Document complete extension resilience census
930f41c  Classify heterogeneous incidence joins
ab55889  Prove universal rescuer forcing obstruction
```

The complete eight-commit mathematics history, from `baae75a` through
`ab55889`, was pushed to
`https://github.com/git-df-scott/graph-reconstruction` on branch `main`.
Remote and local tips were independently read back as `ab55889`.  No access
token was stored in the repository, remote URL, Git configuration, or commit
history.  The remote literature-audit branch was subsequently merged at
`f089ccf`; this Sol 1 ledger was rebased on top of that merge so neither line
of work was overwritten.

## False leads killed

- one prescribed local map must globalize;
- two copies of the frozen primitive can frustrate rescue without collapse;
- a favorable class-count bin and a favorable rescue-count bin necessarily
  belong to the same lift;
- changing between the two strongest primitive orbits changes the coupling
  obstruction;
- cycle-insertion restrictions are responsible for the universal rescuer;
- a surviving abstract globalizer can be removed by binary assignment.

The last item is an exact implication: an exact-label globalizer survives
every binary coloring of the edge classes.

## Live successor

The smallest justified next strike is to relax exactly one hypothesis of the
universal-rescuer theorem: merge one controlled pair of the six old primitive
classes, then recompute the complete deletion-fixed row vocabulary.

The target merge must destroy the row-2 forcing core while avoiding the known
`S4`/`S5` side-symmetry regimes.  There are only 15 unordered old-class pairs,
so this is an exact structural classification problem, not a reason to scale
the graph order.

If a zero exact-label globalizer appears, freeze it immediately, solve binary
assignment-specific separation, construct the parent graphs, compare complete
decks with multiplicity using both exact implementations, and hostilely test
parent nonisomorphism.
