# Resilient-lift rescue-frustration strike

Date: 2026-08-31

## Verdict

`GRC CE: NO`

No zero-globalizer system and no binary assignment-specific separator was
found in the exact domains below.

## Complete exceptional-leaf census

The completed length-two source frontier contains 8,849,705 residual-
centralizer canonical leaves.  Exactly 3,181 require a nonidentity rescue.
Full relabeling and side reversal reduce them to 467 primitive orbits.  Every
exact-label globalizer of every orbit was then used as the outside-deletion
row of a legitimate one-vertex lift, producing 11,410 order-seven families.

| Number of 3-cycle rows | Source leaves | Nonidentity exceptions | Full orbits | Legitimate lifts |
|---:|---:|---:|---:|---:|
| 0 | 95,280 | 5 | 3 | 19 |
| 1 | 126,630 | 7 | 6 | 238 |
| 2 | 843,885 | 63 | 34 | 1,628 |
| 3 | 2,250,202 | 246 | 62 | 2,994 |
| 4 | 3,000,200 | 642 | 117 | 3,074 |
| 5 | 2,000,120 | 1,251 | 142 | 2,142 |
| 6 | 533,388 | 967 | 103 | 1,315 |
| **Total** | **8,849,705** | **3,181** | **467** | **11,410** |

The 467 primitive orbits have class-count distribution

```text
classes 2: 324
classes 3:  96
classes 4:  39
classes 5:   6
classes 6:   2
```

The legitimate lifts have these exact distributions:

```text
lift classes:      3: 10,056; 4: 186; 5: 640; 6: 482; 7: 38; 9: 8
old classes kept:  2: 10,056; 3: 822; 4: 486; 5: 38; 6: 8
globalizers:       2: 6; 3: 6; 4: 16; 6: 66; 8: 504;
                  10: 340; 16: 4,208; 72: 6,264
```

There are zero zero-globalizer lifts and zero assignment-specific
separators.  The histograms are marginal: exact joint recovery additionally
proved that no lift in the `r=2` or `r=4` strata simultaneously has at most
two rescuers and at least six classes.  This prevents the misleading
combination of separately favorable histogram bins.

## Assignment-specific strike

For a parent permutation `p`, let `E_p` be the set of unequal edge-class
pairs which must receive the same binary value for `p` to map `G` to `H`.
An assignment separates the parents exactly when

```text
for every p, some (a,b) in E_p has c[a] != c[b].
```

An exact-label globalizer has `E_p` empty.  It therefore survives every
binary assignment.  Consequently the reported resilient lifts with two or
three exact-label globalizers cannot be separated individually.  Binary
coarsening can create additional isomorphisms but cannot destroy an
exact-label one.

This closes Strike A for every lift having a nonempty exact-label globalizer
set.  The SAT/CSP solver becomes relevant only after coupling removes all
empty `E_p` conditions.

## Strongest recovered lift: nine classes, four rescuers

A newer saved parallel artifact exposed the strongest information-retaining
primitive in this strike.  Its order-six maps are

```text
(0,2,3,1,4,5)
(3,1,0,2,4,5)
(1,3,2,0,4,5)
(2,0,1,3,4,5)
(1,3,2,0,4,5)
(1,3,2,0,4,5)
```

It has six old classes.  Using `(0,2,3,1,4,5)` for outside deletion gives
the legitimate lift

```text
(0,2,3,1,4,5,6)
(3,1,0,2,4,5,6)
(1,3,2,0,4,5,6)
(2,0,1,3,4,5,6)
(1,3,2,0,4,5,6)
(1,3,2,0,4,5,6)
(0,2,3,1,4,5,6)
```

The lift has nine classes, with profile

```text
8,8,8,4,4,4,2,2,2
```

and side arrays

```text
G: 2 1 0 3 4 5 0 1 3 4 5 2 3 4 5 3 4 5 6 7 8
H: 0 2 1 3 4 5 1 2 3 4 5 0 3 4 5 3 4 5 6 7 8
```

Its four exact-label globalizers are

```text
(0,2,3,1,4,5,6)
(1,3,2,0,4,5,6)
(2,0,1,3,4,5,6)
(3,1,0,2,4,5,6).
```

They generate a group of order twelve.  Its centralizer has order six, its
subgroup normalizer order 144, and the rescue-set normalizer order 72, giving
70 rescue-set conjugates.

### Nine-class self-coupling

Every one of the 5,040 twists in both relative orientations was checked.

| Coupled classes | Systems |
|---:|---:|
| 1 | 1,152 |
| 2 | 5,184 |
| 4 | 3,456 |
| 7 | 144 |
| 9 | 144 |

All 10,080 systems have an exact-label globalizer.  Precisely the 144
nine-class systems retain all four rescuers.  Every twist with empty
orientation-correct rescue intersection has at most seven classes and is
identity-rescued.  The 144 nine-class systems have exactly four globalizers;
zero assignment separators exist.

The saved family-level cross-check is broader than the representative run.
For each of two distinct strongest primitive orbits it takes all four
legitimate outside-globalizer lifts.  It checks every ordered pair of lift
choices, both relative orientations, and all 5,040 twists:

- 161,280 same-orbit couplings;
- 161,280 cross-orbit couplings.

The two domains have the identical histogram

```text
classes 1: 18,432
classes 2: 82,944
classes 4: 55,296
classes 7:  2,304, each with 24 globalizers
classes 9:  2,304, each with 4 globalizers.
```

Zero systems in either 161,280-system domain have zero exact-label
globalizers or a binary separator.  Independent replay to a JSON certificate
agreed exactly with these counts.

An initial ranking report incorrectly labeled 72 side-reversed nine-class
systems as having empty old-rescue intersection because it compared against
`R` instead of `R^-1`.  The exact globalizer computation was unaffected.  An
orientation-aware replay proves that all 144 retain all four rescuers.

### Nine-class mixed couplings

Against the seven-class/three-rescuer lift, all 10,080 systems are
identity-rescued and have one, two, or three classes, with counts 5,184,
4,320, and 576.

Against the five-class/two-rescuer lift, the distribution is 5,760 one-class,
4,032 two-class, and 288 three-class systems.  The first two groups are
identity-rescued.  The 288 three-class systems have empty old-rescue
intersection but exactly 16 newly created globalizers each.  No separator
exists.

## Earlier seven-class/three-rescuer lift

The homogeneous double-transposition stratum has three full relabeling and
side-reversal orbits among its five anchored nonidentity exceptions.  Every
primitive has five old edge classes, all nineteen legitimate lifts retain all
five, and every lift has seven total classes.

The strongest primitive maps are

```text
(0,1,3,2,5,4)
(0,1,3,2,5,4)
(3,4,2,0,1,5)
(2,5,0,3,4,1)
(2,5,0,3,4,1)
(3,4,2,0,1,5)
```

Its two-sided old edge-class arrays, in lexicographic edge order, are

```text
G: 4 0 0 1 2 1 2 3 3 0 2 4 4 1 3
H: 4 0 0 2 1 2 1 3 3 0 1 4 4 2 3
```

The three primitive exact-label globalizers are

```text
(0,1,3,2,5,4)
(2,5,0,3,4,1)
(3,4,2,0,1,5)
```

Using the first as the outside-deletion map gives the legitimate order-seven
family

```text
(0,1,3,2,5,4,6)
(0,1,3,2,5,4,6)
(3,4,2,0,1,5,6)
(2,5,0,3,4,1,6)
(2,5,0,3,4,1,6)
(3,4,2,0,1,5,6)
(0,1,3,2,5,4,6)
```

Its seven classes all have size six among the 42 two-sided edge slots.  Its
class arrays are

```text
G: 6 0 0 1 2 3 1 2 4 4 5 0 2 6 3 6 1 3 4 5 5
H: 6 0 0 2 1 3 2 1 4 4 5 0 1 6 3 6 2 3 4 5 5
```

The lift retains exactly the same three rescuers, extended by fixing vertex
6.

## Group-theoretic rescue structure

All three rescuers have cycle type `2+2`.  They generate a group of order six
with vertex orbits

```text
{0,2,3}, {1,4,5}, {6}.
```

The generated group has centralizer order two and normalizer order twelve.
The rescue-set normalizer also has order twelve, giving 420 rescue-set
conjugates and 44 report-only rescue-normalizer double cosets in `S7`.

The rescue set consists of `G`-to-`H` bijections and is not treated as a
subgroup.  Its generated subgroup and normalizers are descriptive ranking
invariants only.  No twists were pruned by those invariants.

## Same-resilient-lift coupling

The exact domain comprises every one of the 5,040 simultaneous vertex twists
in each of two relative side orientations, for 10,080 systems.  Each system
contains two complete legitimate seven-card map families.  Every parent
permutation was searched by exact color-preserving backtracking; all
high-class outcomes had their complete globalizer sets enumerated.

| Coupled classes | Systems |
|---:|---:|
| 1 | 7,776 |
| 2 | 1,224 |
| 3 | 936 |
| 5 | 120 |
| 7 | 24 |

Results:

- zero zero-globalizer systems;
- zero binary separators;
- all 10,056 systems having fewer than seven classes are rescued by identity;
- the 24 seven-class systems retain all three original rescuers;
- the 120 five-class systems have exactly 36 globalizers each;
- among those 120, 48 have disjoint old rescue sets and 72 retain one old
  rescuer.

Thus all 9,264 twists with disjoint old rescue sets are nevertheless rescued
by identity.  A representative disjoint-rescue five-class twist is

```text
(0,4,2,3,5,1,6).
```

For it, the coupled `G`- and `H`-side class arrays are literally identical:

```text
1 0 0 1 1 2 1 1 3 3 4 0 1 1 2 1 1 2 3 4 4
```

## Mixed-resilient coupling

The three-rescuer lift was coupled with a representative seven-class lift
from the eight-rescuer homogeneous-double orbit.  Again all 5,040 twists and
both relative orientations were checked, for 10,080 exact systems.

| Coupled classes | Systems |
|---:|---:|
| 1 | 8,064 |
| 2 | 1,344 |
| 3 | 672 |

Every system is identity-rescued.  Zero systems retain more than three
classes, zero have no exact-label globalizer, and zero have a binary
separator.

## Tiny-rescue Pareto lift

Targeted recovery of both minimum-rescuer strata established that the
requested two-rescuer lift with at least six classes does not exist there.

- In `r=2`, the two two-rescuer lifts have four classes.  The 66 six-class
  lifts have 6, 8, or 16 exact rescuers.
- In `r=4`, zero lifts have both at most two rescuers and at least six
  classes.  The best tiny-rescuer lift has two rescuers and five classes.

The latter lift is

```text
(0,2,3,1,4,5,6)
(2,1,3,0,4,5,6)
(4,5,2,3,0,1,6)
(4,5,2,3,0,1,6)
(0,1,5,2,4,3,6)
(0,1,4,2,3,5,6)
(0,1,3,2,4,5,6)
```

with exact-label rescuers

```text
(0,1,3,2,4,5,6)
(4,5,2,3,0,1,6).
```

### Tiny-rescue self-coupling

All 5,040 twists in both relative orientations were checked, for 10,080
systems.

| Coupled classes | Systems |
|---:|---:|
| 1 | 8,448 |
| 2 | 1,552 |
| 3 | 64 |
| 4 | 8 |
| 5 | 8 |

Every system has an exact-label globalizer.  The eight five-class systems
retain the original two rescuers.  The eight four-class systems retain one
old rescuer but have eight complete globalizers.  Zero systems have a binary
separator.

### Tiny-rescue mixed couplings

Coupling the two-rescuer lift with the three-rescuer/seven-class lift gives
8,640 one-class and 1,440 two-class systems.  All 10,080 systems are
identity-rescued.

Coupling it with the eight-rescuer/seven-class representative gives 8,576
one-class, 1,472 two-class, and 32 four-class systems.  Every system has an
exact-label globalizer; each four-class system has eight.  Again there are no
binary separators.

## Incidence-join obstruction

For two two-sided edge partitions `P_A` and `P_B`, form a bipartite graph with
one left vertex per `P_A` class, one right vertex per `P_B` class, and one edge
for every two-sided edge slot joining the two classes containing that slot.
The coupled edge classes are exactly the connected components of this graph.

This gives the structural comparison sought by the Iron Man protocol:

- extension resilience means the single-lift incidence structure retains the
  five old components and adds two cross-edge components;
- twisting two resilient copies joins swapped asymmetric classes;
- whenever the coupling does not preserve the full seven-class structure, the
  join makes the two parent-side class arrays identical;
- identity then globalizes every assignment, even when the original rescue
  sets are disjoint.

The frozen primitive usually collapsed all the way to one component.  The
resilient primitive can stop at two, three, or five components, but the
relevant obstruction is stronger than connectedness: the joined partition
becomes side-symmetric before the old rescuers are killed.

## Theorems extracted

**Assignment theorem.**  In the binary edge-class construction, the presence
of one exact-label globalizer makes assignment-specific separation
impossible.

**Same-lift coupling theorem (computationally exhaustive).**  Couple the
displayed seven-class, three-rescuer lift with any simultaneous relabeling of
itself or its side reversal.  Every one of the 10,080 coupled systems has an
exact-label globalizer.  All non-aligned outcomes are identity-globalized.

**Mixed-lift coupling theorem (computationally exhaustive).**  Couple the
displayed three-rescuer lift with the recovered eight-rescuer homogeneous
double-transposition lift under any simultaneous relabeling and either side
orientation.  Every one of the 10,080 systems is identity-globalized and has
at most three classes.

**Tiny-rescue coupling theorem (computationally exhaustive).**  For the
displayed two-rescuer/five-class lift, all 10,080 self-couplings and all
20,160 mixed couplings with the three- and eight-rescuer representatives have
an exact-label globalizer.  The three-rescuer mixed domain is entirely
identity-globalized; the eight-rescuer mixed domain retains at most four
classes.

**Nine-class coupling theorem (computationally exhaustive).**  The displayed
nine-class/four-rescuer lift has an exact-label globalizer in all 10,080
self-couplings and all 20,160 mixed couplings with the displayed three- and
two-rescuer Pareto lifts.  Empty rescue intersection forces the self-coupling
to at most seven classes and identity rescue; in the two-rescuer mixed domain
the best frustrated systems have three classes and 16 new globalizers.
Moreover, all 322,560 ordered same- and cross-orbit couplings across the four
outside-map choices have a globalizer; their only informative outcomes have
seven classes with 24 globalizers or nine classes with four.

These are finite theorems about the stated systems, not GRC.

## Verification and reproduction

Run

```bash
python3 scripts/analyze_resilient_lift_couplings.py --second r3
python3 scripts/analyze_resilient_lift_couplings.py --second r8
python3 scripts/analyze_resilient_lift_couplings.py --first r2 --second r2
python3 scripts/analyze_resilient_lift_couplings.py --first r2 --second r3
python3 scripts/analyze_resilient_lift_couplings.py --first r2 --second r8
python3 scripts/analyze_resilient_lift_couplings.py --first r4 --second r4 \
  --globalizer-min-classes 8
python3 scripts/analyze_resilient_lift_couplings.py --first r4 --second r3 \
  --globalizer-min-classes 7
python3 scripts/analyze_resilient_lift_couplings.py --first r4 --second r2 \
  --globalizer-min-classes 3
python3 -m unittest discover -s tests -v
```

The discovery code checks all raw twists rather than trusting a rescue-set
quotient.  The repository's independent exact graph/deck routines remain the
mandatory hostile-verification path if a separator is ever found.

## Next strike

Leave same-carrier pairwise coupling of these representative lift types.
The next local-map construction should impose a heterogeneous extension rule
whose incidence join can remain neither collapsed nor side-symmetric when
the old rescue intersection is empty.  A useful exact successor is to
classify extension rows by the induced bipartite class-incidence signature,
discarding every signature that forces side symmetry before constructing
larger carriers.
